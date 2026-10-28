"use client";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Field } from "@/components/common/Field";
import { register } from "@/lib/api/auth";

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    try {
      await register(String(f.get("email")), String(f.get("password")), String(f.get("name")));
      router.push("/auth/login");
    } catch {
      setError("Could not register (email in use or password too short)");
    }
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto mt-24 max-w-sm space-y-4 p-4">
      <h1 className="text-2xl font-semibold">Create account</h1>
      <Field label="Name" name="name" />
      <Field label="Email" name="email" type="email" required />
      <Field label="Password (min 8)" name="password" type="password" minLength={8} required />
      {error && <p className="text-red-600">{error}</p>}
      <button className="w-full rounded bg-black px-3 py-2 text-white">Sign up</button>
    </form>
  );
}
