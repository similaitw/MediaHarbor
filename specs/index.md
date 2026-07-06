# 開發規格入口

## 建議開發順序

1. [專案改名為 MediaHarbor](rename-to-mediaharbor.md)：已執行，打包除外。
2. [YouTube 下載](youtube-download.md)：已執行。
3. [下載進度資訊](download-progress.md)：已執行 yt-dlp/GUI 進度。
4. [下載核心抽象化](downloader-core.md)：已完成共用 yt-dlp 進度與 YouTube 接入。
5. [GUI 規格](gui.md)：已執行。
6. [測試規格](testing.md)：已執行靜態與 help 檢查。
7. [打包流程](../docs/packaging-guide.md)：本次未執行。

## 固定決策

- 專案正式名稱為 `MediaHarbor`。
- 本機 folder 目標路徑為 `H:\AI_Project\MediaHarbor`；若工作區鎖定，需釋放後再改名。
- `gimy` 保留為來源命令名稱。
- YouTube 初版支援單片與 playlist。
- YouTube 預設下載最佳 mp4。
- GUI 下載資訊使用 log + 進度條 + 狀態欄。

## 本次文件任務不做

- 不打包 exe 或 installer。
