import streamlit as st
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime
from utils.auth import authentication_required


@authentication_required
def export_to_csv(db, patient_id):
    """Export patient session notes and emotion data to CSV."""
    therapist_id = st.session_state.user_id

    # Get patient info
    patient = db.get_patient(patient_id, therapist_id)
    if not patient:
        st.error("Patient not found.")
        return None

    # Export data using the database function
    csv_file = db.export_patient_data_to_csv(patient_id, therapist_id)
    return csv_file


@authentication_required
def export_to_pdf(db, patient_id):
    """Export patient session notes and emotion data to PDF."""
    therapist_id = st.session_state.user_id

    # Get patient info
    patient = db.get_patient(patient_id, therapist_id)
    if not patient:
        st.error("Patient not found.")
        return None

    # Get session notes
    session_notes = db.get_session_notes(patient_id, therapist_id)
    if not session_notes:
        st.error("No session notes to export.")
        return None

    # Create PDF
    pdf = FPDF()
    pdf.add_page()

    # Set up PDF
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MindScribe Patient Report", 0, 1, "C")

    # Patient information
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Patient: {patient['name']}", 0, 1)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Age: {patient['age'] if patient['age'] else 'Not provided'}", 0, 1)
    pdf.cell(0, 8, f"Gender: {patient['gender'] if patient['gender'] else 'Not provided'}", 0, 1)
    pdf.cell(0, 8, f"Contact: {patient['contact'] if patient['contact'] else 'Not provided'}", 0, 1)
    pdf.cell(0, 8, f"Patient since: {patient['created_at'].split()[0] if 'created_at' in patient else 'Unknown'}", 0, 1)

    # Session notes
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Session Notes", 0, 1)

    for i, note in enumerate(session_notes):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Session: {note['timestamp'].split()[0]} at {note['timestamp'].split()[1]}", 0, 1)

        pdf.set_font("Arial", "", 12)
        # Handle multiline text
        pdf.multi_cell(0, 6, note['note_text'])

        # Find dominant emotion
        emotions = note['emotions']
        dominant_emotion = max(emotions, key=lambda x: emotions[x])
        dominant_score = emotions[dominant_emotion]

        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 8, f"Primary emotion detected: {dominant_emotion.capitalize()} (Score: {dominant_score:.2f})", 0, 1)

        # Add emotion scores
        pdf.set_font("Arial", "", 10)
        for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
            pdf.cell(0, 6, f"{emotion.capitalize()}: {score:.2f}", 0, 1)

        pdf.ln(5)

    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c if c.isalnum() else "_" for c in patient['name']])
    filename = f"{safe_name}_report_{timestamp}.pdf"

    # Save the PDF
    pdf.output(filename)
    return filename


def setup_export_options(db):
    """Set up export options in the sidebar."""
    if 'selected_patient_id' not in st.session_state:
        return

    patient_id = st.session_state.selected_patient_id

    st.sidebar.header("Export Options")

    export_format = st.sidebar.radio(
        "Select export format:",
        options=["CSV", "PDF"]
    )

    export_button = st.sidebar.button("Generate Export")

    if export_button:
        if export_format == "CSV":
            csv_file = export_to_csv(db, patient_id)
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

        elif export_format == "PDF":
            try:
                pdf_file = export_to_pdf(db, patient_id)
                if pdf_file:
                    st.sidebar.success(f"Report generated: {pdf_file}")

                    # Create a download button
                    with open(pdf_file, 'rb') as file:
                        st.sidebar.download_button(
                            label="Download PDF Report",
                            data=file,
                            file_name=pdf_file,
                            mime="application/pdf"
                        )
                else:
                    st.sidebar.error("Failed to generate PDF report.")
            except Exception as e:
                st.sidebar.error(f"Error generating PDF: {str(e)}")
                st.sidebar.info("Try CSV export instead, or check if FPDF is installed.")
