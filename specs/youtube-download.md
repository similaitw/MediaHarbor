# Spec: YouTube 下載

## 目標與成功條件

新增 YouTube 下載功能，支援單支影片與 playlist。

成功條件：

- CLI 可執行 `python downloader.py youtube URL`。
- GUI 有 YouTube 模式。
- 單片輸出一個影片檔。
- playlist 依序輸出多個影片檔，檔名不互相覆蓋。
- 預設輸出最佳 mp4。

## Public Interface

CLI：

```shell
python downloader.py youtube "https://www.youtube.com/watch?v=..."
python downloader.py youtube "https://www.youtube.com/playlist?list=..." -o downloads
python downloader.py youtube "URL" --title "custom-name"
python downloader.py youtube "URL" --overwrite
```

GUI：

- Mode 新增 `YouTube`。
- 顯示 URL、Output folder、Title override、Overwrite。
- 不顯示 Gimy 範圍欄位、不顯示 UB1818 quality、不顯示 segments method。

## 主要實作策略

- 新增 `download_youtube(args)`，使用既有 yt-dlp API。
- 共用 `run_yt_dlp()`，但支援傳入 format、playlist template、overwrite 等 options。
- 單片 template：`{title}.%(ext)s`。
- playlist template：`%(playlist_index)03d-%(title)s.%(ext)s`。
- 預設 format 使用最佳影片+音訊，並盡量 merge 成 mp4。

## 邊界情境與錯誤處理

- 不支援 cookies/login/年齡驗證；顯示 yt-dlp 原始錯誤。
- 不承諾支援整個頻道頁。
- playlist 中單支影片失敗時，先沿用 yt-dlp 行為；後續若需要再做逐項錯誤彙整。
- 檔名需經 sanitize 或交由 yt-dlp safe filename 處理。

## 測試計畫

- mock `yt_dlp.YoutubeDL`，確認 format、outtmpl、merge_output_format 設定。
- `python downloader.py youtube --help`。
- 手動用短 YouTube 影片測試。
- 手動用小型 playlist 測試命名與多檔輸出。

## Assumptions

- 預設最佳 mp4。
- 初版不加入格式選擇 UI。
- 初版不加入 cookies/login。
