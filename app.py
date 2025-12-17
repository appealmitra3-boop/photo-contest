import hashlib
import json
import os
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image


# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")
PHOTOS_CSV = os.path.join(DATA_DIR, "photos.csv")
RATINGS_CSV = os.path.join(DATA_DIR, "ratings.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")

# Configuration
ADMIN_USERNAME = "alphabetagamma"  # Admin username for contest control
MAX_PHOTOS_PER_USER = 2  # Maximum photos a user can upload


def inject_css() -> None:
    """Light styling to make the UI feel more polished."""
    st.markdown(
        """
<style>
:root {
  --bg: #f5f7fb;
  --card: #ffffff;
  --border: #e5e7eb;
  --text: #0f172a;
  --muted: #475569;
  --accent: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
}
.stApp {
  background: radial-gradient(circle at 20% 20%, #eef1ff 0, rgba(238, 241, 255, 0) 35%),
              radial-gradient(circle at 80% 0%, #f0f7ff 0, rgba(240, 247, 255, 0) 30%),
              var(--bg);
}
.block-container {
  padding-top: 1.5rem;
  max-width: 1080px;
  margin: 0 auto;
}
.hero {
  background: linear-gradient(135deg, rgba(79,70,229,0.12) 0%, rgba(124,58,237,0.16) 60%, rgba(59,130,246,0.12) 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.8rem 2rem;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
  margin-bottom: 1.2rem;
  text-align: center;
}
.hero-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text);
}
.hero-sub {
  margin-top: 0.35rem;
  color: var(--muted);
}
.section-title {
  margin-top: 1.5rem;
  margin-bottom: 0.35rem;
  font-weight: 800;
  color: var(--text);
}
.section-note {
  color: var(--muted);
  margin-bottom: 0.65rem;
}
.photo-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 0.9rem;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}
.photo-title {
  font-weight: 700;
  color: var(--text);
  margin-top: 0.55rem;
}
.photo-meta {
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}
.stButton > button {
  background-image: var(--accent);
  color: #fff;
  border: none;
  padding: 0.55rem 0.8rem;
  border-radius: 10px;
  font-weight: 700;
  width: 100%;
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.25);
}
.stButton > button:disabled {
  background: #e2e8f0;
  color: #475569;
  box-shadow: none;
}
.stImage > img, .stImage img {
  border-radius: 12px;
  width: 100%;
  object-fit: cover;
}
</style>
""",
        unsafe_allow_html=True,
    )


def ensure_structure() -> None:
    """Create required folders and CSV files if missing."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    if not os.path.exists(PHOTOS_CSV):
        pd.DataFrame(columns=["photo_id", "title", "filename", "uploader", "uploaded_at"]).to_csv(
            PHOTOS_CSV, index=False
        )
    if not os.path.exists(RATINGS_CSV):
        pd.DataFrame(columns=["photo_id", "user_id", "rating"]).to_csv(RATINGS_CSV, index=False)
    
    if not os.path.exists(USERS_CSV):
        pd.DataFrame(columns=["username", "password_hash", "name", "employee_id", "designation"]).to_csv(
            USERS_CSV, index=False
        )
    
    # Initialize config file with default phase (Upload Phase = False, Voting not ended)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"voting_phase_enabled": False, "voting_ended": False}, f)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        photos_df = pd.read_csv(PHOTOS_CSV)
    except pd.errors.EmptyDataError:
        photos_df = pd.DataFrame(columns=["photo_id", "title", "filename", "uploader", "uploaded_at"])

    try:
        ratings_df = pd.read_csv(RATINGS_CSV)
    except pd.errors.EmptyDataError:
        ratings_df = pd.DataFrame(columns=["photo_id", "user_id", "rating"])

    return photos_df, ratings_df


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = "photo_contest_salt_2024"  # Simple salt for this application
    return hashlib.sha256((password + salt).encode()).hexdigest()


def load_users() -> pd.DataFrame:
    """Load users from CSV file."""
    try:
        return pd.read_csv(USERS_CSV)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["username", "password_hash", "name", "employee_id", "designation"])


def save_user(username: str, password: str, name: str, employee_id: str, designation: str) -> bool:
    """Register a new user. Returns True if successful, False if username already exists."""
    users_df = load_users()
    
    # Check if username already exists
    if not users_df.empty and username.lower() in users_df["username"].str.lower().values:
        return False
    
    # Create new user
    password_hash = hash_password(password)
    new_user = {
        "username": username.strip(),
        "password_hash": password_hash,
        "name": name.strip(),
        "employee_id": employee_id.strip(),
        "designation": designation.strip()
    }
    
    users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
    users_df.to_csv(USERS_CSV, index=False)
    return True


def authenticate_user(username: str, password: str) -> tuple[bool, dict]:
    """Authenticate a user. Returns (success, user_info_dict)."""
    users_df = load_users()
    
    if users_df.empty:
        return False, {}
    
    password_hash = hash_password(password)
    user = users_df[
        (users_df["username"].str.lower() == username.lower()) &
        (users_df["password_hash"] == password_hash)
    ]
    
    if user.empty:
        return False, {}
    
    return True, user.iloc[0].to_dict()


def get_user_photo_count(username: str) -> int:
    """Get the number of photos uploaded by a user."""
    photos_df, _ = load_data()
    if photos_df.empty:
        return 0
    return len(photos_df[photos_df["uploader"].str.lower() == username.lower()])


def save_photo(file, title: str, username: str) -> None:
    """Persist uploaded photo and metadata."""
    ext = os.path.splitext(file.name)[1].lower()
    photo_id = str(uuid.uuid4())
    filename = f"{photo_id}{ext}"
    file_path = os.path.join(PHOTOS_DIR, filename)

    image = Image.open(file).convert("RGB")
    image.save(file_path)

    photos_df, _ = load_data()
    new_row = {
        "photo_id": photo_id,
        "title": title.strip(),
        "filename": filename,
        "uploader": username.strip(),
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    photos_df = pd.concat([photos_df, pd.DataFrame([new_row])], ignore_index=True)
    photos_df.to_csv(PHOTOS_CSV, index=False)


def delete_photo(photo_id: str) -> None:
    """Delete a photo: remove file and database entries."""
    photos_df, ratings_df = load_data()
    
    # Find the photo to delete
    photo_row = photos_df[photos_df["photo_id"] == photo_id]
    if photo_row.empty:
        return
    
    # Delete the physical file
    filename = photo_row.iloc[0]["filename"]
    file_path = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass  # File might already be deleted
    
    # Remove photo from photos.csv
    photos_df = photos_df[photos_df["photo_id"] != photo_id]
    photos_df.to_csv(PHOTOS_CSV, index=False)
    
    # Remove all ratings for this photo from ratings.csv
    ratings_df = ratings_df[ratings_df["photo_id"] != photo_id]
    ratings_df.to_csv(RATINGS_CSV, index=False)


def save_rating(photo_id: str, user_id: str, rating: int) -> None:
    """Record a single vote per user overall; moving vote rewrites the record."""
    photos_df, ratings_df = load_data()
    if photo_id not in set(photos_df["photo_id"]):
        return

    # Remove any existing vote by this user (across all photos)
    ratings_df = ratings_df[ratings_df["user_id"] != user_id]

    # Insert the new vote
    ratings_df = pd.concat(
        [ratings_df, pd.DataFrame([{"photo_id": photo_id, "user_id": user_id, "rating": rating}])],
        ignore_index=True,
    )
    ratings_df.to_csv(RATINGS_CSV, index=False)


def get_config() -> dict:
    """Read config file and return as dictionary."""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return {
                "voting_phase_enabled": config.get("voting_phase_enabled", False),
                "voting_ended": config.get("voting_ended", False)
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {"voting_phase_enabled": False, "voting_ended": False}


def save_config(config: dict) -> None:
    """Write config dictionary to config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def get_voting_phase() -> bool:
    """Read voting phase state from config file."""
    return get_config()["voting_phase_enabled"]


def set_voting_phase(enabled: bool) -> None:
    """Write voting phase state to config file, preserving voting_ended status."""
    config = get_config()
    config["voting_phase_enabled"] = enabled
    # Reset voting_ended when switching back to upload phase
    if not enabled:
        config["voting_ended"] = False
    save_config(config)


def get_voting_ended() -> bool:
    """Check if voting has ended."""
    return get_config()["voting_ended"]


def set_voting_ended(ended: bool) -> None:
    """Set voting ended status in config file."""
    config = get_config()
    config["voting_ended"] = ended
    save_config(config)


def compute_leaderboard(show_uploader: bool = False) -> pd.DataFrame:
    """Compute leaderboard. Show uploader names only if show_uploader=True."""
    photos_df, ratings_df = load_data()
    if photos_df.empty:
        columns = ["rank", "title", "uploader", "votes"] if show_uploader else ["rank", "title", "votes"]
        return pd.DataFrame(columns=columns)

    agg = ratings_df.groupby("photo_id")["rating"].count().rename("votes")
    merged = photos_df.merge(agg, left_on="photo_id", right_index=True, how="left")
    merged["votes"] = merged["votes"].fillna(0).astype(int)
    merged = merged.sort_values(by=["votes", "uploaded_at"], ascending=[False, True]).reset_index(drop=True)
    merged.insert(0, "rank", range(1, len(merged) + 1))
    
    if show_uploader:
        return merged[["rank", "title", "uploader", "votes"]]
    else:
        return merged[["rank", "title", "votes"]]


def require_user() -> dict:
    """Handle user authentication (login/register) and return user info dict."""
    if "authenticated_user" not in st.session_state:
        st.session_state.authenticated_user = {}
    
    # If already authenticated, return user info
    if st.session_state.authenticated_user:
        return st.session_state.authenticated_user
    
    # Show login/register tabs
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        st.sidebar.header("Login")
        login_username = st.sidebar.text_input("Username", key="login_username")
        login_password = st.sidebar.text_input("Password", type="password", key="login_password")
        
        if st.sidebar.button("Login", key="login_btn"):
            if login_username and login_password:
                success, user_info = authenticate_user(login_username, login_password)
                if success:
                    st.session_state.authenticated_user = user_info
                    st.sidebar.success(f"Welcome, {user_info['name']}!")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid username or password.")
            else:
                st.sidebar.warning("Please enter both username and password.")
    
    with tab2:
        st.sidebar.header("Register")
        reg_username = st.sidebar.text_input("Username", key="reg_username")
        reg_password = st.sidebar.text_input("Password", type="password", key="reg_password")
        reg_name = st.sidebar.text_input("Full Name", key="reg_name")
        reg_employee_id = st.sidebar.text_input("Employee ID", key="reg_employee_id")
        reg_designation = st.sidebar.text_input("Designation", key="reg_designation")
        
        if st.sidebar.button("Register", key="register_btn"):
            if all([reg_username, reg_password, reg_name, reg_employee_id, reg_designation]):
                if save_user(reg_username, reg_password, reg_name, reg_employee_id, reg_designation):
                    st.sidebar.success("Registration successful! Please login.")
                else:
                    st.sidebar.error("Username already exists. Please choose a different username.")
            else:
                st.sidebar.warning("Please fill all fields.")
    
    return {}


def phase_toggle(username: str) -> bool:
    """Display phase toggle in sidebar and return current state. Only admin can toggle."""
    st.sidebar.divider()
    st.sidebar.header("Contest Control")
    
    current_phase = get_voting_phase()
    voting_ended = get_voting_ended()
    is_admin = username.lower() == ADMIN_USERNAME.lower()
    
    if voting_ended:
        phase_label = "Voting Ended - Results Available"
    elif current_phase:
        phase_label = "Voting Phase Active"
    else:
        phase_label = "Upload Phase Active"
    
    st.sidebar.markdown(f"**Status:** {phase_label}")
    
    # Only allow phase toggle if voting hasn't ended
    if not voting_ended:
        if is_admin:
            toggle_label = "Enable Voting Phase" if not current_phase else "Disable Voting Phase (Back to Upload)"
            new_phase = st.sidebar.toggle(toggle_label, value=current_phase, key="phase_toggle")
            
            if new_phase != current_phase:
                set_voting_phase(new_phase)
                st.sidebar.success(f"Switched to {'Voting' if new_phase else 'Upload'} Phase")
                st.rerun()
        else:
            st.sidebar.info(f"⚠️ Admin access required. Login as '{ADMIN_USERNAME}' to change phase.")
    else:
        st.sidebar.info("Voting has ended. Results are now visible.")
    
    return current_phase


def end_voting_button(username: str) -> None:
    """Display 'End Voting' button only for admin user."""
    voting_phase = get_voting_phase()
    voting_ended = get_voting_ended()
    
    # Only show button during voting phase and if voting hasn't ended
    if voting_phase and not voting_ended:
        st.sidebar.divider()
        st.sidebar.header("Admin Controls")
        
        # Check if user is admin
        is_admin = username.lower() == ADMIN_USERNAME.lower()
        
        if is_admin:
            if st.sidebar.button("🏁 End Voting", type="primary", use_container_width=True):
                set_voting_ended(True)
                st.sidebar.success("Voting has ended! Results are now visible.")
                st.rerun()
        else:
            st.sidebar.info(f"⚠️ Admin access required. Login as '{ADMIN_USERNAME}' to end voting.")


def reset_contest_button(username: str) -> None:
    """Display 'Reset Contest' button for admin to reset back to Upload Phase (for testing)."""
    voting_ended = get_voting_ended()
    is_admin = username.lower() == ADMIN_USERNAME.lower()
    
    # Only show reset button if voting has ended and user is admin
    if voting_ended and is_admin:
        st.sidebar.divider()
        st.sidebar.header("Admin Controls")
        if st.sidebar.button("🔄 Reset Contest (Back to Upload Phase)", type="secondary", use_container_width=True):
            config = get_config()
            config["voting_phase_enabled"] = False
            config["voting_ended"] = False
            save_config(config)
            st.sidebar.success("Contest reset! Back to Upload Phase.")
            st.rerun()


def upload_section(username: str) -> None:
    """Upload section - only shown during Upload Phase."""
    st.markdown('<div class="section-title">Upload a Photo</div>', unsafe_allow_html=True)
    
    # Check photo count
    photo_count = get_user_photo_count(username)
    remaining = MAX_PHOTOS_PER_USER - photo_count
    
    if remaining <= 0:
        st.warning(f"⚠️ You have reached the maximum upload limit of {MAX_PHOTOS_PER_USER} photos.")
        st.info(f"You have uploaded {photo_count} photo(s). Delete a photo to upload a new one.")
        return
    
    st.markdown(f'<div class="section-note">JPG or PNG, title required. You can upload {remaining} more photo(s). ({photo_count}/{MAX_PHOTOS_PER_USER} uploaded)</div>', unsafe_allow_html=True)
    
    # Use user-specific keys to prevent cross-user state persistence
    title_key = f"title_input_{username}"
    uploader_key = f"file_uploader_{username}"
    
    title = st.text_input("Photo Title", key=title_key)
    uploaded_file = st.file_uploader("Select a JPG or PNG image", type=["jpg", "jpeg", "png"], key=uploader_key)

    if st.button("Upload", key=f"upload_btn_{username}"):
        if not title.strip():
            st.warning("Title is required.")
            return
        if not uploaded_file:
            st.warning("Please choose a file.")
            return
        
        # Double-check photo count before uploading
        current_count = get_user_photo_count(username)
        if current_count >= MAX_PHOTOS_PER_USER:
            st.error(f"You have reached the maximum upload limit of {MAX_PHOTOS_PER_USER} photos.")
            return
        
        save_photo(uploaded_file, title, username)
        st.success(f"Photo '{title.strip()}' uploaded successfully!")
        # Clear the form after successful upload
        if title_key in st.session_state:
            del st.session_state[title_key]
        if uploader_key in st.session_state:
            del st.session_state[uploader_key]
        st.rerun()


def gallery_section(username: str = "") -> None:
    """Show gallery of uploaded photos (without uploader names) during Upload Phase."""
    photos_df, _ = load_data()
    is_admin = username.lower() == ADMIN_USERNAME.lower() if username else False
    
    if photos_df.empty:
        st.info("No photos uploaded yet.")
        return
    
    st.markdown('<div class="section-title">Uploaded Photos</div>', unsafe_allow_html=True)
    if is_admin:
        st.markdown('<div class="section-note">All submitted entries. Admin: Delete buttons are available below each photo.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-note">All submitted entries (uploader names hidden for anonymity).</div>', unsafe_allow_html=True)
    
    # Display in a simple grid (3 columns per row)
    cols_per_row = 3
    photo_rows = [
        photos_df.iloc[i : i + cols_per_row] for i in range(0, len(photos_df), cols_per_row)
    ]
    
    for row_df in photo_rows:
        cols = st.columns(len(row_df))
        for col, (_, row) in zip(cols, row_df.iterrows()):
            photo_id = row["photo_id"]
            file_path = os.path.join(PHOTOS_DIR, row["filename"])
            
            with col:
                st.markdown('<div class="photo-card">', unsafe_allow_html=True)
                if os.path.exists(file_path):
                    st.image(file_path, caption=None)
                else:
                    st.warning("Image file missing.")
                st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                
                # Show delete button for admin
                if is_admin:
                    if st.button("🗑️ Delete", key=f"delete-{photo_id}", use_container_width=True):
                        delete_photo(photo_id)
                        st.success(f"Photo '{row['title']}' deleted successfully.")
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)


def rating_section(username: str) -> None:
    """Voting section - only shown during Voting Phase, with anonymity."""
    st.markdown('<div class="section-title">Vote for Photos</div>', unsafe_allow_html=True)
    photos_df, ratings_df = load_data()
    is_admin = username.lower() == ADMIN_USERNAME.lower()

    if photos_df.empty:
        st.info("No photos available for voting.")
        return

    if is_admin:
        st.markdown(
            '<div class="section-note">See all entries and cast your single vote for the best photo. Uploader names are hidden to ensure fair voting. Admin: Delete buttons are available below each photo.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="section-note">See all entries and cast your single vote for the best photo. Uploader names are hidden to ensure fair voting.</div>',
            unsafe_allow_html=True,
        )

    # Determine current vote for this user (if any)
    user_vote = ratings_df[ratings_df["user_id"] == username]
    current_photo_id = user_vote["photo_id"].iloc[0] if not user_vote.empty else None

    # Display in a simple grid (3 columns per row)
    cols_per_row = 3
    photo_rows = [
        photos_df.iloc[i : i + cols_per_row] for i in range(0, len(photos_df), cols_per_row)
    ]

    for row_df in photo_rows:
        cols = st.columns(len(row_df))
        for col, (_, row) in zip(cols, row_df.iterrows()):
            photo_id = row["photo_id"]
            file_path = os.path.join(PHOTOS_DIR, row["filename"])

            with col:
                st.markdown('<div class="photo-card">', unsafe_allow_html=True)
                if os.path.exists(file_path):
                    st.image(file_path, caption=None)
                else:
                    st.warning("Image file missing.")
                st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                # Uploader name NOT displayed for anonymity

                is_current = current_photo_id == photo_id
                button_label = "You voted here" if is_current else "Move your vote here" if current_photo_id else "Vote for this photo"
                disabled = is_current

                if st.button(button_label, key=f"vote-{photo_id}", use_container_width=True, disabled=disabled):
                    save_rating(photo_id, username, 1)
                    st.success("Vote recorded." if not current_photo_id else "Vote moved.")
                    st.rerun()

                if is_current:
                    st.caption("Your current vote.")
                
                # Show delete button for admin
                if is_admin:
                    if st.button("🗑️ Delete", key=f"delete-vote-{photo_id}", use_container_width=True):
                        delete_photo(photo_id)
                        st.success(f"Photo '{row['title']}' deleted successfully.")
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)


def leaderboard_section(show_uploader: bool = False) -> None:
    """Display leaderboard. Show uploader names only if show_uploader=True."""
    st.markdown('<div class="section-title">Leaderboard</div>', unsafe_allow_html=True)
    lb = compute_leaderboard(show_uploader=show_uploader)
    if lb.empty:
        st.info("No entries yet.")
        return
    st.dataframe(lb, hide_index=True, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Photo Contest", page_icon="📸", layout="centered")
    inject_css()
    st.markdown(
        """
<div class="hero">
  <div class="hero-title">In-House Photo Contest</div>
  <div class="hero-sub">Temporary offline system for 2–3 days. Local-only, no cloud.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    ensure_structure()

    user_info = require_user()
    if not user_info:
        st.warning("Please login or register to continue.")
        return
    
    username = user_info.get("username", "")
    
    # Logout button
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.authenticated_user = {}
        st.rerun()

    # Get current phase from toggle (admin only)
    voting_phase = phase_toggle(username)
    
    # Show admin controls (End Voting button and Reset Contest button)
    end_voting_button(username)
    reset_contest_button(username)
    
    voting_ended = get_voting_ended()

    # Show appropriate sections based on phase
    if voting_ended:
        # Voting has ended: Show final results with uploader names
        st.success("🏆 **Voting Has Ended** - Final results are now available!")
        st.divider()
        leaderboard_section(show_uploader=True)
    elif voting_phase:
        # Voting Phase: Show voting, hide leaderboard (results hidden during voting)
        st.info("📊 **Voting Phase Active** - Uploading is disabled. You can now vote for your favorite photos. Results are hidden until voting ends.")
        st.divider()
        rating_section(username)
        # Leaderboard is HIDDEN during voting to prevent influence
    else:
        # Upload Phase: Show upload and gallery, hide voting and leaderboard
        st.info("📤 **Upload Phase Active** - Upload your photos. Voting will begin after the admin enables voting phase.")
        st.divider()
        upload_section(username)
        st.divider()
        gallery_section(username)
        # Leaderboard is HIDDEN during upload phase


if __name__ == "__main__":
    main()

