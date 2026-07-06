# Browser Extension 安裝指南

MediaHarbor Launcher 是一個 WebExtension，可在 Chrome、Microsoft Edge 與 Firefox 使用。它不在瀏覽器裡直接下載影片，而是抓取目前分頁 URL，送到 MediaHarbor URL Checker 檢查，或複製本機 CLI 指令。

下載 zip：

```text
https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/mediaharbor-launcher.zip
```

## 功能

- 自動讀取目前分頁 URL。
- 依 URL 推測來源模式：Gimy、UB1818、YouTube 或 segments。
- 一鍵開啟 MediaHarbor URL Checker。
- 一鍵複製本機 `python downloader.py ...` CLI 指令。

## Chrome 安裝

1. 開啟 `chrome://extensions`。
2. 打開右上角 `Developer mode`。
3. 點 `Load unpacked`。
4. 選擇專案內的 `extension` 資料夾。若使用 release zip，請先解壓縮再選擇解壓後的資料夾。
5. 將 MediaHarbor 圖示固定到工具列。

## Microsoft Edge 安裝

1. 開啟 `edge://extensions`。
2. 打開 `Developer mode`。
3. 點 `Load unpacked`。
4. 選擇專案內的 `extension` 資料夾。若使用 release zip，請先解壓縮再選擇解壓後的資料夾。
5. 將 MediaHarbor 圖示固定到工具列。

## Firefox 暫時安裝

1. 開啟 `about:debugging#/runtime/this-firefox`。
2. 點 `Load Temporary Add-on...`。
3. 選擇 `extension/manifest.json`。
4. MediaHarbor Launcher 會暫時安裝到 Firefox，重開瀏覽器後需重新載入。

## 使用方式

1. 打開影片頁、playlist 頁或已知 segment URL 頁。
2. 點瀏覽器工具列的 MediaHarbor。
3. 確認 URL 和 Source mode。
4. 點 `Open URL Checker` 開啟 URL Checker，或點 `Copy CLI` 後到本機終端機執行。

## 打包 zip

```powershell
Compress-Archive -Path extension\* -DestinationPath extension\mediaharbor-launcher.zip -Force
```

打包後可將 zip 上傳到 GitHub Release，或交給使用者手動解壓後載入。
