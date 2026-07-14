# 🚀 SYSTEM SPECIFICATION: LEARNLOOP (AI-Powered EdTech)

## 1. SYSTEM OVERVIEW
**LearnLoop** is an AI-powered Learning Management System (LMS) and automated quiz generation platform. The system allows educators to seamlessly convert raw documents (PDF, Docx, Text) into smart multiple-choice questions using Google Gemini, manage classrooms, and track student progress in real-time.

### 1.1. Tech Stack
*   **Backend:** Python 3.10+, FastAPI (Asynchronous, High Performance), Uvicorn.
*   **AI Engine:** Google Generative AI (Gemini 1.5 Flash).
*   **Database:** SQLite (MVP Phase) -> Ready to scale to PostgreSQL.
*   **Frontend:** HTML5, CSS3 (Tailwind CSS/Bootstrap), Vanilla JavaScript (Fetch API).
*   **Authentication:** JWT (JSON Web Tokens) combined with bcrypt for password hashing.

### 1.2. Role-Based Access Control (RBAC)
*   **Guest:** Can only access the Landing Page, Login, Register, and Forgot Password screens.
*   **Teacher:** Can create classes, generate AI quizzes, assign homework, and view class analytics.
*   **Student:** Can join classes via Invite Code, take live quizzes, and review scores/explanations.

---

## 2. DATABASE ARCHITECTURE (THEORETICAL ERD)
The system utilizes 5 primary entities:
1.  **`Users`**: `id`, `email`, `password_hash`, `full_name`, `role` (teacher/student).
2.  **`Classes`**: `id`, `name`, `invite_code`, `teacher_id`.
3.  **`Enrollments`**: `id`, `student_id`, `class_id`.
4.  **`Quizzes`**: `id`, `class_id`, `title`, `raw_document`, `quiz_data` (JSON), `created_at`.
5.  **`Sessions`**: `id`, `student_id`, `quiz_id`, `score`, `total`, `accuracy`, `time_taken`, `submitted_at`.

---

## 3. DETAILED UI/UX & FEATURES SPECIFICATION

### 🔴 PART 1: AUTHENTICATION FLOW

#### Screen 1: Splash / Landing Page
*   **Purpose:** Introduce LearnLoop and navigate users.
*   **UI Components:**
    *   Hero Section: Headline "Turn documents into quizzes in 10 seconds".
    *   Call-to-Action (CTA): 2 distinct buttons "I am a Teacher" & "I am a Student".
*   **Behavior:** Clicking a CTA redirects to Screen 2 with the role parameter passed.

#### Screen 2: Login & Register
*   **Purpose:** Grant system access.
*   **UI Components (Register Tab):**
    *   Role Selector (Radio buttons): [ ] Teacher [ ] Student.
    *   Inputs: Full Name, Email, Password, Confirm Password.
    *   Validation: Password > 8 chars, alphanumeric.
*   **UI Components (Login Tab):**
    *   Inputs: Email, Password.
    *   Link: "Forgot Password?".
    *   Action: Login button.
*   **API Interaction:** 
    *   `POST /api/auth/login` -> Returns JWT Token (stored in `localStorage`). Redirects to respective Dashboard based on Role.

#### Screen 3: Forgot Password
*   **UI Components:** Email Input -> "Send Recovery Link" button.
*   **Behavior:** Simulates sending a 6-digit OTP via email. Screen transitions to OTP verification and new password setup.

---

### 🔵 PART 2: TEACHER PORTAL

#### Screen 4: Teacher Dashboard
*   **Purpose:** Centralized management hub for educators.
*   **UI Components:**
    *   **Sidebar Navigation:** Dashboard, Classes, Quiz Bank, Settings.
    *   **Widgets:** Total Classes, Total AI Quizzes Generated, Total Active Students.
    *   **Quick Access:** Top 3 recently active classes (Clickable cards).

#### Screen 5: Class Management & Detail
*   **Purpose:** Create classes and manage student rosters.
*   **UI Components:**
    *   "Create New Class" Button (Opens modal for Class Name -> Auto-generates a 6-char `invite_code` e.g., `A7B9X2`).
    *   Prominent `invite_code` display with a "Copy" button.
    *   **Students Tab:** List of enrolled students (with a "Remove/Kick" action).
    *   **Quizzes Tab:** Assigned quizzes for this specific class. Prominent "Generate AI Quiz" button.

#### Screen 6: AI Quiz Generator Studio (The Core)
*   **Purpose:** Interface to interact with Google Gemini for quiz creation.
*   **UI Components:**
    *   **Step 1 - Input:** Drag & Drop zone for files (PDF, Docx) or a large Textbox for raw text. Slider to select Question Count (5 - 50). "Generate AI Quiz" button.
    *   **Step 2 - Loading State:** Engaging animations ("Reading document...", "Analyzing context...", "Generating questions...") to retain user attention.
    *   **Step 3 - Review & Edit:** List of generated questions. 
        *   Inline editing: Teachers can click directly on the text to modify questions or options.
        *   "Regenerate" button per question for fine-tuning.
    *   **Step 4 - Publish:** Input for Quiz Title (e.g., "Chapter 1: Biology"), Dropdown to select Target Class, "Save & Publish" button.

#### Screen 7: Analytics & Reports
*   **Purpose:** Visualize class performance.
*   **UI Components:**
    *   Dropdowns: Select Class -> Select Quiz.
    *   Bar chart displaying score distribution (0-100%).
    *   Data Table: Student Name, Score, Accuracy (%), Time Taken, Submission Date.

---

### 🟢 PART 3: STUDENT PORTAL

#### Screen 8: Student Dashboard
*   **Purpose:** Landing page for students post-login.
*   **UI Components:**
    *   Prominent Action: "Join a Class" (Modal for `invite_code` input).
    *   Section 1: **"Pending Assignments"** (List of newly assigned quizzes with "New" tags).
    *   Section 2: **"My Classes"** (List of currently enrolled classes).

#### Screen 9: Live Quiz Arena
*   **Purpose:** Focused, distraction-free testing environment.
*   **UI Components:**
    *   **Sticky Header:** Quiz Title, Student Name, and Countdown Timer (Optional).
    *   **Main Content:** Pagination (1 question per screen) or smooth vertical scrolling.
    *   Large, clear Option buttons (A, B, C, D) with active selection highlights.
    *   "Submit" button at the bottom. Includes a safety Alert ("You have 2 unanswered questions. Submit anyway?") if applicable.
    *   *Under the hood:* Auto-saves draft answers to `localStorage` to prevent data loss on network drops.

#### Screen 10: Quiz Result & Insights
*   **Purpose:** Immediate feedback upon submission.
*   **UI Components:**
    *   Massive Score Circle in the center (e.g., 80/100 Points - 80%).
    *   Time Taken metric: e.g., 12m 45s.
    *   **Detailed Breakdown:** List of all questions.
        *   Correct: Green checkmark.
        *   Incorrect: Red cross on the chosen answer, green highlight on the correct answer.
        *   **AI Explanation Box:** Appears below each question detailing *WHY* the answer is correct/incorrect, fostering actual learning.

---

## 4. CORE DATA FLOW (FOR DEVELOPMENT)
The AI quiz generation lifecycle operates as follows:
1. `Frontend` sends Document File + Number of Questions to `Backend` via `multipart/form-data`.
2. `Backend` (FastAPI) extracts raw text from the file (using PyPDF2/docx2txt).
3. `Backend` injects text into a structured prompt (enforcing JSON schema) -> Sent to `Gemini API`.
4. `Gemini API` returns a JSON string containing an array of objects (`q`, `options`, `answer`, `explanation`).
5. `Backend` parses the JSON, stores it in the `Quizzes` table (SQLite).
6. `Backend` returns the `quiz_id` and data payload to the `Frontend` to render the Review UI (Screen 6).
