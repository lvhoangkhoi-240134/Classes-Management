# 🚀 FUNCTIONAL SYSTEM SPECIFICATION: LEARNLOOP (Homework & Practice LMS)
**Target Audience:** Full-Stack Engineers, System Architects, Product Managers.
**Focus:** Core features, business logic, data flow, validation rules, and system behavior. UI/UX styling is explicitly excluded.

---

## 1. SYSTEM ARCHITECTURE & CORE WORKFLOWS

### 1.1. AI Processing Pipeline (Dual-Use Engine)
1. **Ingestion:** System receives raw files (PDF/DOCX/TXT) via `multipart/form-data`.
2. **Extraction:** Backend parses the document using native Python libraries (`PyPDF2`, `python-docx`) to extract UTF-8 text.
3. **Prompt Injection:** Text is wrapped in a strict system prompt enforcing a predefined JSON schema.
4. **Validation:** Backend intercepts AI response. Attempts `json.loads()`. Triggers auto-retry on malformed JSON.
5. **Persistence (Teacher Flow):** JSON mapped to `Assignments` table for manual review and editing.
6. **Ephemeral Execution (Student Flow):** JSON mapped directly to a temporary `SelfStudy_Sessions` table for immediate practice bypassing the edit phase.

### 1.2. Authentication & Authorization Lifecycle
*   **Method:** Stateless JWT stored in HTTP-only cookies or secure LocalStorage.
*   **Restriction:** Closed institutional system. No Third-Party SSO permitted.
*   **Role-Based Access Control (RBAC):** Strictly enforced via backend middleware. `get_current_user` validates roles (Teacher vs. Student).

---

## 2. DETAILED FUNCTIONAL SCREEN SPECIFICATIONS

### MODULE A: INSTITUTIONAL ONBOARDING & AUTHENTICATION

#### Screen 1: System Landing Page & Entry Routing
*   **Function:** Initial entry point. Routes users based on session state.
*   **Business Logic:** Decodes valid JWT -> redirects to respective dashboard. If none, displays CTA.

#### Screen 2: Institutional Registration System
*   **Input Fields & Validation Rules:**
    *   `Role Selector`: Radio group (Teacher/Student).
    *   `Institution Code`: Matches DB of valid school codes.
    *   `Institutional Email`, `Student/Staff ID`, `Password`.
*   **Action Behaviors:** Dispatches `POST /api/auth/register`.

#### Screen 3: Login & Password Recovery
*   **Function:** Secure login & SMTP-based password reset for institutional emails.

---

### MODULE B: TEACHER WORKSPACE (Course & Homework Management)
*   **Global Layout Rule:** Left Sidebar Navigation required for all screens in this module.

#### Screen 4: Teacher Global Dashboard (The Entry Point)
*   **Function:** High-level ecosystem overview and schedule management.
*   **Data Aggregation Widgets:**
    *   `Widget: Color-Coded Teaching Calendar`: A weekly/monthly calendar view visualizing the teacher's schedule (e.g., upcoming classes, lectures).
    *   `Widget: Global Metrics`: Total Active Courses, System-wide Pending Submissions.
    *   `Widget: AI Insights`: High-level alerts (e.g., "Students are struggling with Module 4").

#### Screen 5: Course Hub (Subject Entry Screen)
*   **Function:** Central directory for all subjects taught by the teacher. Accessed via "Courses" in the sidebar.
*   **Data Display:** 
    *   Grid/List of `Course Cards`.
    *   `Button: Create New Course`: Opens modal to generate a new course and `invite_code`.
*   **Action Behaviors:** Clicking a Course Card routes to Screen 6.

#### Screen 6: Course Detail & Roster (Deep Dive)
*   **Function:** Deep dive into a specific course's configuration.
*   **Interactive Elements:**
    *   `Badge`: Course Invite Code (with Regenerate button).
    *   `Data Table: Enrolled Students`: Lists ID, Name, Email. Includes "Remove Student" action.

#### Screen 7: Assignment Bank (Filtered Entry Screen)
*   **Function:** Central repository of homework. Accessed via sidebar.
*   **Data Display:** Mandatory `Course Filter` dropdown or folder-based structure. Users must select a course before viewing the paginated list of assignments (`Title`, `Deadline`, `Status`).
*   **Interactive Elements:**
    *   `Button: Create from Scratch` (Routes to Screen 9).
    *   `Button: Generate with AI Studio` (Routes to Screen 8).

#### Screen 8: Teacher AI Studio (Data Ingestion)
*   **Function:** Captures source material for AI homework generation.
*   **Input Fields:** `File Uploader`, `Question Count Slider`, `Difficulty Level Dropdown`.

#### Screen 9: Assignment Editor (QA & Manual Edit)
*   **Function:** Human-in-the-loop editing.
*   **Interactive Elements:** Question Stem, Options A/B/C/D, Correct Answer dropdown, AI Explanation textarea.
*   **Publishing Actions:** `Deadline Picker`, `Button: Publish to Course`.

#### Screen 10: Deep Analytics & Item Analysis
*   **Function:** Evaluates student understanding and material suitability.
*   **Data Rendered:** `Class Average Score`, `Item Analysis` (flags high-failure questions), `Export to CSV`.

---

### MODULE C: STUDENT WORKSPACE (Practice & Self-Study)
*   **Global Layout Rule:** Strict Left Sidebar Navigation (Mirroring Teacher Workspace for UI consistency).

#### Screen 11: Student Global Dashboard (The Entry Point)
*   **Function:** Hub for time management and overview.
*   **Data Aggregation Widgets:**
    *   `Widget: Master Calendar`: Color-coded calendar showing class schedules and assignment deadlines.
    *   `Widget: Upcoming Deadlines`: List of tasks due within 24-48 hours.
    *   `Widget: AI Study Recommendations`: Data-driven insights based on recent performance.

#### Screen 12: Course Hub (Student Entry Screen)
*   **Function:** Directory of enrolled subjects. Accessed via "Courses" in the sidebar.
*   **Interactive Elements:**
    *   `Input: Invite Code` + `Button: Join Course`.
    *   Grid/List of Enrolled `Course Cards` (Displays progress bars).
*   **Action Behaviors:** Clicking a Course Card routes to Screen 13.

#### Screen 13: Course Detail (Assignments View)
*   **Function:** Workload scoped to a single course.
*   **Data Display:** List of Assignments categorized by "To Do" vs "Completed".
*   **Action Behaviors:** `Button: Start Practice` routes to Screen 14.

#### Screen 14: Practice Environment (Homework Execution)
*   **Function:** Low-stakes execution of homework.
*   **Rules:** Auto-saves to `localStorage` on click. Triggers validation check on submit.

#### Screen 15: Review & AI Tutoring View
*   **Function:** Real-time grading and conceptual correction.
*   **Data Display:** Highlights Correct/Wrong answers. Binds the `AI Tutoring Explanation` below each question.

---

### MODULE D: STUDENT SELF-STUDY STUDIO (Personal Practice)
*   **Global Layout Rule:** Accessed via dedicated sidebar tab.

#### Screen 16: Self-Study Ingestion
*   **Function:** Allows students to upload personal notes for exam revision.
*   **Input Fields:** `File Uploader`, `Question Count Slider`.

#### Screen 17: Instant Practice Mode
*   **Function:** Bypasses Teacher editing. AI output is instantly rendered as a practice test. Saves to isolated `Personal_Study_History` table.
