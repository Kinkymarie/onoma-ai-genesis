"use client";
import { useState, type FormEvent } from "react";
import { Field } from "@/components/common/Field";
import { setup2fa, verify2fa } from "@/lib/api/auth";

export default function TwoFactorPage() {
  const [uri, setUri] = useState("");
  const [status, setStatus] = useState("");

  async function onVerify(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      await verify2fa(String(new FormData(e.currentTarget).get("code")));
      setStatus("2FA enabled");
    } catch {
      setStatus("Invalid code");
    }
  }

  return (
    <div className="mx-auto mt-24 max-w-sm space-y-4 p-4">
      <h1 className="text-2xl font-semibold">Two-factor authentication</h1>
      <button className="rounded border px-3 py-2" onClick={async () => setUri((await setup2fa()).otpauth_uri)}>
        Generate secret
      </button>
      {uri && <p className="break-all text-xs">Add to your authenticator app: {uri}</p>}
      <form onSubmit={onVerify} className="space-y-2">
        <Field label="Code" name="code" inputMode="numeric" required />
        <button className="rounded bg-black px-3 py-2 text-white">Verify</button>
      </form>
      {status && <p>{status}</p>}
    </div>
  );
}
