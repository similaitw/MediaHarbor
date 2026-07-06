# Spec: GUI

## 目標與成功條件

GUI 要支援多網站來源選擇，並在下載時提供清楚的進度與錯誤資訊。

成功條件：

- 視窗標題為 `MediaHarbor`。
- Mode 包含 Gimy batch、Gimy single、UB1818、YouTube、Manual segments。
- 欄位依模式顯示，不出現不相關設定。
- 下載期間 UI 不凍結。
- 下載進度可視化。

## Public Interface

GUI 模式：

- `Gimy batch`
- `Gimy single`
- `UB1818`
- `YouTube`
- `Manual segments`

共同欄位：

- URL 或 Base URL。
- Output folder。
- Title override。
- Overwrite。
- Start Download。
- Clear Log。

進度欄位：

- Current file。
- Percent。
- Speed。
- ETA。
- Progressbar。

## 主要實作策略

- 保留 worker thread。
- stdout/stderr 繼續導到 log queue。
- 新增 progress queue event。
- `_on_mode_change()` 控制欄位顯示。
- `_build_args()` 產生對應 argparse Namespace。

## 邊界情境與錯誤處理

- 必填 URL 空白時顯示 messagebox。
- 數字欄位錯誤時顯示 messagebox。
- worker 執行中禁止重複開始。
- 下載失敗時恢復 Start button，log 顯示錯誤。

## 測試計畫

- 手動切換每個 mode，確認欄位正確。
- 手動測試錯誤輸入。
- mock downloader function，確認 GUI 不凍結且 log/進度更新。

## Assumptions

- GUI 繼續使用 tkinter。
- 初版不新增取消下載按鈕。
