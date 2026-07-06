import argparse
import base64
from dataclasses import dataclass
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import requests


APP_NAME = "MediaHarbor"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://gimy01.com/",
}

UB1818_API_BASE = "https://api.ub1818.com"
UB1818_CLIENT_PRIVATE_KEY_ENV = "MEDIAHARBOR_UB1818_CLIENT_PRIVATE_KEY"
UB1818_CLIENT_PRIVATE_KEY_FILE = Path("secrets/ub1818_client_private_key.pem")
UB1818_SERVER_PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCeBQWotWOpsuPn3PAA+bcmM8YD
fEOzPz7hb/vItV43vBJV2FcM72Hdcv3DccIFuEV9LQ8vcmuetld98eksja9vQ1Ol
8rTnjpTpMbd4HedevSuIhWidJdMAOJKDE3AgGFcQvQePs80uXY2JhTLkRn2ICmDR
/fb32OwWY3QGOvLcuQIDAQAB
-----END PUBLIC KEY-----"""


@dataclass
class Episode:
    number: int
    title: str
    url: str


def sanitize_filename(name):
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned or "video"


def strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*m", "", text or "")


def parse_percent(percent_text):
    text = strip_ansi(percent_text).replace("%", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def notify(title, text):
    if sys.platform != "darwin":
        return

    subprocess.run(
        ["osascript", "-e", f'display notification "{text}" with title "{title}"'],
        check=False,
    )


def make_headers(referer=None):
    headers = DEFAULT_HEADERS.copy()
    if referer:
        headers["Referer"] = referer
    return headers


def fetch_text(url, headers=None, verify=True):
    response = requests.get(url, headers=headers or DEFAULT_HEADERS, timeout=(10, 30), verify=verify)
    response.raise_for_status()
    return response.text


def strip_tags(html):
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def extract_episode_number(text):
    patterns = [
        r"(?:第|EP?\s*|Episode\s*)(\d+)(?:集|話|话)?",
        r"(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def parse_player_data(html):
    match = re.search(r"var\s+player_data\s*=\s*(\{.*?\})\s*</script>", html, re.DOTALL)
    if not match:
        match = re.search(r"var\s+player_data\s*=\s*(\{.*?\})\s*;", html, re.DOTALL)
    if not match:
        raise ValueError("Could not find player_data in the Gimy page.")

    return json.loads(match.group(1))


def import_ub1818_crypto():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives.padding import PKCS7
    except ImportError as exc:
        raise RuntimeError("UB1818 support requires cryptography. Install it with: python -m pip install cryptography") from exc

    return serialization, asymmetric_padding, Cipher, algorithms, modes, PKCS7


def load_ub1818_client_private_key():
    private_key = os.environ.get(UB1818_CLIENT_PRIVATE_KEY_ENV)
    if private_key:
        return private_key.encode("utf-8")

    key_path = Path(__file__).resolve().parent / UB1818_CLIENT_PRIVATE_KEY_FILE
    if key_path.is_file():
        return key_path.read_bytes()

    raise RuntimeError(
        "UB1818 support requires a client private key. Set "
        f"{UB1818_CLIENT_PRIVATE_KEY_ENV} or create {UB1818_CLIENT_PRIVATE_KEY_FILE}."
    )


class Ub1818Client:
    def __init__(self, referer):
        serialization, asymmetric_padding, Cipher, algorithms, modes, PKCS7 = import_ub1818_crypto()
        self.asymmetric_padding = asymmetric_padding
        self.Cipher = Cipher
        self.algorithms = algorithms
        self.modes = modes
        self.PKCS7 = PKCS7
        self.private_key = serialization.load_pem_private_key(load_ub1818_client_private_key(), password=None)
        self.public_key = serialization.load_pem_public_key(UB1818_SERVER_PUBLIC_KEY)
        self.referer = referer

    def post(self, path, payload):
        filtered = filter_ub1818_payload(payload)
        query_string = urlencode(sorted(filtered.items())).lower()
        timestamp = str(int(time.time() * 1000))
        signature_base = f"-{query_string}-{timestamp}"
        signature = hashlib.md5(signature_base.encode("utf-8")).hexdigest()

        response = requests.post(
            f"{UB1818_API_BASE}{path}",
            data=self.encrypt_payload(payload),
            headers={
                "Content-Type": "application/json",
                "X-TOKEN": "",
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE": signature,
                "Origin": "https://ub1818.com",
                "Referer": self.referer,
                "User-Agent": DEFAULT_HEADERS["User-Agent"],
            },
            timeout=(10, 30),
        )
        response.raise_for_status()
        decoded = json.loads(self.decrypt_payload(response.text))
        if decoded.get("error") != 0:
            raise RuntimeError(decoded.get("message") or "UB1818 API returned an error.")
        return decoded.get("data") or {}

    def encrypt_payload(self, payload):
        key = "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(32))
        iv = b"abcdefghijklmnop"
        padder = self.PKCS7(128).padder()
        raw_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        padded = padder.update(raw_json) + padder.finalize()
        encryptor = self.Cipher(self.algorithms.AES(key.encode("utf-8")), self.modes.CBC(iv)).encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        encrypted_key = self.public_key.encrypt(key.encode("utf-8"), self.asymmetric_padding.PKCS1v15())
        return f"{base64.b64encode(encrypted).decode()}.{base64.b64encode(encrypted_key).decode()}"

    def decrypt_payload(self, payload):
        parts = payload.split(".", 1)
        if len(parts) != 2:
            raise RuntimeError("UB1818 API returned an unexpected response format.")

        encrypted_text, encrypted_key = parts
        key = self.private_key.decrypt(
            base64.b64decode(encrypted_key),
            self.asymmetric_padding.PKCS1v15(),
        )
        decryptor = self.Cipher(self.algorithms.AES(key), self.modes.CBC(b"abcdefghijklmnop")).decryptor()
        padded = decryptor.update(base64.b64decode(encrypted_text)) + decryptor.finalize()
        unpadder = self.PKCS7(128).unpadder()
        return (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")


def filter_ub1818_payload(payload):
    return {
        key: value
        for key, value in payload.items()
        if value not in ("", None, False) and value != 0 and value != "0"
    }


def extract_ub1818_video_id(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    video_ids = query.get("video_id") or query.get("id")
    if not video_ids:
        raise ValueError("UB1818 URL must contain video_id.")
    return int(video_ids[0])


def extract_ub1818_lid(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    values = query.get("lid")
    if not values:
        return None
    return int(values[0])


def resolve_ub1818_media(url, quality=1):
    video_id = extract_ub1818_video_id(url)
    requested_lid = extract_ub1818_lid(url)
    client = Ub1818Client(referer=url)

    info = client.post("/video/info", {"id": video_id})
    video = info.get("video") or {}
    fragments = info.get("video_fragment_list") or []
    if not fragments:
        raise ValueError("UB1818 did not return any episode fragments for this video.")

    fragment = next((item for item in fragments if item.get("id") == requested_lid), None) if requested_lid else None
    if fragment is None:
        fragment = fragments[0]

    available_qualities = fragment.get("qualities") or [1]
    selected_quality = quality if quality in available_qualities else available_qualities[0]
    if selected_quality >= 2:
        print("[W] UB1818 higher qualities may require login; falling back to site/API behavior if rejected.")

    source = client.post(
        "/video/source",
        {
            "video_id": video_id,
            "video_fragment_id": fragment["id"],
            "quality": selected_quality,
        },
    )
    video_source = source.get("video_soruce") or source.get("video_source") or {}
    media_url = video_source.get("url")
    if not media_url:
        raise ValueError("UB1818 source response did not contain a media URL.")

    base_title = video.get("title_tr") or video.get("title") or f"ub1818_{video_id}"
    symbol = fragment.get("symbol")
    title = f"{base_title}-第{symbol}集" if symbol else base_title
    return media_url, sanitize_filename(title), selected_quality


def extract_episode_links(html, base_url):
    link_pattern = re.compile(
        r"<a\b(?P<attrs>[^>]*)>(?P<label>.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )
    href_pattern = re.compile(r"""href\s*=\s*["'](?P<href>[^"']+)["']""", re.IGNORECASE)
    seen = set()
    episodes = []

    for match in link_pattern.finditer(html):
        href_match = href_pattern.search(match.group("attrs"))
        if not href_match:
            continue

        href = href_match.group("href").strip()
        if not href or href.startswith("#") or href.lower().startswith("javascript:"):
            continue

        label = strip_tags(match.group("label"))
        href_lower = href.lower()
        label_lower = label.lower()
        looks_like_episode = (
            "gimy" in urljoin(base_url, href).lower()
            or "play" in href_lower
            or "vodplay" in href_lower
            or "episode" in href_lower
            or "第" in label
            or "集" in label
            or "ep" in label_lower
        )
        number = extract_episode_number(label) or extract_episode_number(href)

        if not looks_like_episode or number is None:
            continue

        absolute_url = urljoin(base_url, href)
        if absolute_url in seen:
            continue
        seen.add(absolute_url)
        episodes.append(Episode(number=number, title=label or f"Episode {number}", url=absolute_url))

    return episodes


def find_canonical_page_url(html, base_url):
    patterns = [
        r"""<a\b[^>]*href=["'](?P<href>[^"']+)["'][^>]*>\s*(?:.+?播放列表|.+?劇情|.+?详情|.+?詳情|.+?返回.+?)\s*</a>""",
        r"""<a\b[^>]*(?:class|id)=["'][^"']*(?:detail|vod|info|show)[^"']*["'][^>]*href=["'](?P<href>[^"']+)["']""",
        r"""<link\b[^>]*rel=["']canonical["'][^>]*href=["'](?P<href>[^"']+)["']""",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            return urljoin(base_url, match.group("href"))
    return None


def discover_episodes(url):
    html = fetch_text(url)
    episodes = extract_episode_links(html, url)
    if episodes:
        return episodes

    canonical_url = find_canonical_page_url(html, url)
    if canonical_url and canonical_url != url:
        canonical_html = fetch_text(canonical_url)
        episodes = extract_episode_links(canonical_html, canonical_url)
        if episodes:
            return episodes

    raise ValueError(
        "Could not discover episode links. Try a Gimy title page, or download a single episode with the gimy command."
    )


def filter_episodes(episodes, from_episode=None, to_episode=None):
    filtered = []
    for episode in episodes:
        if from_episode is not None and episode.number < from_episode:
            continue
        if to_episode is not None and episode.number > to_episode:
            continue
        filtered.append(episode)
    return filtered


def dedupe_episodes_by_number(episodes):
    seen_numbers = set()
    unique_episodes = []
    for episode in episodes:
        if episode.number in seen_numbers:
            print(f"[I] Skip duplicate episode {episode.number}: {episode.url}")
            continue
        seen_numbers.add(episode.number)
        unique_episodes.append(episode)
    return unique_episodes


def make_batch_titles(episodes):
    width = max(2, max(len(str(episode.number)) for episode in episodes))
    titles = []
    for episode in episodes:
        episode_label = f"{episode.number:0{width}d}"
        titles.append(sanitize_filename(f"{episode_label}-第{episode_label}集"))
    return titles


def parse_m3u8_segments(m3u8_url, headers=None, verify=True):
    content = fetch_text(m3u8_url, headers=headers, verify=verify)
    segments = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        resolved_url = urljoin(m3u8_url, line)
        if line.endswith(".m3u8") or ".m3u8" in line:
            return parse_m3u8_segments(resolved_url, headers=headers, verify=verify)
        segments.append(resolved_url)

    if not segments:
        raise ValueError("The m3u8 playlist did not contain downloadable media segments.")

    return segments


def write_filelist(destination_path, file_names):
    path_filelist = destination_path / "filelist.txt"
    with path_filelist.open("w", encoding="utf-8") as ff:
        for file_name in file_names:
            ff.write(f"file '{file_name}'\n")
    return path_filelist


def download_file(url, destination, overwrite=False, headers=None, verify=True):
    if destination.exists() and not overwrite:
        print(f"[I] Skip existing {destination.name}")
        return

    print(f"[I] Downloading {destination.name}")
    with requests.get(
        url,
        headers=headers or DEFAULT_HEADERS,
        timeout=(10, 60),
        stream=True,
        verify=verify,
    ) as response:
        response.raise_for_status()
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)


def run_ffmpeg_concat(filelist_path, output_path, overwrite=False):
    ffmpeg_path = find_tool("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if ffmpeg_path is None:
        raise RuntimeError("ffmpeg was not found. Install ffmpeg or add it to PATH.")

    command = [
        ffmpeg_path,
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(filelist_path),
        "-c",
        "copy",
    ]
    if overwrite:
        command.append("-y")
    command.append(str(output_path))

    print(f"[I] Merging to {output_path}")
    run_command(command)


def find_tool(executable_name):
    candidates = []
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            [
                app_dir / executable_name,
                app_dir / "_internal" / executable_name,
            ]
        )
    else:
        candidates.append(Path(__file__).resolve().parent / executable_name)

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return shutil.which(executable_name)


def run_command(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )

    if process.stdout is not None:
        for line in process.stdout:
            print(line.rstrip())

    return_code = process.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)


def run_yt_dlp(
    media_url,
    output_template,
    extra_args=None,
    progress_callback=None,
    format_selector=None,
    overwrite=False,
):
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("yt-dlp was not found. Install it with: python -m pip install yt-dlp") from exc

    print("[I] Running yt-dlp")
    options = {
        "nocheckcertificate": True,
        "continuedl": True,
        "overwrites": overwrite,
        "merge_output_format": "mp4",
        "outtmpl": str(output_template),
        "logger": YtDlpLogger(),
        "progress_hooks": [make_yt_dlp_progress_hook(progress_callback)],
    }
    if format_selector:
        options["format"] = format_selector

    if extra_args:
        for index, value in enumerate(extra_args):
            if value == "--referer" and index + 1 < len(extra_args):
                options["referer"] = extra_args[index + 1]

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([media_url])


class YtDlpLogger:
    def debug(self, message):
        if message.startswith("[debug]"):
            return
        print(message)

    def warning(self, message):
        print(f"[W] {message}")

    def error(self, message):
        print(f"[E] {message}")


def make_yt_dlp_progress_hook(progress_callback=None):
    def hook(status):
        progress = normalize_yt_dlp_progress(status)
        if progress_callback:
            progress_callback(progress)
        yt_dlp_progress_hook(status, progress=progress)

    return hook


def normalize_yt_dlp_progress(status):
    percent = strip_ansi(status.get("_percent_str", "")).strip()
    speed = strip_ansi(status.get("_speed_str", "")).strip()
    eta = strip_ansi(status.get("_eta_str", "")).strip()
    filename = status.get("filename") or status.get("tmpfilename") or ""
    downloaded_bytes = status.get("downloaded_bytes")
    total_bytes = status.get("total_bytes") or status.get("total_bytes_estimate")
    return {
        "status": status.get("status"),
        "filename": filename,
        "percent": percent,
        "percent_float": parse_percent(percent),
        "speed": speed,
        "eta": eta,
        "downloaded_bytes": downloaded_bytes,
        "total_bytes": total_bytes,
    }


def yt_dlp_progress_hook(status, progress=None):
    progress = progress or normalize_yt_dlp_progress(status)
    if status.get("status") == "downloading":
        percent = progress.get("percent")
        speed = progress.get("speed")
        eta = progress.get("eta")
        filename = Path(progress.get("filename") or "").name
        parts = ["[I] Downloading"]
        if percent:
            parts.append(percent)
        if speed:
            parts.append(f"at {speed}")
        if eta:
            parts.append(f"ETA {eta}")
        if filename:
            parts.append(filename)
        print(" ".join(parts))
    elif status.get("status") == "finished":
        filename = progress.get("filename") or status.get("filename", "")
        print(f"[I] Downloaded {filename}")


def download_media_url(page_url, media_url, title, output_dir, method, overwrite, progress_callback=None):
    print(f"[I] Title: {title}")
    print(f"[I] Media URL: {media_url}")
    request_headers = make_headers(page_url)

    if method == "segments":
        if ".m3u8" not in media_url.lower():
            raise ValueError("Segment mode requires an m3u8 URL.")

        video_dir = output_dir / title
        video_dir.mkdir(parents=True, exist_ok=True)
        segment_urls = parse_m3u8_segments(media_url, headers=request_headers, verify=False)
        file_names = []

        for index, segment_url in enumerate(segment_urls):
            suffix = Path(segment_url.split("?", 1)[0]).suffix or ".ts"
            file_name = f"{index:06d}{suffix}"
            file_names.append(file_name)
            download_file(
                segment_url,
                video_dir / file_name,
                overwrite=overwrite,
                headers=request_headers,
                verify=False,
            )

        filelist_path = write_filelist(video_dir, file_names)
        output_path = video_dir / f"{title}.ts"
        run_ffmpeg_concat(filelist_path, output_path, overwrite=overwrite)
        print(f"[I] Done: {output_path}")
    else:
        output_template = output_dir / f"{title}.%(ext)s"
        run_yt_dlp(
            media_url,
            output_template,
            extra_args=["--referer", page_url],
            progress_callback=progress_callback,
            overwrite=overwrite,
        )
        print(f"[I] Done: {output_dir}")


def download_gimy_page(args):
    html = fetch_text(args.url)
    player_data = parse_player_data(html)

    media_url = player_data.get("url")
    if not media_url:
        raise ValueError("player_data did not contain a url field.")

    media_url = urljoin(args.url, media_url)
    vod_name = player_data.get("vod_data", {}).get("vod_name") or player_data.get("title") or "gimy_video"
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    title = sanitize_filename(args.title or vod_name)
    download_media_url(
        args.url,
        media_url,
        title,
        output_dir,
        args.method,
        args.overwrite,
        progress_callback=getattr(args, "progress_callback", None),
    )

    notify(APP_NAME, "Download finished!")


def download_ub1818_page(args):
    media_url, default_title, selected_quality = resolve_ub1818_media(args.url, quality=args.quality)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    title = sanitize_filename(args.title or default_title)
    print(f"[I] UB1818 quality: {selected_quality}")
    download_media_url(
        args.url,
        media_url,
        title,
        output_dir,
        args.method,
        args.overwrite,
        progress_callback=getattr(args, "progress_callback", None),
    )
    notify(APP_NAME, "Download finished!")


def is_youtube_playlist_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return "list" in query and ("playlist" in parsed.path.lower() or "watch" not in parsed.path.lower())


def download_youtube(args):
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    is_playlist = is_youtube_playlist_url(args.url)
    if is_playlist:
        if args.title:
            print("[W] --title is ignored for YouTube playlists to avoid overwriting files.")
        output_template = output_dir / "%(playlist_index)03d-%(title)s.%(ext)s"
    else:
        title = sanitize_filename(args.title) if args.title else "%(title)s"
        output_template = output_dir / f"{title}.%(ext)s"

    print("[I] Source: YouTube")
    print(f"[I] URL: {args.url}")
    print(f"[I] Output: {output_template}")
    run_yt_dlp(
        args.url,
        output_template,
        progress_callback=getattr(args, "progress_callback", None),
        format_selector="bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best[ext=mp4]/best",
        overwrite=args.overwrite,
    )
    notify(APP_NAME, "Download finished!")


def make_single_episode_args(url, output_dir, title, method, overwrite, progress_callback=None):
    return argparse.Namespace(
        url=url,
        output_dir=output_dir,
        title=title,
        method=method,
        overwrite=overwrite,
        progress_callback=progress_callback,
    )


def download_batch(args):
    episodes = discover_episodes(args.url)
    episodes = sorted(episodes, key=lambda episode: episode.number)
    episodes = dedupe_episodes_by_number(episodes)
    episodes = filter_episodes(episodes, args.from_episode, args.to_episode)

    if not episodes:
        raise ValueError("No episodes matched the requested range.")

    titles = make_batch_titles(episodes)
    failed_episodes = []
    success_count = 0

    print(f"[I] Found {len(episodes)} episode(s).")
    for episode, title in zip(episodes, titles):
        print(f"[I] Episode {episode.number}: {episode.url}")
        single_args = make_single_episode_args(
            url=episode.url,
            output_dir=args.output_dir,
            title=title,
            method=args.method,
            overwrite=args.overwrite,
            progress_callback=getattr(args, "progress_callback", None),
        )
        try:
            download_gimy_page(single_args)
            success_count += 1
        except Exception as exc:
            print(f"[E] Episode {episode.number} failed: {exc}")
            failed_episodes.append((episode, exc))

    print("[I] Batch summary")
    print(f"[I] Success: {success_count}")
    print(f"[I] Failed: {len(failed_episodes)}")

    if failed_episodes:
        print("[E] Failed episodes")
        for episode, exc in failed_episodes:
            print(f"[E] Episode {episode.number}: {episode.url} ({exc})")
        return 1

    notify(APP_NAME, "Batch download finished!")
    return 0


def generate_manual_segments(base_url, begin_from, end_at, counter_prefix, extension):
    for count in range(begin_from, end_at + 1):
        file_count = str(count).zfill(counter_prefix)
        yield file_count, base_url + file_count + extension


def download_manual_segments(args):
    destination_path = Path(args.output_dir).expanduser().resolve()
    destination_path.mkdir(parents=True, exist_ok=True)

    file_names = []
    retry_list = []
    for file_count, url in generate_manual_segments(
        args.base_url,
        args.begin,
        args.end,
        args.counter_prefix,
        args.extension,
    ):
        file_name = f"{file_count}{args.extension}"
        file_names.append(file_name)
        try:
            download_file(url, destination_path / file_name, overwrite=args.overwrite)
        except requests.RequestException as exc:
            print(f"[E] Failed {url}: {exc}")
            retry_list.append(url)

    write_filelist(destination_path, file_names)
    if args.merge:
        run_ffmpeg_concat(
            destination_path / "filelist.txt",
            destination_path / args.merge,
            overwrite=args.overwrite,
        )

    if retry_list:
        print("[E] Download failed list")
        for url in retry_list:
            print(url)

    notify(APP_NAME, "Download finished!")


def build_parser():
    parser = argparse.ArgumentParser(
        description="MediaHarbor downloads videos from multiple supported sources."
    )
    subparsers = parser.add_subparsers(dest="command")

    gimy_parser = subparsers.add_parser(
        "gimy",
        help="Download from a Gimy episode page URL.",
    )
    gimy_parser.add_argument("url", help="Gimy episode page URL.")
    gimy_parser.add_argument("-o", "--output-dir", default="downloads", help="Directory to save videos.")
    gimy_parser.add_argument("--title", help="Override output file/folder name.")
    gimy_parser.add_argument(
        "--method",
        choices=["yt-dlp", "segments"],
        default="yt-dlp",
        help="Use yt-dlp for automatic download/merge, or download m3u8 segments with ffmpeg concat.",
    )
    gimy_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    gimy_parser.set_defaults(func=download_gimy_page)

    ub1818_parser = subparsers.add_parser(
        "ub1818",
        help="Download from a UB1818 play page URL.",
    )
    ub1818_parser.add_argument("url", help="UB1818 play page URL containing video_id.")
    ub1818_parser.add_argument("-o", "--output-dir", default="downloads", help="Directory to save videos.")
    ub1818_parser.add_argument("--title", help="Override output file/folder name.")
    ub1818_parser.add_argument("--quality", type=int, default=1, help="Requested quality number. Default: 1.")
    ub1818_parser.add_argument(
        "--method",
        choices=["yt-dlp", "segments"],
        default="yt-dlp",
        help="Use yt-dlp for automatic download/merge, or download m3u8 segments with ffmpeg concat.",
    )
    ub1818_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    ub1818_parser.set_defaults(func=download_ub1818_page)

    youtube_parser = subparsers.add_parser(
        "youtube",
        help="Download from a YouTube video or playlist URL.",
    )
    youtube_parser.add_argument("url", help="YouTube video or playlist URL.")
    youtube_parser.add_argument("-o", "--output-dir", default="downloads", help="Directory to save videos.")
    youtube_parser.add_argument("--title", help="Override output file name for a single video.")
    youtube_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    youtube_parser.set_defaults(func=download_youtube)

    batch_parser = subparsers.add_parser(
        "batch",
        help="Discover and download multiple Gimy episodes from a title or episode page.",
    )
    batch_parser.add_argument("url", help="Gimy title page or episode page URL.")
    batch_parser.add_argument("-o", "--output-dir", default="downloads", help="Directory to save videos.")
    batch_parser.add_argument("--from", dest="from_episode", type=int, help="First episode number to download.")
    batch_parser.add_argument("--to", dest="to_episode", type=int, help="Last episode number to download.")
    batch_parser.add_argument(
        "--method",
        choices=["yt-dlp", "segments"],
        default="yt-dlp",
        help="Use yt-dlp for automatic download/merge, or download m3u8 segments with ffmpeg concat.",
    )
    batch_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    batch_parser.set_defaults(func=download_batch)

    segments_parser = subparsers.add_parser(
        "segments",
        help="Download manually configured numbered .ts segments.",
    )
    segments_parser.add_argument("base_url", help="URL prefix before the zero-padded segment number.")
    segments_parser.add_argument("--begin", type=int, default=0, help="First segment number.")
    segments_parser.add_argument("--end", type=int, required=True, help="Last segment number.")
    segments_parser.add_argument("--counter-prefix", type=int, default=6, help="Zero padding width.")
    segments_parser.add_argument("--extension", default=".ts", help="Segment extension.")
    segments_parser.add_argument("-o", "--output-dir", default="E20", help="Directory to save segments.")
    segments_parser.add_argument("--merge", help="Merge downloaded segments into this output filename.")
    segments_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    segments_parser.set_defaults(func=download_manual_segments)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 2

    try:
        result = args.func(args)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Terminating program.")
        return 130
    except Exception as exc:
        print(f"[E] {exc}", file=sys.stderr)
        return 1

    if isinstance(result, int):
        return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
