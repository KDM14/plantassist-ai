# Screen Recording Script — PlantAssist AI Demo
# Duration: ~2.5 minutes
# Tool: QuickTime Player (macOS) or Loom

---

## BEFORE YOU START

1. Backend running:  `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Frontend running: `cd frontend && npm run dev`
3. Browser open at:  `http://localhost:5173`
4. Phone connected to same Wi-Fi, browser open to `http://192.168.0.213:5173`
5. Browser DevTools closed (clean look)
6. Screen brightness high

---

## SEGMENT 1 — App Introduction (0:00–0:30)

**Show:** `http://localhost:5173`

**Narrate:**
> "This is PlantAssist AI — a manufacturing knowledge copilot built for shop-floor supervisors.
> I'll show you how a supervisor can get instant, sourced answers from their plant's official PDFs."

**Action:** Scroll slowly to show:
- Header: "PlantAssist AI — Your Manufacturing Knowledge Copilot"
- Greeting: "Good morning/evening, Supervisor."
- Four Quick Action cards (Maintenance, Quality, Safety, Alarms)

---

## SEGMENT 2 — Question 1: Coolant Concentration (0:30–1:00)

**Narrate:**
> "Let me ask the first question from BiztelAI's sample set."

**Action:** Click the chat input and type:
```
What is the recommended coolant concentration for the TX-200?
```
Press Enter / click Send.

**Wait for response (~2 seconds), then narrate:**
> "The app returns the answer — 6 to 8 percent — with the exact source document and page number.
> This is from the TX-200 Preventive Maintenance manual, page 1.
> The supervisor can tap the source card to see the exact excerpt."

**Show:** Evidence badge ("Supported by documents") and source card.

---

## SEGMENT 3 — Question 2: Lockout Tagout (1:00–1:35)

**Narrate:**
> "Now a safety question — one where accuracy is critical."

**Action:** Type:
```
Who is allowed to remove a lockout lock, and what happens if that person is unavailable?
```
Press Enter.

**Wait for response, then narrate:**
> "Only the authorised person who applied the lock can remove it.
> If unavailable — escalation to Production Manager and Safety Officer is required,
> and the event must be recorded on form SF-12.
> Source: SAF-SOP-003, the Lockout Tagout procedure document."

**Show:** Source cards referencing SAF-SOP-003, pages 1 and 2.

---

## SEGMENT 4 — Unanswerable Question (1:35–2:00)

**Narrate:**
> "What if someone asks something the documents don't cover?"

**Action:** Type:
```
What is the salary structure and overtime policy for shift supervisors?
```
Press Enter.

**Wait for response, then narrate:**
> "PlantAssist AI correctly says it cannot answer this.
> HR and payroll information is not in the manufacturing documents,
> and the app refuses to guess — it tells the supervisor to consult the right person.
> The 'Not in documents' badge makes this clear at a glance."

**Show:** Amber/red "Insufficient evidence" badge.

---

## SEGMENT 5 — Mobile Demo (2:00–2:30)

**Switch to phone.**

**Narrate:**
> "The app is designed for the shop floor — mobile first.
> I'm now on my phone, on the same Wi-Fi, at the laptop's LAN IP."

**Show:** Phone browser URL bar with `http://192.168.0.213:5173`

**Action:** Tap the "Alarms" quick action card (or type):
```
What does alarm AL-104 mean and what should I do?
```

**Wait for response, then narrate:**
> "AL-104 is 'Way lube oil level low' — top up with ISO VG 68 oil and press RESET.
> Full answer, with source, on a 6-inch screen. Fast. Accurate. Traceable."

---

## CLOSING (2:30)

**Back on laptop:**

**Narrate:**
> "PlantAssist AI — built with FastAPI, ChromaDB, sentence-transformers, React and Tailwind.
> 53 automated tests passing. Ready for the next iteration."

**Stop recording.**

---

## TIPS

- Speak slowly and clearly
- Pause 2–3 seconds after each answer appears before narrating
- If answer is slow (model loading), say: "The first query warms up the embedding model — subsequent queries are faster."
- Keep phone visible in frame for segment 5 (selfie cam or screen share to laptop)
