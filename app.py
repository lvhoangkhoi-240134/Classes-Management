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
    
    st.divider()

    if role == "Student":
        st.header("🎓 Student Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["My Decks", "Study Session", "Progress"])
        
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
            st.subheader("Study Session")
            if st.button("Start Review (Due Cards Only)", type="primary"):
                st.write("Fetching cards where next_review_date <= today...")
                
                st.markdown("### Card 1: Fill in the gap")
                st.write("**Front:** The {CPU} is the brain of the computer.")
                
                if st.button("Show Answer"):
                    st.success("**Back:** CPU")
                    st.write("Rate your difficulty to schedule the next review:")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.button("0 - Again")
                    col2.button("1 - Hard")
                    col3.button("2 - Good")
                    col4.button("3 - Easy")

        with tab3:
            st.subheader("My Progress Analytics")
            st.write("Accuracy percentage over time:")
            st.line_chart(st.session_state.mock_progress)

    elif role == "Teacher":
        st.header("👨‍🏫 Teacher Dashboard")
        
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
                st.write(f"Viewing analytics for class: **{selected_class}**")
                
                st.markdown("---")
                st.write("**Student:** Tran Thi Bao Ngan")
                st.write("**Last active:** Today")
                st.line_chart(st.session_state.mock_progress)
            else:
                st.warning("Please create a class first to view student analytics.")

if __name__ == '__main__':
    main()
