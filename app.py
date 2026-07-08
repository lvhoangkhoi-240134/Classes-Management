import streamlit as st
import pandas as pd
import ai_engine
from datetime import datetime
import io
import PyPDF2
import docx

st.set_page_config(page_title="LearnLoop", layout="wide", page_icon="📚")

if 'session_history' not in st.session_state:
    st.session_state.session_history = []
if 'current_exam' not in st.session_state:
    st.session_state.current_exam = None
if 'exam_start_time' not in st.session_state:
    st.session_state.exam_start_time = None
if 'students' not in st.session_state:
    st.session_state.students = []
if 'classes' not in st.session_state:
    st.session_state.classes = []

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

def main():
    st.title("📚 LearnLoop")
    st.sidebar.title("Login / Roles")
    
    role = st.sidebar.selectbox("Who are you?", ["Student", "Teacher"])
    user_name = st.sidebar.text_input("Full Name:")
    api_key = st.sidebar.text_input("Google Gemini API Key:", type="password")
    
    if role == "Student":
        code = st.sidebar.text_input("Class Invite Code (Optional):")
        if st.sidebar.button("Login as Student"):
            if user_name:
                if not any(s['name'] == user_name for s in st.session_state.students):
                    st.session_state.students.append({"name": user_name, "code": code})
                st.sidebar.success(f"Logged in as {user_name}")
            else:
                st.sidebar.error("Please enter your name.")

    if not user_name:
        st.info("👈 Please enter your name in the sidebar to start.")
        return

    if role == "Student":
        st.header(f"🎓 Dashboard: {user_name}")
        tab1, tab2 = st.tabs(["AI Study Session", "Progress Analytics"])
        
        with tab1:
            if st.session_state.current_exam is None:
                col1, col2 = st.columns(2)
                with col1:
                    num_qs = st.selectbox("Number of Questions", [5, 10, 20, 50])
                with col2:
                    uploaded_file = st.file_uploader("Upload material (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])
                
                if uploaded_file and st.button("Generate & Start Exam", type="primary"):
                    if not api_key:
                        st.error("Missing Google Gemini API Key in the sidebar!")
                    else:
                        with st.spinner(f"AI is analyzing your file and crafting {num_qs} questions... (This might take a minute)"):
                            raw_text = extract_text_from_file(uploaded_file)
                            qs = ai_engine.generate_smart_mcqs(raw_text, num_qs, api_key)
                            
                            if isinstance(qs, dict) and "error" in qs:
                                st.error(qs["error"])
                            elif isinstance(qs, list) and len(qs) > 0:
                                st.session_state.current_exam = qs
                                st.session_state.exam_start_time = datetime.now()
                                st.rerun()
                            else:
                                st.error("Unknown error occurred while generating questions.")
            else:
                exam_data = st.session_state.current_exam
                if not isinstance(exam_data, list) or len(exam_data) == 0 or not isinstance(exam_data[0], dict):
                    st.error("Question data structure is corrupted. Please clear and regenerate.")
                    if st.button("Clear Corrupted Session"):
                        st.session_state.current_exam = None
                        st.rerun()
                else:
                    st.warning("Exam in progress! Do not refresh the page.")
                    with st.form("exam_form"):
                        user_answers = {}
                        for i, q in enumerate(exam_data):
                            st.markdown(f"**Q{i+1}:** {q.get('q', 'Error reading question')}")
                            options = q.get('options', [])
                            user_answers[i] = st.radio(
                                f"Options for Q{i+1}", 
                                options, 
                                key=f"q_{i}", 
                                index=None, 
                                label_visibility="collapsed"
                            )
                            st.markdown("---")
                        
                        submit_exam = st.form_submit_button("Submit Exam")
                        if submit_exam:
                            score = 0
                            total = len(exam_data)
                            
                            for i, q in enumerate(exam_data):
                                if user_answers.get(i) == q.get('answer'):
                                    score += 1
                                    
                            time_taken = datetime.now() - st.session_state.exam_start_time
                            minutes, seconds = divmod(time_taken.total_seconds(), 60)
                            time_str = f"{int(minutes)}m {int(seconds)}s"
                            accuracy = (score / total) * 100 if total > 0 else 0
                            
                            st.session_state.session_history.append({
                                "student": user_name, 
                                "session_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "accuracy": accuracy, 
                                "score": score, 
                                "total": total,
                                "time_taken": time_str
                            })
                            
                            st.session_state.last_result = {
                                "score": score, 
                                "total": total, 
                                "time": time_str,
                                "details": exam_data, 
                                "answers": user_answers
                            }
                            st.session_state.current_exam = None
                            st.rerun()

            if 'last_result' in st.session_state and st.session_state.current_exam is None:
                res = st.session_state.last_result
                st.success(f"### Exam Completed!\n**Score:** {res['score']}/{res['total']} | **Time Taken:** {res['time']}")
                
                with st.expander("View Explanations & Corrections"):
                    for i, q in enumerate(res['details']):
                        user_ans = res['answers'].get(i)
                        correct_ans = q.get('answer')
                        if user_ans == correct_ans:
                            st.success(f"✅ Q{i+1}: Correct!")
                        else:
                            st.error(f"❌ Q{i+1}: Incorrect. You chose '{user_ans}'. Correct: '{correct_ans}'.")
                            st.info(f"**Explanation:** {q.get('explanation', 'No explanation provided.')}")
                
                if st.button("Start New Session"):
                    del st.session_state.last_result
                    st.rerun()

        with tab2:
            user_sessions = [s for s in st.session_state.session_history if s['student'] == user_name]
            if user_sessions:
                df = pd.DataFrame(user_sessions)
                df['Session'] = [f"Session {i+1}" for i in range(len(df))]
                st.write("### Accuracy Over Time (%)")
                st.line_chart(df.set_index('Session')['accuracy'])
                st.dataframe(df[['session_date', 'score', 'total', 'accuracy', 'time_taken']])
            else:
                st.info("Complete an AI Study Session to generate your progress chart.")

    elif role == "Teacher":
        st.header(f"👨‍🏫 Teacher Dashboard: {user_name}")
        tab1, tab2 = st.tabs(["Class Management", "Student Analytics"])
        
        with tab1:
            class_name = st.text_input("Class Name")
            if st.button("Create Class"):
                import random, string
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                st.session_state.classes.append({"name": class_name, "code": code})
                st.success(f"Class '{class_name}' created! Invite Code: **{code}**")
                
            st.divider()
            st.write("### My Classes")
            for c in st.session_state.classes:
                st.info(f"🏫 **{c['name']}** | Invite Code: `{c['code']}`")

        with tab2:
            if st.session_state.classes:
                selected_class = st.selectbox("Select Class", [c['name'] for c in st.session_state.classes])
                class_code = next((c['code'] for c in st.session_state.classes if c['name'] == selected_class), None)
                
                enrolled_students = [s['name'] for s in st.session_state.students if s['code'] == class_code]
                if enrolled_students:
                    selected_student = st.selectbox("Select Student", enrolled_students)
                    student_sessions = [s for s in st.session_state.session_history if s['student'] == selected_student]
                    if student_sessions:
                        df_t = pd.DataFrame(student_sessions)
                        df_t['Session'] = [f"Session {i+1}" for i in range(len(df_t))]
                        st.line_chart(df_t.set_index('Session')['accuracy'])
                        st.dataframe(df_t[['session_date', 'score', 'total', 'accuracy', 'time_taken']])
                    else:
                        st.info("This student hasn't taken any exams yet.")
                else:
                    st.info("No students have joined this class yet.")
            else:
                st.warning("Create a class first.")

if __name__ == '__main__':
    main()
