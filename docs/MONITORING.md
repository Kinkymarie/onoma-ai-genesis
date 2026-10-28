# Monitoring

- Prometheus metrics at `/metrics` (`http_requests_total`, `http_request_seconds`). Restrict this path at the proxy in production.
- Structured JSON logs go to stdout; ship them with CloudWatch or Datadog agents.
- Set `SENTRY_DSN` and install `sentry-sdk` to enable error tracking.
- Probes: `/api/health` (liveness), `/api/health/db` (readiness).
