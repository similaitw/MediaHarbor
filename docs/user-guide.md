# 使用者指南

## GUI

啟動：

```shell
python gui.py
```

目前 GUI 支援：

- Gimy 多集批次下載。
- Gimy 單集下載。
- UB1818 影片下載。
- YouTube 影片與 playlist 下載。
- 手動 segments 下載。
- 下載進度條、百分比、速度、ETA、目前檔案。

## CLI

### Gimy 單集

```shell
python downloader.py gimy "https://gimy01.com/..." -o downloads
```

可用選項：

- `--title`：覆蓋輸出名稱。
- `--method yt-dlp|segments`：選擇下載方式。
- `--overwrite`：覆蓋既有檔案。

### Gimy 多集

```shell
python downloader.py batch "https://gimy01.com/..." --from 1 --to 12
```

批次下載遇到單集失敗時會繼續下一集，最後列出失敗清單。

### UB1818

```shell
python downloader.py ub1818 "https://ub1818.com/play.html?video_id=59748"
```

可用選項：

- `--quality 1`：指定品質編號，預設為 1。
- `--title`：覆蓋輸出名稱。
- `--method yt-dlp|segments`：選擇下載方式。

UB1818 API 解密需要本機 private key。請使用環境變數 `MEDIAHARBOR_UB1818_CLIENT_PRIVATE_KEY`，或把 PEM 檔放在 `secrets/ub1818_client_private_key.pem`；`secrets/` 不會提交到 Git。

### 手動 segments

```shell
python downloader.py segments "https://example.com/path/video" --begin 0 --end 120 --merge output.ts
```

這個模式適合已知 segment URL 編號規則的情境。

### YouTube

YouTube 支援單片與 playlist：

```shell
python downloader.py youtube "https://www.youtube.com/watch?v=..."
python downloader.py youtube "https://www.youtube.com/playlist?list=..."
python downloader.py youtube "https://www.youtube.com/watch?v=..." --title "custom-name"
```

## 常見錯誤

- `ffmpeg was not found`：需要安裝 ffmpeg 或使用未來打包好的 MediaHarbor installer。
- `Could not find player_data`：Gimy 頁面結構可能改變，或輸入不是播放頁。
- `UB1818 URL must contain video_id`：UB1818 URL 需要包含 `video_id` query。
- YouTube 登入/年齡驗證/地區限制：直接顯示 yt-dlp 原始錯誤，不做 cookies/login 支援。
