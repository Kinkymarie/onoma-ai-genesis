"use client";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Field } from "@/components/common/Field";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    try {
      await login(String(f.get("email")), String(f.get("password")), String(f.get("totp") || "") || undefined);
      router.push("/dashboard");
    } catch {
      setError("Invalid credentials or 2FA code");
    }
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto mt-24 max-w-sm space-y-4 p-4">
      <h1 className="text-2xl font-semibold">Sign in</h1>
      <Field label="Email" name="email" type="email" required />
      <Field label="Password" name="password" type="password" required />
      <Field label="2FA code (if enabled)" name="totp" inputMode="numeric" />
      {error && <p className="text-red-600">{error}</p>}
      <button className="w-full rounded bg-black px-3 py-2 text-white">Sign in</button>
      <a href="/auth/signup" className="text-sm underline">Create account</a>{" "}
      <a href="/auth/forgot-password" className="text-sm underline">Forgot password?</a>
    </form>
  );
}
