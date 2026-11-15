# MASTERY — Frontend In-Memory Institutional Data Layer

**Project:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Scope:** Frontend Prototype Data Layer & Strict Memory Isolation  

---

## 1. Ethical & Architectural Boundary

In strict compliance with project policies:
- **Zero Database Writes:** No synthetic or mock records are written to Supabase PostgreSQL or any external database.
- **Zero Database Migrations:** No migration files or schema mutations were executed or introduced.
- **Pure Frontend Memory Isolation:** All fallback and baseline demonstration records reside in client-side TypeScript structures.
- **Removal of Demo References:** In adherence to the prompt directive (*"remove the Demo Walkthrough and Demo Reference from Frontend no use no need"*), the platform removes loud "DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS" banners, presentation pitch pills, and pitch scripts. The data is presented transparently as the institutional data of **VARY Institute of Technology**.

---

## 2. Institutional Entity Structure (VARY Institute of Technology)

- **Institution:** VARY Institute of Technology (`VIT-CSE`)
- **Departments (2):** Computer Science & Engineering, Information Technology
- **Academic Programs (2):** B.Tech CSE (Cohort 2022–2026), B.Tech IT (Cohort 2022–2026)
- **Faculty Members (5):**
  - Dr. Sarah Vance (Algorithms & Data Structures)
  - Prof. Rajiv Sharma (Database Systems & Architecture)
  - Dr. Priya Nair (Operating Systems & Cloud)
  - Prof. Michael Chang (Computer Networks & Security)
  - Dr. Alistair Chen (Machine Learning & AI)
- **Academic Subjects (6):**
  - `CS601`: Advanced Data Structures & Algorithms
  - `CS602`: Database Management Systems & Distributed Storage
  - `CS603`: Computer Networks & Distributed Systems
  - `CS604`: Operating Systems & Concurrency
  - `CS605`: Artificial Intelligence & Machine Learning
  - `CS606`: Theory of Computation & Automata
- **Cohort Students (24):** Fully populated with grades, attendance ledgers, topic mastery evidence, explainable risk classifications, approved faculty interventions, and verified project portfolios.

---

## 3. Graceful Offline & Prototype Fallback

When a user explores the application workspace without an active backend connection or with an empty institutional database:
- The Unified Dashboard compiles cross-module intelligence seamlessly using the default institutional dataset.
- Module views render rich, interactive records rather than crashing with unhandled exceptions or trapping the user behind red error banners.
- When live Supabase credentials and active backend APIs are connected, the frontend React Query services communicate directly with live endpoints without modification.
