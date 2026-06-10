# InfraWatch 🔭

> Sistema de observabilidad cloud-native (self-hosted) para aplicaciones containerizadas,
> con monitorización en tiempo real, CI/CD automatizado y seguridad integrada.

![CI/CD](https://github.com/alejandro-pastor/Infrawatch/actions/workflows/ci-cd.yml/badge.svg)
![Docker Hub](https://img.shields.io/docker/pulls/pastorops/infrawatch)
![Security](https://img.shields.io/badge/security-Trivy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Stack Tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Backend** | Python 3.11 + FastAPI |
| **Bases de datos** | PostgreSQL 16, Redis 7 |
| **Contenedores** | Docker, Docker Compose |
| **Monitorización** | Prometheus, Grafana |
| **CI/CD** | GitHub Actions |
| **Seguridad** | Trivy (escaneo de vulnerabilidades) |

---

## Arquitectura

```
Cliente → FastAPI (8000) → PostgreSQL  (persistencia)
                         → Redis       (caché)

Prometheus (9090) ←── scrape /metrics ──→ FastAPI
Grafana    (3000) ←── datasource      ──→ Prometheus

5 servicios orquestados con Docker Compose en red interna aislada.
```

---

## Cómo ejecutar

```bash
git clone https://github.com/alejandro-pastor/Infrawatch.git
cd Infrawatch
cp .env.example .env      # configura tus variables de entorno
docker-compose up -d --build
```

| Puerto | Servicio |
|--------|----------|
| `8000` | FastAPI (API REST) |
| `9090` | Prometheus |
| `3000` | Grafana |

> **Nota:** Las credenciales se gestionan mediante variables de entorno (`.env`).
> Nunca se incluyen en el repositorio.

---

## Pipeline CI/CD

Cada `push` a `main` ejecuta automáticamente:

1. **Build** de la imagen Docker
2. **Escaneo de seguridad** con Trivy — severidad `CRITICAL` provoca fallo del pipeline (`exit-code: 1`)
3. **Push a Docker Hub** (`pastorops/infrawatch`) — solo si el escaneo pasa

Este flujo implementa el principio **Shift-Left Security**: las vulnerabilidades se detectan
y bloquean antes de que la imagen llegue a producción.

---

## Dashboard Grafana

El panel de control incluye tres métricas principales:

- **Request Rate** — Peticiones por segundo (`rate()`)
- **P95 Latency** — Latencia en el percentil 95
- **API Requests** — Contador acumulado de llamadas a la API

![Grafana Dashboard](docs/grafana-dashboard.png)

---

## Seguridad

- **Trivy en pipeline:** bloquea el despliegue ante vulnerabilidades críticas
- **Imagen optimizada:** `python:3.11-slim` con `perl-base` eliminado → CVEs críticos reducidos a 0
- **Gestión de secretos:** variables de entorno con `.env` + GitHub Secrets para el pipeline
- **Principio de mínimo privilegio** aplicado en todos los tokens de acceso

---

## Estado del proyecto

> 🚧 Proyecto en desarrollo activo

| Funcionalidad | Estado |
|---------------|--------|
| Stack base (FastAPI + PostgreSQL + Redis) | ✅ Completado |
| Contenedorización con Docker Compose | ✅ Completado |
| Pipeline CI/CD con GitHub Actions | ✅ Completado |
| Escaneo de seguridad con Trivy | ✅ Completado |
| Monitorización con Prometheus + Grafana | ✅ Completado |
| Despliegue en Oracle Cloud (Free Tier) | 🔜 Próximo |
| Alertas automáticas en Grafana (email/Slack) | 🔜 Próximo |
| Tests automatizados con pytest | 🔜 Próximo |
| Logs centralizados con Grafana Loki | 🔜 Próximo |
| Métricas de PostgreSQL y Redis | 🔜 Próximo |

---

## Autor

**Alejandro Pastor** — [github.com/alejandro-pastor](https://github.com/alejandro-pastor) · [LinkedIn](https://www.linkedin.com/in/alejandro-pastor-devops)
