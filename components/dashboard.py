import streamlit as st
from utils.auth import authentication_required
import pandas as pd


@authentication_required
def render_dashboard(db):
    """Render the therapist dashboard with patient management."""
    st.title(f"Welcome, {st.session_state.user_name}")

    st.markdown("## Your Patients")

    # Get patients for the logged-in therapist
    patients = db.get_patients(st.session_state.user_id)

    # Display patients in a table
    if patients:
        # Convert to DataFrame for easier display
        df = pd.DataFrame(patients)
        # Select only relevant columns for display
        display_cols = ['id', 'name', 'age', 'gender', 'contact']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols]
            df_display = df_display.rename(columns={'id': 'Patient ID'})

            # Hide index
            st.dataframe(df_display.set_index('Patient ID'), use_container_width=True)
        else:
            st.error("Patient data columns are missing expected fields.")
    else:
        st.info("You don't have any patients yet. Add your first patient below.")

    # Add new patient form
    st.markdown("### Add New Patient")
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120, step=1)
        with col2:
            gender = st.selectbox("Gender", ["", "Male", "Female", "Non-binary", "Other", "Prefer not to say"])
            contact = st.text_input("Contact Information (Phone/Email)")

        notes = st.text_area("Initial Notes (Optional)")
        submit_button = st.form_submit_button("Add Patient")

    if submit_button:
        if not name:
            st.error("Patient name is required.")
        else:
            # Add the patient to the database
            patient_id = db.add_patient(
                st.session_state.user_id,
                name,
                age if age > 0 else None,
                gender if gender else None,
                contact,
                notes
            )

            if patient_id:
                st.success(f"Patient '{name}' added successfully!")
                # Refresh the page to show the updated patient list
                st.rerun()
            else:
                st.error("Failed to add patient.")

    # Patient selection for detailed view
    if patients:
        st.markdown("### View Patient Records")

        # Create patient selection dropdown
        patient_options = {p['id']: f"{p['name']} (ID: {p['id']})" for p in patients}
        selected_patient_id = st.selectbox(
            "Select a patient to view details",
            options=list(patient_options.keys()),
            format_func=lambda x: patient_options[x]
        )

        if selected_patient_id:
            view_button = st.button("View Patient Details")
            if view_button:
                # Store the selected patient in session state and navigate to patient view
                st.session_state.selected_patient_id = selected_patient_id
                st.rerun()

    # Admin section (optional)
    with st.expander("Admin Tools"):
        st.markdown("### Delete Patient")

        if patients:
            patient_to_delete = st.selectbox(
                "Select patient to delete",
                options=list(patient_options.keys()),
                format_func=lambda x: patient_options[x],
                key="delete_patient_select"
            )

            if patient_to_delete:
                delete_button = st.button(
                    "Delete Patient",
                    help="This will permanently delete the patient and all their session notes."
                )

                if delete_button:
                    confirm = st.checkbox("I understand this action cannot be undone")
                    if confirm:
                        if db.delete_patient(patient_to_delete, st.session_state.user_id):
                            st.success("Patient deleted successfully.")
                            # If we were viewing this patient, clear the selection
                            if 'selected_patient_id' in st.session_state and st.session_state.selected_patient_id == patient_to_delete:
                                del st.session_state.selected_patient_id
                            st.rerun()
                        else:
                            st.error("Failed to delete patient.")
        else:
            st.info("No patients to delete.")
