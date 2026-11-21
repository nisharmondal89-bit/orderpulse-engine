# Architecture Decision Records & Technical Tradeoffs

This document captures the key engineering decisions behind **OrderPulse**, translated for both **engineering peers** (reliability, latency, data integrity) and **non-technical stakeholders** (cost, customer experience, delivery speed).

---

## 1. Polyglot Persistence: PostgreSQL + MongoDB

| Audience | Explanation |
| :--- | :--- |
| **Non-Technical Partners** | We use **two specialized filing cabinets**: a strict ledger (PostgreSQL) so financial and order records are never lost or miscalculated, and a flexible flight-recorder (MongoDB) to store raw receipts from external shipping/payment partners whose formats change frequently. |
| **Engineering Tradeoff** | **Chosen:** PostgreSQL for ACID transactional integrity (`Order`, `OrderItem`) + MongoDB for schema-less webhook audit payloads (`webhook_logs`).<br>**Alternative Considered:** Storing JSONB columns inside PostgreSQL.<br>**Why This Wins Here:** Isolates high-volume, unstructured third-party write/read audit logs from transactional order tables, avoiding index bloat and rigid migrations when upstream partner payloads evolve. |

---

## 2. Asynchronous Event Processing (Celery + Redis) vs. Synchronous HTTP Calls

| Audience | Explanation |
| :--- | :--- |
| **Non-Technical Partners** | When a customer clicks "Place Order," they get an instant confirmation in under 50ms. If a third-party shipping or payment partner is slow or temporarily down, our background worker automatically retries without making the customer wait or losing their order. |
| **Engineering Tradeoff** | **Chosen:** Decoupled Celery worker backed by Redis with exponential backoff (`max_retries=3`), triggered via `transaction.on_commit()`.<br>**Alternative Considered:** Synchronous `requests.post()` inside the Django view.<br>**Why This Wins Here:** Prevents external third-party latency or outages from exhausting Gunicorn worker threads. Using `transaction.on_commit()` eliminates race conditions where a worker reads an order ID before PostgreSQL finishes committing the transaction. |

---

## 3. Automated Query-Count Guardrails in CI (`pytest` + `prefetch_related`)

| Audience | Explanation |
| :--- | :--- |
| **Non-Technical Partners** | As our order volume grows from 10 orders to 100,000 orders, the dashboard stays just as fast. Automated checks block code changes that would accidentally slow down the database. |
| **Engineering Tradeoff** | **Chosen:** Explicit `prefetch_related("items")` paired with `django_assert_num_queries(2)` in CI.<br>**Alternative Considered:** Relying solely on manual code reviews or late-stage APM alerts.<br>**Why This Wins Here:** Catches N+1 query regressions deterministically during pull requests before they ever reach production. |

---

## 4. Stateless Containerization for Cloud Portability

| Audience | Explanation |
| :--- | :--- |
| **Non-Technical Partners** | The entire application runs identically on a developer's laptop and in the cloud, cutting onboarding time to minutes and avoiding vendor lock-in. |
| **Engineering Tradeoff** | **Chosen:** 12-Factor environment configuration (`DATABASE_URL`, `MONGO_URI`, `REDIS_URL`) packaged in a slim Python 3.12 Docker image.<br>**Why This Wins Here:** Deploys with zero code changes to **AWS ECS / Fargate**, **GCP Cloud Run**, or **Azure Container Apps**. |
