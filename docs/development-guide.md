# 開發指南

## 專案位置

本機規格化位置：

```text
H:\AI_Project\MediaHarbor
```

## 環境需求

- Python 3.8+
- ffmpeg
- Python dependencies：

```shell
python -m pip install -r requirements.txt
```

## 常用指令

靜態檢查：

```shell
python -m py_compile downloader.py gui.py
python -m pip check
```

CLI help：

```shell
python downloader.py --help
```

啟動 GUI：

```shell
python gui.py
```

## 專案結構

```text
README.md
downloader.py
gui.py
requirements.txt
docs/
specs/
installer/
```

## 開發順序

建議依照 `specs/index.md`：

1. 文件與規格補齊。
2. 專案改名為 MediaHarbor。
3. 新增 YouTube 下載。
4. 新增下載進度資料流與 GUI 進度 UI。
5. 整理 downloader core。
6. 補測試與手動驗證。
7. 最後再打包 installer。

## 注意事項

- `gimy` 是來源命令名稱，不等同專案名稱。
- 新功能應盡量復用 yt-dlp 共用流程。
- 不要在未確認前改動 Git remote。
- 打包前要確認 `ffmpeg.exe` 與 `ffprobe.exe` 會被放入 dist。
