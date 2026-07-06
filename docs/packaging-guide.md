# 打包指南

## 目的

此文件記錄 MediaHarbor 打包流程。本次執行不重新執行 PyInstaller、不執行 Inno Setup、不產生新的 exe 或 installer。

## 預期輸出

改名完成後，預期產物：

```text
dist\MediaHarbor\MediaHarbor.exe
installer-output\MediaHarborSetup.exe
```

## PyInstaller

預期使用 `MediaHarbor.spec` 建置：

```shell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean MediaHarbor.spec
```

建置完成後確認：

```text
dist\MediaHarbor\MediaHarbor.exe
dist\MediaHarbor\ffmpeg.exe
dist\MediaHarbor\ffprobe.exe
```

## Inno Setup

預期使用：

```shell
iscc installer\MediaHarbor.iss
```

若 `iscc` 不在 PATH，使用實際安裝路徑，例如：

```shell
& "C:\Users\simil\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\MediaHarbor.iss
```

## 打包前檢查

```shell
python -m py_compile downloader.py gui.py
python -m pip check
python downloader.py --help
```

## 本次不執行

- 不重建 `dist/`。
- 不重建 `installer-output/`。
- 不更新安裝檔。
