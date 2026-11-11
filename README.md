# PlantAssist AI 🏭

**Your Manufacturing Knowledge Copilot**

PlantAssist AI is a Retrieval-Augmented Generation (RAG) application built for shop-floor supervisors at precision manufacturing plants. Supervisors can ask questions in natural language and get accurate, traceable answers drawn exclusively from their plant's official PDF documents — SOPs, maintenance manuals, and safety procedures.

> Built as a take-home assignment for BiztelAI Technologies (Junior Software Engineer – Full Stack / AI).  
> 📹 **Video Demo Walkthrough (Loom):** [Watch Demo (2.5 mins)](https://www.loom.com/share/055cc596510547cb8c8c5a190952f6c2)

---

## The Problem

A manufacturing plant has hundreds of PDFs covering quality, maintenance, and safety. During a shift, a supervisor facing a machine alarm or a maintenance query must either hunt through binders of paper documents or wait for an experienced colleague. Both are slow and risky.

**PlantAssist AI** gives that supervisor an instant, grounded answer from the official documents, with the source document and page number always shown — so they can verify and act confidently.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PlantAssist AI                       │
│                                                         │
│  ┌──────────┐    HTTP     ┌──────────────────────────┐  │
│  │  React   │ ──────────► │      FastAPI Backend      │  │
│  │  Vite    │ ◄────────── │                          │  │
│  │  Tailwind│             │  ┌────────┐  ┌────────┐  │  │
│  └──────────┘             │  │  RAG   │  │ SQLite │  │  │
│                           │  │Pipeline│  │History │  │  │
│                           │  └───┬────┘  └────────┘  │  │
│                           │      │                    │  │
│                           │  ┌───▼──────────────────┐ │  │
│                           │  │  ChromaDB (vectors)  │ │  │
│                           │  │  SentenceTransformers│ │  │
│                           │  └──────────────────────┘ │  │
│                           │      │                    │  │
│                           │  ┌───▼──────────────────┐ │  │
│                           │  │  LLM (OpenAI/Gemini/ │ │  │
│                           │  │  Ollama / Fallback)   │ │  │
│                           │  └──────────────────────┘ │  │
│                           └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**RAG Pipeline:**
1. User query → embedding (all-MiniLM-L6-v2)
2. Semantic search over ChromaDB (cosine similarity)
3. Two-stage abstention: similarity threshold + lexical subject-overlap guard
4. Retrieved chunks → LLM prompt (or direct excerpt fallback)
5. Answer + sources returned to UI

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic |
| PDF extraction | PyMuPDF (pymupdf), pypdf (fallback) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector store | ChromaDB (local, persistent) |
| LLM | OpenAI / Google Gemini / Ollama (configurable) |
| Conversation history | SQLite (aiosqlite) |
| Frontend | React 18, Vite, Tailwind CSS, Lucide React |
| Testing | Pytest, FastAPI TestClient |

---

## Project Structure

```
plantassist-ai/
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings (env-driven)
│   │   ├── database.py        # SQLite: conversations & messages
│   │   ├── main.py            # FastAPI app, CORS, startup
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── chat.py        # POST /api/chat
│   │   │   ├── documents.py   # GET/POST /api/documents
│   │   │   └── health.py      # GET /api/health
│   │   ├── services/
│   │   │   ├── ingestion.py   # PDF → chunks → ChromaDB
│   │   │   ├── retrieval.py   # Semantic search + abstention
│   │   │   ├── llm.py         # LLM integration + fallback
│   │   │   └── rag.py         # Orchestrates the full RAG pipeline
│   │   └── utils/
│   │       └── pdf_extractor.py  # PyMuPDF, chunking, hashing
│   ├── ingest.py              # CLI ingestion script
│   ├── requirements.txt
│   └── tests/
│       ├── conftest.py
│       ├── test_ingestion.py
│       ├── test_rag.py
│       └── test_api.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── SourceCard.jsx
│   │   │   ├── EvidenceBadge.jsx
│   │   │   ├── QuickActions.jsx
│   │   │   └── LoadingDots.jsx
│   │   ├── hooks/useChat.js
│   │   └── utils/api.js       # Auto-detects LAN backend URL
│   └── vite.config.js         # host: 0.0.0.0 for LAN access
├── data/
│   └── docs/                  # Place your PDFs here
├── THINKING.md
├── README.md
└── .env.example
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

Optional:
- An OpenAI, Google Gemini, or Ollama API key for synthesized LLM answers.  
  Without one, the app runs in **fallback mode** — it returns direct document excerpts clearly labeled. Answers are still grounded and sourced.

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/plantassist-ai.git
cd plantassist-ai
```

### 2. Configure environment (optional LLM)

```bash
cp .env.example .env
# Edit .env to add your LLM API key if desired:
#   OPENAI_API_KEY=sk-...
#   or GEMINI_API_KEY=...
```

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Place PDFs in the docs folder

```bash
# Copy your manufacturing PDFs to:
data/docs/
```

The four sample PDFs for this assignment are:
- `MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf`
- `QC-SOP-014_Rev03_Incoming_Material_Inspection.pdf`
- `QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf`
- `SAF-SOP-003_Lockout_Tagout_Procedure.pdf`

### 6. Ingest PDFs into the vector store

```bash
python3 backend/ingest.py
```

To force re-ingestion of all documents:
```bash
python3 backend/ingest.py --force
```

You should see output like:
```
Ingested MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf → 5 chunks
Ingested SAF-SOP-003_Lockout_Tagout_Procedure.pdf → 5 chunks
...
Total: 4 documents, 21 chunks
```

---

## Running the Application

### Start the backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### Start the frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The UI is now available at `http://localhost:5173`.

---

## Local Network Access (Phone / Tablet)

PlantAssist AI is designed to be used on mobile devices on the shop floor.

**Find your laptop's LAN IP:**
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'
```

Then open on your phone:
```
http://<YOUR-LAN-IP>:5173
```

The frontend auto-detects the backend at `<same-host>:8000`, so no configuration is needed.  
Make sure your phone is connected to the same Wi-Fi network as your laptop.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Submit a question, get an answer with sources |
| `GET` | `/api/health` | Health check + indexed document count |
| `GET` | `/api/documents` | List all indexed documents |
| `POST` | `/api/documents/ingest` | Trigger ingestion via API |
| `GET` | `/api/history/{conversation_id}` | Retrieve conversation history |

### Example: POST /api/chat

**Request:**
```json
{
  "question": "What is the recommended coolant concentration for the TX-200?",
  "conversation_id": null
}
```

**Response:**
```json
{
  "answer": "The recommended coolant concentration for the TX-200 is 6–8%...",
  "sources": [
    {
      "document_name": "MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf",
      "page_number": 1,
      "excerpt": "Coolant concentration: 6–8% (refractometer check)...",
      "similarity": 0.82
    }
  ],
  "evidence_status": "supported",
  "conversation_id": "uuid-here"
}
```

---

## Running Tests

```bash
cd backend
python3 -m pytest tests/ -v
```

Expected output: **53 passed**

The test suite covers:
- PDF extraction and chunking (`test_ingestion.py`)
- RAG pipeline logic, abstention, and evidence evaluation (`test_rag.py`)
- All API endpoints via FastAPI TestClient (`test_api.py`)

---

## Sample Questions & Answers

### BiztelAI Provided Questions

**Q1: What is the recommended coolant concentration for the TX-200 CNC machine?**

> **Answer:** The recommended coolant concentration for the TX-200 is **6–8%**, verified using a refractometer check.  
> **Source:** MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf, Page 1

---

**Q2: What does alarm AL-104 mean, and what action should be taken?**

> **Answer:** Alarm AL-104 indicates **"Way lube oil level low."** The required action is to top up the way lube oil to the MAX mark using **ISO VG 68 oil**, then press **RESET** to clear the alarm.  
> **Source:** MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf, Page 2

---

**Q3: Who is allowed to remove a lockout lock, and what happens if that person is unavailable?**

> **Answer:** Only the **authorised person who applied the lock** may remove it. If that person is unavailable:
> 1. The Shift Supervisor attempts to contact them.
> 2. If unreachable, both the **Production Manager** and the **Safety Officer** must jointly authorise removal.
> 3. The machine must be physically inspected before re-energisation.
> 4. The incident is recorded on form **SF-12**.  
>
> **Source:** SAF-SOP-003_Lockout_Tagout_Procedure.pdf, Pages 1–2

---

**Q4: What is the dimensional tolerance for the BH-220 component outer diameter?**

> **Answer:** The outer diameter tolerance for component BH-220 is **90.000 ±0.050 mm**. It is classified as a **Major** characteristic and must be measured with a **digital caliper**.  
> **Source:** QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, Page 2

---

**Q5: How often should the spindle runout be checked, and who is responsible?**

> **Answer:** Spindle runout must be checked **monthly** by a **Maintenance Technician** using a dial indicator, with an acceptance criterion of ≤ 0.005 mm TIR.  
> **Source:** MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf, Page 1

---

### My Own Questions (5)

**CQ1: What type of hydraulic oil is used in the TX-200, and when should it be replaced?**

> **Answer:** The TX-200 uses **ISO VG 46 hydraulic oil**, which should be replaced **yearly**. The way lube system uses **ISO VG 68 oil**.  
> **Source:** MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf, Page 1

---

**CQ2: What is the required torque and sequence for tightening chuck jaws on the TX-200?**

> **Answer:** Chuck jaws must be tightened to **110 Nm** using a **calibrated torque wrench**, in a **criss-cross (star) sequence** to ensure even clamping.  
> **Source:** MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf, Page 2

---

**CQ3: What action must be taken if a critical defect is found during incoming material inspection?**

> **Answer:** If a **Critical** defect is found, the **entire lot must be rejected and returned to the supplier**. Sorting of the lot is **not permitted**.  
> **Source:** QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, Page 1

---

**CQ4: What is the procedure if the person who applied a lockout lock cannot be reached?**

> **Answer:** The Shift Supervisor must first attempt to contact the absent lock owner. If unreachable, the **Production Manager and Safety Officer must jointly authorise** removal of the lock. The machine must be physically inspected before re-energisation, and the event recorded on form **SF-12**.  
> **Source:** SAF-SOP-003_Lockout_Tagout_Procedure.pdf, Pages 1–2

---

**CQ5: What is the salary structure and overtime policy for shift supervisors? *(Unanswerable)*

> **Answer:** "I couldn't find sufficient information in the available manufacturing documents to answer this question reliably. Please consult your supervisor or the relevant equipment specialist."  
> *(Correctly abstained — HR/payroll information is not present in the indexed SOPs or manuals.)*

---

## Known Limitations

- **No LLM key → fallback mode:** Without an API key, answers are direct document excerpts clearly labeled as such. Configure `OPENAI_API_KEY` or `GEMINI_API_KEY` in `.env` for synthesized answers.
- **English only:** All documents and queries are expected in English.
- **No user authentication:** Suitable for a trusted internal network; not production-hardened.
- **No offline mode:** Requires network connectivity to reach the backend.
- **Scanned PDFs not supported:** OCR is not included; text-based PDFs only.

---

## What I Would Build Next

1. **Voice input** — a mic button so supervisors can ask questions hands-free while wearing gloves
2. **Offline PWA** — cache the last N answers for use in dead-zone areas of the plant
3. **Multi-language support** — Tamil, Hindi for shop-floor workers; English for supervisors
4. **Document upload in UI** — drag-and-drop new PDFs directly from the browser
5. **Feedback loop** — thumbs up/down per answer, feeding back to improve retrieval
6. **Role-based access** — separate views for operators, supervisors, maintenance engineers
7. **Alert integration** — push notifications when a document relevant to an active alarm is updated

---

## License

MIT — built for the BiztelAI assignment. Not for production use without further hardening.
