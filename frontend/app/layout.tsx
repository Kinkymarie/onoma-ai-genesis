import "@/styles/globals.css";
import type { ReactNode } from "react";
import { Providers } from "./providers";

export const metadata = { title: "Onoma AI Genesis" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
