"use client";

import { useMemo, useState } from "react";
import {
  Anchor,
  ArrowRight,
  CheckCircle2,
  Clipboard,
  DownloadCloud,
  FileVideo,
  Loader2,
  Radio,
  RotateCcw,
  Terminal,
  Waves
} from "lucide-react";

const INSTALLER_URL = "https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/MediaHarborSetup.exe";

const MODES = [
  { id: "single", label: "Gimy single", icon: FileVideo },
  { id: "batch", label: "Gimy batch", icon: Radio },
  { id: "ub1818", label: "UB1818", icon: Anchor },
  { id: "youtube", label: "YouTube", icon: DownloadCloud },
  { id: "segments", label: "Segments", icon: Waves }
];

const SAMPLE_URLS = {
  single: "https://gimy01.com/...",
  batch: "https://gimy01.com/...",
  ub1818: "https://ub1818.com/play.html?video_id=59748",
  youtube: "https://www.youtube.com/watch?v=...",
  segments: "https://example.com/path/video"
};

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

  const ActiveIcon = activeMode?.icon || FileVideo;

  return (
    <main className="shell">
      <section className="workspace">
        <div className="mast">
          <div>
            <p className="eyebrow">MediaHarbor Web Console</p>
            <h1>把下載任務先在雲端拆解清楚。</h1>
          </div>
          <div className="runtime-pill">
            <span />
            Vercel safe mode
          </div>
          <a className="download-pill" href={INSTALLER_URL}>
            <DownloadCloud size={17} />
            Windows installer
          </a>
        </div>

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

        <form className="control-surface" onSubmit={resolveSource}>
          <div className="source-header">
            <div className="source-icon">
              <ActiveIcon size={24} />
            </div>
            <div>
              <p>{activeMode?.label}</p>
              <span>{mode === "single" ? "Gimy playback page can be resolved on Vercel." : "This mode is prepared for worker handoff."}</span>
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
      </section>

      <aside className="result-rail">
        <div className="image-band" aria-hidden="true">
          <img src="/mediaharbor-screenshot.png" alt="" />
        </div>

        <section className="result-panel">
          <div className="panel-title">
            <Terminal size={18} />
            Result
          </div>

          {!result && !error && (
            <div className="empty-state">
              <p>Waiting for a source.</p>
              <span>Gimy single resolves to a stream URL here; larger download jobs are prepared for a worker.</span>
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
                  <dt>Vercel download</dt>
                  <dd>{result.canDownloadOnVercel ? "Ready" : "Worker recommended"}</dd>
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
      </aside>
    </main>
  );
}
