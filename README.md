#  FUNCTIONAL SYSTEM SPECIFICATION: LEARNLOOP (Homework & Practice LMS)
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

#### Screen 4: Teacher Global Dashboard & Subject Manager
*   **Function:** High-level ecosystem overview and Subject management.
*   **Data Aggregation Widgets:** `Total Active Courses`, `Pending Submissions`, `Recent Activity Feed`.
*   **Interactive Elements:**
    *   `Button: Create New Course`: Opens modal (Input: Course Name, Subject Tag, Semester). Auto-generates a 6-char `invite_code`.
    *   `List: My Courses`: Clickable cards navigating to Screen 5.

#### Screen 5: Course Roster & Settings Manager
*   **Function:** Deep dive into a specific course's configuration.
*   **Interactive Elements:**
    *   `Button: Regenerate Invite Code`: Invalidates old code for security.
    *   `Data Table: Enrolled Students`: Lists ID, Name, Email.
    *   `Button: Remove Student`: Hard deletes from `Enrollments` (preserves historical grades).

#### Screen 6: Assignment Bank
*   **Function:** Central repository of homework and practice sets.
*   **Data Display:** Paginated list. Columns: `Title`, `Target Course`, `Deadline`, `Status`.
*   **Interactive Elements:**
    *   `Search Bar`: Triggers `GET /api/assignments?search=query`.
    *   `Button: Create from Scratch`: Opens Screen 8 in Manual Mode (No AI).
    *   `Button: Generate with AI Studio`: Redirects to Screen 7.

#### Screen 7: Teacher AI Studio (Data Ingestion)
*   **Function:** Captures source material for AI homework generation.
*   **Input Fields & Validation Rules:**
    *   `File Uploader`: Accepts `.txt, .pdf, .docx` (Max 10MB).
    *   `Slider: Question Count`: Integer from 5 to 50.
    *   `Dropdown: Difficulty Level`: Select (Basic Recall, Comprehension, Application).
*   **Action Behaviors:** `Button: Analyze & Generate` -> UI enters un-dismissable Loading State.

#### Screen 8: Assignment Editor (QA & Manual Edit)
*   **Function:** Human-in-the-loop editing. Supports both AI-generated arrays and manual creation from scratch.
*   **Interactive Elements (Per Question Block):**
    *   `Input: Question Stem`, `Inputs: Options A/B/C/D`, `Dropdown: Correct Answer`.
    *   `Textarea: AI/Teacher Explanation`: Editable rationale for the answer.
    *   `Button: Add Blank Question`: Appends an empty block for manual input.
    *   `Button: Delete Question`.
*   **Publishing Actions:**
    *   `Input: Deadline Picker`: Sets a strict due date (Timestamp).
    *   `Button: Publish to Course`: Updates DB status, makes assignment visible to students.

#### Screen 9: Deep Analytics & Item Analysis
*   **Function:** Evaluates student understanding and material suitability.
*   **Data Rendered:**
    *   `Metric: Class Average Score` & `Metric: Submission Rate`.
    *   `Widget: Item Analysis (Difficult Questions)`: Flags questions where >50% of the class answered incorrectly. Highlights which wrong option was most chosen to identify common misconceptions.
    *   `Student Table`: Lists absolute scores, time taken, and submission timestamp.
    *   `Action: Export to CSV` for gradebooks.

---

### MODULE C: STUDENT WORKSPACE (Practice & Self-Study)

#### Screen 10: Student Global Dashboard & Calendar
*   **Function:** Hub for active assignments and time management.
*   **Data Aggregation:**
    *   `Input: Invite Code` + `Button: Join Course`.
    *   `Widget: Upcoming Deadlines`: Chronological list of pending assignments mapping to `Assignments.deadline`. Visually flags "Due in 24h" in red.
    *   `Widget: Course Overview`: List of enrolled courses.

#### Screen 11: Specific Course View
*   **Function:** Workload scoped to a single course.
*   **Data Display:**
    *   List of Assignments. Status indicators: "To Do" vs "Completed".
    *   `Button: Start Practice`: Proceeds to Screen 12.

#### Screen 12: Practice Environment (Homework Execution)
*   **Function:** Low-stakes execution of homework.
*   **Initialization Logic:** Randomizes option order client-side.
*   **Interactive Elements & Rules:**
    *   `Radio Group: Options`: One selection per question.
    *   `State Management`: Answers auto-saved to browser `localStorage` on click to prevent data loss.
    *   `Button: Submit Homework`: Triggers validation check for unanswered questions. Dispatches `POST /api/sessions/submit`.

#### Screen 13: Review & AI Tutoring View
*   **Function:** Real-time grading and conceptual correction.
*   **UI Data Binding (Read-Only):**
    *   `Score Header`: Displays final score.
    *   `Question Review Loop`: Highlights user's choice vs. correct answer.
    *   `AI Tutoring Block`: Binds the `explanation` string directly below the question, clarifying *why* the answer is correct for immediate learning.

---

### MODULE D: STUDENT SELF-STUDY STUDIO (Personal Practice)

#### Screen 14: Self-Study Ingestion
*   **Function:** Allows students to upload their own notes to generate quick practice tests for exam revision.
*   **Input Fields:**
    *   `File Uploader`: Drag & drop personal study materials.
    *   `Slider: Question Count`.
*   **Action Behaviors:** `Button: Generate Quick Practice`. Dispatches payload to AI Engine.

#### Screen 15: Instant Practice Mode
*   **Function:** Bypasses the Teacher's "Edit" phase. The AI output is instantly rendered as an interactive quiz for the student.
*   **Business Logic:** 
    *   Upon generation, immediately loads a view identical to Screen 12. 
    *   Upon submission, routes to Screen 13 for AI explanations.
    *   Data is saved to a separate `Personal_Study_History` table, NOT visible to the teacher, ensuring privacy in self-study.
