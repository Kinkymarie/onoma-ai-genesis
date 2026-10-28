# Onoma AI Genesis frontend

The Next.js dashboard renders project, agent, memory, and health data from the
FastAPI MVP. It displays a clear offline state when the API is unavailable.

## Run locally

```sh
npm ci
cp .env.example .env.local
npm run dev
```

Set `API_BASE_URL` to the backend base URL in `.env.local` (defaults to
`http://127.0.0.1:8000`). Start the backend using the instructions in
[`../backend/README.md`](../backend/README.md), then open `http://localhost:3000`.

The API is fetched by the Next.js server; no browser-side credentials or CORS
configuration are needed for this read-only dashboard. Authentication,
mutations, and the remaining product routes are not implemented yet.

Run `npm run lint` and `npm run build` to validate the frontend.
