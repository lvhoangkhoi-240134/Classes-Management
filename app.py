import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime
import io
import re
import PyPDF2
import docx

st.set_page_config(page_title="LearnLoop", layout="wide", page_icon="📚")

if 'decks' not in st.session_state:
    st.session_state.decks = []
if 'classes' not in st.session_state:
    st.session_state.classes = []
if 'students' not in st.session_state:
    st.session_state.students = []
if 'session_history' not in st.session_state:
    st.session_state.session_history = []
if 'current_exam' not in st.session_state:
    st.session_state.current_exam = None
if 'exam_start_time' not in st.session_state:
    st.session_state.exam_start_time = None

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.txt'):
        text = uploaded_file.read().decode('utf-8')
    elif uploaded_file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
    elif uploaded_file.name.endswith('.docx'):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + " "
    return text

def generate_ai_mcqs(text, num_questions):
    sentences = re.split(r'(?<=[.!?]) +', text)
    valid_sentences = [s.strip() for s in sentences if len(s.split()) > 10]
    
    if len(valid_sentences) == 0:
        return []
        
    if len(valid_sentences) < num_questions:
        valid_sentences = valid_sentences * (num_questions // len(valid_sentences) + 1)
        
    selected_sentences = random.sample(valid_sentences, num_questions)
    all_words = list(set(re.findall(r'\b[a-zA-Z]{5,}\b', text)))
    
    if len(all_words) < 10:
        all_words += ["Concept", "Process", "System", "Analysis", "Data", "Method", "Theory", "Application"]
        
    questions = []
    for s in selected_sentences:
        words_in_s = [w for w in s.split() if len(w) > 4 and w.isalpha()]
        if not words_in_s:
            continue
            
        answer = random.choice(words_in_s)
        question_text = s.replace(answer, "________", 1)
        
        options = [answer]
        attempts = 0
        while len(options) < 4 and attempts < 20:
            distractor = random.choice(all_words)
            if distractor not in options and distractor.lower() != answer.lower():
                options.append(distractor)
            attempts += 1
            
        random.shuffle(options)
        questions.append({
            "q": question_text,
            "options": options,
            "answer": answer,
            "original_sentence": s
        })
    return questions

def main():
    st.title("📚 LearnLoop")
    st.write("Your intelligent flashcard learning platform.")

    st.sidebar.title("Login / Roles")
    role = st.sidebar.selectbox("Who are you?", ["Student", "Teacher"])
    
    user_name = st.sidebar.text_input("Enter your full name:")
    
    if role == "Student":
        invite_code = st.sidebar.text_input("Enter Class Invite Code (Optional):")
        if st.sidebar.button("Login as Student") and user_name:
            student_exists = any(s['name'] == user_name for s in st.session_state.students)
            if not student_exists:
                st.session_state.students.append({"name": user_name, "code": invite_code})
            st.sidebar.success(f"Logged in as {user_name}")
            
    elif role == "Teacher":
        if st.sidebar.button("Login as Teacher") and user_name:
            st.sidebar.success(f"Logged in as Professor {user_name}")

    st.divider()

    if role == "Student" and user_name:
        st.header(f"🎓 Student Dashboard: {user_name}")
        
        tab1, tab2, tab3 = st.tabs(["My Decks", "AI Study Session", "Progress"])
        
        with tab1:
            st.subheader("Create New Deck")
            with st.form("new_deck_form", clear_on_submit=True):
                d_title = st.text_input("Deck Title")
                d_desc = st.text_area("Description")
                submitted = st.form_submit_button("Create Deck")
                if submitted and d_title:
                    st.session_state.decks.append({
                        "title": d_title, 
                        "desc": d_desc, 
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success(f"Deck '{d_title}' has been created successfully!")
            
            st.divider()
            st.subheader("Existing Decks")
            if st.session_state.decks:
                for d in st.session_state.decks:
                    st.info(f"**{d['title']}**\n\n{d['desc']}\n\n*Created on: {d['date']}*")
            else:
                st.write("No decks found.")

        with tab2:
            st.subheader("AI-Powered Exam Session")
            
            if st.session_state.current_exam is None:
                col1, col2 = st.columns(2)
                with col1:
                    num_qs = st.selectbox("Number of Questions", [5, 10, 20, 50, 100])
                with col2:
                    uploaded_file = st.file_uploader("Upload lesson material (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])
                
                if uploaded_file is not None:
                    if st.button("Generate & Start Session", type="primary"):
                        with st.spinner("Reading file and generating questions..."):
                            raw_text = extract_text_from_file(uploaded_file)
                            generated_qs = generate_ai_mcqs(raw_text, num_qs)
                            
                            if generated_qs:
                                st.session_state.current_exam = generated_qs
                                st.session_state.exam_start_time = datetime.now()
                                st.rerun()
                            else:
                                st.error("Could not generate questions. The file might be empty or contain too little text.")
            else:
                st.warning("Exam in progress! Do not refresh the page.")
                
                with st.form("exam_form"):
                    user_answers = {}
                    for i, q in enumerate(st.session_state.current_exam):
                        st.markdown(f"**Q{i+1}:** {q['q']}")
                        user_answers[i] = st.radio(f"Options for Q{i+1}", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
                        st.markdown("---")
                        
                    submit_exam = st.form_submit_button("Submit Exam")
                    
                    if submit_exam:
                        end_time = datetime.now()
                        time_taken = end_time - st.session_state.exam_start_time
                        minutes, seconds = divmod(time_taken.total_seconds(), 60)
                        
                        score = 0
                        results_ui = []
                        
                        for i, q in enumerate(st.session_state.current_exam):
                            is_correct = user_answers[i] == q['answer']
                            if is_correct:
                                score += 1
                                results_ui.append((f"✅ Q{i+1}: Correct!", "success", ""))
                            else:
                                results_ui.append((f"❌ Q{i+1}: Incorrect. You chose '{user_answers[i]}'. Correct answer: '{q['answer']}'", "error", f"Explanation: Based on the text -> '{q['original_sentence']}'"))
                        
                        total_qs = len(st.session_state.current_exam)
                        accuracy = (score / total_qs) * 100
                        
                        session_data = {
                            "student": user_name,
                            "session_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "score": score,
                            "total": total_qs,
                            "accuracy": accuracy,
                            "time_taken": f"{int(minutes)}m {int(seconds)}s"
                        }
                        st.session_state.session_history.append(session_data)
                        
                        st.session_state.last_exam_results = {
                            "score": score,
                            "total": total_qs,
                            "time": f"{int(minutes)}m {int(seconds)}s",
                            "details": results_ui
                        }
                        
                        st.session_state.current_exam = None
                        st.session_state.exam_start_time = None
                        st.rerun()
                        
            if 'last_exam_results' in st.session_state and st.session_state.current_exam is None:
                res = st.session_state.last_exam_results
                st.success(f"### Exam Completed!\n**Final Score:** {res['score']}/{res['total']}\n**Time Taken:** {res['time']}")
                
                with st.expander("View Detailed Results & Explanations"):
                    for title, status, explanation in res['details']:
                        if status == "success":
                            st.success(title)
                        else:
                            st.error(title)
                            st.info(explanation)
                
                if st.button("Start New Session"):
                    del st.session_state.last_exam_results
                    st.rerun()

        with tab3:
            st.subheader("My Progress Analytics")
            user_sessions = [s for s in st.session_state.session_history if s['student'] == user_name]
            
            if user_sessions:
                df = pd.DataFrame(user_sessions)
                df['Session'] = [f"Session {i+1}" for i in range(len(df))]
                
                st.write("**Accuracy Over Recent Sessions (%)**")
                st.line_chart(df.set_index('Session')['accuracy'])
                
                st.write("**Session History Log**")
                st.dataframe(df[['session_date', 'score', 'total', 'accuracy', 'time_taken']])
            else:
                st.info("Complete an AI Study Session to generate your progress chart.")

    elif role == "Teacher" and user_name:
        st.header(f"👨‍🏫 Teacher Dashboard: {user_name}")
        
        tab1, tab2 = st.tabs(["Class Management", "Student Analytics"])
        
        with tab1:
            st.subheader("Create a New Class")
            with st.form("new_class_form", clear_on_submit=True):
                c_name = st.text_input("Class Name")
                submitted = st.form_submit_button("Create Class & Generate Code")
                if submitted and c_name:
                    code = generate_invite_code()
                    st.session_state.classes.append({"name": c_name, "code": code})
                    st.success(f"Class '{c_name}' created! Invite Code: **{code}**")
            
            st.divider()
            st.subheader("My Classes")
            if st.session_state.classes:
                for c in st.session_state.classes:
                    st.info(f"🏫 **{c['name']}** | Invite Code: `{c['code']}`")
            else:
                st.write("No classes created yet.")

        with tab2:
            st.subheader("Student Progress Analytics")
            if st.session_state.classes:
                selected_class = st.selectbox("Select Class", [c['name'] for c in st.session_state.classes])
                class_code = next(c['code'] for c in st.session_state.classes if c['name'] == selected_class)
                
                enrolled_students = [s['name'] for s in st.session_state.students if s['code'] == class_code]
                
                if enrolled_students:
                    selected_student = st.selectbox("Select Student", enrolled_students)
                    st.markdown("---")
                    st.write(f"**Viewing analytics for:** {selected_student}")
                    
                    student_sessions = [s for s in st.session_state.session_history if s['student'] == selected_student]
                    
                    if student_sessions:
                        df_teacher = pd.DataFrame(student_sessions)
                        df_teacher['Session'] = [f"Session {i+1}" for i in range(len(df_teacher))]
                        st.line_chart(df_teacher.set_index('Session')['accuracy'])
                        st.dataframe(df_teacher[['session_date', 'score', 'total', 'accuracy', 'time_taken']])
                    else:
                        st.info("This student has not completed any study sessions yet.")
                else:
                    st.info("No students have joined this class using the invite code yet.")
            else:
                st.warning("Please create a class first to view student analytics.")
                
    elif not user_name:
        st.info("👈 Please enter your name in the sidebar and click Login to access your dashboard.")

if __name__ == '__main__':
    main()
