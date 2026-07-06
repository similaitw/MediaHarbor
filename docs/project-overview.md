# 專案總覽

## 目標

MediaHarbor 是多網站影片下載工具，提供 CLI、GUI 與 Vercel Web Console。它的核心目標是讓使用者用一致的流程處理不同來源的影片，並在下載時看到清楚的狀態、速度與錯誤訊息。

## 目標使用者

- 想用 GUI 下載影片、但不想手動處理 m3u8 或 ffmpeg 的使用者。
- 需要批次下載集數或 playlist 的使用者。
- 願意用 CLI 做自動化或測試的進階使用者。

## 支援來源

| 來源 | 狀態 | 說明 |
| --- | --- | --- |
| Gimy | 已有 | 支援單集與作品多集批次下載。 |
| UB1818 | 已有 | 支援解析站內 API 並下載 m3u8。 |
| YouTube | 已有 | 支援單片與 playlist。 |
| 手動 HLS segments | 已有 | 使用者提供分段 URL pattern。 |

## 現況

專案正式名稱為 `MediaHarbor`。本機資料夾目標路徑為 `H:\AI_Project\MediaHarbor`；若目前工作區程序鎖定舊資料夾，需在釋放鎖定後從 `H:\AI_Project\GimyDownloader` 改名。

目前已上線：

- Vercel Web Console：<https://mediaharbor-pi.vercel.app>
- Windows installer v1.0.0：<https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/MediaHarborSetup.exe>

## 限制

- 不處理需登入、cookies、年齡驗證或地區限制的網站流程。
- 需登入、cookies、年齡驗證或地區限制的 YouTube 內容會直接顯示 yt-dlp 錯誤。
- manual segments 目前以逐檔 log 為主，未做整體百分比。
- Web Console 不直接執行長時間影片下載、ffmpeg 合併或大檔暫存；這些任務仍建議使用本機 GUI/CLI 或後續背景 worker。

## 參考來源

詳細來源與 attribution 見 [references.md](references.md)。
