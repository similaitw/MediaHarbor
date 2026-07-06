# Spec: 下載核心抽象化

## 目標與成功條件

整理多網站下載流程，讓 Gimy、UB1818、YouTube 都能共用輸出、進度、錯誤處理與 yt-dlp 設定。

成功條件：

- 新來源不需要複製大量下載邏輯。
- yt-dlp 設定集中管理。
- GUI 和 CLI 能共享同一組 downloader functions。

## Public Interface

保留現有 CLI：

```shell
python downloader.py gimy URL
python downloader.py ub1818 URL
python downloader.py batch URL
python downloader.py segments BASE_URL
```

新增 YouTube 後：

```shell
python downloader.py youtube URL
```

## 主要實作策略

- 將「解析來源 URL」與「下載 media URL」拆開。
- Gimy/UB1818 先解析成 media URL，再交給共用下載函式。
- YouTube 直接交給 yt-dlp，但仍使用共用 output/progress 設定。
- 建立共用 option builder，例如 output template、overwrite、referer、format、progress callback。

## 邊界情境與錯誤處理

- 來源解析錯誤需顯示來源名稱與 URL。
- media URL 缺失時丟出明確錯誤。
- 批次下載單集失敗不停止後續任務。
- overwrite 行為需在所有來源一致。

## 測試計畫

- mock Gimy `player_data` 解析。
- mock UB1818 API resolve。
- mock YouTube yt-dlp options。
- 檢查 batch 單集失敗仍繼續。

## Assumptions

- yt-dlp 是主要下載引擎。
- segments mode 保留作為進階/備援功能。
