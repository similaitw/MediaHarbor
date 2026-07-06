import "./globals.css";

export const metadata = {
  title: "MediaHarbor",
  description: "A web control surface for MediaHarbor source inspection and download planning."
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
