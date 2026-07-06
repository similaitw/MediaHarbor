# Vercel 部署指南

MediaHarbor Web Console 使用 Next.js App Router，可直接部署到 Vercel。

## 本機驗證

```shell
npm install
npm run dev
npm run build
npm audit --audit-level=moderate
```

本機預設可用：

```text
http://127.0.0.1:3000
```

若 3000 port 被占用，可改用：

```shell
npx next dev -H 127.0.0.1 -p 3001
```

## Vercel 部署

1. 到 Vercel 新增 Project。
2. 匯入 GitHub repo：`similaitw/MediaHarbor`。
3. Framework Preset 選 Next.js。
4. Build Command 使用 `npm run build`。
5. Install Command 使用 `npm install`。
6. Deploy。

`vercel.json` 已設定 `/api/resolve` 的最大執行時間為 60 秒。

## 目前 Web 版能力

- 提供可操作的下載任務控制台。
- Gimy single 可透過 `/api/resolve` 解析 `player_data` 與 stream URL。
- YouTube、UB1818、Gimy batch、manual segments 會產生任務計畫與 CLI 指令。

## 為什麼不直接在 Vercel 下載影片

Vercel Functions 適合短時間 API 請求，不適合長時間影片下載、ffmpeg 合併與大檔暫存。Hobby plan 的 Function 最長 5 分鐘；Pro/Enterprise 可設定更長，但仍有 bundle、暫存檔與執行時間限制。

若要做完整線上下載，建議架構如下：

- Vercel：前端、登入、建立下載任務。
- Queue：Upstash Redis、Supabase Queue 或其他任務佇列。
- Worker：Railway、Fly.io、Render、VPS 或自架 Docker worker，負責 `yt-dlp`、ffmpeg、批次下載。
- Storage：Vercel Blob、S3、R2 或 Supabase Storage，保存完成檔案。
- Webhook/API：worker 完成後回寫任務狀態與下載連結。
