# MediaHarbor

MediaHarbor 是一個多網站影片下載工具，目標是把不同來源的影片下載流程整理成一致的 CLI 與 GUI 體驗。專案目前由原本的 Gimy 下載器演進而來，後續會逐步整理為可維護的多來源架構。

> 本機資料夾目標名稱為 `H:\AI_Project\MediaHarbor`。目前工作區程序仍鎖定舊資料夾時，需在關閉相關程序後再從 `H:\AI_Project\GimyDownloader` 改名。

## 目前功能狀態

| 功能 | 狀態 | 備註 |
| --- | --- | --- |
| Gimy 單集下載 | 已有 | CLI 命令保留為 `gimy`，代表來源名稱。 |
| Gimy 多集批次下載 | 已有 | CLI 命令為 `batch`。 |
| UB1818 下載 | 已有 | 支援 `play.html?video_id=...`。 |
| 手動 HLS 分段下載 | 已有 | CLI 命令為 `segments`。 |
| GUI | 已有 | 已改名為 MediaHarbor，並加入 YouTube 與進度資訊。 |
| YouTube 下載 | 已有 | 支援單片與 playlist。 |
| 下載進度 UI | 已有 | GUI 顯示目前檔案、百分比、速度、ETA。 |
| Windows 安裝檔 | 已有 | v1.0.0 installer 已上架到 GitHub Releases。 |

## 快速開始

### 線上網站版本

MediaHarbor Web Console 已部署在 Vercel：

```text
https://mediaharbor-pi.vercel.app
```

網站右上角提供 Windows installer 下載，檔案由 GitHub Release 提供，不放進 Vercel 部署包。

```text
https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/MediaHarborSetup.exe
```

本機開發 Web Console：

```shell
npm install
npm run dev
npm run build
```

目前 Web 版定位為來源解析與任務規劃介面。Gimy single 可在 Vercel API 解析 stream URL；YouTube、UB1818、batch、segments 這類長時間下載/合併任務，建議交給背景 worker 與物件儲存，不直接在 Vercel Function 內執行。

部署說明見：[Vercel 部署指南](docs/vercel-deployment.md)

Browser extension 可將目前分頁 URL 送到 Web Console：

```text
https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/mediaharbor-launcher.zip
```

### 本機 Python 版本

安裝依賴：

```shell
python -m pip install -r requirements.txt
```

啟動 GUI：

```shell
python gui.py
```

使用 CLI：

```shell
python downloader.py gimy "https://gimy01.com/..."
python downloader.py batch "https://gimy01.com/..." --from 1 --to 12
python downloader.py ub1818 "https://ub1818.com/play.html?video_id=59748"
python downloader.py youtube "https://www.youtube.com/watch?v=..."
python downloader.py youtube "https://www.youtube.com/playlist?list=..."
python downloader.py segments "https://example.com/path/video" --begin 0 --end 120 --merge output.ts
```

YouTube 下載預設使用最佳 mp4，並在 playlist 模式用集數序號避免檔名覆蓋：

```shell
python downloader.py youtube "https://www.youtube.com/watch?v=..." --title "my-video"
python downloader.py youtube "https://www.youtube.com/playlist?list=..." -o downloads
```

## 文件導覽

- [專案總覽](docs/project-overview.md)
- [使用者指南](docs/user-guide.md)
- [開發指南](docs/development-guide.md)
- [打包指南](docs/packaging-guide.md)
- [Vercel 部署指南](docs/vercel-deployment.md)
- [Browser Extension 安裝指南](docs/browser-extension.md)
- [參考來源](docs/references.md)
- [開發規格入口](specs/index.md)

## 參考來源

- 目前 repo remote：<https://github.com/similaitw/MediaHarbor>
- 使用者提供的參考專案：<https://github.com/jcwlin/GimyYoutubeDownloader>

本專案會在文件中保留上述來源 attribution。MediaHarbor 的目標不是維持單一 Gimy 下載器，而是將既有實作整理成多網站支援工具。

## 開發原則

- 專案名稱統一使用 `MediaHarbor`。
- `gimy`、`ub1818`、`youtube` 是來源名稱，可以保留在 CLI 與規格中。
- 已完成：文件、改名設定、YouTube、下載進度、GUI 整合。
- 已完成：文件、改名設定、YouTube、下載進度、GUI 整合、Vercel Web Console、v1.0.0 Windows installer。
