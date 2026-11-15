# Learning Engagement & Ethical AI Governance Framework

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026 (Track: AI, CyberSecurity and Digital Trust)  
**Document Code:** GOV-ENG-05  
**Version:** 1.0  
**Status:** Mandatory Institutional Policy

---

## 1. Core Ethical Principles

MASTERY adheres strictly to human-centered educational technology principles, privacy-by-design, and digital trust.

### 1.1 Non-Invasive Interaction Telemetry
MASTERY captures only explicit, observable user-system interaction events:
- `ASSESSMENT_STARTED`: Candidate initiated exam session.
- `ANSWER_SAVED`: Candidate made an initial choice or entered text.
- `ANSWER_REVISED`: Candidate reconsidered and modified an existing answer.
- `ASSESSMENT_SUBMITTED`: Candidate confirmed and finalized the submission.
- `SESSION_IDLE_DETECTED`: Observable period with no client interaction.

### 1.2 Prohibited Surveillance Technologies
The MASTERY platform strictly **PROHIBITS and EXCLUDES**:
- Webcam-based facial expression analysis or gaze tracking.
- Audio or microphone monitoring.
- Keystroke dynamics profiling or biometric typing analysis.
- Third-party algorithmic emotion detection.
- Covert background surveillance software.

---

## 2. The Scientific Non-Attention Disclaimer

Any presentation of engagement telemetry—in faculty dashboards, analytics charts, exports, or reports—must be accompanied by the mandatory scientific disclaimer:

> **SCIENTIFIC DISCLAIMER:**  
> Learning engagement telemetry reflects observable human-computer interactions (events, timestamps, revisions). These behavioral traces must NEVER be equated with internal cognitive attention, mental concentration, or student intelligence.

### 2.1 Why Participation Does Not Equal Comprehension
- A student may reflect deeply for 10 minutes without touching the mouse or keyboard; this must never be categorized as "unattentive" or "disengaged".
- High revision counts may indicate careful analytical revision rather than confusion or indecisiveness.
- Rapid completion of items may reflect pre-existing mastery rather than superficial guessing.

---

## 3. Data Protection & Access Controls

1. **Candidate Anonymity & Protection:**
   Observable telemetry events are stored in `learning_engagement_events` with Row-Level Security (RLS) active. Students can only view their own engagement events.
2. **Faculty Usage Policy:**
   Faculty members use engagement telemetry exclusively for diagnostic reflection and assessment item difficulty calibration, never for punitive actions.
3. **Auditability & Digital Trust:**
   Every verified assessment result released to institutional records creates a permanent, immutable entry in `academic_record_audits`.
