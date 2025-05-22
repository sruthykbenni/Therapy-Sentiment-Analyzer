import streamlit as st
import os
import pathlib
from utils.database import Database
from utils.auth import login_user, signup_user, logout_user, is_authenticated
from components.dashboard import render_dashboard
from components.patient_view import render_patient_view
from components.exports import setup_export_options

# Set page configuration
st.set_page_config(
    page_title="MindScribe - Therapist Portal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load and inject custom CSS
def load_css():
    css_file = pathlib.Path(__file__).parent / "assets" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {css_file}")


# Initialize the application
def init_app():
    # Initialize session state variables if they don't exist
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

    # Connect to the database
    db = Database()
    return db


# Render the sidebar
def render_sidebar(db):
    with st.sidebar:
        st.title("MindScribe")
        st.caption("Therapist Portal")

        # Show user info and logout button if authenticated
        if is_authenticated():
            st.write(f"Logged in as: **{st.session_state.user_name}**")
            if st.button("Logout"):
                logout_user()

        st.markdown("---")

        # Navigation
        if is_authenticated():
            if st.button("Dashboard", key="nav_dashboard"):
                if 'selected_patient_id' in st.session_state:
                    del st.session_state.selected_patient_id
                st.rerun()

            # Only show patient options if a patient is selected
            if 'selected_patient_id' in st.session_state:
                st.write("#### Patient Options")

                # Add export options to the sidebar
                setup_export_options(db)

        # App information
        st.markdown("---")
        st.markdown("""
        **MindScribe**  
        A therapist portal with emotion analysis.  
        v1.0.0
        """)


# Main application layout
def main():
    # Initialize the app and database
    db = init_app()

    # Load custom CSS
    load_css()

    # Render the sidebar
    render_sidebar(db)

    # Main content area
    if not is_authenticated():
        # Show login or signup page
        col1, col2 = st.columns([1, 1])

        with col1:
            login_user(db)

        with col2:
            st.markdown("### New to MindScribe?")
            signup_user(db)

    else:
        # Check if a patient is selected
        if 'selected_patient_id' in st.session_state:
            # Show patient view
            render_patient_view(db)
        else:
            # Show dashboard
            render_dashboard(db)

    # Close the database connection when the app is done
    db.close()


if __name__ == "__main__":
    main()