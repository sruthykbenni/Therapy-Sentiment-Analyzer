import streamlit as st
import hashlib
import secrets
import string


def generate_salt():
    """Generate a random salt for password hashing."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(16))


def hash_password(password, salt=None):
    """Hash a password with a salt using SHA-256."""
    if salt is None:
        salt = generate_salt()

    # Combine password and salt, then hash
    hash_obj = hashlib.sha256((password + salt).encode())
    password_hash = hash_obj.hexdigest()

    # Return both the hash and the salt
    return f"{salt}${password_hash}"


def verify_password(stored_hash, provided_password):
    """Verify a password against a stored hash."""
    # Extract salt from the stored hash
    salt, hash_value = stored_hash.split('$')

    # Hash the provided password with the same salt
    hash_obj = hashlib.sha256((provided_password + salt).encode())
    calculated_hash = hash_obj.hexdigest()

    # Compare the calculated hash with the stored hash
    return hash_value == calculated_hash


def login_user(db):
    """Handle user login process."""
    st.title("MindScribe Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        if not username or not password:
            st.error("Please provide both username and password.")
            return None

        therapist = db.get_therapist_by_username(username)

        if not therapist:
            st.error("Username not found.")
            return None

        if not verify_password(therapist['password_hash'], password):
            st.error("Incorrect password.")
            return None

        # Set session state for the logged in user
        st.session_state.user_id = therapist['id']
        st.session_state.username = therapist['username']
        st.session_state.user_name = therapist['name']

        # Force a rerun to refresh the page
        st.rerun()

        return therapist

    return None


def signup_user(db):
    """Handle user signup process."""
    st.title("Create MindScribe Account")

    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        submit_button = st.form_submit_button("Sign Up")

    if submit_button:
        # Validate inputs
        if not username or not password or not name or not email:
            st.error("All fields are required.")
            return False

        if password != confirm_password:
            st.error("Passwords don't match.")
            return False

        # Check if username already exists
        existing_user = db.get_therapist_by_username(username)
        if existing_user:
            st.error("Username already exists. Please choose another one.")
            return False

        # Hash password and create user
        password_hash = hash_password(password)
        user_id = db.add_therapist(username, password_hash, name, email)

        if user_id:
            st.success("Account created successfully! Please login.")
            return True
        else:
            st.error("Failed to create account. Username or email may already be in use.")
            return False

    return False


def logout_user():
    """Log out the current user."""
    for key in ['user_id', 'username', 'user_name']:
        if key in st.session_state:
            del st.session_state[key]

    # Force a rerun to refresh the page
    st.rerun()


def is_authenticated():
    """Check if a user is currently authenticated."""
    return 'user_id' in st.session_state


def authentication_required(func):
    """Decorator to ensure a user is authenticated before accessing a page."""

    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.error("Please login to access this page.")
            return None
        return func(*args, **kwargs)

    return wrapper