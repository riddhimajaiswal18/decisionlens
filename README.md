# 🧠 DecisionLens — Engineering Intelligence Platform

<div align="center">

<img src="https://img.shields.io/badge/Hackathon-Supermemory%20Build%20Challenge-6366f1?style=for-the-badge&logo=lightning&logoColor=white"/>
<img src="https://img.shields.io/badge/Stack-FastAPI%20%2B%20React%20%2B%20Supermemory-14b8a6?style=for-the-badge&logo=react&logoColor=white"/>
<img src="https://img.shields.io/badge/Status-Hackathon%20Ready-10b981?style=for-the-badge&logo=checkmarx&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge"/>

---

### *"Turn engineering conversations into institutional memory."*

**DecisionLens** watches your GitHub PRs, Slack threads, and Markdown ADRs —  
extracts structured knowledge objects — and stores them in **Supermemory**  
for instant, evidence-backed retrieval. Never lose context again.

---

</div>

## 🎯 The Problem

> **Knowledge gets lost.** Every day, critical engineering decisions are made in Slack threads, PR comments, and ADR documents — and then forgotten.

```
Senior engineer leaves  →  Why Redis?  →  Nobody knows anymore.
New team member joins   →  Repeats same debates, same mistakes.
Architecture review     →  Zero institutional memory to draw from.
```

**This is the $1.8T problem of institutional knowledge loss** — and it's entirely solvable.

---

## 💡 The Solution — DecisionLens

```
┌─────────────────────────────────────────────────────────────────┐
│                    DecisionLens Pipeline                         │
│                                                                   │
│   Sources         Ingest          Extract        Memory           │
│  ┌────────┐     ┌────────┐     ┌────────┐     ┌────────────┐    │
│  │ GitHub │────▶│Normalize│────▶│  EKPP  │────▶│Supermemory │    │
│  │ Slack  │     │Artifact │     │ Ollama │     │  :6767     │    │
│  │  ADRs  │     │ Queue   │     │  Demo  │     │            │    │
│  └────────┘     └────────┘     └────────┘     └─────┬──────┘    │
│                                                       │           │
│                                                       ▼           │
│                                              ┌──────────────┐    │
│                                              │ Intelligence  │    │
│                                              │  Timeline     │    │
│                                              │  Trends       │    │
│                                              │  Q&A          │    │
│                                              └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)              │
│  Dashboard · Memory Graph · Ask · Timeline · Trends   │
│  Dark/Light Mode · ⌘K Command Palette · Live Charts   │
└─────────────────────┬────────────────────────────────┘
                       │ REST API (auto-fallback to demo)
┌─────────────────────▼────────────────────────────────┐
│              BACKEND (FastAPI + Python)                │
│  /ingest  /search  /health  /memories  /trends        │
│  Source Connectors → Ingestion Engine → EKPP          │
└─────────────────────┬────────────────────────────────┘
                       │ Semantic Memory SDK
┌─────────────────────▼────────────────────────────────┐
│           SUPERMEMORY (localhost:6767)                  │
│   Long-term semantic memory · Vector search            │
│   Knowledge objects · Evidence retrieval               │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Knowledge Object Types

| Type | Description | Example |
|------|-------------|---------|
| 🟣 **Decision** | Final choice made by the team | *"Use Redis for session revocation"* |
| 🔵 **Tradeoff** | Trade evaluated during decision | *"Redis adds operational overhead vs JWT"* |
| 🟡 **Alternative** | Option that was rejected | *"Firebase — rejected due to vendor lock-in"* |
| 🟠 **Architecture Change** | Structural modification | *"Kafka introduced as billing event boundary"* |
| 🔴 **Open Question** | Unresolved debate | *"Should we shard PostgreSQL now or later?"* |
| ⚪ **Document** | Raw ADR or RFC | *"ADR-001: Multi-tenant Authorization"* |

---

## 🕸️ Memory Graph — Knowledge Topology

```
                    ┌─────────────────┐
                    │  DecisionLens 🧠 │  ← Central hub
                    └────────┬────────┘
         ┌──────────┬────────┼────────┬──────────┐
         ▼          ▼        ▼        ▼          ▼
    Supermemory   Redis⚡  Kafka📨  PostgreSQL🐘  Supabase🗄️
    [:6767]     [session] [events]  [primary DB]  [auth+RLS]
         │          │                   │
         ▼          ▼                   ▼
    [Stripe💳]  [JWT⛔]            [Markdown📝]
                rejected           ADR corpus
```

**12 nodes · 15 typed edges · Active edge highlighting on selection**

---

## 📈 Real Data — Seeded Corpus

```
┌─────────────────────────────────────────────────┐
│          Technology Mention Volume               │
│                                                   │
│  Redis       ████████████████████████  24        │
│  PostgreSQL  █████████████████████    21        │
│  Kafka       █████████████████        17        │
│  Supabase    ██████████████           14        │
│  Firebase    ██████                    6        │
│                                                   │
│          Knowledge Object Mix                     │
│                                                   │
│  Decisions   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  48               │
│  Tradeoffs   ▓▓▓▓▓▓▓▓▓▓       31               │
│  Arch Chgs   ▓▓▓▓▓            16               │
│  Recurring   ▓▓▓▓▓▓           18               │
│  Open Qs     ▓▓                6               │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
python >= 3.11
node >= 18
supermemory running on localhost:6767

# Optional (for LLM extraction)
ollama with llama3.2 or similar
```

### 1 — Start Supermemory

```bash
# Clone and run supermemory locally
git clone https://github.com/supermemoryai/supermemory
cd supermemory && npm install && npm run dev
# → Running on http://localhost:6767
```

### 2 — Backend Setup

```bash
cd decisionlens/backend

# Create virtualenv
python -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env → set SUPERMEMORY_API_URL=http://localhost:6767

# Start the API
uvicorn app.main:app --reload --port 8000
# → API running on http://localhost:8000
```

### 3 — Seed the Demo Corpus

```bash
cd decisionlens

# This is the primary demo path for judges
python scripts/seed.py

# Expected output:
# ✓ Seeded 48 decisions
# ✓ Seeded 31 tradeoffs
# ✓ Seeded 16 architecture changes
# ✓ Memory corpus ready in Supermemory
```

### 4 — Frontend Setup

```bash
cd decisionlens/frontend
npm install
npm run dev
# → Dashboard at http://localhost:5173
```

---

## 🎬 Judge Demo Path

```
Step 1  →  Open http://localhost:5173
Step 2  →  Dashboard shows live stats (48 decisions, 31 tradeoffs, 16 arch changes)
Step 3  →  Click "Memory Graph" → explore 12-node hub-and-spoke graph
Step 4  →  Click "Ask DecisionLens" → type "Why did we choose Redis?"
Step 5  →  See evidence-backed answer with source quotes + confidence score
Step 6  →  Click "Architecture Timeline" → see chronological decision history
Step 7  →  Click "Technology Trends" → see Redis adoption vs Firebase rejection
Step 8  →  Click "Ingest Documents" → upload an ADR Markdown file live
Step 9  →  Watch the memory graph update with new extracted knowledge nodes
```

---

## 🧠 How Supermemory Powers Everything

```python
# Storing a knowledge object
client.memory.add(
    content = "Decision: Use Redis for immediate session revocation",
    metadata = {
        "kind":       "decision",
        "entity":     "Redis",
        "source":     "slack:C-PLATFORM-2024",
        "confidence": 0.94,
        "tradeoff":   "Operational overhead vs stateless JWT",
        "evidence":   "We chose Redis because we need immediate revocation..."
    }
)

# Retrieving evidence-backed answers
results = client.memory.search(
    query    = "Why did we choose Redis over JWT?",
    top_k    = 5,
    filters  = {"kind": "decision"}
)
# → Returns ranked memories with source evidence
```

**Supermemory acts as the long-term semantic brain** — every decision, tradeoff, and architecture change is stored as a searchable, evidence-backed memory object.

---

## 🔌 Source Connectors

| Connector | What It Extracts | Status |
|-----------|------------------|--------|
| 🐙 **GitHub** | PR descriptions, commit messages, code comments | ✅ Active |
| 💬 **Slack** | Engineering channel threads, decision discussions | ✅ Active |
| 📝 **Markdown** | ADRs, RFCs, design docs with `Decision:` patterns | ✅ Active |
| 🗂️ **Notion** | Wiki pages and decision logs | 🔧 Planned |
| 🎫 **Jira** | Ticket descriptions and resolution notes | 🔧 Planned |

---

## 🎨 Frontend Pages

| Page | Key Features |
|------|-------------|
| 🏠 **Overview** | Hero banner · Vertical pipeline · Radial mindmap · 4 stat cards with sparklines · Bar chart · Donut chart · Activity feed |
| 🕸️ **Memory Graph** | 12-node SVG force-graph · Dot-grid bg · Glow filters · Active edge highlighting · Node detail sidebar |
| 💬 **Ask** | Suggested query chips · Evidence trail · Confidence progress bar · Rejected alternatives panel |
| 🕰️ **Timeline** | Color-coded glowing timeline · Confidence bar chart · Architecture layer summaries |
| 🔁 **Recurring** | Per-topic colored cards · Intensity bars · Frequency chart |
| 📈 **Trends** | Adoption volume bars · Signal badges · Adoption/rejection donut |
| 📜 **History** | Entity search · Participant chips · Evidence timeline · Tradeoffs panel |
| 📤 **Ingest** | Animated drop zone · Live extraction preview · ADR sample block |
| ⚙️ **Settings** | Brain mode selector · Integration status · Privacy features |

---

## 🗂️ Project Structure

```
decisionlens/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── connectors/
│   │   │   ├── github.py        # GitHub PR/commit connector
│   │   │   ├── slack.py         # Slack thread connector
│   │   │   └── markdown.py      # ADR/RFC connector
│   │   ├── extraction/
│   │   │   ├── ekpp.py          # Knowledge Pattern Processor
│   │   │   ├── ollama.py        # LLM-backed extractor
│   │   │   └── demo.py          # Regex-based demo extractor
│   │   └── memory/
│   │       └── supermemory.py   # Supermemory SDK wrapper
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # 9 pages + SVG charts + ⌘K search
│   │   ├── index.css            # Dark glassmorphism design system
│   │   ├── components/
│   │   │   └── PageShell.tsx    # Sidebar + topbar + mobile nav
│   │   ├── data/
│   │   │   └── demo.ts          # Fallback demo fixtures
│   │   └── services/
│   │       └── api.ts           # Auto-fallback API client
│   └── package.json
│
├── scripts/
│   └── seed.py                  # Judge demo corpus seeder
│
└── README.md                    # You are here ✦
```

---

## 🔬 Extraction Pipeline — Technical Deep Dive

```
Raw Input (GitHub PR / Slack Thread / Markdown ADR)
         │
         ▼
  ┌─────────────┐
  │  Normalizer │  → Strips noise, extracts plain text
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     ┌──────────────────────────────────┐
  │    EKPP     │────▶│  Pattern Matching (Demo Mode)     │
  │  Processor  │     │  "Decision:", "Tradeoff:", etc.   │
  └──────┬──────┘     └──────────────────────────────────┘
         │             ┌──────────────────────────────────┐
         └────────────▶│  Ollama LLM (Production Mode)    │
                       │  llama3.2 · structured output    │
                       └──────────────────────────────────┘
         │
         ▼
  ┌─────────────┐
  │  Supermemory│  → Stores as typed memory with metadata
  │   :6767     │
  └─────────────┘
```

**Two extraction modes:**
- 🟢 **Demo mode** — Regex-based, instant, no LLM required. Perfect for judges.
- 🔵 **Ollama mode** — Full LLM extraction with structured output. Higher accuracy.

---

## 📐 API Reference

```bash
# Health check
GET  /health
# → { "status": "ok", "supermemory": "connected" }

# Ingest a document
POST /ingest
{
  "source": "github",
  "content": "PR #184: Added Kafka for billing events...",
  "metadata": { "url": "github.com/org/repo/pull/184" }
}

# Semantic search
POST /search
{
  "query": "Why did we choose Redis over JWT?",
  "top_k": 5,
  "filter": { "kind": "decision" }
}

# Get all memories
GET  /memories?limit=50&kind=decision

# Get technology trends
GET  /trends

# Get architecture timeline
GET  /timeline
```

---

## 🏆 Hackathon — Supermemory Build Challenge

**This project was built for the Supermemory Build Challenge** with the goal of demonstrating Supermemory as the backbone of an engineering intelligence platform.

### Supermemory Usage
| Feature | How Supermemory is Used |
|---------|------------------------|
| **Memory Storage** | Every extracted knowledge object stored as a typed memory with rich metadata |
| **Semantic Search** | Natural-language Q&A powered by Supermemory vector search |
| **Evidence Retrieval** | Source quotes surfaced from stored memories for evidence-backed answers |
| **Long-term Persistence** | All knowledge survives server restarts — true institutional memory |

### Innovation
- **Multi-source ingestion** — GitHub + Slack + Markdown in one unified memory
- **Structured extraction** — EKPP turns raw text into typed knowledge objects  
- **Evidence-first design** — Every answer cites its source memory
- **Zero cloud dependency** — 100% self-hosted, data never leaves your infrastructure

---

## 👥 Team

| Name | Role |
|------|------|
| **Riddhi Majaiswal** | Backend · Supermemory integration · Extraction pipeline |
| **Sai Chaitu** | Frontend · UI/UX · Design system · Visualizations |

**Repository:** [riddhimajaiswal18/decisionlens](https://github.com/riddhimajaiswal18/decisionlens)

---

## 📜 License

MIT © 2026 DecisionLens Team

---

<div align="center">

**Built with ❤️ for the Supermemory Build Challenge**

*"Everything you need to know from Day 0."*

</div>
