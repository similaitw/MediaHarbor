const WEB_CONSOLE_URL = "https://mediaharbor-pi.vercel.app";

const urlInput = document.getElementById("urlInput");
const modeSelect = document.getElementById("modeSelect");
const openConsoleButton = document.getElementById("openConsole");
const copyCliButton = document.getElementById("copyCli");
const statusText = document.getElementById("status");

function extensionApi() {
  return typeof browser !== "undefined" ? browser : chrome;
}

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

function commandMode(mode) {
  return mode === "single" ? "gimy" : mode;
}

function buildConsoleUrl() {
  const params = new URLSearchParams({
    mode: modeSelect.value,
    url: urlInput.value.trim()
  });
  return `${WEB_CONSOLE_URL}/?${params.toString()}#console`;
}

function buildCliCommand() {
  const rawUrl = urlInput.value.trim();
  const mode = commandMode(modeSelect.value);
  return `python downloader.py ${mode} ${JSON.stringify(rawUrl)} -o "downloads"`;
}

async function loadCurrentTab() {
  try {
    const api = extensionApi();
    const tabs = await api.tabs.query({ active: true, currentWindow: true });
    const tabUrl = tabs?.[0]?.url || "";
    urlInput.value = tabUrl;
    modeSelect.value = inferModeFromUrl(tabUrl);
    statusText.textContent = tabUrl ? "Current tab loaded." : "Paste a URL to continue.";
  } catch (error) {
    statusText.textContent = "Could not read current tab URL.";
  }
}

openConsoleButton.addEventListener("click", async () => {
  const rawUrl = urlInput.value.trim();
  if (!rawUrl) {
    statusText.textContent = "Paste a URL first.";
    return;
  }

  await extensionApi().tabs.create({ url: buildConsoleUrl() });
  statusText.textContent = "Opened MediaHarbor Web Console.";
});

copyCliButton.addEventListener("click", async () => {
  const rawUrl = urlInput.value.trim();
  if (!rawUrl) {
    statusText.textContent = "Paste a URL first.";
    return;
  }

  await navigator.clipboard.writeText(buildCliCommand());
  statusText.textContent = "CLI command copied.";
});

urlInput.addEventListener("input", () => {
  modeSelect.value = inferModeFromUrl(urlInput.value);
});

loadCurrentTab();
