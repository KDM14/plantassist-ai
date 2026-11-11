# THINKING.md — PlantAssist AI

---

## 1. Understand the User

### Who is a Shop-Floor Supervisor?

A shop-floor supervisor at a precision manufacturing plant (like Kaveri Precision Components, Hosur) typically:

- Oversees **10–30 operators** across a shift (usually 8–12 hours, often rotating shifts)
- Is responsible for **production targets, quality outcomes, machine uptime and worker safety**
- Has **5–15 years of manufacturing experience** but may have limited formal IT or digital tool experience
- Operates in a **loud, physically demanding environment** — near running CNC machines, with coolant mist, metal chips and compressed air noise
- Frequently moves across the shop floor rather than sitting at a desk
- Primarily uses a **mobile phone or tablet** for communications; desktop computers are rare on the floor
- Must make decisions **quickly** — machine downtime is expensive, quality escapes can reach customers

### Their Typical Day (Assumed)

| Time | Activity |
|------|----------|
| Start of shift | Walk the floor, review previous shift handover, check machine status |
| During shift | Respond to alarms, inspect quality issues, approve decisions, escalate problems |
| Ongoing | Refer to SOPs when unusual situations arise |
| End of shift | Handover report, follow up on open issues |

**Key information needs during a shift:**
- "Machine X is showing alarm Y — what does it mean and what do I do?"
- "We're about to do maintenance — what's the LOTO procedure?"
- "Incoming batch from supplier — what dimensions should QC check?"
- "My operator is asking about coolant concentration — what's the spec?"

### Frustrations with the Current State (Assumptions)

1. **PDFs are hard to navigate on a phone.** Pinching, zooming, scrolling through 20-page manuals is frustrating when standing next to a machine.
2. **Documents are scattered.** SOPs may be on a shared drive, printed binders, QMS systems — no single point of access.
3. **Search is non-existent or poor.** CTRL+F only works if you know the exact term. Semantic search doesn't exist.
4. **Multiple document revisions create confusion.** Which version is current? Rev 03 or Rev 04?
5. **Context is missing.** The supervisor knows the problem symptom but needs to map it to the right document.
6. **Time pressure is real.** A stopped machine costs money every minute. Reading a manual takes time they don't have.
7. **Escalation loops are slow.** Calling an engineer, waiting for a callback — when a quick answer might have been in the docs.

### Consequences of Wrong Information

In manufacturing, incorrect information can cause:
- **Safety incidents** (e.g., re-energising a machine during maintenance without proper LOTO)
- **Quality escapes** (e.g., accepting a batch with the wrong tolerance)
- **Equipment damage** (e.g., using wrong hydraulic oil spec)
- **Non-compliance** (e.g., not following the latest revision of a procedure)

This is why **accuracy, source traceability and appropriate abstention** are non-negotiable requirements.

### Assumptions Made

- Supervisors are literate and comfortable in English (or their local language — this app uses English only, which may be a limitation)
- Mobile connectivity is available on the shop floor via Wi-Fi
- The plant has a standard Windows/Android environment; iOS is also common
- Supervisors have authority to look up procedures but must still follow the official chain for maintenance execution
- The app supplements — it does not replace — official QMS systems and physical SOPs

---

## 2. User Journey

### Scenario: Alarm during CNC turning shift

**Persona:** Rajan, Shift Supervisor, 11 years experience, using an Android phone mid-shift.

---

**Step 1 — Problem arises**
Rajan is walking the floor at 2 AM. CNC-07 stops with an alarm. The operator calls him over.

**Step 2 — Opens PlantAssist AI**
Rajan opens the app on his phone, connected to the plant's Wi-Fi. He sees the welcome screen: "Good morning, Supervisor. How can I help you with your operations today?"

**Step 3 — Uses Quick Action or types question**
He taps the "Machine Troubleshooting" quick action card. The question pre-populates: *"The TX-200 is showing alarm AL-104. What does it mean and what should I do?"*
He sends it.

**Step 4 — App searches documents**
The app shows a "Searching documents..." loading indicator. The RAG pipeline runs:
- Query embedding generated
- ChromaDB searches semantic similarity across the indexed chunks
- Top 5 relevant chunks retrieved from the maintenance manual

**Step 5 — Answer displayed**
The app responds:
> "Alarm AL-104 means Way lube oil level low. Top up with ISO VG 68 oil to the MAX mark, then press RESET. The machine can continue after reset.
> Source: MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf, Page 2"

Rajan sees the green "Document sourced" badge and the source card showing the exact document and page number.

**Step 6 — Rajan verifies and acts**
He sends his operator to top up the lube oil. Machine restarts. Problem solved in under 3 minutes.

**Step 7 — Rajan's follow-up question**
He wonders about the correct lube oil spec and types: "What type of oil should I use for the TX-200 way lube system?" — gets the ISO VG 68 answer immediately.

---

### Failure Scenarios and How the App Handles Them

| Scenario | App Behaviour |
|----------|--------------|
| **No relevant document** | Returns abstention message: "I couldn't find sufficient information in the available manufacturing documents..." with amber "Not in documents" badge |
| **Ambiguous question** | LLM answers based on best-matched context; if multiple interpretations, it notes the ambiguity |
| **Contradictory documents** (e.g., Rev 03 vs Rev 04 of QC-SOP-014) | LLM instructed to note contradictions and advise checking the latest revision |
| **Outdated documents** | App cannot know if content is outdated — this is documented as a limitation; source citations help users verify |
| **Poor PDF extraction** (scanned PDFs) | Extractor logs a warning, ingestion stats show it; app may return limited or no results |
| **Network failure** | Frontend catches fetch error, shows "Connection error: check if backend is running" |
| **LLM API failure** | Backend catches exception, returns evidence_status=error with the retrieved sources still shown |
| **Incorrect retrieval** | Similarity score shown; if below threshold, abstention triggers |
| **Safety-critical uncertainty** | Safety keyword detection adds disclaimer: "⚠️ For safety-critical operations, follow approved plant procedures and escalate uncertainty to your supervisor" |
| **Mobile connectivity drop** | Graceful error message shown; previous answers remain visible in the conversation |

---

## 3. AI Challenge

### Prompt Used

> "Act as a skeptical manufacturing supervisor and enterprise product manager. Critically evaluate this proposed AI copilot user journey. Identify unrealistic assumptions, missing requirements, safety risks, workflow problems, usability limitations and product improvements. Do not simply agree with the proposal. Explain what would prevent a real supervisor from using this application."

### Key AI Critique Points (Conversation Excerpts)

---

**AI (as Skeptical Supervisor):**

> "Rajan tapping the app at 2 AM while standing next to a noisy CNC machine? In my experience, the first reaction is to call the maintenance engineer, not open an app. Why would I trust an AI over a person I've worked with for years? Also, if this is a safety-critical alarm, there should be a warning before the operator acts — not just an answer."

**AI (as Product Manager):**

> "The user journey assumes Wi-Fi connectivity is reliable across the shop floor. In many plants, coverage near heavy machinery is poor due to metal shielding. What's your offline strategy?
>
> Also, you have two versions of QC-SOP-014 indexed — Rev 03 and Rev 04. What happens when the AI returns an answer from Rev 03 (the outdated version)? The supervisor has no way to know which is current unless you surface that information prominently.
>
> And where's the feedback loop? If the AI gives a wrong answer, how does the QC or Safety Manager find out and correct it?"

**AI (as Supervisor):**

> "What if I'm wearing thick gloves? Touch-typing on a small phone keyboard is not realistic. Voice input would be far more useful. And the answers — I don't want a paragraph. I want one line: what the problem is and what to do. Only then do I want more."

**AI (as Product Manager):**

> "Three things missing from your implementation plan:
> 1. **Audit trail** — in regulated manufacturing, every query and answer may need to be logged for compliance purposes.
> 2. **Document freshness indicators** — when was each document last updated? The app should surface this.
> 3. **Multi-language support** — shop-floor workers in India often work better in Tamil or Hindi than English."

---

### My Reflection

**What I agreed with:**

- The concern about **document versioning** is valid and important. I addressed this by: (a) indexing both Rev 03 and Rev 04 and letting the LLM see both; (b) instructing the LLM to flag contradictions between documents; (c) showing the source document name which includes the revision number. A future improvement would be a "superseded document" warning.

- The **offline strategy** gap is real. Currently the app requires connectivity. I've noted this as a known limitation and a future improvement item.

- The **audit trail** point is well-taken. I implemented SQLite conversation history which provides basic traceability. A production system would need a more robust audit log with timestamps, user IDs and query-response pairs.

- **Safety escalation** — I added explicit safety keyword detection and a prominent warning banner on all safety-related answers, reinforcing that the app is not a replacement for plant-approved procedures.

**What I disagreed with:**

- The claim that supervisors "won't use an app" and will always call an engineer. This may be true for safety-critical maintenance but is not true for quick operational queries (coolant concentration, alarm meanings). The Quick Action cards target exactly these high-frequency, low-stakes lookups.

- The voice input suggestion: valuable long-term, but scope-inappropriate for a 5–6 hour assignment. I designed the Quick Action cards as a glove-friendly alternative — large touch targets, pre-populated questions, minimal typing.

**What I changed:**

- Added **prominent evidence badges** (Document sourced vs Not in documents) so the supervisor always knows whether the answer has backing.
- Made source document names prominent with revision numbers visible.
- Added the **safety warning banner** for safety-related queries.
- Noted the abstention message should mention consulting a supervisor, not just "look at the documents."
- Added the conversation history API to support future compliance/audit use cases.

---

## 4. The Improvement I Added and Why I Chose It

### Feature: Shop-Floor Quick Action Mode

**What it is:**
Four large, touch-friendly cards on the home screen covering the most common supervisor query categories:
1. Machine Troubleshooting
2. Safety Procedures
3. Quality Inspection
4. Preventive Maintenance

Each card pre-populates a contextually relevant question. One tap → question sent → answer delivered. No typing required.

**Why I chose this over other possible improvements:**

The core user insight is that supervisors in a live production environment don't have the luxury of composing a well-structured question. They are:
- Standing up, possibly with gloves on
- Under time pressure (every minute of machine downtime costs money)
- Dealing with an immediate, specific problem

The Quick Action pattern reduces interaction to **one tap** for the most frequent query types. It also acts as a discoverability mechanism — new users see what the app can answer, which lowers the adoption barrier.

I deliberately chose **breadth** (four distinct categories) over depth, because the goal is to handle the 80% of common queries efficiently, not to build an exhaustive menu.

**Why not voice input?**
Voice input requires a speech-to-text integration (browser API or external service), is unreliable in noisy environments, and raises privacy concerns in a plant setting. Quick Action cards solve the "typing is hard with gloves" problem more reliably.

**Why not offline mode?**
Offline RAG would require the entire vector store and LLM to run on the device — practical with Ollama but requiring a local GPU or significant download. This is noted as a future improvement but is out of scope for a 5–6 hour exercise.

---

## 5. Final Reflection

### What I Would Build Next

1. **Document freshness tracking and superseded document warnings.** When Rev 04 of a document exists, the app should warn if any chunk from Rev 03 is cited. This prevents supervisors from acting on outdated procedures.

2. **Voice input.** Even basic browser Web Speech API integration would dramatically improve usability in a shop-floor context. The backend API is already well-structured to receive queries from any input source.

3. **Offline-capable progressive web app (PWA).** Caching the most recent conversation and health status offline would improve reliability in poor-connectivity areas of the plant.

4. **Role-based access and audit logging.** A production deployment would need user authentication, per-user query logs, and integration with the plant's QMS for compliance reporting.

5. **Multi-language support.** For plants in India, support for Tamil, Hindi and Telugu would significantly broaden adoption among operators who may query the app themselves.

6. **Document upload and automatic ingestion** via the UI — currently accessible via API but not surfaced in the frontend.

7. **Feedback loop.** A thumbs up/down on each answer, with feedback stored for QA review. Incorrect answers flagged by supervisors should trigger a document review.

### What Remains Uncertain

- **LLM answer quality in production.** The RAG pipeline is well-structured but answer quality depends heavily on the LLM. A few documents and a small context window mean the system should perform well, but I cannot guarantee accuracy without sustained testing against real plant queries.

- **Wi-Fi coverage.** The assignment assumes reliable connectivity. Real shop-floor coverage varies significantly.

- **Document quality.** The four supplied PDFs are clean, well-structured text PDFs. Real plant documents may be scanned, poorly formatted, or in mixed languages — requiring OCR and more robust extraction.

- **User adoption.** Technology adoption on a shop floor is a people problem as much as a technology problem. Training, management buy-in and trust-building are outside the app's scope.

### What I Would Ask the Customer

1. How many documents does the plant actually have? (Affects ChromaDB sizing and retrieval quality)
2. Are any documents scanned or image-only PDFs?
3. What languages do supervisors primarily work in?
4. Is there an existing QMS we need to integrate with?
5. What are the compliance and audit requirements for query logging?
6. What devices are supervisors actually using? (Android/iOS, screen size)
7. Is internet connectivity available on the shop floor, or must it work on a local LAN only?

### Biggest Technical Challenge

**The two versions of QC-SOP-014 (Rev 03 and Rev 04) represent a real production risk.** Both are indexed because both were provided. The LLM receives chunks from both and must synthesise a coherent answer. Without explicit version control logic, the app may cite an outdated procedure.

I handled this by:
- Ensuring the source document name (including revision) is always shown prominently
- Instructing the LLM to flag contradictions between documents
- Noting in the README that document curation is the administrator's responsibility

A proper fix would require a document lifecycle management layer with explicit supersession tracking.

### Challenges During Implementation

1. **Vite scaffold via npx was interactive and couldn't be automated** — I created the frontend package.json and configuration files manually instead.

2. **ChromaDB cosine distance conversion** — ChromaDB returns cosine distance (0=identical, 2=opposite), not similarity. I converted using `similarity = 1 - (distance / 2)` and tuned the relevance threshold to 0.35 after testing against the actual documents.

3. **PyMuPDF API changes** — The new PyMuPDF 2.x API has changed method names (`get_text` etc.). I handled this with a fallback to `pypdf` when PyMuPDF fails.

4. **Dependency conflicts** — The shared Anaconda environment had many pre-installed packages with version conflicts. These don't affect PlantAssist AI's runtime as only the packages it uses matter.

### Deployment Challenges

**Local Network Access:**
- Backend binds to `0.0.0.0:8000` — accessible from any device on the same Wi-Fi
- Frontend binds to `0.0.0.0:5173` via Vite's `server.host: true`
- Frontend uses `window.location.hostname` to auto-detect the backend URL — no hardcoded `localhost`
- Find your LAN IP: `ipconfig getifaddr en0` (macOS)
- Mobile URL: `http://<your-ip>:5173`

**Firewall:** macOS may prompt to allow incoming connections for Node.js and Python. Accept both prompts.

### Limitations of the Current Solution

| Limitation | Severity | Mitigation |
|-----------|----------|------------|
| No document version control | High | Show source name with revision; LLM flags contradictions |
| No offline support | Medium | Document as known limitation |
| No user authentication | Medium | Acceptable for internal LAN deployment |
| English-only | Medium | Note in README |
| LLM hallucination risk | High | Strict grounding instructions; abstention logic; source citations required |
| Scanned PDF support (OCR) | Low for provided docs | Log warning; skip empty-text pages |
| No voice input | Low | Quick Action cards as alternative |
