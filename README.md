# 🚀 FUNCTIONAL SYSTEM SPECIFICATION: LEARNLOOP (LMS & AI Engine)
**Document Version:** 2.0
**Target Audience:** Full-Stack Engineers, System Architects, Product Managers.
**Focus:** Core features, business logic, data flow, validation rules, and system behavior. UI/UX styling is explicitly excluded.

---

## 1. SYSTEM ARCHITECTURE & CORE WORKFLOWS

### 1.1. AI Processing Pipeline (The Core Engine)
1. **Ingestion:** System receives raw files (PDF/DOCX/TXT) or raw text via `multipart/form-data`.
2. **Extraction:** Backend parses the document using native Python libraries (`PyPDF2`, `python-docx`) to extract UTF-8 text.
3. **Chunking & Tokenization:** If text exceeds Gemini's context window, it is chunked. 
4. **Prompt Injection:** Text is wrapped in a strict system prompt enforcing a predefined JSON schema.
5. **Validation:** The AI response is intercepted. The backend attempts to `json.loads()`. If it fails (malformed JSON), a regex cleanup is triggered, or an automatic retry is initiated.
6. **Persistence:** Validated JSON is mapped to the `Quizzes` table.

### 1.2. Authentication & Authorization Lifecycle
*   **Method:** Stateless JWT (JSON Web Tokens) stored in HTTP-only cookies or secure LocalStorage.
*   **Role-Based Access Control (RBAC):** Every API endpoint requires a dependency check (`get_current_user`). Actions are blocked with `403 Forbidden` if a Student attempts to hit a Teacher endpoint.

---

## 2. DETAILED FUNCTIONAL SCREEN SPECIFICATIONS

### MODULE A: ONBOARDING & AUTHENTICATION

#### Screen 1: System Landing Page & Entry Routing
*   **Function:** Initial entry point routing users based on intent and session state.
*   **Business Logic:**
    *   System checks for existing valid JWT token on load.
    *   If valid token exists: Decode payload -> redirect to `/teacher/dashboard` or `/student/dashboard` based on `role`.
    *   If no token: Display Call-to-Actions (CTA).
*   **Interactive Elements:**
    *   `Button: Teacher Entry`: Redirects to Registration (Role pre-set to Teacher).
    *   `Button: Student Entry`: Redirects to Registration (Role pre-set to Student).
    *   `Link: Login`: Redirects to unified Login screen.

#### Screen 2: Unified Registration System
*   **Function:** Account creation and initial database seeding.
*   **Input Fields & Validation Rules:**
    *   `Role Selector`: Radio group (Teacher/Student). Mandatory.
    *   `Full Name`: String. Min 2, Max 50 characters. Strips leading/trailing spaces.
    *   `Email`: Must match standard email regex. Must uniquely exist in `Users` table (triggers `409 Conflict` if duplicate).
    *   `Password`: Minimum 8 characters, at least 1 uppercase, 1 number.
    *   `Confirm Password`: Must strictly match `Password`.
*   **Action Behaviors:**
    *   `Button: Create Account`: Dispatches `POST /api/auth/register`. Payload includes bcrypt-hashed password.
    *   **Success State:** Auto-generates JWT, logs user in, redirects to respective Dashboard.

#### Screen 3: Login & Session Management
*   **Function:** Authenticates existing users and issues session tokens.
*   **Input Fields & Validation Rules:**
    *   `Email`: Required.
    *   `Password`: Required.
*   **Action Behaviors:**
    *   `Button: Login`: Dispatches `POST /api/auth/login`. 
    *   **Error State 1:** If email not found -> "Account does not exist."
    *   **Error State 2:** If password incorrect -> "Invalid credentials."
    *   **Security Measure:** Rate limiting applied (max 5 failed attempts per 15 mins to prevent brute force).

#### Screen 4: Password Recovery & OTP Verification
*   **Function:** Secure account recovery workflow.
*   **Phase 1 (Request):** User inputs Email. Backend verifies existence. If true, generates a 6-digit OTP, stores in DB with a 10-minute expiration timestamp, and triggers Email Service.
*   **Phase 2 (Verify):** User inputs 6-digit OTP. 
    *   *Logic:* DB checks if OTP matches AND `current_time < expiration_time`.
*   **Phase 3 (Reset):** User inputs new password. DB overwrites `password_hash`.

---

### MODULE B: TEACHER WORKSPACE

#### Screen 5: Teacher Global Dashboard
*   **Function:** High-level overview of the teacher's ecosystem.
*   **Data Aggregation Widgets:**
    *   `Total Active Classes`: `COUNT(id)` from `Classes` where `teacher_id = current_user.id`.
    *   `Total Students`: Count of unique `student_id` in `Enrollments` across all teacher's classes.
    *   `Recent Activity Feed`: Fetches top 5 recent `Sessions` (student quiz submissions).
*   **Action Behaviors:**
    *   `Button: Create Quick Class`: Opens modal to input Class Name. Auto-generates a unique 6-character alphanumeric `invite_code`. Inserts into `Classes` table.

#### Screen 6: Class Roster & Settings Manager
*   **Function:** Deep dive into a specific class's configuration.
*   **Interactive Elements:**
    *   `Input: Class Name`: Editable field. Updates `Classes` table on blur.
    *   `Button: Regenerate Invite Code`: Invalidates old code, generates a new 6-character string, updates DB. Useful if the old code leaked.
    *   `Data Table: Enrolled Students`: Lists `full_name`, `email`, `join_date`.
    *   `Button: Remove Student`: Hard deletes the record from `Enrollments`. (Cascading rule: Does NOT delete the student's past quiz `Sessions`).

#### Screen 7: Quiz Bank / Assessment Hub
*   **Function:** Central repository of all quizzes created by the teacher.
*   **Data Display:** Paginated list of quizzes. Columns: `Title`, `Target Class`, `Question Count`, `Creation Date`, `Status` (Draft/Published).
*   **Interactive Elements:**
    *   `Search Bar`: Triggers `GET /api/quizzes?search=query` to filter by title.
    *   `Button: Delete Quiz`: Triggers soft-delete (updates `is_deleted = True`) to preserve historical student data.
    *   `Button: Launch AI Studio`: Redirects to the AI generation pipeline (Screen 8).

#### Screen 8: AI Studio (Step 1) - Data Ingestion
*   **Function:** Captures source material for the AI.
*   **Input Fields & Validation Rules:**
    *   `File Uploader`: Accepts `.txt, .pdf, .docx`. Max file size: 10MB. File is parsed in-memory, NOT saved to physical storage to save server costs.
    *   `Text Area (Alternative)`: Manual text paste. Max 50,000 characters.
    *   `Slider: Question Count`: Integer from 5 to 50.
*   **Action Behaviors:**
    *   `Button: Analyze & Generate`: Dispatches raw text and question count to `POST /api/ai/generate`. UI enters an un-dismissable Loading State preventing duplicate submissions.

#### Screen 9: AI Studio (Step 2) - QA & Editing
*   **Function:** Human-in-the-loop validation of AI output.
*   **Data Binding:** Renders the JSON array returned by Gemini into a list of editable blocks.
*   **Interactive Elements (Per Question Block):**
    *   `Input: Question Stem`: Editable string.
    *   `Inputs: Options A/B/C/D`: Editable strings.
    *   `Dropdown: Correct Answer`: Forces teacher to select which option is the key.
    *   `Textarea: AI Explanation`: Editable string. Allows teacher to refine the AI's reasoning.
    *   `Button: Delete Question`: Removes block from the array.
    *   `Button: Add Question`: Appends an empty block to the array for manual addition.
*   **Action Behaviors:**
    *   `Button: Save as Draft`: Serializes the current DOM state to JSON, saves to `Quizzes` with `status='draft'`.
    *   `Button: Publish to Class`: Saves JSON, updates `status='published'`, making it immediately queryable by students in that class.

#### Screen 10: Performance Analytics & Reporting
*   **Function:** Statistical breakdown of student performance per quiz.
*   **Input Filters:** Dropdown (Select Class) -> Dropdown (Select Quiz).
*   **Data Rendered:**
    *   `Average Score`: Arithmetic mean of all `score` values in `Sessions` for the selected quiz.
    *   `Student Table`: Lists all students, their absolute score, percentage, and submission timestamp.
    *   `Action: Export to CSV`: Compiles the data table into a `.csv` file and triggers browser download.

---

### MODULE C: STUDENT WORKSPACE

#### Screen 11: Student Global Dashboard
*   **Function:** The student's hub for active assignments.
*   **Data Aggregation:**
    *   `Section: Pending Tasks`: Queries `Quizzes` mapped to the student's `Enrollments` where `quiz_id` does NOT exist in the student's `Sessions`.
    *   `Section: Completed Tasks`: Queries `Sessions` for this student.
*   **Action Behaviors:**
    *   `Input: Invite Code`: Text input.
    *   `Button: Join Class`: Dispatches `POST /api/enroll`. 
        *   *Validation:* Checks if code exists in `Classes`. Checks if student is already enrolled. If successful, inserts into `Enrollments`.

#### Screen 12: Specific Class View
*   **Function:** Displays workload scoped to a single class.
*   **Data Display:** 
    *   List of published Quizzes for this specific `class_id`.
    *   Status indicators: "To Do" (Clickable -> Starts Exam) vs "Completed" (Clickable -> Views Score).

#### Screen 13: Live Assessment Environment (Exam Room)
*   **Function:** Execution of the quiz.
*   **Initialization Logic:** Fetches `quiz_data` (JSON) from Backend. Randomizes option order (A, B, C, D are shuffled client-side so students can't share simple letter answers).
*   **Interactive Elements & Rules:**
    *   `Radio Group: Options`: Only one selection allowed per question.
    *   `State Management`: Selected answers are written to browser `localStorage` on every click (Key: `draft_quiz_{id}`). If the browser crashes, reloading the page hydrates the form from `localStorage`.
    *   `Button: Submit Exam`: 
        *   *Validation:* Checks if array length of answers equals total questions. If missing, triggers Warning Modal ("You have X unanswered questions. Proceed?").
*   **Data Submission:** Dispatches `POST /api/sessions/submit` with `{student_id, quiz_id, answers_array, time_taken}`.

#### Screen 14: Automated Grading & AI Tutoring View
*   **Function:** Real-time feedback, grading, and conceptual correction.
*   **Calculation Logic (Backend):** Iterates through submitted `answers_array`, compares with the `answer` key in the original `quiz_data`. Calculates `total_correct` and `accuracy_percentage`. Saves to `Sessions` table.
*   **UI Data Binding (Read-Only):**
    *   `Score Header`: Displays final calculated score (e.g., "8/10").
    *   `Question Review Loop`: Renders every question.
        *   If Correct: UI highlights the user's choice.
        *   If Incorrect: UI highlights the user's wrong choice in a negative state, highlights the correct key in a positive state.
    *   `AI Tutoring Block`: Directly binds the `explanation` string (generated by Gemini in Screen 8) below every question, fulfilling the core EdTech value proposition (explaining the *why*).
    *   `Button: Back to Dashboard`: Clears `localStorage` draft and returns to Screen 11.
