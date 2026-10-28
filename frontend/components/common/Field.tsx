import type { InputHTMLAttributes } from "react";

export function Field({ label, ...props }: { label: string } & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block">{label}</span>
      <input className="w-full rounded border px-3 py-2 dark:bg-gray-900" {...props} />
    </label>
  );
}
