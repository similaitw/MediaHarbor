# 打包指南

## 目的

此文件記錄 MediaHarbor 打包流程。v1.0.0 已產生 Windows installer 並上架到 GitHub Releases。

## 預期輸出

正式產物：

```text
dist\MediaHarbor\MediaHarbor.exe
installer-output\MediaHarborSetup.exe
```

v1.0.0 Release asset：

```text
https://github.com/similaitw/MediaHarbor/releases/download/v1.0.0/MediaHarborSetup.exe
```

目前 v1.0.0 installer 大小為 `140,952,752` bytes，約 `134.42 MiB`。

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

## 發布位置

- 不將 exe/installer 放入 Git repository。
- Installer 放在 GitHub Releases。
- Vercel 網站只連到 Release asset，不把 installer 放進部署包。
