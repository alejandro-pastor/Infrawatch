# InfraWatch 🔭

> Sistema de observabilidad cloud-native (self-hosted) para aplicaciones containerizadas,
> con monitorización en tiempo real, alertas automatizadas, alta disponibilidad, 
> agregación de logs y seguridad integrada.

![CI/CD](https://github.com/alejandro-pastor/Infrawatch/actions/workflows/ci-cd.yml/badge.svg)
![Docker Hub](https://img.shields.io/docker/pulls/pastorops/infrawatch)
![Security](https://img.shields.io/badge/security-Trivy-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/github/v/release/alejandro-pastor/Infrawatch)

---

## Stack Tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Backend** | Python 3.11 + FastAPI |
| **Bases de datos** | PostgreSQL 16, Redis 7 |
| **Contenedores** | Docker, Docker Compose |
| **Reverse proxy** | Nginx (con security headers y JSON logging) |
| **Monitorización** | Prometheus, Grafana, cAdvisor |
| **Alerting** | Alertmanager (HA con gossip protocol) + Slack |
| **Log Aggregation** | Promtail + Loki (structured JSON logs) |
| **External monitoring** | UptimeRobot (dead-man's switch) |
| **CI/CD** | GitHub Actions |
| **Seguridad** | Trivy (escaneo de vulnerabilidades), non-root containers |

---

## Arquitectura

```
                                          External monitoring
                                          ┌──────────────────┐
                                          │  UptimeRobot     │
                                          │  (5 min checks)  │
                                          └──────────────────┘
                                                   ▲
                                                   │ HTTP (externo)
                                                   │
Cliente → Nginx (8080) → FastAPI (8000) → PostgreSQL  (persistencia)
                              │            → Redis       (caché)
                              │ /metrics
                              ▼
                       Prometheus (9090)
                              │ scrape
                              │ cAdvisor (métricas de host)
                              │ Promtail  (métricas de logs)
                              ▼
                       Alertmanager HA ─┐
                       (9093 + 9094 gossip)
                              │
                              ▼
                          Slack (#alerts-infra)

Log pipeline:
  Contenedores → Promtail (recoge) → Loki (3100) → Grafana (visualiza)

11 servicios orquestados con Docker Compose en red interna aislada.
```

---

## Cómo ejecutar

```bash
git clone https://github.com/alejandro-pastor/Infrawatch.git
cd Infrawatch
# Asegúrate de tener un archivo .env con las variables de entorno configuradas
docker-compose up -d --build
```

| Puerto | Servicio | Tipo |
|--------|----------|------|
| `8000` | FastAPI (API REST) | Público |
| `9090` | Prometheus | Público |
| `3000` | Grafana | Público |
| `8080` | Nginx (reverse proxy) | Público |
| `9093` | Alertmanager (HA primary) | Público |
| `3100` | Loki | Interno (no expuesto) |
| `9094` | Alertmanager gossip (HA) | Interno (no expuesto) |
| `8080` | cAdvisor (métricas host) | Interno (no expuesto) |

> **Nota:** Las credenciales se gestionan mediante variables de entorno (`.env`).
> Nunca se incluyen en el repositorio. El webhook de Slack está en `alertmanager.yml`
> (también en `.gitignore`).

---

## Pipeline CI/CD

Cada `push` a `main` ejecuta automáticamente:

1. **Build** de la imagen Docker
2. **Tests** con pytest — verifica endpoints, JSON y resiliencia ante fallos de Redis/PostgreSQL
3. **Escaneo de seguridad** con Trivy — severidad `CRITICAL` provoca fallo del pipeline (`exit-code: 1`)
4. **Push a Docker Hub** (`pastorops/infrawatch`) — solo si tests y escaneo pasan

Este flujo implementa el principio **Shift-Left Security**: las vulnerabilidades se detectan
y bloquean antes de que la imagen llegue a producción.

---

## Dashboard Grafana

El panel de control incluye **6 paneles** en una cuadrícula 3×2:

### Fila 1 — Métricas de aplicación (Prometheus)

- **Request Rate** — Peticiones por segundo (`rate()`)
- **P95 Latency** — Latencia en el percentil 95
- **API Requests** — Contador acumulado de llamadas a la API

### Fila 2 — Observabilidad de plataforma

- **Container CPU Usage** (cAdvisor) — Uso de CPU por contenedor en tiempo real
- **Container Memory Usage** (cAdvisor) — Consumo de memoria por contenedor (MB)
- **Container Logs** (Loki) — Logs en vivo de todos los contenedores, filtrables por `service`

![Grafana Dashboard](docs/grafana-dashboard.png)

---

## Pipeline de Logs

```
Contenedores → Promtail (recoge) → Loki (almacena) → Grafana (visualiza)
```

| Componente | Puerto | Función |
|------------|--------|---------|
| Promtail | 9080 | Recoge logs de Docker y los envía a Loki |
| Loki | 3100 (interno) | Almacena y indexa logs para búsqueda con LogQL |
| Grafana | 3000 | Visualiza logs en el panel "Container Logs" o "Explore" |

**Formato de logs**: JSON estructurado con `python-json-logger` en FastAPI/uvicorn,
y `log_format json_combined escape=json` en Nginx. Esto permite que Loki indexe
campos como `level`, `logger`, `module` y permita búsquedas tipo:
`{service="api"} | json | level="ERROR"`.

**Retención**: 7 días (`168h`), configurable en `loki-config.yml`.

---

## Production Hardening

InfraWatch implementa las mejores prácticas de producción:

| Práctica | Implementación |
|----------|----------------|
| **Non-root containers** | Usuario `appuser` (UID 1000) en la imagen de FastAPI |
| **Health checks** | Todos los servicios tienen `healthcheck` definido |
| **Resource limits** | `deploy.resources.limits` (memoria + CPU) en cada servicio |
| **Restart policies** | `restart: unless-stopped` en todos los servicios |
| **Log rotation** | `max-size: 10m, max-file: 3` en docker logging driver |
| **Pinned versions** | Todas las imágenes con tag fijo (no `:latest`) |
| **Read-only mounts** | Configs y Docker socket montados `:ro` cuando es posible |
| **Graceful degradation** | `try/except` en main.py para Redis y PostgreSQL |

---

## Decisiones Técnicas

| Necesidad | Elegimos | Alternativa descartada | Por qué |
|-----------|----------|----------------------|---------|
| Log aggregation | **Loki + Promtail** | ELK (Elasticsearch) | Loki es 10x más ligero, se integra nativamente con Grafana, y usa labels como Prometheus |
| Alerting | **Alertmanager** | Grafana Alerting nativo | Alertmanager es el estándar de la industria, ofrece deduplicación de alertas mediante gossip protocol, y permite HA (alta disponibilidad) |
| HA de Alertmanager | **2 instancias con gossip** | Alertmanager único | Tolerancia a fallos: si una instancia cae, la otra sigue enviando alertas a Slack |
| Orquestación | **Docker Compose** | Kubernetes | Docker Compose es suficiente para un proyecto single-server con 11 contenedores |
| Structured logging | **python-json-logger** | Format string manual | Escapa correctamente caracteres especiales (comillas, saltos de línea) en JSON |
| Security headers | **Nginx (X-Frame, CSP, XSS)** | Sin headers | Mitiga XSS, clickjacking y MIME sniffing en producción |
| Monitoreo externo | **UptimeRobot** | Monitoreo interno | Un dead-man's switch requiere vigilancia externa — el sistema de monitoreo no puede vigilarse a sí mismo |
| Resource isolation | **cgroups por servicio** | Sin límites | Un servicio desbocado (memory leak) no tumba al resto del stack |

---

## Alerting

El sistema incluye alertas automatizadas que monitorizan la salud en tiempo real:

| Alerta | Severidad | Condición | Duración |
|--------|-----------|-----------|----------|
| `APIDown` | 🔴 CRITICAL | API no responde (up == 0) | > 2 minutos |
| `HighLatency` | 🟡 WARNING | P95 latencia > 2 segundos | > 5 minutos |
| `LowRequestRate` | 🟡 WARNING | Peticiones casi 0 pero API arriba | > 10 minutos |
| `AlertmanagerDown` | 🔴 CRITICAL | Alertmanager no responde (dead-man's switch) | > 2 minutos |

### Flujo de alertas

```
Prometheus (evalúa reglas) → Alertmanager HA (deduplica + agrupa) → Slack (#alerts-infra)
                                       ↑
                                  gossip protocol
                              (sincroniza entre instancias)
```

**Configuración:**
- **Canal de Slack:** `#alerts-infra`
- **Resolución:** Notificación automática cuando el problema se resuelve (`send_resolved: true`)
- **Agrupación:** Por `alertname` y `severity` para evitar spam
- **Reenvío:** Cada 4h si la alerta no se resuelve

Las reglas están definidas en `rules/fastapi-alerts.yml` y la configuración de Alertmanager
en `alertmanager.yml` (este último en `.gitignore` por contener el webhook URL).

### HA de Alertmanager

Dos instancias (`alertmanager-1` y `alertmanager-2`) corren simultáneamente con
**gossip protocol** (puerto 9094, red interna). Prometheus envía cada alerta a
**ambas** instancias, garantizando cero pérdida de notificaciones aunque una caiga.

---

## Seguridad

- **Trivy en pipeline:** bloquea el despliegue ante vulnerabilidades críticas
- **Imagen optimizada:** `python:3.11.9-slim` con `perl-base` eliminado → CVEs críticos reducidos a 0
- **Non-root containers:** FastAPI corre como `appuser` (UID 1000), no como root
- **Security headers en Nginx:** `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`
- **Health checks:** Docker monitoriza el estado de cada servicio y reinicia si es necesario
- **Gestión de secretos:** variables de entorno con `.env` + GitHub Secrets para el pipeline
- **Principio de mínimo privilegio** aplicado en todos los tokens de acceso
- **Sin exposición innecesaria:** Loki, cAdvisor y gossip de Alertmanager **NO** se exponen al host
- **Webhook URL protegido:** `alertmanager.yml` está en `.gitignore` para evitar exposición del secreto de Slack

### Production Security Considerations

> ⚠️ **Nota para despliegue en producción real:**
> - `Loki` está configurado sin autenticación (`auth_enabled: false`) para desarrollo local.
>   En producción, habilitar `auth_enabled: true` o poner un reverse proxy con basic auth.
> - Grafana usa credenciales por defecto (`admin/admin`). **Cambiarlas antes de desplegar**.
> - Los secrets se gestionan con `.env` (gitignored). Para producción usar Docker secrets, 
>   HashiCorp Vault, o un secrets manager cloud-native.
> - `Promtail` requiere acceso al socket de Docker (`/var/run/docker.sock:ro`) para
>   descubrir contenedores. Esto es un trade-off conocido de seguridad documentado en la 
>   [issue #1 del proyecto](https://github.com/alejandro-pastor/Infrawatch).

---

## Tests

La API incluye 5 tests automatizados:

| Test | Tipo | Qué verifica |
|------|------|--------------|
| `test_health` | Smoke test | `/health` responde 200 con `{"status": "healthy"}` |
| `test_root_status` | Smoke test | `/` responde 200 siempre |
| `test_root_json_fields` | Estructural | El JSON contiene `status`, `total_api_requests` y `database_connected` |
| `test_root_without_redis` | Resiliencia | La API responde 200 aunque Redis esté caído |
| `test_root_without_db` | Resiliencia | La API responde 200 aunque PostgreSQL esté caído |

Los tests se ejecutan automáticamente en cada `push` a `main` vía GitHub Actions, **antes** del escaneo de seguridad y del despliegue.

---

## Estado del proyecto

> ✅ v1.0.0 — Production-Ready Observability Stack

| Funcionalidad | Estado |
|---------------|--------|
| Stack base (FastAPI + PostgreSQL + Redis) | ✅ Completado |
| Contenedorización con Docker Compose | ✅ Completado |
| Pipeline CI/CD con GitHub Actions | ✅ Completado |
| Escaneo de seguridad con Trivy | ✅ Completado |
| Monitorización con Prometheus + Grafana | ✅ Completado |
| Nginx como proxy inverso | ✅ Completado |
| Alertas automáticas con Alertmanager + Slack | ✅ Completado |
| Tests automatizados con pytest | ✅ Completado |
| Production Hardening (non-root, health checks, resource limits) | ✅ Completado |
| HA Alertmanager (gossip protocol, 2 instancias) | ✅ Completado |
| Logs estructurados JSON (Promtail + Loki) | ✅ Completado |
| Métricas de host con cAdvisor | ✅ Completado |
| External monitoring (UptimeRobot dead-man's switch) | ✅ Completado |
| Despliegue en Oracle Cloud (Free Tier) | ❌ Pospuesto — sin capacidad ARM disponible |
| Métricas de PostgreSQL y Redis (exporters) | 🔜 Próximo (v1.1.0) |

---

## Autor

**Alejandro Pastor** — [github.com/alejandro-pastor](https://github.com/alejandro-pastor) · [LinkedIn](https://www.linkedin.com/in/alejandro-pastor-devops)
