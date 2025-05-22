import sqlite3
import os
import json
from datetime import datetime
import pandas as pd


class Database:
    def __init__(self, db_path="database.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = None
        self.create_tables()

    def get_connection(self):
        """Get SQLite connection, creating it if needed."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create therapists table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS therapists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create patients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            therapist_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (therapist_id) REFERENCES therapists(id)
        )
        ''')

        # Create session_notes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            therapist_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            emotions TEXT NOT NULL,  -- JSON string of emotion data
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (therapist_id) REFERENCES therapists(id)
        )
        ''')

        conn.commit()

    def add_therapist(self, username, password_hash, name, email):
        """Add a new therapist to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO therapists (username, password_hash, name, email) VALUES (?, ?, ?, ?)",
                (username, password_hash, name, email)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Username or email already exists

    def get_therapist_by_username(self, username):
        """Get therapist data by username."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM therapists WHERE username = ?", (username,))
        therapist = cursor.fetchone()

        if therapist:
            return dict(therapist)
        return None

    def add_patient(self, therapist_id, name, age=None, gender=None, contact=None, notes=None):
        """Add a new patient for a therapist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO patients (therapist_id, name, age, gender, contact, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (therapist_id, name, age, gender, contact, notes)
        )
        conn.commit()
        return cursor.lastrowid

    def get_patients(self, therapist_id):
        """Get all patients for a therapist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM patients WHERE therapist_id = ? ORDER BY name", (therapist_id,))
        patients = cursor.fetchall()

        return [dict(patient) for patient in patients]

    def get_patient(self, patient_id, therapist_id):
        """Get a specific patient with validation for the therapist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM patients WHERE id = ? AND therapist_id = ?",
            (patient_id, therapist_id)
        )
        patient = cursor.fetchone()

        if patient:
            return dict(patient)
        return None

    def update_patient(self, patient_id, therapist_id, name, age=None, gender=None, contact=None, notes=None):
        """Update patient information."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """UPDATE patients 
               SET name = ?, age = ?, gender = ?, contact = ?, notes = ?
               WHERE id = ? AND therapist_id = ?""",
            (name, age, gender, contact, notes, patient_id, therapist_id)
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete_patient(self, patient_id, therapist_id):
        """Delete a patient and all related session notes."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # First delete associated session notes
        cursor.execute(
            "DELETE FROM session_notes WHERE patient_id = ? AND therapist_id = ?",
            (patient_id, therapist_id)
        )

        # Then delete the patient
        cursor.execute(
            "DELETE FROM patients WHERE id = ? AND therapist_id = ?",
            (patient_id, therapist_id)
        )

        conn.commit()
        return cursor.rowcount > 0

    def add_session_note(self, patient_id, therapist_id, note_text, emotions):
        """Add a new session note with emotion analysis results."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Convert emotions dict to JSON string
        emotions_json = json.dumps(emotions)

        cursor.execute(
            "INSERT INTO session_notes (patient_id, therapist_id, note_text, emotions) VALUES (?, ?, ?, ?)",
            (patient_id, therapist_id, note_text, emotions_json)
        )
        conn.commit()
        return cursor.lastrowid

    def get_session_notes(self, patient_id, therapist_id):
        """Get all session notes for a specific patient."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT * FROM session_notes 
               WHERE patient_id = ? AND therapist_id = ?
               ORDER BY timestamp DESC""",
            (patient_id, therapist_id)
        )
        notes = cursor.fetchall()

        result = []
        for note in notes:
            note_dict = dict(note)
            note_dict['emotions'] = json.loads(note_dict['emotions'])
            result.append(note_dict)

        return result

    def get_emotions_dataframe(self, patient_id, therapist_id):
        """Get emotion data as a pandas DataFrame for visualization."""
        notes = self.get_session_notes(patient_id, therapist_id)

        if not notes:
            return pd.DataFrame()

        data = []
        for note in notes:
            timestamp = note['timestamp']
            emotions = note['emotions']

            # Find the emotion with highest score
            dominant_emotion = max(emotions, key=lambda x: emotions[x])

            row = {
                'timestamp': timestamp,
                'dominant_emotion': dominant_emotion
            }
            # Add individual emotion scores
            for emotion, score in emotions.items():
                row[emotion] = score

            data.append(row)

        df = pd.DataFrame(data)

        # Convert timestamp strings to datetime objects
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')

        return df

    def export_patient_data_to_csv(self, patient_id, therapist_id):
        """Export all data for a patient to a CSV file."""
        patient = self.get_patient(patient_id, therapist_id)
        if not patient:
            return None

        notes = self.get_session_notes(patient_id, therapist_id)

        # Create a DataFrame for the session notes
        rows = []
        for note in notes:
            emotions = note['emotions']
            dominant_emotion = max(emotions, key=lambda x: emotions[x])

            row = {
                'Date': note['timestamp'],
                'Note': note['note_text'],
                'Dominant Emotion': dominant_emotion
            }
            # Add individual emotion scores
            for emotion, score in emotions.items():
                row[f"Score: {emotion}"] = score

            rows.append(row)

        notes_df = pd.DataFrame(rows)

        # Create a filename with patient name and timestamp
        safe_name = "".join([c if c.isalnum() else "_" for c in patient['name']])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_records_{timestamp}.csv"

        # Save to CSV
        if not notes_df.empty:
            notes_df.to_csv(filename, index=False)
            return filename
        return None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None