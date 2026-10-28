"use client";
import { useState, type FormEvent } from "react";
import { Field } from "@/components/common/Field";
import { forgotPassword } from "@/lib/api/auth";

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    await forgotPassword(String(new FormData(e.currentTarget).get("email")));
    setSent(true);
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto mt-24 max-w-sm space-y-4 p-4">
      <h1 className="text-2xl font-semibold">Reset password</h1>
      <Field label="Email" name="email" type="email" required />
      <button className="w-full rounded bg-black px-3 py-2 text-white">Send reset email</button>
      {sent && <p>If the account exists, a reset email was sent.</p>}
    </form>
  );
}
