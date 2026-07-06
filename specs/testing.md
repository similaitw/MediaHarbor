# Spec: 測試規格

## 目標與成功條件

建立後續開發的基本驗證清單，避免多來源功能互相影響。

成功條件：

- 每次功能改動至少跑靜態檢查。
- YouTube、進度、GUI 皆有 mock 測試或手動驗證方案。
- 打包前有固定 checklist。

## Public Interface

常用檢查指令：

```shell
python -m py_compile downloader.py gui.py
python -m pip check
python downloader.py --help
```

文件檢查：

```shell
rg "GimyDownloader" . --glob "!build/**" --glob "!dist/**" --glob "!installer-output/**"
rg "MediaHarbor" README.md docs specs
rg "jcwlin|MrNegativeTW|github.com" README.md docs specs
```

## 主要實作策略

- 對 downloader core 使用 mock，避免測試真的下載大型影片。
- 對 yt-dlp options 做單元測試。
- 對 progress hook 做純函式資料轉換測試。
- GUI 以手動驗證為主，必要時抽出可測試的 args builder。

## 邊界情境與錯誤處理

- 網站結構變動時，測試需能分辨解析錯誤與網路錯誤。
- YouTube 測試避免依賴需要登入或年齡驗證的影片。
- 打包測試不應覆蓋使用者下載資料。

## 測試計畫

- Gimy：mock HTML，確認 media URL 解析。
- UB1818：mock API response，確認 media URL 與 title。
- YouTube：mock yt-dlp，確認單片/playlist template。
- Progress：mock status dict，確認 CLI/GUI 欄位。
- GUI：手動切換 mode，確認欄位與錯誤提示。
- Packaging：確認 dist 中有 exe、ffmpeg、ffprobe。

## Assumptions

- 目前沒有完整測試框架，後續可新增 `tests/`。
- 網路整合測試以手動或小型 smoke test 為主。
