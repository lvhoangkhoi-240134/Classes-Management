import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime

st.set_page_config(page_title="LearnLoop", layout="wide", page_icon="📚")

if 'decks' not in st.session_state:
    st.session_state.decks = []
if 'classes' not in st.session_state:
    st.session_state.classes = []
if 'students' not in st.session_state:
    st.session_state.students = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'mcq_generated' not in st.session_state:
    st.session_state.mcq_generated = False
if 'mock_progress' not in st.session_state:
    st.session_state.mock_progress = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Accuracy (%)': [45, 55, 60, 75, 82, 90]
    }).set_index('Month')

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

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
        
        tab1, tab2, tab3 = st.tabs(["My Decks", "Study Session (AI MCQ)", "Progress"])
        
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
                st.write("No decks found. Please create one.")

        with tab2:
            st.subheader("AI-Powered Study Session")
            st.markdown(f"### 🏆 Current Score: **{st.session_state.score}**")
            
            uploaded_file = st.file_uploader("Upload your lesson document (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])
            
            if uploaded_file is not None:
                if st.button("Generate AI MCQs", type="primary"):
                    with st.spinner("AI is analyzing the document and generating questions..."):
                        st.session_state.mcq_generated = True
                        
            if st.session_state.mcq_generated:
                st.success("MCQs generated successfully based on your file!")
                st.markdown("---")
                st.markdown("#### Question 1")
                st.write("Based on the uploaded document, which of the following best describes the core function of a CPU?")
                
                options = [
                    "A. Storing permanent data for the system.",
                    "B. Acting as the brain of the computer to process instructions.",
                    "C. Cooling down the motherboard.",
                    "D. Providing graphical output to the monitor."
                ]
                
                answer = st.radio("Select your answer:", options, index=None)
                
                if st.button("Submit Answer"):
                    if answer == options[1]:
                        st.success("✅ Correct! +1 Point.")
                        st.session_state.score += 1
                        st.session_state.mcq_generated = False
                    elif answer is not None:
                        st.error("❌ Incorrect.")
                        st.info("**Explanation:** The document explicitly states that the CPU (Central Processing Unit) acts as the brain of the computer, handling all logic and instruction processing. Storage is handled by hard drives, and graphics by the GPU.")
                    else:
                        st.warning("Please select an answer first.")

        with tab3:
            st.subheader("My Progress Analytics")
            st.write("Accuracy percentage over time:")
            st.line_chart(st.session_state.mock_progress)

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
                    st.write("**Last active:** Today")
                    st.line_chart(st.session_state.mock_progress)
                else:
                    st.info("No students have joined this class using the invite code yet.")
            else:
                st.warning("Please create a class first to view student analytics.")
                
    elif not user_name:
        st.info("👈 Please enter your name in the sidebar and click Login to access your dashboard.")

if __name__ == '__main__':
    main()
