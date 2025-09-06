# CatalystAI - Enterprise API Discovery & Onboarding Platform

## Project Overview

CatalystAI is an LLM-powered API discovery and one-click onboarding platform that provisions access via OIDC, raises Jira tickets to AD/Platform teams, and ranks services using SOLAR-style signals.

# Product Team Roles vs. What Our Tool Solves

| Role                         | Before (Manual Work)                                                                                                                                      | After (With Our Tool)                                                                                                                                      | Time Saved / ROI                               |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| **Product Manager (PM)**     | - Spend hours hunting API docs & onboarding steps.<br>- Compile reports manually from Jira, Confluence, Slack.<br>- Copy-paste release notes from PRs.   | - Ask “Which API supports 2,500 TPS for wallet?” → instant answer with docs, owner, SLA, onboarding.<br>- Auto-generated release notes & status reports.<br>- Unified semantic search across all docs. | **30–40% less time** on admin tasks → focus on roadmap & strategy |
| **Technical Program Manager (TPM/PMO)** | - Maintain spreadsheets for dependencies & risks.<br>- Create decks manually for execs every week.<br>- Follow-up with multiple teams for updates. | - Auto-generated portfolio dashboards & risk heatmaps from live data.<br>- Knowledge graph identifies dependencies & bottlenecks.<br>- Automated stakeholder updates. | **50%+ less reporting overhead**; faster risk detection |
| **Engineering Manager / Tech Lead** | - Track down upstream/downstream API SLAs manually.<br>- Gather TPS & error data from multiple tools.<br>- Onboarding steps scattered in wikis.   | - One query retrieves API details, telemetry, owner, onboarding.<br>- Proactive SLA & performance monitoring built-in.<br>- Developer onboarding playbooks generated. | **20–30% less time** wasted on info hunting; faster go-lives |
| **Compliance / Governance**  | - Manually collect audit evidence.<br>- Match controls to projects by hand.<br>- Miss compliance impacts until too late.                                  | - Auto-map controls to initiatives.<br>- Automated evidence retrieval (logs, approvals).<br>- Change alerts for compliance-relevant APIs.                    | **50% faster audit readiness**; reduced compliance risk |
| **Customer Experience Liaison** | - Read through thousands of tickets manually.<br>- Manually categorize NPS feedback.                                                                   | - AI clusters feedback themes & links to features.<br>- Prioritized, actionable insights delivered automatically.                                          | **30% faster insights**, improved customer-focused decisions |
| **Portfolio Manager / Exec** | - Wait for manually created reports.<br>- No proactive risk visibility.                                                                                   | - Real-time dashboards, KPIs, and predictive risk alerts.<br>- Reports generated on-demand.                                                                | **Instant visibility**, fewer surprises; **better ROI tracking** |


## Quick Start

### Prerequisites
- Docker and Docker Compose
- Java 21
- Python 3.11+
- Node.js 18+
- pnpm

### Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd CatalystAI

# Start infrastructure services
docker-compose up -d postgres redis keycloak vault

# Start the applications
docker-compose up -d catalog-api rag-service ingest-adapters web

# Or run locally
pnpm install
pnpm dev
```

### Services

- **catalog-api**: Spring Boot GraphQL/REST API
- **rag-service**: RAG and vector search service
- **ingest-adapters**: Python FastAPI for API ingestion
- **web**: Next.js frontend application

## Architecture

- **PostgreSQL**: Relational data storage
- **Vector Database**: Semantic search (Weaviate/Qdrant)
- **Redis**: Caching and queuing
- **Keycloak**: Identity and access management
- **Vault**: Secrets management

## Development

See individual service directories for detailed development instructions.
