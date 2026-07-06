# Spec: 專案改名為 MediaHarbor

## 目標與成功條件

將專案對外名稱完整改為 `MediaHarbor`，同時保留 `gimy` 作為來源名稱。

成功條件：

- GUI title 顯示 `MediaHarbor`。
- exe 名稱為 `MediaHarbor.exe`。
- installer 名稱為 `MediaHarborSetup.exe`。
- 本機資料夾改為 `H:\AI_Project\MediaHarbor`。
- `rg "GimyDownloader"` 只在歷史、來源或遷移說明中出現。

## Public Interface

- CLI 入口仍為 `python downloader.py ...`。
- 來源命令不變：`gimy`、`ub1818`、`batch`、`segments`。
- 後續新增 `youtube`。

## 主要實作策略

- 將 GUI class `GimyDownloaderGui` 改為 `MediaHarborGui`。
- 將通知標題改為 `MediaHarbor`。
- 將 PyInstaller spec 改名為 `MediaHarbor.spec`，輸出 name 改為 `MediaHarbor`。
- 將 Inno Setup script 改名為 `installer\MediaHarbor.iss`。
- 將 installer AppName、DefaultDirName、OutputBaseFilename 改為 MediaHarbor。
- 本機資料夾從 `H:\AI_Project\GimyDownloader` 改為 `H:\AI_Project\MediaHarbor`。
- Git remote 暫不自動更動；若 GitHub repo 改名，建議更新 remote 到 `https://github.com/MrNegativeTW/MediaHarbor`。

## 邊界情境與錯誤處理

- 若 `H:\AI_Project\MediaHarbor` 已存在，先停止並請使用者決定合併或改名。
- rename folder 前確認沒有 dev server 或打包工具正在使用該目錄。
- 保留舊來源名稱 `gimy`，避免破壞使用者現有命令。

## 測試計畫

```shell
python -m py_compile downloader.py gui.py
python downloader.py --help
rg "GimyDownloader" . --glob "!build/**" --glob "!dist/**" --glob "!installer-output/**"
```

手動確認 GUI title、installer script 與 dist 輸出路徑。

## Assumptions

- `MediaHarbor` 是正式名稱。
- `gimy` 是來源名稱，不視為專案名殘留。
- 本 spec 後續才執行；本次只建立文件。
