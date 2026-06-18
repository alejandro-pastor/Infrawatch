# Changelog

All notable changes to InfraWatch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-06-18

### Fixed
- **CI**: tests now mounted as volume from repo (`-v $GITHUB_WORKSPACE/app/tests:/app/tests:ro`) instead of being included in the Docker image. The production image stays clean (no tests), but CI can still run pytest.
- **Dockerfile**: replaced `addgroup`/`adduser` (Perl scripts) with `groupadd`/`useradd` (shadow binaries), since we removed `perl-base` for security.
- **Dockerfile**: added `apt-get upgrade -y` to update OS packages, fixing 7 of 9 CRITICAL CVEs detected by Trivy.
- **CI**: replaced static `.trivyignore` with `--ignore-unfixed` flag in Trivy action. The remaining 2 CVEs (CVE-2025-7458 in sqlite, CVE-2023-45853 in zlib) have no fix in Debian 12 stable — `--ignore-unfixed` ignores them dynamically, no manual maintenance required.
- **Docker Compose**: removed unsupported `resources.reservations.cpus` from all services (docker-compose v3.8 only supports `memory` in reservations).

## [1.0.0] - 2026-06-18

### Added
- **11-service containerized observability stack** orchestrated with Docker Compose: api, cache_redis, db_postgres, nginx, prometheus, grafana, alertmanager-1, alertmanager-2, loki, promtail, cadvisor.
- **High Availability Alertmanager** with gossip protocol (port 9094 internal). Two instances (`alertmanager-1`, `alertmanager-2`) run simultaneously; Prometheus sends alerts to both. No single point of failure.
- **Log aggregation** with Loki + Promtail. Structured JSON logs from FastAPI (`python-json-logger`) and Nginx (`log_format json_combined`).
- **Container resource metrics** with cAdvisor. Real-time CPU, memory, and network metrics per container.
- **Production hardening**:
  - Non-root containers (FastAPI runs as `appuser`, UID 1000)
  - Health checks for all 11 services
  - Resource limits (memory + CPU) per service
  - `restart: unless-stopped` on all services
  - Log rotation (`max-size: 10m, max-file: 3`)
  - Pinned image versions (no `:latest`)
  - Read-only mounts where possible
- **Security headers in Nginx**: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`.
- **Dead-man's switch** with UptimeRobot external monitoring (manual configuration).
- **New Prometheus alert rule**: `AlertmanagerDown` — fires if Alertmanager is unresponsive for 2+ minutes.
- **`.dockerignore`** to exclude tests, cache, secrets from Docker images.
- **External monitoring placeholder** in README (Production Security Considerations section).

### Security
- Loki and cAdvisor ports NOT exposed to host (internal Docker network only).
- Alertmanager-2 panel and gossip port (9094) NOT exposed to host.
- `SLACK_WEBHOOK_URL` removed from `.env` (single source of truth: `alertmanager.yml` in `.gitignore`).
- Orphan `requirements-test.txt` removed (was duplicate of `requirements.txt`).

### Known Limitations (Documented Trade-offs)
- **Loki without auth** (`auth_enabled: false`): acceptable for local dev; production should enable multi-tenant mode.
- **Grafana default credentials** (`admin/admin`): must be changed before any production deployment.
- **Promtail requires Docker socket** (`/var/run/docker.sock:ro`): standard trade-off for log aggregation.
