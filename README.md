# 🛡️ Ironsight — Autonomous AI Security Operations Center & Threat Intelligence

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq AI](https://img.shields.io/badge/AI-Groq%20LLM-orange?style=for-the-badge)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-blueviolet?style=for-the-badge)](https://www.trychroma.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Neo4j](https://img.shields.io/badge/Graph_DB-Neo4j%205-008CC1?style=for-the-badge&logo=neo4j)](https://neo4j.com/)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

**Ironsight** is an enterprise-grade, autonomous AI Security Operations Center (SOC) and Threat Intelligence Platform. Designed for modern infrastructure, it unifies real-time attack surface discovery, autonomous vulnerability scanning, and AI-driven remediation into a single, cohesive command center.

It consists of three specialized AI engines working in tandem:
1. **Ironsight SOC**: The core attack surface mapping and vulnerability orchestration engine.
2. **Aegis AI**: A local, RAG-powered security advisory engine that analyzes vulnerabilities and synthesizes actionable remediation playbooks.
3. **Praxis GRC**: The enterprise governance, risk, and compliance command center.

---

## ✨ Core Capabilities

### 🛡️ Autonomous Attack Surface Reconnaissance
- **Agentic Orchestration**: Automatically dispatch scanning tools (Nmap, Nuclei, etc.) via Celery background workers.
- **Continuous Monitoring**: Define targets and let Ironsight continuously monitor ports, services, and live CVEs in the background.

### 🧠 Aegis AI — RAG-Powered Remediation
- **Contextual Playbooks**: Integrates cutting-edge LLMs to analyze finding output and generate step-by-step remediation scripts.
- **Threat Memory**: Powered by ChromaDB vector storage, Aegis recalls past findings and learns from historical remediation successes.

### 🕸️ Graph Attack Surface Topology
- **Interactive Threat Modeling**: Leverages Neo4j to map complex asset relationships and target-to-vulnerability linkages (`(Target)-[:HAS_VULNERABILITY]->(Vulnerability)`).
- **Blast Radius Analysis**: Dynamically query and visualize network topologies to prioritize remediation based on true risk.

### 🔒 Enterprise-Grade Security Architecture
- **Unified Authentication**: JWT-based authentication bridging the Next.js frontend with the FastAPI backend, utilizing bcrypt for password hashing.
- **Secure Job Execution**: Subprocess arguments are isolated and strictly parameterized, entirely eliminating RCE vulnerabilities.
- **Postgres Persistence**: A single source of truth using PostgreSQL and SQLAlchemy models for complete data integrity across the platform.

### 📊 Observability & Audit Trails
- **S3 Evidence Vault**: MinIO seamlessly archives raw scan logs, report artifacts, and compliance evidence.
- **OpenSearch Indexing**: Direct ingestion of finding events for full-text search, threat hunting, and compliance auditing. *(Note: You can populate the dashboard with synthetic sample data using `python scripts/demo_telemetry.py` for evaluation purposes).*

---

## 🏗️ System Architecture

Ironsight utilizes a modern microservice architecture, orchestrated by Docker Compose and routed via an Nginx API Gateway.

```text
                                  +-----------------------+
                                  |     Web Clients       |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |     Nginx Gateway     |
                                  |       (Port 80)       |
                                  +-----+-----+-----+-----+
                                        |     |     |
            +---------------------------+     |     +---------------------------+
            |                                 |                                 |
            v                                 v                                 v
+-----------+-----------+         +-----------+-----------+         +-----------+-----------+
|    Ironsight UI Hub    |         |    Aegis AI Frontend  |         |   Praxis Web Frontend  |
|   Next.js (Port 3000) |         |     (Port 8080)       |         |   Vite (Port 5173)    |
+-----------+-----------+         +-----------------------+         +-----------------------+
            |
            v
+-----------+-----------+         +-----------------------+
|   Ironsight FastAPI    |<------->|    Aegis AI Engine    |
|       (Port 8000)     |         | FastAPI + Groq LLM    |
+-----+-----+-----+-----+         | ChromaDB (Port 8090)  |
      |     |     |               +-----------------------+
      |     v     |
      |  +--+-------------------+
      |  |  Celery Task Worker  |
      |  +--+-------------------+
      |     |
      v     v
+-----+-----+-----+-----+---------------------+-------+-----+---------------------+
|   PostgreSQL + PGVector |      Neo4j Graph    |    MinIO S3    |     OpenSearch    |
|      (Port 5432)      |      (Port 7687)    |  (Port 9000)   |    (Port 9200)    |
+-----------------------+---------------------+----------------+-------------------+
```

---

## 🚀 Quick Start Guide

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [Groq API Key](https://console.groq.com/) *(Required for Aegis AI remediation synthesis)*

### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/cyber-ironsight.git
cd cyber-ironsight
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and set your credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ironsight_db
NEO4J_AUTH=neo4j/ironsight_neo4j
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

### 3. Launch the Platform
Start all microservices in detached mode:
```bash
docker-compose up -d
```
Verify all containers are running successfully:
```bash
docker-compose ps
```

---

## 🌐 Access Points

Once all services are healthy, access the platform components via:

- **Ironsight Gateway**: [http://localhost](http://localhost)
- **Ironsight SOC Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Aegis AI Interface**: [http://localhost:8080](http://localhost:8080)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) *(Default: `neo4j` / `ironsight_neo4j`)*
- **PgAdmin**: [http://localhost:5050](http://localhost:5050) *(Default: `admin@ironsight.ai` / `admin`)*
- **Grafana Dashboards**: [http://localhost:3001](http://localhost:3001) *(Default: `admin` / `ironsight`)*

---

## 📡 Core API Reference

The Ironsight backend is completely powered by a secure, JWT-authenticated FastAPI layer.

### Authentication
- `POST /login` — Exchange credentials for a JWT Bearer token.
- `POST /register` — Provision a new user and organization.

### Intelligence & Orchestration
- `GET /analytics/` — Fetch aggregate telemetry across targets, active scans, and critical CVEs.
- `POST /orchestrate` — Deploy an agentic swarm against a target to fulfill a specific security goal.

### Targets & Scans
- `POST /targets/?hostname={target}` — Register a new target for surveillance.
- `GET /targets/` — List all registered targets.
- `GET /scans/` — Fetch list of all active and completed scans with timeline data.
- `GET /scans/{scan_id}` — Inspect specific scan findings and artifacts.

---

## ⚠️ Disclaimer & Ethical Use

Ironsight is intended strictly for authorized security auditing, defensive threat intelligence, and educational purposes. **Ensure you have explicit authorization before adding targets or executing scans against any network or system.** The authors are not responsible for misuse of this tool.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.