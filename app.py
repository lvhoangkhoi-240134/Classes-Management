import streamlit as st
import pandas as pd
import ai_engine
import database
from datetime import datetime
import PyPDF2
import docx

st.set_page_config(page_title="LearnLoop", layout="wide", page_icon="📚")

database.init_db()

if 'current_exam' not in st.session_state:
    st.session_state.current_exam = None
if 'exam_start_time' not in st.session_state:
    st.session_state.exam_start_time = None

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

def generate_random_code():
    import random, string
    st.session_state.class_code_input = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

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
                database.enroll_student(user_name, code)
                st.sidebar.success(f"Logged in as {user_name}")

    if not user_name:
        st.info("👈 Please enter your name to start.")
        return

    if role == "Student":
        st.header(f"🎓 Dashboard: {user_name}")
        tab1, tab2 = st.tabs(["AI Study Session", "Progress"])
        
        with tab1:
            if st.session_state.current_exam is None:
                num_qs = st.selectbox("Number of Questions", [5, 10, 20])
                uploaded_file = st.file_uploader("Upload material", type=["txt", "pdf", "docx"])
                
                if uploaded_file and st.button("Start Exam"):
                    if not api_key:
                        st.error("Missing API Key!")
                    else:
                        with st.spinner("AI is analyzing..."):
                            raw_text = extract_text_from_file(uploaded_file)
                            qs = ai_engine.generate_smart_mcqs(raw_text, num_qs, api_key)
                            if isinstance(qs, list):
                                st.session_state.current_exam = qs
                                st.session_state.exam_start_time = datetime.now()
                                st.rerun()
                            else:
                                st.error(qs.get("error", "Failed to generate."))
            else:
                with st.form("exam_form"):
                    user_answers = {}
                    for i, q in enumerate(st.session_state.current_exam):
                        st.markdown(f"**Q{i+1}:** {q.get('q')}")
                        user_answers[i] = st.radio("Options", q.get('options'), key=f"q_{i}", index=None, label_visibility="collapsed")
                    
                    if st.form_submit_button("Submit"):
                        score = sum(1 for i, q in enumerate(st.session_state.current_exam) if user_answers.get(i) == q.get('answer'))
                        time_taken = str(datetime.now() - st.session_state.exam_start_time)
                        database.save_session(user_name, (score/len(st.session_state.current_exam))*100, score, len(st.session_state.current_exam), time_taken)
                        st.session_state.last_res = {"score": score, "total": len(st.session_state.current_exam), "details": st.session_state.current_exam, "answers": user_answers}
                        st.session_state.current_exam = None
                        st.rerun()

            if 'last_res' in st.session_state:
                res = st.session_state.last_res
                st.success(f"Result: {res['score']}/{res['total']}")
                for i, q in enumerate(res['details']):
                    if res['answers'].get(i) != q.get('answer'):
                        st.error(f"Q{i+1} Wrong. Correct: {q.get('answer')}. Expl: {q.get('explanation')}")
                if st.button("Clear"):
                    del st.session_state.last_res
                    st.rerun()

        with tab2:
            df = pd.DataFrame(database.get_student_sessions(user_name))
            if not df.empty: 
                st.line_chart(df['accuracy'])
            else: 
                st.info("No data.")

    elif role == "Teacher":
        st.header("👨‍🏫 Teacher Dashboard")
        tab1, tab2 = st.tabs(["Class Management", "Student Analytics"])
        
        with tab1:
            name = st.text_input("Class Name")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                custom_code = st.text_input("Invite Code (Manual or Random)", key="class_code_input")
            with col2:
                st.write("")
                st.write("")
                st.button("Random Code", on_click=generate_random_code)

            if st.button("Create"):
                if not name or not custom_code:
                    st.error("Please provide both Class Name and Invite Code.")
                elif database.check_code_exists(custom_code):
                    st.error(f"Invite code '{custom_code}' already exists! Please choose another one.")
                else:
                    database.create_class(name, user_name, custom_code)
                    st.success(f"Class '{name}' created! Invite Code: {custom_code}")
                    st.session_state.class_code_input = ""
                    
            st.divider()
            st.write("### My Classes")
            my_classes = database.get_teacher_classes(user_name)
            for c in my_classes:
                st.info(f"🏫 **{c['name']}** | Invite Code: `{c['code']}`")

        with tab2:
            my_classes = database.get_teacher_classes(user_name)
            if my_classes:
                selected_class = st.selectbox("Select Class", [c['name'] for c in my_classes])
                class_code = next((c['code'] for c in my_classes if c['name'] == selected_class), None)
                
                enrolled_students = database.get_students_in_class(class_code)
                if enrolled_students:
                    selected_student = st.selectbox("Select Student", enrolled_students)
                    student_sessions = database.get_student_sessions(selected_student)
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
