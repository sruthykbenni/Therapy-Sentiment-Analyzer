import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from utils.auth import authentication_required
from utils.emotion import analyze_emotions, plot_emotion_bar_chart, plot_emotion_trends


@authentication_required
def render_patient_view(db):
    """Render the detailed view for a selected patient."""
    # Check if a patient is selected
    if 'selected_patient_id' not in st.session_state:
        st.error("No patient selected.")
        return

    patient_id = st.session_state.selected_patient_id
    therapist_id = st.session_state.user_id

    # Get patient data
    patient = db.get_patient(patient_id, therapist_id)
    if not patient:
        st.error("Patient not found.")
        return

    # Display patient header
    st.title(f"Patient: {patient['name']}")

    # Patient info section
    with st.expander("Patient Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Age:** {patient['age'] if patient['age'] else 'Not provided'}")
            st.write(f"**Gender:** {patient['gender'] if patient['gender'] else 'Not provided'}")
        with col2:
            st.write(f"**Contact:** {patient['contact'] if patient['contact'] else 'Not provided'}")
            st.write(f"**Patient since:** {patient['created_at'].split()[0] if 'created_at' in patient else 'Unknown'}")

        if patient.get('notes'):
            st.write("**Initial Notes:**")
            st.write(patient['notes'])

    # Back to dashboard button
    if st.button("Back to Dashboard"):
        if 'selected_patient_id' in st.session_state:
            del st.session_state.selected_patient_id
        st.rerun()

    # Get session notes for this patient
    session_notes = db.get_session_notes(patient_id, therapist_id)

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Session Notes", "Emotional Trends"])

    # Tab 1: Session Notes
    with tab1:
        st.header("Session Notes")

        # Form for adding new session notes
        with st.form("add_session_note"):
            st.subheader("Add New Session Note")
            note_text = st.text_area("Session Notes", height=150)
            submitted = st.form_submit_button("Save & Analyze")

            if submitted:
                if not note_text:
                    st.error("Please enter session notes.")
                else:
                    # Analyze emotions in the text
                    emotions = analyze_emotions(note_text)

                    if emotions:
                        # Save note with emotion analysis
                        note_id = db.add_session_note(patient_id, therapist_id, note_text, emotions)

                        if note_id:
                            st.success("Session note saved successfully!")

                            # Display emotion analysis
                            st.subheader("Emotion Analysis")
                            fig = plot_emotion_bar_chart(emotions)
                            if fig:
                                st.pyplot(fig)

                            # Refresh to update the notes list
                            st.rerun()
                        else:
                            st.error("Failed to save session note.")
                    else:
                        st.error("Failed to analyze emotions. Please try again.")

        # Display existing session notes
        if session_notes:
            st.subheader("Previous Session Notes")

            for i, note in enumerate(session_notes):
                with st.expander(f"Session: {note['timestamp'].split()[0]} at {note['timestamp'].split()[1]}",
                                 expanded=i == 0):
                    st.write(note['note_text'])

                    # Find dominant emotion
                    emotions = note['emotions']
                    dominant_emotion = max(emotions, key=lambda x: emotions[x])
                    dominant_score = emotions[dominant_emotion]

                    st.write(
                        f"**Primary emotion detected:** {dominant_emotion.capitalize()} (Score: {dominant_score:.2f})")

                    # Show emotion chart
                with st.expander("View Full Emotion Analysis"):
                    fig = plot_emotion_bar_chart(emotions)
                    if fig:
                        st.pyplot(fig)
        else:
            st.info("No session notes yet. Add your first note above.")

    # Tab 2: Emotional Trends
    with tab2:
        st.header("Emotional Trends Analysis")

        if not session_notes:
            st.info("No session data available for trend analysis. Add session notes to see trends.")
        else:
            # Get emotion data as DataFrame
            df = db.get_emotions_dataframe(patient_id, therapist_id)

            if not df.empty:
                # Distribution of dominant emotions
                st.subheader("Distribution of Dominant Emotions")
                fig1 = plot_emotion_trends(df, emotion_type='dominant')
                if fig1:
                    st.pyplot(fig1)

                # Line charts for specific emotions over time
                st.subheader("Emotion Trends Over Time")

                # Get list of emotions
                emotion_columns = [col for col in df.columns if col not in ['timestamp', 'dominant_emotion']]

                if emotion_columns:
                    selected_emotion = st.selectbox(
                        "Select emotion to view trend:",
                        options=emotion_columns
                    )

                    if selected_emotion:
                        fig2 = plot_emotion_trends(df, emotion_type=selected_emotion)
                        if fig2:
                            st.pyplot(fig2)

                        # Summary statistics
                        st.subheader("Summary Statistics")
                        avg_score = df[selected_emotion].mean()
                        max_score = df[selected_emotion].max()
                        min_score = df[selected_emotion].min()

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Average Score", f"{avg_score:.2f}")
                        col2.metric("Maximum Score", f"{max_score:.2f}")
                        col3.metric("Minimum Score", f"{min_score:.2f}")

                        # Show recent trend direction
                        if len(df) >= 2:
                            recent_trend = df[selected_emotion].iloc[-1] - df[selected_emotion].iloc[-2]
                            trend_direction = "increasing" if recent_trend > 0 else "decreasing" if recent_trend < 0 else "stable"
                            st.write(f"**Recent trend:** {selected_emotion.capitalize()} is {trend_direction}.")
            else:
                st.warning("Error processing emotion data for trends.")

    # Export options
    st.sidebar.header("Export Options")
    export_csv = st.sidebar.button("Export to CSV")
    if export_csv:
        csv_file = db.export_patient_data_to_csv(patient_id, therapist_id)
        if csv_file:
            st.sidebar.success(f"Data exported to {csv_file}")

            # Create a download button
            with open(csv_file, 'rb') as file:
                st.sidebar.download_button(
                    label="Download CSV File",
                    data=file,
                    file_name=csv_file,
                    mime="text/csv"
                )
        else:
            st.sidebar.error("Failed to export data or no data to export.")
