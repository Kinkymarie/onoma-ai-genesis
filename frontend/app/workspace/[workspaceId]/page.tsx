"use client";
import { useState, type FormEvent } from "react";
import { chat } from "@/lib/api/agents";

export default function WorkspacePage({ params }: { params: { workspaceId: string } }) {
  const [reply, setReply] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setReply((await chat(String(new FormData(e.currentTarget).get("message")))).reply);
  }

  return (
    <main className="mx-auto max-w-3xl space-y-4 p-8">
      <h1 className="text-2xl font-semibold">Workspace {params.workspaceId}</h1>
      <form onSubmit={onSubmit} className="flex gap-2">
        <input name="message" className="flex-1 rounded border px-3 py-2 dark:bg-gray-900" required />
        <button className="rounded bg-black px-3 py-2 text-white">Ask Onoma</button>
      </form>
      {reply && <pre className="whitespace-pre-wrap rounded border p-3">{reply}</pre>}
    </main>
  );
}
