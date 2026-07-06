import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const maxDuration = 60;

const DEFAULT_HEADERS = {
  "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
  Referer: "https://gimy01.com/"
};

function sanitizeFilename(name) {
  return String(name || "video")
    .replace(/[\\/*?:"<>|]/g, "")
    .trim() || "video";
}

function resolveUrl(baseUrl, maybeUrl) {
  try {
    return new URL(maybeUrl, baseUrl).toString();
  } catch {
    return maybeUrl;
  }
}

function parsePlayerData(html) {
  const match =
    html.match(/var\s+player_data\s*=\s*(\{.*?\})\s*<\/script>/s) ||
    html.match(/var\s+player_data\s*=\s*(\{.*?\})\s*;/s);

  if (!match) {
    throw new Error("Could not find player_data in the Gimy page.");
  }

  return JSON.parse(match[1]);
}

async function fetchText(url, referer) {
  const response = await fetch(url, {
    headers: {
      ...DEFAULT_HEADERS,
      ...(referer ? { Referer: referer } : {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Source returned HTTP ${response.status}.`);
  }

  return response.text();
}

function buildCliCommand({ mode, url, title, outputDir, fromEpisode, toEpisode, quality, method }) {
  const command = mode === "single" ? "gimy" : mode;
  const pieces = ["python", "downloader.py", command, JSON.stringify(url)];

  if (outputDir) {
    pieces.push("-o", JSON.stringify(outputDir));
  }
  if (title && ["single", "ub1818", "youtube"].includes(mode)) {
    pieces.push("--title", JSON.stringify(title));
  }
  if (mode === "batch") {
    if (fromEpisode) {
      pieces.push("--from", String(fromEpisode));
    }
    if (toEpisode) {
      pieces.push("--to", String(toEpisode));
    }
  }
  if (mode === "segments") {
    if (fromEpisode) {
      pieces.push("--begin", String(fromEpisode));
    }
    if (toEpisode) {
      pieces.push("--end", String(toEpisode));
    }
  }
  if (mode === "ub1818" && quality) {
    pieces.push("--quality", String(quality));
  }
  if (["single", "batch", "ub1818"].includes(mode) && method) {
    pieces.push("--method", method);
  }

  return pieces.join(" ");
}

async function resolveGimy({ url, title }) {
  const html = await fetchText(url);
  const playerData = parsePlayerData(html);
  const mediaUrl = playerData.url;

  if (!mediaUrl) {
    throw new Error("player_data did not contain a url field.");
  }

  const vodName = playerData?.vod_data?.vod_name || playerData.title || "gimy_video";

  return {
    status: "resolved",
    title: sanitizeFilename(title || vodName),
    mediaUrl: resolveUrl(url, mediaUrl),
    source: "Gimy",
    canDownloadOnVercel: false,
    nextStep: "Vercel can resolve the stream URL. Use a worker or local MediaHarbor for long downloads and merging."
  };
}

function resolveYoutube({ url, title }) {
  return {
    status: "planned",
    title: sanitizeFilename(title || "YouTube video"),
    mediaUrl: null,
    source: "YouTube",
    canDownloadOnVercel: false,
    nextStep:
      "YouTube extraction and media download should run in a background worker with yt-dlp, storage, and rate-limit controls."
  };
}

function resolveUb1818({ quality }) {
  return {
    status: "worker-required",
    title: "UB1818 video",
    mediaUrl: null,
    source: "UB1818",
    quality: quality || 1,
    canDownloadOnVercel: false,
    nextStep:
      "UB1818 requires a private key and encrypted API calls. Keep that in worker secrets rather than browser or static code."
  };
}

function resolveManualSegments({ url, fromEpisode, toEpisode }) {
  const begin = Number(fromEpisode || 0);
  const end = Number(toEpisode || begin);
  const preview = Array.from({ length: Math.min(Math.max(end - begin + 1, 0), 5) }, (_, index) => {
    return `${url}${String(begin + index).padStart(6, "0")}.ts`;
  });

  return {
    status: "planned",
    title: "Manual HLS segments",
    mediaUrl: null,
    source: "Manual segments",
    preview,
    canDownloadOnVercel: false,
    nextStep: "Segment downloads and ffmpeg concat need a worker with temporary storage and ffmpeg."
  };
}

export async function POST(request) {
  try {
    const payload = await request.json();
    const mode = payload.mode || "single";
    const url = String(payload.url || "").trim();

    if (!url) {
      return NextResponse.json({ error: "URL is required." }, { status: 400 });
    }

    let result;
    if (mode === "single") {
      result = await resolveGimy(payload);
    } else if (mode === "youtube") {
      result = resolveYoutube(payload);
    } else if (mode === "ub1818") {
      result = resolveUb1818(payload);
    } else if (mode === "segments") {
      result = resolveManualSegments(payload);
    } else if (mode === "batch") {
      result = {
        status: "worker-required",
        title: "Gimy batch",
        mediaUrl: null,
        source: "Gimy",
        canDownloadOnVercel: false,
        nextStep: "Batch discovery and multiple downloads should run in a queued worker."
      };
    } else {
      return NextResponse.json({ error: `Unsupported mode: ${mode}` }, { status: 400 });
    }

    return NextResponse.json({
      ...result,
      cliCommand: buildCliCommand(payload),
      vercelLimit:
        "This Vercel app is designed for source inspection and job planning. Long downloads should be offloaded to a worker and object storage."
    });
  } catch (error) {
    return NextResponse.json({ error: error.message || "Resolve failed." }, { status: 500 });
  }
}
