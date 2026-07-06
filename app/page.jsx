"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Anchor,
  ArrowRight,
  CheckCircle2,
  Clipboard,
  DownloadCloud,
  FileVideo,
  Gauge,
  Github,
  Layers3,
  Loader2,
  MonitorDown,
  Radio,
  RotateCcw,
  Route,
  ShieldCheck,
  Terminal,
  Waves
} from "lucide-react";

const INSTALLER_URL = "https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/MediaHarborSetup.exe";
const EXTENSION_ZIP_URL = "https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/mediaharbor-launcher.zip";
const RELEASE_URL = "https://github.com/similaitw/MediaHarbor/releases/tag/v1.0.0";

const MODES = [
  { id: "single", label: "Gimy single", icon: FileVideo },
  { id: "batch", label: "Gimy batch", icon: Radio },
  { id: "ub1818", label: "UB1818", icon: Anchor },
  { id: "youtube", label: "YouTube", icon: DownloadCloud },
  { id: "segments", label: "Segments", icon: Waves }
];

const FEATURES = [
  {
    title: "多來源下載",
    body: "Gimy、UB1818、YouTube 與手動 HLS segments 用同一套輸出流程管理。",
    icon: Layers3
  },
  {
    title: "GUI 進度監控",
    body: "桌面版顯示目前檔案、百分比、速度、ETA，批次下載時也能看懂狀態。",
    icon: Gauge
  },
  {
    title: "瀏覽器快速送件",
    body: "Chrome、Edge、Firefox 擴充功能可把目前分頁 URL 送進 MediaHarbor。",
    icon: Route
  },
  {
    title: "內建影音工具",
    body: "Windows installer 包含 MediaHarbor、ffmpeg 與 ffprobe，安裝後即可使用。",
    icon: MonitorDown
  }
];

const PIPELINE = [
  ["01", "貼上來源", "輸入影片、playlist、集數頁或 segment pattern。"],
  ["02", "解析任務", "確認標題、來源、輸出路徑與 CLI 指令。"],
  ["03", "下載合併", "桌面版接手 yt-dlp、HLS segments 與 ffmpeg 合併。"]
];

const SAMPLE_URLS = {
  single: "https://gimy01.com/...",
  batch: "https://gimy01.com/...",
  ub1818: "https://ub1818.com/play.html?video_id=59748",
  youtube: "https://www.youtube.com/watch?v=...",
  segments: "https://example.com/path/video"
};

function inferModeFromUrl(rawUrl) {
  const urlText = String(rawUrl || "").toLowerCase();
  if (urlText.includes("youtube.com") || urlText.includes("youtu.be")) {
    return "youtube";
  }
  if (urlText.includes("ub1818.com")) {
    return "ub1818";
  }
  if (urlText.includes(".ts") || urlText.includes(".m3u8")) {
    return "segments";
  }
  return "single";
}

export default function Home() {
  const [mode, setMode] = useState("single");
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [outputDir, setOutputDir] = useState("downloads");
  const [fromEpisode, setFromEpisode] = useState("");
  const [toEpisode, setToEpisode] = useState("");
  const [quality, setQuality] = useState("1");
  const [method, setMethod] = useState("yt-dlp");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const activeMode = useMemo(() => MODES.find((item) => item.id === mode), [mode]);
  const ActiveIcon = activeMode?.icon || FileVideo;

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initialUrl = params.get("url");
    const initialMode = params.get("mode");

    if (initialUrl) {
      setUrl(initialUrl);
      setMode(MODES.some((item) => item.id === initialMode) ? initialMode : inferModeFromUrl(initialUrl));
    } else if (MODES.some((item) => item.id === initialMode)) {
      setMode(initialMode);
    }
  }, []);

  async function resolveSource(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    setResult(null);
    setCopied(false);

    try {
      const response = await fetch("/api/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode,
          url,
          title,
          outputDir,
          fromEpisode,
          toEpisode,
          quality,
          method
        })
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Resolve failed.");
      }

      setResult(data);
    } catch (resolveError) {
      setError(resolveError.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function copyCommand() {
    if (!result?.cliCommand) {
      return;
    }

    await navigator.clipboard.writeText(result.cliCommand);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  function resetForm() {
    setUrl("");
    setTitle("");
    setFromEpisode("");
    setToEpisode("");
    setQuality("1");
    setMethod("yt-dlp");
    setResult(null);
    setError("");
  }

  return (
    <main>
      <section className="hero" id="top">
        <img className="hero-image" src="/mediaharbor-screenshot.png" alt="" />
        <div className="hero-shade" />

        <nav className="topbar" aria-label="Primary navigation">
          <a className="brand-lockup" href="#top" aria-label="MediaHarbor home">
            <span className="brand-mark">MH</span>
            <span>MediaHarbor</span>
          </a>
          <div className="nav-links">
            <a href="#features">功能</a>
            <a href="#extension">Extension</a>
            <a href={RELEASE_URL}>Release</a>
          </div>
        </nav>

        <div className="hero-copy">
          <p className="eyebrow">Windows GUI · CLI · Browser Extension</p>
          <h1>多來源影片下載，一次整理到位。</h1>
          <p className="lead">
            MediaHarbor 將 Gimy、UB1818、YouTube 與 HLS segments 整理成一致的操作流程。桌面版負責下載、進度監控與影音合併，瀏覽器擴充功能負責把目前分頁快速送進任務流程。
          </p>
          <div className="hero-actions">
            <a className="primary-link" href={INSTALLER_URL}>
              <DownloadCloud size={18} />
              Download for Windows
            </a>
            <a className="ghost-link" href={EXTENSION_ZIP_URL}>
              <MonitorDown size={18} />
              Get Browser Extension
            </a>
          </div>
        </div>

        <div className="signal-strip" aria-label="Product status">
          <div>
            <strong>v1.0.0</strong>
            <span>GitHub Release</span>
          </div>
          <div>
            <strong>134.42 MiB</strong>
            <span>Installer with ffmpeg</span>
          </div>
          <div>
            <strong>5 sources</strong>
            <span>Gimy, UB1818, YouTube, batch, segments</span>
          </div>
        </div>
      </section>

      <section className="section intro-band" id="features">
        <div className="section-heading">
          <p className="eyebrow dark">軟體功能</p>
          <h2>從解析、下載到合併，都用同一套流程處理。</h2>
        </div>
        <div className="feature-grid">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <article className="feature-card" key={feature.title}>
                <Icon size={24} />
                <h3>{feature.title}</h3>
                <p>{feature.body}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="section workflow-band">
        <div className="workflow-copy">
          <p className="eyebrow dark">Workflow</p>
          <h2>從 URL 到完成檔案，拆成三個清楚步驟。</h2>
        </div>
        <div className="pipeline">
          {PIPELINE.map(([number, titleText, body]) => (
            <article className="pipeline-step" key={number}>
              <span>{number}</span>
              <h3>{titleText}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="console-section" id="console">
        <div className="console-heading">
          <p className="eyebrow">URL Checker</p>
          <h2>線上工具只做來源檢查，不取代桌面版。</h2>
          <p>
            這個區塊用來快速檢查 URL 與產生 CLI 指令。YouTube、批次下載與 ffmpeg 合併仍由 Windows 桌面版處理。
          </p>
        </div>

        <div className="console-layout">
          <form className="control-surface" onSubmit={resolveSource}>
            <div className="mode-strip" role="tablist" aria-label="Download source">
              {MODES.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    className={item.id === mode ? "mode-button active" : "mode-button"}
                    type="button"
                    onClick={() => {
                      setMode(item.id);
                      setResult(null);
                      setError("");
                    }}
                    title={item.label}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="source-header">
              <div className="source-icon">
                <ActiveIcon size={24} />
              </div>
              <div>
                <p>{activeMode?.label}</p>
                <span>{mode === "single" ? "Gimy playback pages can be inspected here." : "This mode is prepared for desktop handoff."}</span>
              </div>
            </div>

            <label className="field span-2">
              <span>URL</span>
              <input
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder={SAMPLE_URLS[mode]}
                required
              />
            </label>

            {["single", "ub1818", "youtube"].includes(mode) && (
              <label className="field">
                <span>Title override</span>
                <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Optional" />
              </label>
            )}

            <label className="field">
              <span>Output folder</span>
              <input value={outputDir} onChange={(event) => setOutputDir(event.target.value)} />
            </label>

            {["single", "batch", "ub1818"].includes(mode) && (
              <label className="field">
                <span>Method</span>
                <select value={method} onChange={(event) => setMethod(event.target.value)}>
                  <option value="yt-dlp">yt-dlp</option>
                  <option value="segments">segments</option>
                </select>
              </label>
            )}

            {mode === "ub1818" && (
              <label className="field">
                <span>Quality</span>
                <input value={quality} onChange={(event) => setQuality(event.target.value)} inputMode="numeric" />
              </label>
            )}

            {["batch", "segments"].includes(mode) && (
              <>
                <label className="field">
                  <span>{mode === "batch" ? "From episode" : "Begin"}</span>
                  <input value={fromEpisode} onChange={(event) => setFromEpisode(event.target.value)} inputMode="numeric" />
                </label>
                <label className="field">
                  <span>{mode === "batch" ? "To episode" : "End"}</span>
                  <input value={toEpisode} onChange={(event) => setToEpisode(event.target.value)} inputMode="numeric" />
                </label>
              </>
            )}

            <div className="actions span-2">
              <button className="primary" type="submit" disabled={isLoading}>
                {isLoading ? <Loader2 className="spin" size={18} /> : <ArrowRight size={18} />}
                Resolve source
              </button>
              <button className="secondary" type="button" onClick={resetForm} title="Reset form">
                <RotateCcw size={18} />
              </button>
            </div>
          </form>

          <section className="result-panel">
            <div className="panel-title">
              <Terminal size={18} />
              Result
            </div>

            {!result && !error && (
              <div className="empty-state">
                <p>Waiting for a source.</p>
                <span>Gimy single resolves to a stream URL here; larger download jobs are prepared for a worker or the Windows app.</span>
              </div>
            )}

            {error && <div className="error-box">{error}</div>}

            {result && (
              <div className="result-stack">
                <div className="status-row">
                  <CheckCircle2 size={18} />
                  <span>{result.status}</span>
                </div>

                <dl>
                  <div>
                    <dt>Source</dt>
                    <dd>{result.source}</dd>
                  </div>
                  <div>
                    <dt>Title</dt>
                    <dd>{result.title}</dd>
                  </div>
                  <div>
                    <dt>Download path</dt>
                    <dd>{result.canDownloadOnVercel ? "Ready" : "Use desktop app"}</dd>
                  </div>
                </dl>

                {result.mediaUrl && (
                  <a className="media-link" href={result.mediaUrl} target="_blank" rel="noreferrer">
                    Open resolved media URL
                  </a>
                )}

                {result.preview?.length > 0 && (
                  <div className="preview-list">
                    {result.preview.map((item) => (
                      <code key={item}>{item}</code>
                    ))}
                  </div>
                )}

                <p className="next-step">{result.nextStep}</p>

                <div className="command-box">
                  <code>{result.cliCommand}</code>
                  <button type="button" onClick={copyCommand} title="Copy CLI command">
                    <Clipboard size={16} />
                    {copied ? "Copied" : "Copy"}
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>
      </section>

      <section className="download-section">
        <div>
          <p className="eyebrow dark">Installer</p>
          <h2>桌面版負責完整下載與影音合併。</h2>
          <p>Windows installer 已包含必要執行檔與影音工具。安裝後用 GUI 或 CLI 下載、合併、批次處理。</p>
        </div>
        <div className="download-actions">
          <a className="primary-link dark" href={INSTALLER_URL}>
            <DownloadCloud size={18} />
            Download MediaHarborSetup.exe
          </a>
          <a className="ghost-link dark" href={EXTENSION_ZIP_URL}>
            <MonitorDown size={18} />
            Browser extension
          </a>
          <a className="ghost-link dark" href={RELEASE_URL}>
            <Github size={18} />
            View GitHub Release
          </a>
        </div>
      </section>

      <section className="extension-section" id="extension">
        <div className="extension-copy">
          <p className="eyebrow dark">Browser Extension</p>
          <h2>在 Chrome、Edge、Firefox 直接把目前分頁送進 MediaHarbor。</h2>
          <p>
            MediaHarbor Launcher 會讀取目前分頁 URL、推測來源類型，並開啟 URL Checker 或複製本機 CLI 指令。擴充功能不直接下載影片，下載仍交給桌面版。
          </p>
        </div>
        <div className="install-steps">
          <article>
            <span>Chrome / Edge</span>
            <p>開啟 extensions 頁面，啟用 Developer mode，選擇 Load unpacked，載入專案的 extension 資料夾。</p>
          </article>
          <article>
            <span>Firefox</span>
            <p>開啟 about:debugging，選擇 This Firefox，Load Temporary Add-on，載入 extension/manifest.json。</p>
          </article>
        </div>
      </section>

      <footer className="footer">
        <span>MediaHarbor</span>
        <span>Built for source inspection, desktop downloading, and tidy batch workflows.</span>
        <span className="footer-badge">
          <ShieldCheck size={15} />
          Desktop app + Browser extension
        </span>
      </footer>
    </main>
  );
}
