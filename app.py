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
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    
    if role == "Student":
        code = st.sidebar.text_input("Class Invite Code:")
        if st.sidebar.button("Login"):
            if user_name:
                st.session_state.students.append({"name": user_name, "code": code})
                st.sidebar.success(f"Logged in as {user_name}")

    if not user_name:
        st.info("Please enter your name in the sidebar to start.")
        return

    if role == "Student":
        st.header(f"🎓 Dashboard: {user_name}")
        tab1, tab2 = st.tabs(["AI Study Session", "Progress"])
        
        with tab1:
            if st.session_state.current_exam is None:
                num_qs = st.selectbox("Number of Questions", [10, 20, 50, 100])
                uploaded_file = st.file_uploader("Upload material (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])
                
                if uploaded_file and st.button("Start Exam"):
                    if not api_key:
                        st.error("Missing API Key!")
                    else:
                        with st.spinner("AI is crafting your exam..."):
                            raw_text = extract_text_from_file(uploaded_file)
                            qs = ai_engine.generate_smart_mcqs(raw_text, num_qs, api_key)
                            if qs:
                                st.session_state.current_exam = qs
                                st.session_state.exam_start_time = datetime.now()
                                st.rerun()
            else:
                with st.form("exam_form"):
                    user_answers = {}
                    for i, q in enumerate(st.session_state.current_exam):
                        st.markdown(f"**Q{i+1}:** {q['q']}")
                        user_answers[i] = st.radio("Options", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
                    
                    if st.form_submit_button("Submit Exam"):
                        score = sum(1 for i, q in enumerate(st.session_state.current_exam) if user_answers[i] == q['answer'])
                        total = len(st.session_state.current_exam)
                        time_taken = datetime.now() - st.session_state.exam_start_time
                        
                        st.session_state.session_history.append({
                            "student": user_name, "accuracy": (score/total)*100, "score": score, "total": total
                        })
                        st.session_state.last_result = {"score": score, "total": total, "details": st.session_state.current_exam, "answers": user_answers}
                        st.session_state.current_exam = None
                        st.rerun()

            if 'last_result' in st.session_state:
                res = st.session_state.last_result
                st.success(f"Score: {res['score']}/{res['total']}")
                for i, q in enumerate(res['details']):
                    if res['answers'][i] != q['answer']:
                        st.error(f"Q{i+1} Wrong. Correct: {q['answer']}. Expl: {q['explanation']}")
                if st.button("Clear Results"):
                    del st.session_state.last_result
                    st.rerun()

        with tab2:
            df = pd.DataFrame([s for s in st.session_state.session_history if s['student'] == user_name])
            if not df.empty:
                st.line_chart(df['accuracy'])
            else:
                st.info("No data yet.")

    elif role == "Teacher":
        st.header(f"👨‍🏫 Teacher Dashboard: {user_name}")
        class_name = st.text_input("Class Name")
        if st.button("Create Class"):
            st.success(f"Class '{class_name}' created!")

if __name__ == '__main__':
    main()
