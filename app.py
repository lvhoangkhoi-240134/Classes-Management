import streamlit as st

st.set_page_config(page_title="LearnLoop", layout="wide", page_icon="📚")

def main():
    st.title("📚 Welcome to LearnLoop")
    st.write("Your intelligent flashcard learning platform.")

    st.sidebar.title("Login / Roles")
    role = st.sidebar.selectbox("Who are you?", ["Student", "Teacher"])

    st.divider()

    if role == "Student":
        st.header("🎓 Student Dashboard")
        st.write("Here you can create Decks, review MCQs, and view your progress.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Create New Deck ➕", use_container_width=True):
                st.info("Deck creation feature will be connected to the database soon!")
        with col2:
            if st.button("Start Study Session 🧠", use_container_width=True):
                st.success("System will filter cards with next_review_date <= today.")
        with col3:
            if st.button("View Progress Chart 📈", use_container_width=True):
                st.warning("Waiting for data connection from study_daily_stats table...")

    elif role == "Teacher":
        st.header("👨‍🏫 Teacher Dashboard")
        st.write("Manage classes, issue Invite Codes, and track student progress.")
        
        st.subheader("Create a new class")
        class_name = st.text_input("Enter class name:")
        if st.button("Create Class & Get Code"):
            if class_name:
                st.success(f"Successfully created class '{class_name}'! The invite code is: **XYZ123**")
            else:
                st.error("Please enter a class name!")

if __name__ == '__main__':
    main()