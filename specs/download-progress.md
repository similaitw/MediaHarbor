# Spec: 下載進度資訊

## 目標與成功條件

下載時顯示清楚的進度資訊，包含下載速度、百分比、ETA、目前檔案。

成功條件：

- CLI log 顯示 `%`、速度、ETA。
- GUI 顯示 log + 進度條 + 目前檔案 + 百分比 + 速度 + ETA。
- Gimy、UB1818、YouTube 使用 yt-dlp 時皆共用同一套進度資料流。

## Public Interface

CLI 輸出範例：

```text
[I] Downloading 42.3% at 3.1MiB/s ETA 00:52 filename.mp4
```

GUI 顯示欄位：

- 目前檔案。
- 百分比。
- 速度。
- ETA。
- Progressbar。
- 詳細 log。

## 主要實作策略

- 強化 `yt_dlp_progress_hook()`，從 status 擷取：
  - `_percent_str`
  - `_speed_str`
  - `_eta_str`
  - `filename`
  - `downloaded_bytes`
  - `total_bytes` 或 `total_bytes_estimate`
- 新增可選 progress callback，讓 GUI 不必只解析 stdout。
- GUI worker thread 透過 queue 傳遞 progress event。
- Text log 保留完整訊息。

## 邊界情境與錯誤處理

- total size 不明時，GUI progressbar 改為 indeterminate 或只顯示文字百分比空值。
- merge 階段無百分比時顯示「合併中」。
- 下載完成時進度設為 100%，狀態顯示完成。
- 下載失敗時保留最後狀態並顯示錯誤。

## 測試計畫

- 單元測試 progress status 轉換。
- mock GUI queue，確認 progress event 能更新狀態。
- 手動下載短影片，確認 CLI/GUI 都有速度、百分比、ETA。

## Assumptions

- 進度資料以 yt-dlp 為主。
- manual segments 初版可先維持逐檔 log，不一定要有整體百分比。
