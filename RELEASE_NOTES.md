# v1.0.0 — Production-Ready Observability Stack

> **Released:** 18 June 2026
> **Status:** Stable

First stable release of InfraWatch, a self-hosted observability platform for containerized applications with production-grade security and high availability.

## Highlights

- **11-service containerized stack** orchestrated with Docker Compose
- **Production hardening:** non-root containers, health checks, resource limits, restart policies
- **High Availability alerting:** two Alertmanagers with gossip protocol (no single point of failure)
- **Log aggregation:** Loki + Promtail with JSON-structured logs
- **Container resource metrics:** cAdvisor integration
- **External monitoring:** UptimeRobot as dead-man's switch
- **Alerting:** 4 alert rules with Slack integration (APIDown, HighLatency, LowRequestRate, AlertmanagerDown)
- **CI/CD:** automated tests + Trivy security scanning + Docker Hub push

## Stack (11 services)

| Service | Purpose | Port |
|---------|---------|------|
| `api` | FastAPI application | 8000 |
| `cache_redis` | Redis cache | 6379 (internal) |
| `db_postgres` | PostgreSQL database | 5432 (internal) |
| `nginx` | Reverse proxy | 8080 |
| `prometheus` | Metrics collection | 9090 |
| `grafana` | Visualization dashboards | 3000 |
| `alertmanager-1` | Alert routing (HA primary) | 9093 |
| `alertmanager-2` | Alert routing (HA secondary) | 9093 (internal) |
| `loki` | Log aggregation | 3100 (internal) |
| `promtail` | Log collection agent | 9080 (internal) |
| `cadvisor` | Container resource metrics | 8080 (internal) |

## Production Hardening

- **Non-root containers:** FastAPI runs as `appuser` (UID 1000), not root
- **Health checks:** All 11 services have Docker healthchecks defined
- **Resource limits:** Memory and CPU limits per service to prevent noisy-neighbor issues
- **Restart policies:** `restart: unless-stopped` on all services
- **Log rotation:** `max-size: 10m, max-file: 3` to prevent disk fill
- **Pinned versions:** All images use specific tags (no `:latest`) for reproducibility
- **Read-only mounts:** Configs and Docker socket mounted `:ro` when possible
- **Graceful degradation:** `try/except` in main.py for Redis and PostgreSQL

## High Availability

Two Alertmanager instances (`alertmanager-1` and `alertmanager-2`) run simultaneously with **gossip protocol** on port 9094 (internal network). Prometheus sends each alert to **both** instances, guaranteeing zero loss of notifications even if one instance fails.

## Observability Stack

- **Loki + Promtail:** Structured JSON logs aggregated and indexed by labels
- **cAdvisor:** Real-time CPU, memory, and network metrics per container
- **Grafana dashboard:** 6 panels (Request Rate, P95 Latency, API Requests, Container CPU, Container Memory, Container Logs)
- **Nginx security headers:** X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy

## Security

- **Trivy scanning in CI/CD:** Blocks deployment on CRITICAL vulnerabilities
- **Optimized base image:** `python:3.11.9-slim` with `perl-base` removed (zero CRITICAL CVEs)
- **Security headers:** Nginx implements OWASP-recommended headers
- **No public exposure:** Loki, cAdvisor, and Alertmanager HA gossip not exposed to host
- **Secrets management:** `.env` gitignored, `alertmanager.yml` (with Slack webhook) gitignored
- **Token principle of least privilege:** Applied to all access tokens

## Known Limitations (Documented Trade-offs)

- **Loki without auth** (`auth_enabled: false`): Acceptable for local dev; production should enable multi-tenant mode or use a reverse proxy with basic auth
- **Grafana default credentials** (`admin/admin`): Must be changed before any production deployment
- **Promtail requires Docker socket** (`/var/run/docker.sock:ro`): Standard trade-off for log aggregation; alternative is Docker log driver to Loki directly

## What's Next

- **v1.1.0:** PostgreSQL and Redis Prometheus exporters for database observability
- **v2.0.0:** Cloud deployment (Oracle Cloud Free Tier when ARM capacity available)
