# PlantAssist AI — 5-Minute Video Walkthrough Script (Simple English)

**Candidate:** Dhanush Manikanta  
**Role:** Junior Software Engineer – Full Stack / AI (BiztelAI)  
**Target Duration:** ~5 Minutes  
**PDF on Desktop:** `/Users/dhanushmanikanta/Desktop/PlantAssist_AI_Screen_Recording_Script.pdf`

---

## 1. Quick Copy-Paste Cheat Sheet for the 4 Questions

1. **Question 1 (Sample Question):**
   ```text
   What is the recommended coolant concentration for the TX-200 CNC machine?
   ```

2. **Question 2 (Safety SOP):**
   ```text
   Who is allowed to remove a lockout lock, and what happens if that person is unavailable?
   ```

3. **Question 3 (Unanswerable / Abstention):**
   ```text
   What is the salary structure and overtime policy for shift supervisors?
   ```

4. **Question 4 (Phone Demo):**
   ```text
   What does alarm AL-104 mean, and what action should be taken?
   ```

---

## 2. Minute-by-Minute Teleprompter (Simple English)

### ⏱️ Minute 0:00 – 0:45 | Part 1: Introduction & The Shop Floor Problem
- **🖥️ What to show:** PlantAssist AI home screen at `http://localhost:5173`. Move mouse smoothly across the banner.
- **🗣️ What to say:**
  > "Hello everyone. My name is Dhanush Manikanta. Today, I am happy to show you **PlantAssist AI** — a smart manufacturing assistant built for shop-floor supervisors.
  >
  > Let me first explain the real problem this solves. In a manufacturing plant, shift supervisors are responsible for workers, machines, and safety. But they also have hundreds of pages of technical PDFs — machine manuals, quality checklists, and safety SOPs.
  >
  > When a machine suddenly stops or an alarm beeps, the supervisor does not have time to walk to a computer or flip through a 100-page oily paper manual. They need a quick, simple, and accurate answer right there on the floor. That is why I built PlantAssist AI."

---

### ⏱️ Minute 0:45 – 1:30 | Part 2: UI Tour Built for Shop Floor Realities
- **🖥️ What to show:** Hover over the 4 Quick Action cards (Maintenance, Quality, Safety, Alarms).
- **🗣️ What to say:**
  > "Before we ask our first question, take a quick look at the screen. The interface is designed specially for a factory floor.
  >
  > Factory floors have bright overhead lights and supervisors are often on the move. So we used high-contrast colors, clear fonts, and big buttons. Right here on the home screen, we have four Quick Action cards for common daily needs: Machine Maintenance, Quality Inspection, Safety Procedures, and Machine Alarms.
  >
  > A supervisor can simply click any card, or type a question in everyday plain English."

---

### ⏱️ Minute 1:30 – 2:15 | Part 3: Question 1 — Coolant Concentration
- **🖥️ What to show:** Paste Question 1, press Enter. Wait 1 second. Point to answer, green badge, and source card.
- **🗣️ What to say:**
  > "Now, let us try our first question from the assignment: *'What is the recommended coolant concentration for the TX-200 CNC machine?'*
  >
  > I will click send... and in about one second, we get our answer. The app tells us: the recommended concentration is **6 to 8 percent**, checked with a refractometer.
  >
  > Why is this important? If coolant is too weak, cutting tools overheat and break. If it is too strong, it wastes expensive coolant oil and leaves sticky marks on metal parts. And look below the answer: there is a green badge that says **'Supported by documents'**, and a card showing the exact source: **MNT-MAN-CNC-02, the Preventive Maintenance manual, Page 1**. The supervisor can click it and verify the page immediately. There is zero guesswork."

---

### ⏱️ Minute 2:15 – 3:00 | Part 4: Question 2 — Safety LOTO Procedure
- **🖥️ What to show:** Paste Question 2, press Enter. Point to the safety steps and source cards.
- **🗣️ What to say:**
  > "Next, let us ask a question about safety. In a factory, safety is the number one priority. A wrong answer here could cause a serious accident.
  >
  > Let us ask: *'Who is allowed to remove a lockout lock, and what happens if that person is unavailable?'*
  >
  > Look at how clearly PlantAssist AI answers this. First, it states the strict rule: only the person who attached the lock is allowed to remove it. But what if that person has already left the factory?
  >
  > The app gives the exact step-by-step company rule: the supervisor must first try to call them on the phone. If they cannot be reached, the **Production Manager** and the **Safety Officer** must both give written permission. Then, the machine must be physically checked before turning the power back on, and the incident must be recorded on Form SF-12.
  >
  > All of this comes directly from **SAF-SOP-003, Pages 1 and 2**."

---

### ⏱️ Minute 3:00 – 3:45 | Part 5: Unanswerable Question (Refusing to Guess)
- **🖥️ What to show:** Paste Question 3, press Enter. Point to the amber "Insufficient Evidence" badge and refusal message.
- **🗣️ What to say:**
  > "Now, let us test something very important: what happens if someone asks a question that is NOT in the plant documents?
  >
  > For example: *'What is the salary structure and overtime policy for shift supervisors?'*
  >
  > Many generic AI chatbots try to make up a convincing answer. But on a factory floor, making things up is dangerous. Notice what PlantAssist AI does: it shows an amber badge saying **'Insufficient evidence'**.
  >
  > And it clearly says: *'I could not find sufficient information in the available manufacturing documents to answer this question reliably. Please consult your supervisor or HR.'*
  >
  > We built a two-stage filter inside the search engine. It checks whether the words and meaning actually match our technical documents. Because salary rules are not in our machine SOPs, the app honestly abstains. That is how you build real trust with plant supervisors."

---

### ⏱️ Minute 3:45 – 4:30 | Part 6: Mobile Demo on Local Wi-Fi
- **🖥️ What to show:** Show mobile phone at `http://192.168.0.213:5173`. Tap "Alarms" or ask AL-104 question.
- **🗣️ What to say:**
  > "Now, let us look at how a supervisor will actually use this during their shift. A supervisor walks 10,000 steps a day across the plant. They do not carry a laptop around.
  >
  > Here, I have opened PlantAssist AI on my mobile phone, connected to the exact same local Wi-Fi at IP address **192.168.0.213**.
  >
  > The application automatically fits the phone screen. The buttons are big and easy to tap with one thumb. Let us tap the 'Alarms' button or ask: *'What does alarm AL-104 mean, and what action should be taken?'*
  >
  > Instantly, right on my phone, it answers: Alarm AL-104 means 'Way lube oil level is low'. The required action is to top up with ISO VG 68 oil to the MAX mark, and press RESET. It also shows the source: Page 2 of the maintenance manual.
  >
  > Fast, clear, and right in the palm of their hand."

---

### ⏱️ Minute 4:30 – 5:00 | Part 7: Code Architecture, Tests & Conclusion
- **🖥️ What to show:** Switch back to laptop. Show terminal with 53 passing tests, or show the GitHub repo.
- **🗣️ What to say:**
  > "To wrap up, let us take a quick look under the hood.
  >
  > The backend is built with **Python and FastAPI**. It extracts text from PDFs using PyMuPDF, creates local embeddings with Sentence Transformers, and stores them in ChromaDB. The frontend is built with **React, Vite, and Tailwind CSS**. Everything can run completely locally on a plant laptop without expensive cloud servers.
  >
  > We also wrote a full test suite with **53 automated unit and integration tests**, covering PDF parsing, vector search, and all API endpoints. Every single test is passing.
  >
  > The entire code is open and public on GitHub at **github.com/KDM14/plantassist-ai**, along with my complete THINKING document.
  >
  > Thank you very much to Pugazh and the BiztelAI team for this assignment. I look forward to speaking with you!"

---

## 3. Ready-to-Send Email Template for BiztelAI

```text
Subject: BiztelAI Assignment Submission — PlantAssist AI (Dhanush Manikanta)

Hi Pugazh,

Thank you for the opportunity. Please find my complete assignment submission below:

A. Public GitHub Repository:
https://github.com/KDM14/plantassist-ai

Contains:
• Complete FastAPI backend, ChromaDB vector store, and React/Vite/Tailwind frontend.
• README.md: Full installation guide, architecture diagram, and answers to the 5 sample questions + 5 original questions (including edge-case and abstention tests).
• THINKING.md: Detailed user persona analysis, user journey, AI challenge dialogue and reflections, rationale for the chosen improvement, and engineering takeaways.
• 53 automated unit and integration tests: 100% passing.

B. Screen Recording Walkthrough:
[PASTE YOUR LOOM OR GOOGLE DRIVE LINK HERE]

Shows:
1. Answering 2 sample questions with exact source document and page citations.
2. Explicit abstention on out-of-scope question (preventing hallucination).
3. Live mobile demonstration running on a smartphone over the local Wi-Fi network.

Looking forward to discussing the implementation in the next round!

Best regards,
Dhanush Manikanta
```
