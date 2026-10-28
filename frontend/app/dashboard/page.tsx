"use client";
import useSWR from "swr";
import { useAuth } from "@/hooks/useAuth";
import { listProjects } from "@/lib/api/projects";

export default function DashboardPage() {
  const { authenticated, logout } = useAuth();
  const { data } = useSWR(authenticated ? "projects" : null, listProjects);
  if (!authenticated) return <a className="p-8 underline" href="/auth/login">Sign in</a>;
  return (
    <main className="mx-auto max-w-3xl space-y-4 p-8">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <ul className="list-disc pl-6">
        {(data ?? []).map((p: { id: number; name: string }) => (
          <li key={p.id}><a className="underline" href={`/workspace/${p.id}`}>{p.name}</a></li>
        ))}
      </ul>
      <a className="underline" href="/settings">Settings</a>{" "}
      <button className="underline" onClick={() => logout()}>Sign out</button>
    </main>
  );
}
