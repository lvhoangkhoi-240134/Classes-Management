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
*   **Interactive Elements:** `Button: Teacher Portal`, `Button: Student Portal`.

#### Screen 2: Institutional Registration System
*   **Input Fields & Validation Rules:**
    *   `Role Selector`: Radio group (Teacher/Student).
    *   `Institution Code`: Matches DB of valid school codes (e.g., "RMIT_VN").
    *   `Full Name`, `Institutional Email` (Regex enforced `.edu`), `Student/Staff ID`.
    *   `Password` (Min 8 chars, 1 uppercase, 1 number), `Confirm Password`.
*   **Action Behaviors:** `Button: Create Account` -> Dispatches `POST /api/auth/register`.

#### Screen 3: Login & Password Recovery
*   **Function:** Secure login & SMTP-based password reset for institutional emails.
*   **Security:** Rate-limiting applied to prevent brute-force attacks.

---

### MODULE B: TEACHER WORKSPACE (Course & Homework Management)
*   **Global Layout Rule:** Left Sidebar Navigation (`Dashboard`, `Courses`, `Assignment Bank`, `AI Studio`, `Analytics`) is persistent across this module.

#### Screen 4: Teacher Global Dashboard (The Entry Point)
*   **Function:** High-level ecosystem overview and schedule management.
*   **Data Aggregation Widgets:**
    *   `Widget: Color-Coded Teaching Calendar`: A weekly/monthly calendar view visualizing the teacher's schedule.
    *   `Widget: Global Metrics`: Total Active Courses, System-wide Pending Submissions.
    *   `Widget: AI Insights`: High-level alerts (e.g., "Students in CS101 are struggling with Module 4").

#### Screen 5: Course Hub (Subject Entry Screen)
*   **Function:** Central directory for all subjects taught by the teacher.
*   **Data Display:** 
    *   Grid/List of `Course Cards`.
    *   `Button: Create New Course`: Opens modal to generate a new course and `invite_code`.
*   **Action Behaviors:** Clicking a Course Card routes to Screen 6.

#### Screen 6: Course Detail & Roster (Deep Dive)
*   **Function:** Deep dive into a specific course's configuration.
*   **Interactive Elements:**
    *   `Badge`: Course Invite Code (with Regenerate button).
    *   `Data Table: Enrolled Students`: Lists ID, Name, Email. Includes "Remove Student" action (preserves historical grades).

#### Screen 7: Assignment Bank (Filtered Entry Screen)
*   **Function:** Central repository of homework.
*   **Data Display:** Mandatory `Course Filter` dropdown. Users must select a course before viewing the paginated list of assignments (`Title`, `Deadline`, `Status`).
*   **Interactive Elements:**
    *   `Button: Create from Scratch` (Routes to Screen 9).
    *   `Button: Generate with AI Studio` (Routes to Screen 8).

#### Screen 8: Teacher AI Studio (Data Ingestion Entry)
*   **Function:** Captures source material for AI homework generation.
*   **Input Fields & Validation Rules:**
    *   `File Uploader`: Accepts `.txt, .pdf, .docx` (Max 10MB).
    *   `Slider: Question Count`: Integer from 5 to 50.
    *   `Dropdown: Difficulty Level`: Select (Basic Recall, Comprehension, Application).
*   **Action Behaviors:** `Button: Analyze & Generate` -> UI enters un-dismissable Loading State.

#### Screen 9: Assignment Editor (QA & Manual Edit)
*   **Function:** Human-in-the-loop editing. Supports both AI-generated arrays and manual creation from scratch.
*   **Interactive Elements (Per Question Block):**
    *   `Input: Question Stem`, `Inputs: Options A/B/C/D`, `Dropdown: Correct Answer`.
    *   `Textarea: AI/Teacher Explanation`: Editable rationale for the answer.
    *   `Button: Add Blank Question`: Appends an empty block for manual input.
    *   `Button: Delete Question`.
*   **Publishing Actions:**
    *   `Input: Deadline Picker`: Sets a strict due date (Timestamp).
    *   `Button: Publish to Course`: Updates DB status, makes assignment visible to students.

#### Screen 10: Analytics Hub (Reporting Entry Screen)
*   **Function:** The gateway to all reporting and statistics.
*   **Data Aggregation Widgets:** `Global Class Averages`, `Top Performing Courses`.
*   **Interactive Elements:**
    *   `Dropdown 1: Select Course` (Mandatory).
    *   `Dropdown 2: Select Assignment` (Cascades from Dropdown 1).
*   **Action Behaviors:** `Button: Generate Report` routes to Screen 11.

#### Screen 11: Deep Analytics & Item Analysis (Detail Screen)
*   **Function:** Evaluates student understanding and material suitability for a specific assignment.
*   **Data Rendered:**
    *   `Metric: Assignment Average Score` & `Submission Rate`.
    *   `Widget: Item Analysis`: Flags questions where >50% of the class answered incorrectly. Highlights which wrong option was most chosen to identify common misconceptions.
    *   `Data Table: Student Grades`: Lists absolute scores, time taken, and submission timestamp.
    *   `Action: Export to CSV` for gradebooks.

---

### MODULE C: STUDENT WORKSPACE (Practice & Coursework)
*   **Global Layout Rule:** Left Sidebar Navigation (`Dashboard`, `Courses`, `Self-Study`) mirroring the Teacher workspace for consistency.

#### Screen 12: Student Global Dashboard (The Entry Point)
*   **Function:** Hub for time management and overview.
*   **Data Aggregation Widgets:**
    *   `Widget: Master Calendar`: Color-coded calendar showing class schedules and assignment deadlines.
    *   `Widget: Upcoming Deadlines`: Chronological list of tasks. Visually flags "Due in 24h" in red.
    *   `Widget: AI Study Recommendations`: Data-driven insights based on recent performance.

#### Screen 13: Course Hub (Student Entry Screen)
*   **Function:** Directory of enrolled subjects.
*   **Interactive Elements:**
    *   `Input: Invite Code` + `Button: Join Course`.
    *   Grid/List of Enrolled `Course Cards` (Displays progress bars).
*   **Action Behaviors:** Clicking a Course Card routes to Screen 14.

#### Screen 14: Course Detail (Assignments View)
*   **Function:** Workload scoped to a single course.
*   **Data Display:** List of Assignments categorized by "To Do" vs "Completed".
*   **Action Behaviors:** `Button: Start Practice` routes to Screen 15.

#### Screen 15: Practice Environment (Homework Execution)
*   **Function:** Low-stakes execution of homework.
*   **Initialization Logic:** Randomizes option order client-side.
*   **Interactive Elements & Rules:**
    *   `Radio Group: Options`: One selection per question.
    *   `State Management`: Answers auto-saved to browser `localStorage` on click to prevent data loss.
    *   `Button: Submit Homework`: Triggers validation check for unanswered questions. Dispatches `POST /api/sessions/submit`.

#### Screen 16: Review & AI Tutoring View
*   **Function:** Real-time grading and conceptual correction.
*   **UI Data Binding (Read-Only):**
    *   `Score Header`: Displays final score.
    *   `Question Review Loop`: Highlights user's choice vs. correct answer.
    *   `AI Tutoring Block`: Binds the `explanation` string directly below the question, clarifying *why* the answer is correct for immediate learning.

---

### MODULE D: STUDENT SELF-STUDY STUDIO (Personal Practice)

#### Screen 17: Self-Study Ingestion (Entry Screen)
*   **Function:** Allows students to upload their own notes to generate quick practice tests for exam revision without teacher intervention.
*   **Input Fields:**
    *   `File Uploader`: Drag & drop personal study materials.
    *   `Slider: Question Count`.
*   **Action Behaviors:** `Button: Generate Quick Practice`. Dispatches payload to AI Engine.

#### Screen 18: Instant Practice Mode
*   **Function:** Bypasses the Teacher's "Edit" phase. The AI output is instantly rendered as an interactive quiz for the student.
*   **Business Logic:** 
    *   Upon generation, immediately loads a view functionally identical to Screen 15. 
    *   Upon submission, routes to Screen 16 for AI explanations.
    *   Data is saved to a separate `Personal_Study_History` table, NOT visible to the teacher, ensuring privacy in self-study.
