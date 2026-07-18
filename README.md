# 🧠 DecisionLens

<p align="center">
  <strong>Engineering memory for teams that cannot afford to forget why decisions were made.</strong>
</p>

<p align="center">
  DecisionLens turns GitHub, Slack, and Markdown discussions into searchable, evidence-backed organizational intelligence powered by Supermemory.
</p>

<p align="center">
  <img alt="Hackathon Ready" src="https://img.shields.io/badge/Hackathon-Ready-0f766e?style=for-the-badge" />
  <img alt="React" src="https://img.shields.io/badge/React-TypeScript-2563eb?style=for-the-badge&logo=react" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi" />
  <img alt="Supermemory" src="https://img.shields.io/badge/Supermemory-AI%20Memory-111827?style=for-the-badge" />
  <img alt="Ollama" src="https://img.shields.io/badge/Ollama-Local%20LLM-f59e0b?style=for-the-badge" />
</p>

---

## 🔗 Submission Links

| Item | Link |
| --- | --- |
| 🚀 Live deployment | [decision-lens.netlify.app](https://agent-6a54fce0eb46362cdafc6cd7--decision-lens.netlify.app/) |
| 💻 Public GitHub repository | [github.com/riddhimajaiswal18/decisionlens](https://github.com/riddhimajaiswal18/decisionlens.git) |
| 🐦 Tweet / X post | [x.com/i/status/2078329346322796996](https://x.com/i/status/2078329346322796996) |

---

## ✨ Product Poster

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   🧠 DecisionLens                                                            │
│                                                                              │
│   Raw engineering conversations                                              │
│          ↓                                                                   │
│   Evidence-backed decisions, tradeoffs, alternatives, timelines              │
│          ↓                                                                   │
│   A living memory graph for your engineering organization                    │
│                                                                              │
│   GitHub  •  Slack  •  Markdown  •  Supermemory  •  Ollama-ready             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **One-line pitch:** DecisionLens is an engineering intelligence workspace that answers questions like _“Why did we choose Redis?”_ using the actual conversations, pull requests, ADRs, and tradeoffs behind the decision.

---

## 🚀 Why DecisionLens Exists

Engineering teams make important decisions every day, but the reasoning often disappears inside:

| Source | What Gets Lost | Why It Matters |
| --- | --- | --- |
| GitHub PRs | tradeoffs, rejected approaches, implementation rationale | future developers only see the final code |
| Slack threads | informal decisions, unresolved concerns, ownership clues | valuable context becomes unsearchable noise |
| ADRs/RFCs | historical architecture choices | documents become stale without linked evidence |
| Onboarding chats | repeated explanations | senior engineers lose time repeating context |

DecisionLens does not behave like a generic document search tool. It extracts **structured engineering knowledge** and keeps the original evidence attached.

---

## 🏆 Hackathon Value

```mermaid
quadrantChart
  title "DecisionLens positioning"
  x-axis "Generic search" --> "Engineering intelligence"
  y-axis "Low memory" --> "Long-term memory"
  quadrant-1 "Ideal hackathon zone"
  quadrant-2 "Useful but shallow"
  quadrant-3 "Basic tools"
  quadrant-4 "Memory without domain meaning"
  "Keyword search": [0.18, 0.25]
  "Static docs": [0.30, 0.36]
  "Generic RAG bot": [0.48, 0.58]
  "DecisionLens": [0.86, 0.88]
```

DecisionLens demonstrates a concrete Supermemory use case:

```text
Raw engineering artifacts → structured knowledge objects → Supermemory → decision intelligence UI
```

---

## 🧩 What It Can Do Now

| Capability | Status | Description |
| --- | --- | --- |
| 📊 Overview dashboard | ✅ Working | high-level engineering memory metrics and demo path |
| 🕸️ Memory graph | ✅ Working | Obsidian-style interactive map of decisions, technologies, artifacts, and uploaded memories |
| 💬 Ask DecisionLens | ✅ Working | asks questions against live API data or demo/local memories |
| 🕰️ Architecture timeline | ✅ Working | shows source-grounded decision evolution |
| 🔁 Recurring discussions | ✅ Working | identifies topics that keep returning |
| 📈 Technology trends | ✅ Working | compares adoption/rejection signals |
| 📜 Decision history | ✅ Working | traces how a technology or decision evolved |
| 📤 Markdown upload | ✅ Working | queues files through FastAPI and creates immediate local demo memories |
| 🧠 Local browser demo brain | ✅ Working | tests extraction without Ollama or Supermemory |
| 🦙 Ollama extraction | 🟡 Supported | backend extraction provider is implemented; requires local model setup |
| 🧬 Supermemory integration | 🟡 Supported | client, serializer, seed path, and intelligence endpoints exist; requires configured service |
| 🔌 GitHub/Slack connectors | 🟡 Basic | connector code and sample seeding exist; production OAuth/app setup is future work |
| 🧱 Notion connector | ⚪ Planned | not implemented yet, but fits the Artifact connector contract |

---

## 🖼️ Product Tour

| Area | Experience |
| --- | --- |
| **Overview** | polished command center for judges and teammates |
| **Memory Graph** | interactive visual map inspired by Obsidian knowledge graphs |
| **Ask DecisionLens** | source-grounded answers with evidence and confidence |
| **Timeline** | architecture evolution from identity to caching to event pipelines |
| **Trends** | adoption/rejection signals across technologies |
| **Upload** | instant no-LLM demo extraction from Markdown |

### Demo UI Shape

```mermaid
mindmap
  root((DecisionLens))
    Overview
      Metrics
      Source pipeline
      Judge demo path
    Memory Graph
      Technologies
      Decisions
      Uploaded memories
      Evidence panel
    Ask
      Historical context
      Citations
      Local demo memories
    Intelligence
      Timeline
      Recurring topics
      Trends
      Decision history
    Ingestion
      Markdown
      GitHub samples
      Slack samples
```

---

## 🏗️ System Architecture

```mermaid
flowchart LR
  subgraph Sources["Engineering Sources"]
    GH["GitHub PRs / commits"]
    SL["Slack threads"]
    MD["Markdown ADRs / RFCs"]
    NT["Notion docs (planned)"]
  end

  subgraph Ingestion["DecisionLens Ingestion"]
    C["Source connectors"]
    B["Ingestion buffer"]
    I["Ingestion engine"]
    Q["Artifact queue"]
  end

  subgraph Extraction["Engineering Knowledge Processing Pipeline"]
    LLM["LLM / Ollama / demo extractor"]
    KO["Knowledge objects"]
    EV["Evidence validation"]
  end

  subgraph Memory["Memory Layer"]
    SM["Supermemory"]
    SR["Semantic retrieval"]
  end

  subgraph Product["DecisionLens Product"]
    API["FastAPI"]
    UI["React dashboard"]
    GRAPH["Memory graph"]
    ASK["Ask DecisionLens"]
  end

  GH --> C
  SL --> C
  MD --> C
  NT -. future .-> C
  C --> B --> I --> Q --> LLM --> KO --> EV --> SM --> SR --> API --> UI
  UI --> GRAPH
  UI --> ASK
```

---

## 🧠 Brain Modes

DecisionLens is designed so you can demo quickly and scale later.

```mermaid
flowchart TB
  A["Choose a brain mode"]
  A --> B["Browser demo brain"]
  A --> C["Local Ollama brain"]
  A --> D["Managed/company LLM brain"]

  B --> B1["No setup"]
  B --> B2["Parses Markdown lines like Decision: ..."]
  B --> B3["Updates Memory Graph immediately"]

  C --> C1["Private local extraction"]
  C --> C2["Runs qwen3:8b or another Ollama model"]
  C --> C3["Used by backend EKPP"]

  D --> D1["Enterprise model provider"]
  D --> D2["Best for production scale"]
```

| Mode | Requires LLM? | Requires Supermemory? | Best For |
| --- | --- | --- | --- |
| Browser demo brain | ❌ No | ❌ No | hackathon demo, quick testing |
| Ollama brain | ✅ Local | 🟡 Recommended | privacy-first local extraction |
| Managed LLM brain | ✅ Hosted | ✅ Yes | production/company deployment |

**Supermemory is the long-term semantic memory layer.**
**The brain is the extractor that turns raw artifacts into structured knowledge before storage.**

---

## 📊 Demo Intelligence Snapshot

```mermaid
pie title Demo knowledge object mix
  "Decisions" : 48
  "Tradeoffs" : 31
  "Architecture changes" : 16
  "Recurring topics" : 18
  "Open questions" : 6
```

```mermaid
xychart-beta
  title "Engineering discussion volume by technology"
  x-axis ["Redis", "PostgreSQL", "Kafka", "Supabase", "Firebase"]
  y-axis "Mentions" 0 --> 30
  bar [24, 21, 17, 14, 6]
```

---

## ⚡ Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/riddhimajaiswal18/decisionlens.git
cd decisionlens
cp .env.example .env
```

### 2. Run with Docker

```bash
docker compose up --build
```

Open:

- Dashboard: [http://localhost:5173](http://localhost:5173)
- API health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 3. Run locally without Docker

Backend:

```bash
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Test Without LLM or Supermemory

This is the fastest and safest hackathon demo path.

1. Start the frontend and backend.
2. Open **Markdown upload**.
3. Upload a `.md` file like this:

```md
# Session Revocation ADR

Decision: Use Redis for immediate session revocation.
Tradeoff: Redis adds operational ownership.
Alternative: Fully stateless JWT sessions.
Architecture Change: Session middleware checks Redis before tenant queries.
Open Question: Should enterprise sessions use a shorter TTL?
```

4. Open **Memory graph**.
5. Click the uploaded memory node.
6. Open **Ask DecisionLens** and ask:

```text
Why did we choose Redis?
```

The browser demo brain will parse the Markdown and create local session memories immediately.

---

## 🦙 Test With Ollama

Use Ollama when you want local LLM extraction through the backend EKPP.

```bash
ollama serve
ollama pull qwen3:8b
```

Set `.env`:

```env
EXTRACTION_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT=120
```

Then run:

```bash
python scripts/seed.py
```

---

## 🧬 Test With Supermemory

Set `.env`:

```env
SUPERMEMORY_BASE_URL=
SUPERMEMORY_API_KEY=
SUPERMEMORY_CONTAINER_TAG=decisionlens
```

Seed the demo corpus:

```bash
python scripts/seed.py
```

The dashboard automatically prefers live FastAPI/Supermemory responses when available and falls back to polished demo data when they are not.

---

## 🔌 Connector Status

| Connector | Current Status | How To Use Today | Production Work Needed |
| --- | --- | --- | --- |
| Markdown | ✅ Working | upload `.md` / `.mdx` files or seed sample data | ingestion job status UI |
| GitHub | 🟡 Basic | sample PRs, commits, comments via seed script | GitHub OAuth/app installation |
| Slack | 🟡 Basic | sample Slack threads via seed script | Slack bot, events, permissions |
| Notion | ⚪ Planned | not available yet | Notion API connector |
| Meetings | ⚪ Future | not available yet | transcript ingestion |

---

## 🧭 Judge Demo Script

```mermaid
journey
  title DecisionLens Hackathon Demo
  section First impression
    Open Overview: 5: Presenter
    Explain the problem: 5: Presenter
  section Visual wow
    Open Memory Graph: 5: Presenter
    Click decision nodes: 5: Presenter
  section End-to-end workflow
    Upload Markdown ADR: 5: Presenter
    Show instant extracted memories: 5: Presenter
    Ask about uploaded decision: 5: Presenter
  section Supermemory story
    Explain memory layer: 4: Presenter
    Show architecture diagram: 4: Presenter
```

Recommended questions:

| Question | What DecisionLens Should Show |
| --- | --- |
| Why did we choose Redis? | decision, tradeoff, alternative, evidence |
| Why did we use PostgreSQL RLS? | architecture rationale and history |
| What alternatives were rejected? | Firebase/stateless JWT/Kafka alternatives |
| What keeps coming up repeatedly? | recurring discussion topics |

---

## 📁 Repository Layout

```text
decisionlens/
├── backend/                 FastAPI, ingestion, memory, intelligence contracts
├── frontend/                React + TypeScript + Vite + Tailwind dashboard
├── sample-data/             GitHub, Slack, and Markdown demo corpus
├── scripts/seed.py          Connector → EKPP → Supermemory demo seed pipeline
├── docs/demo.md             Judge-ready demo guide
├── docs/adr/                Architecture decision records
├── docker-compose.yml       Full-stack local deployment
└── README.md                Product and technical guide
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Lucide icons |
| Backend | FastAPI, Pydantic, async service contracts |
| Memory | Supermemory integration boundary |
| Extraction | Browser demo extractor, Ollama provider, structured extraction contracts |
| Sources | Markdown, GitHub samples, Slack samples |
| Deployment | Docker Compose, local dev servers |

---

## ✅ Verification

Current validation commands:

```bash
cd frontend
npm run build
```

```bash
python -m pytest tests
python -m compileall backend scripts
```

Expected current status:

| Check | Status |
| --- | --- |
| Frontend production build | ✅ Passing |
| Python tests | ✅ Passing |
| Backend/script compile | ✅ Passing |
| Local API health | ✅ Working |
| Markdown upload demo flow | ✅ Working |

---

## 📈 Roadmap

```mermaid
gantt
  title DecisionLens Roadmap
  dateFormat  YYYY-MM-DD
  section Hackathon
  Polished dashboard             :done,    a1, 2026-07-10, 2d
  Memory graph                   :done,    a2, 2026-07-12, 1d
  Browser demo brain             :done,    a3, 2026-07-12, 1d
  section Next
  GitHub OAuth installation      :active,  b1, 2026-07-14, 4d
  Slack app event ingestion      :         b2, 2026-07-16, 5d
  Persistent ingestion jobs      :         b3, 2026-07-18, 5d
  Notion connector               :         b4, 2026-07-22, 4d
  Workspace auth and permissions :         b5, 2026-07-24, 6d
```

---

## 🔮 Future Work

- Add authenticated workspaces and role-based access.
- Add real GitHub OAuth installation flow.
- Add Slack app event subscription and permission management.
- Add Notion connector.
- Persist ingestion job status and expose upload progress.
- Add streaming answers and richer evidence navigation.
- Add production deployment templates.
- Add screenshot/video assets for the final hackathon submission.

---

## 💡 Final Vision

DecisionLens is not just a dashboard. It is a memory layer for engineering organizations.

```mermaid
flowchart TB
  A["New engineer asks: Why was this built this way?"]
  B["DecisionLens searches engineering memory"]
  C["Supermemory retrieves relevant knowledge"]
  D["DecisionLens explains decisions, tradeoffs, alternatives"]
  E["Engineer sees source evidence"]
  F["Team stops losing institutional knowledge"]

  A --> B --> C --> D --> E --> F
```

> **DecisionLens helps teams remember not only what they built, but why they built it.**
