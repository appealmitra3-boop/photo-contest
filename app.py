import base64
import hashlib
import io
import json
import os
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image

# Try to import Cloudinary, but allow app to work without it
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False


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
THEMES = [
    "Happy Department is an Efficient Department",
    "New Income Tax Act",
]


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
  padding-top: 1rem;
  max-width: 1080px;
  margin: 0 auto;
}
/* Main page title styling */
.main-page-title {
  text-align: center;
  margin: 1rem 0 1.5rem 0;
  padding: 1.5rem 0;
  border-bottom: 3px solid #4f46e5;
}
.main-page-title h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  padding: 0;
}
.main-page-title h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #475569;
  margin: 0.5rem 0 0 0;
  padding: 0;
}
/* Hide empty containers that might appear at top - but NOT ones with content */
.block-container > div:first-child:empty:not(:has(.main-page-title)),
.block-container > div:empty:first-of-type:not(:has(.main-page-title)),
div[data-testid]:empty:not(:has(.main-page-title)),
.element-container:empty:not(:has(.main-page-title)),
.stMarkdown:empty:not(:has(.main-page-title)) {
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  visibility: hidden !important;
}
/* Hide empty column containers */
div[data-testid="column"]:empty,
div[data-testid="column"]:has(> div:empty:only-child),
div[data-testid="column"]:not(:has(*)) {
  display: none !important;
  height: 0 !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  visibility: hidden !important;
}
/* Hide empty Streamlit containers that appear as boxes */
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:empty:only-child),
div[data-testid="element-container"]:empty,
div[data-testid="stVerticalBlock"]:has(> div:empty:only-child),
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:empty) {
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}
/* Hide any empty containers with borders that might appear as boxes */
div[style*="border"]:empty,
div[class*="photo-card"]:empty {
  display: none !important;
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
/* Style Photo Title input and Theme dropdown with purple borders */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select {
  border: 2px solid #4f46e5 !important;
  border-radius: 8px !important;
  padding: 0.5rem 0.75rem !important;
  transition: border-color 0.2s ease !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stSelectbox"] select:focus {
  border-color: #7c3aed !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
}
div[data-testid="stTextInput"] input:hover,
div[data-testid="stSelectbox"] select:hover {
  border-color: #6366f1 !important;
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
        pd.DataFrame(
            columns=[
                "photo_id",
                "title",
                "filename",
                "uploader",
                "uploaded_at",
                "status",
                "rejection_reason",
                "theme",
            ]
        ).to_csv(PHOTOS_CSV, index=False)
    if not os.path.exists(RATINGS_CSV):
        pd.DataFrame(columns=["photo_id", "user_id", "rating"]).to_csv(RATINGS_CSV, index=False)
    
    if not os.path.exists(USERS_CSV):
        pd.DataFrame(columns=["employee_id", "name", "posting_details", "is_admin"]).to_csv(
            USERS_CSV, index=False
        )
    
    # Initialize config file with default phase (Upload Phase = False, Voting not ended)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"voting_phase_enabled": False, "voting_ended": False}, f)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        photos_df = pd.read_csv(PHOTOS_CSV)
        # Ensure cloudinary_url and image_base64 columns exist for backward compatibility
        if "cloudinary_url" not in photos_df.columns:
            photos_df["cloudinary_url"] = None
        if "image_base64" not in photos_df.columns:
            photos_df["image_base64"] = None
        # Ensure status and rejection_reason columns exist for moderation
        if "status" not in photos_df.columns:
            photos_df["status"] = "approved"  # Set existing photos as approved for backward compatibility
        if "rejection_reason" not in photos_df.columns:
            photos_df["rejection_reason"] = None
        # Ensure theme column exists
        if "theme" not in photos_df.columns:
            photos_df["theme"] = "Unspecified"
    except pd.errors.EmptyDataError:
        photos_df = pd.DataFrame(
            columns=[
                "photo_id",
                "title",
                "filename",
                "uploader",
                "uploaded_at",
                "cloudinary_url",
                "image_base64",
                "status",
                "rejection_reason",
                "theme",
            ]
        )

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
        return pd.DataFrame(columns=["employee_id", "name", "posting_details", "is_admin"])


def login_or_create_user(employee_id: str, name: str, posting_details: str) -> tuple[bool, dict]:
    """Login or auto-create user. Returns (success, user_info_dict)."""
    users_df = load_users()
    employee_id = employee_id.strip().upper()
    name = name.strip()
    posting_details = posting_details.strip()
    
    # Check if user exists
    if not users_df.empty:
        # Convert employee_id column to string and handle NaN values
        users_df["employee_id"] = users_df["employee_id"].astype(str).replace("nan", "")
        user = users_df[users_df["employee_id"].str.upper() == employee_id]
        if not user.empty:
            # User exists, update info if changed
            user_info = user.iloc[0].to_dict()
            user_info["name"] = name
            user_info["posting_details"] = posting_details
            # Update in dataframe
            users_df.loc[users_df["employee_id"].str.upper() == employee_id, "name"] = name
            users_df.loc[users_df["employee_id"].str.upper() == employee_id, "posting_details"] = posting_details
            users_df.to_csv(USERS_CSV, index=False)
            return True, user_info
    
    # User doesn't exist, create new user
    new_user = {
        "employee_id": employee_id,
        "name": name,
        "posting_details": posting_details,
        "is_admin": False
    }
    
    users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
    users_df.to_csv(USERS_CSV, index=False)
    return True, new_user


def authenticate_admin(username: str, password: str) -> tuple[bool, dict]:
    """Authenticate admin user. Returns (success, user_info_dict)."""
    users_df = load_users()
    
    # Convert employee_id column to string and handle NaN values
    if not users_df.empty:
        users_df["employee_id"] = users_df["employee_id"].astype(str).replace("nan", "")
    
    # Check if admin user exists, if not create it
    admin_user = users_df[users_df["employee_id"].str.upper() == ADMIN_USERNAME.upper()] if not users_df.empty else pd.DataFrame()
    
    if admin_user.empty:
        # Create admin user if doesn't exist
        new_admin = {
            "employee_id": ADMIN_USERNAME.upper(),
            "name": "Admin User",
            "posting_details": "Administrator",
            "is_admin": True
        }
        users_df = pd.concat([users_df, pd.DataFrame([new_admin])], ignore_index=True)
        users_df.to_csv(USERS_CSV, index=False)
        return True, new_admin
    
    admin_info = admin_user.iloc[0].to_dict()
    
    # Simple admin authentication - username must match ADMIN_USERNAME
    # Password check can be enhanced later if needed
    if username.upper() == ADMIN_USERNAME.upper():
        admin_info["is_admin"] = True
        return True, admin_info
    
    return False, {}


def get_user_photo_count(employee_id: str) -> int:
    """Get the number of photos uploaded by a user."""
    photos_df, _ = load_data()
    if photos_df.empty or "uploader" not in photos_df.columns:
        return 0
    
    # Convert uploader column to string and handle NaN values
    photos_df["uploader"] = photos_df["uploader"].astype(str)
    # Filter out 'nan' strings
    photos_df = photos_df[photos_df["uploader"] != "nan"]
    # Exclude rejected photos from count so users can re-upload if rejected
    if "status" in photos_df.columns:
        photos_df = photos_df[photos_df["status"] != "rejected"]
    
    return len(photos_df[photos_df["uploader"].str.upper() == employee_id.upper()])


def is_cloudinary_configured() -> bool:
    """Check if Cloudinary is configured via Streamlit secrets."""
    if not CLOUDINARY_AVAILABLE:
        return False
    try:
        secrets = st.secrets.get("cloudinary", {})
        return bool(secrets.get("cloud_name") and secrets.get("api_key") and secrets.get("api_secret"))
    except Exception:
        return False


def init_cloudinary() -> None:
    """Initialize Cloudinary with credentials from Streamlit secrets."""
    if not CLOUDINARY_AVAILABLE or not is_cloudinary_configured():
        return
    try:
        secrets = st.secrets.get("cloudinary", {})
        cloudinary.config(
            cloud_name=secrets.get("cloud_name"),
            api_key=secrets.get("api_key"),
            api_secret=secrets.get("api_secret"),
            secure=True
        )
    except Exception:
        pass


def get_photo_image(photo_row: pd.Series) -> Image.Image | None:
    """Get photo image from Cloudinary (preferred), base64, or local file (fallback)."""
    photo_id = photo_row.get("photo_id", "")
    
    # Try Cloudinary first (best for cloud deployment)
    if CLOUDINARY_AVAILABLE and is_cloudinary_configured() and photo_id:
        try:
            init_cloudinary()
            # Check if cloudinary_url exists in the row
            if "cloudinary_url" in photo_row and pd.notna(photo_row["cloudinary_url"]) and photo_row["cloudinary_url"]:
                import requests
                response = requests.get(photo_row["cloudinary_url"], timeout=10)
                if response.status_code == 200:
                    return Image.open(io.BytesIO(response.content))
        except Exception:
            pass
    
    # Try base64 (for backward compatibility)
    if "image_base64" in photo_row and pd.notna(photo_row["image_base64"]) and photo_row["image_base64"]:
        try:
            image_data = base64.b64decode(photo_row["image_base64"])
            return Image.open(io.BytesIO(image_data))
        except Exception:
            pass
    
    # Fallback to local file
    file_path = os.path.join(PHOTOS_DIR, photo_row.get("filename", ""))
    if file_path and os.path.exists(file_path):
        try:
            return Image.open(file_path)
        except Exception:
            pass
    
    return None


def save_photo(file, title: str, employee_id: str, theme: str) -> None:
    """Persist uploaded photo and metadata. Upload to Cloudinary if configured, else use base64."""
    ext = os.path.splitext(file.name)[1].lower()
    photo_id = str(uuid.uuid4())
    filename = f"{photo_id}{ext}"
    file_path = os.path.join(PHOTOS_DIR, filename)

    image = Image.open(file).convert("RGB")
    
    # Save locally (for backward compatibility)
    image.save(file_path)
    
    cloudinary_url = None
    
    # Upload to Cloudinary if configured (best for cloud deployment)
    if CLOUDINARY_AVAILABLE and is_cloudinary_configured():
        try:
            init_cloudinary()
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            
            upload_result = cloudinary.uploader.upload(
                buffer,
                public_id=f"photo_contest/{photo_id}",
                folder="photo_contest",
                resource_type="image"
            )
            cloudinary_url = upload_result.get("secure_url") or upload_result.get("url")
        except Exception as e:
            # If Cloudinary upload fails, fall back to base64
            pass
    
    # Store as base64 if Cloudinary not configured or upload failed
    image_base64 = None
    if not cloudinary_url:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    photos_df, _ = load_data()
    new_row = {
        "photo_id": photo_id,
        "title": title.strip(),
        "filename": filename,
        "uploader": employee_id.strip().upper(),
        "uploaded_at": datetime.utcnow().isoformat(),
        "cloudinary_url": cloudinary_url,  # Cloudinary URL if available
        "image_base64": image_base64,  # Base64 fallback if Cloudinary not used
        "status": "pending",  # New photos start as pending approval
        "rejection_reason": None,  # Rejection reason if rejected
        "theme": theme,
    }
    photos_df = pd.concat([photos_df, pd.DataFrame([new_row])], ignore_index=True)
    photos_df.to_csv(PHOTOS_CSV, index=False)


def approve_photo(photo_id: str) -> None:
    """Approve a pending photo, making it visible to all users."""
    photos_df, _ = load_data()
    photos_df.loc[photos_df["photo_id"] == photo_id, "status"] = "approved"
    photos_df.loc[photos_df["photo_id"] == photo_id, "rejection_reason"] = None
    photos_df.to_csv(PHOTOS_CSV, index=False)


def reject_photo(photo_id: str, reason: str = "") -> None:
    """Reject a pending photo, keeping it hidden from other users."""
    photos_df, _ = load_data()
    photos_df.loc[photos_df["photo_id"] == photo_id, "status"] = "rejected"
    photos_df.loc[photos_df["photo_id"] == photo_id, "rejection_reason"] = reason if reason else None
    photos_df.to_csv(PHOTOS_CSV, index=False)


def delete_photo(photo_id: str) -> None:
    """Delete a photo: remove from Cloudinary, local file, and database entries."""
    photos_df, ratings_df = load_data()
    
    # Find the photo to delete
    photo_row = photos_df[photos_df["photo_id"] == photo_id]
    if photo_row.empty:
        return
    
    photo_data = photo_row.iloc[0]
    
    # Delete from Cloudinary if configured
    if CLOUDINARY_AVAILABLE and is_cloudinary_configured():
        try:
            init_cloudinary()
            cloudinary_url = photo_data.get("cloudinary_url")
            if cloudinary_url and pd.notna(cloudinary_url):
                # Extract public_id from URL or use photo_id
                public_id = f"photo_contest/{photo_id}"
                cloudinary.uploader.destroy(public_id, resource_type="image")
        except Exception:
            pass  # Continue even if Cloudinary delete fails
    
    # Delete the physical file
    filename = photo_data.get("filename")
    if filename:
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
    """Compute leaderboard. Show uploader names only if show_uploader=True. Only includes approved photos."""
    photos_df, ratings_df = load_data()
    
    # Filter to only approved photos
    approved_df = photos_df[photos_df["status"] == "approved"].copy()
    
    if approved_df.empty:
        columns = ["rank", "title", "uploader", "votes"] if show_uploader else ["rank", "title", "votes"]
        return pd.DataFrame(columns=columns)

    agg = ratings_df.groupby("photo_id")["rating"].count().rename("votes")
    merged = approved_df.merge(agg, left_on="photo_id", right_index=True, how="left")
    merged["votes"] = merged["votes"].fillna(0).astype(int)
    merged = merged.sort_values(by=["votes", "uploaded_at"], ascending=[False, True]).reset_index(drop=True)
    merged.insert(0, "rank", range(1, len(merged) + 1))
    
    if show_uploader:
        return merged[["rank", "title", "uploader", "votes"]]
    else:
        return merged[["rank", "title", "votes"]]


def require_user() -> dict:
    """Handle user authentication (simplified login) and return user info dict."""
    if "authenticated_user" not in st.session_state:
        st.session_state.authenticated_user = {}
    
    # If already authenticated, return user info
    if st.session_state.authenticated_user:
        return st.session_state.authenticated_user
    
    # Show login/admin tabs
    tab1, tab2 = st.sidebar.tabs(["Login", "Admin Login"])
    
    with tab1:
        st.sidebar.header("Login")
        login_name = st.sidebar.text_input("Name", key="login_name")
        login_employee_id = st.sidebar.text_input("Employee ID", key="login_employee_id")
        login_posting = st.sidebar.text_input("Posting Details", key="login_posting")
        
        if st.sidebar.button("Login", key="login_btn"):
            if login_name and login_employee_id and login_posting:
                success, user_info = login_or_create_user(login_employee_id, login_name, login_posting)
                if success:
                    st.session_state.authenticated_user = user_info
                    st.sidebar.success(f"Welcome, {user_info['name']}!")
                    st.rerun()
                else:
                    st.sidebar.error("Login failed. Please try again.")
            else:
                st.sidebar.warning("Please fill all fields.")
    
    with tab2:
        st.sidebar.header("Admin Login")
        admin_username = st.sidebar.text_input("Admin Username", key="admin_username")
        admin_password = st.sidebar.text_input("Admin Password", type="password", key="admin_password")
        
        if st.sidebar.button("Admin Login", key="admin_login_btn"):
            if admin_username and admin_password:
                success, user_info = authenticate_admin(admin_username, admin_password)
                if success:
                    st.session_state.authenticated_user = user_info
                    st.sidebar.success(f"Welcome, Admin!")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid admin credentials.")
            else:
                st.sidebar.warning("Please enter admin username and password.")
    
    return {}


def phase_toggle(employee_id: str) -> bool:
    """Display phase toggle in sidebar and return current state. Only admin can toggle."""
    st.sidebar.divider()
    st.sidebar.header("Contest Control")
    
    current_phase = get_voting_phase()
    voting_ended = get_voting_ended()
    is_admin = employee_id.upper() == ADMIN_USERNAME.upper() if employee_id else False
    
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


def end_voting_button(employee_id: str) -> None:
    """Display 'End Voting' button only for admin user."""
    voting_phase = get_voting_phase()
    voting_ended = get_voting_ended()
    
    # Only show button during voting phase and if voting hasn't ended
    if voting_phase and not voting_ended:
        st.sidebar.divider()
        st.sidebar.header("Admin Controls")
        
        # Check if user is admin
        is_admin = employee_id.upper() == ADMIN_USERNAME.upper()
        
        if is_admin:
            if st.sidebar.button("🏁 End Voting", type="primary", use_container_width=True):
                set_voting_ended(True)
                st.sidebar.success("Voting has ended! Results are now visible.")
                st.rerun()
        else:
            st.sidebar.info(f"⚠️ Admin access required. Login as '{ADMIN_USERNAME}' to end voting.")


def reset_contest_button(employee_id: str) -> None:
    """Display 'Reset Contest' button for admin to reset back to Upload Phase (for testing)."""
    voting_ended = get_voting_ended()
    is_admin = employee_id.upper() == ADMIN_USERNAME.upper()
    
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


def moderation_section(employee_id: str) -> None:
    """Admin-only section to review and approve/reject pending photos."""
    photos_df, _ = load_data()
    
    # Get pending photos
    pending_df = photos_df[photos_df["status"] == "pending"].copy()
    rejected_df = photos_df[photos_df["status"] == "rejected"].copy()
    pending_df["theme"] = pending_df.get("theme", "Unspecified").fillna("Unspecified")
    rejected_df["theme"] = rejected_df.get("theme", "Unspecified").fillna("Unspecified")
    
    st.markdown('<div class="section-title">📋 Photo Moderation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Review and approve/reject uploaded photos. Only approved photos are visible to other users.</div>', unsafe_allow_html=True)
    
    # Show pending photos
    if pending_df.empty:
        st.success("✅ No pending photos. All photos have been reviewed.")
    else:
        st.subheader(f"⏳ Pending Review ({len(pending_df)} photo(s))")
        theme_groups = THEMES + ["Other/Unspecified"]
        for theme in theme_groups:
            if theme == "Other/Unspecified":
                theme_df = pending_df[~pending_df["theme"].isin(THEMES)]
                display_name = "Other / Unspecified"
            else:
                theme_df = pending_df[pending_df["theme"] == theme]
                display_name = theme
            if theme_df.empty:
                continue
            
            st.markdown(f"**Theme: {display_name} ({len(theme_df)} pending)**")
            cols_per_row = 2
            pending_rows = [
                theme_df.iloc[i : i + cols_per_row] for i in range(0, len(theme_df), cols_per_row)
            ]
            
            for row_df in pending_rows:
                # Only create columns for actual photos to avoid empty containers
                num_photos = len(row_df)
                cols = st.columns(num_photos)
                for idx, (col, (_, row)) in enumerate(zip(cols, row_df.iterrows())):
                    photo_id = row["photo_id"]
                    
                    with col:
                        st.markdown('<div class="photo-card" style="border: 2px solid #f59e0b;">', unsafe_allow_html=True)
                        photo_image = get_photo_image(row)
                        if photo_image:
                            st.image(photo_image, caption=None)
                        else:
                            st.warning("Image file missing.")
                        
                        st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                        st.caption(f"Theme: {row.get('theme', 'Unspecified')}")
                        
                        # Show uploader info for admin
                        uploader_id = row.get("uploader", "Unknown")
                        users_df = load_users()
                        uploader_info = users_df[users_df["employee_id"].astype(str).str.upper() == uploader_id.upper()]
                        if not uploader_info.empty:
                            uploader_name = uploader_info.iloc[0].get("name", "Unknown")
                            st.caption(f"Uploaded by: {uploader_name} ({uploader_id})")
                        
                        col_approve, col_reject = st.columns(2)
                        with col_approve:
                            if st.button("✅ Approve", key=f"approve-{photo_id}", use_container_width=True, type="primary"):
                                approve_photo(photo_id)
                                st.success(f"Photo '{row['title']}' approved!")
                                st.rerun()
                        
                        with col_reject:
                            if st.button("❌ Reject", key=f"reject-{photo_id}", use_container_width=True):
                                reject_photo(photo_id, "Rejected by admin")
                                st.info(f"Photo '{row['title']}' rejected.")
                                st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
    
    # Show rejected photos (optional - admin can see what was rejected)
    if not rejected_df.empty:
        with st.expander(f"❌ Rejected Photos ({len(rejected_df)})"):
            theme_groups = THEMES + ["Other/Unspecified"]
            for theme in theme_groups:
                if theme == "Other/Unspecified":
                    theme_df = rejected_df[~rejected_df["theme"].isin(THEMES)]
                    display_name = "Other / Unspecified"
                else:
                    theme_df = rejected_df[rejected_df["theme"] == theme]
                    display_name = theme
                if theme_df.empty:
                    continue
                
                st.markdown(f"**Theme: {display_name} ({len(theme_df)} rejected)**")
                cols_per_row = 2
                rejected_rows = [
                    theme_df.iloc[i : i + cols_per_row] for i in range(0, len(theme_df), cols_per_row)
                ]
                
                for row_df in rejected_rows:
                    # Only create columns for actual photos to avoid empty containers
                    num_photos = len(row_df)
                    cols = st.columns(num_photos)
                    for idx, (col, (_, row)) in enumerate(zip(cols, row_df.iterrows())):
                        photo_id = row["photo_id"]
                        
                        with col:
                            st.markdown('<div class="photo-card" style="border: 2px solid #ef4444; opacity: 0.7;">', unsafe_allow_html=True)
                            photo_image = get_photo_image(row)
                            if photo_image:
                                st.image(photo_image, caption=None)
                            else:
                                st.warning("Image file missing.")
                            
                            st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                            st.caption(f"Theme: {row.get('theme', 'Unspecified')}")
                            st.caption(f"Status: ❌ Rejected")
                            
                            if st.button("✅ Approve", key=f"approve-rejected-{photo_id}", use_container_width=True):
                                approve_photo(photo_id)
                                st.success(f"Photo '{row['title']}' approved!")
                                st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)


def upload_section(employee_id: str) -> None:
    """Upload section - only shown during Upload Phase."""
    st.markdown('<div class="section-title">Upload a Photo</div>', unsafe_allow_html=True)
    
    # Show user's own photos with status
    photos_df, _ = load_data()
    user_photos = photos_df[photos_df["uploader"].astype(str).str.upper() == employee_id.upper()].copy()
    
    if not user_photos.empty:
        st.markdown("### Your Uploaded Photos")
        cols_per_row = 3
        user_photo_rows = [
            user_photos.iloc[i : i + cols_per_row] for i in range(0, len(user_photos), cols_per_row)
        ]
        
        for row_df in user_photo_rows:
            cols = st.columns(len(row_df))
            for col, (_, row) in zip(cols, row_df.iterrows()):
                with col:
                    st.markdown('<div class="photo-card">', unsafe_allow_html=True)
                    photo_image = get_photo_image(row)
                    if photo_image:
                        st.image(photo_image, caption=None, use_container_width=True)
                    st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                    st.caption(f"Theme: {row.get('theme', 'Unspecified')}")
                    
                    # Show status badge
                    status = row.get("status", "approved")
                    if status == "pending":
                        st.markdown('<div style="color: #f59e0b; font-weight: bold; margin: 0.5rem 0;">⏳ Pending Review</div>', unsafe_allow_html=True)
                        st.caption("Waiting for admin approval")
                    elif status == "approved":
                        st.markdown('<div style="color: #10b981; font-weight: bold; margin: 0.5rem 0;">✅ Approved</div>', unsafe_allow_html=True)
                        st.caption("Visible to all users")
                    elif status == "rejected":
                        st.markdown('<div style="color: #ef4444; font-weight: bold; margin: 0.5rem 0;">❌ Rejected</div>', unsafe_allow_html=True)
                        rejection_reason = row.get("rejection_reason", "")
                        if rejection_reason:
                            st.caption(f"Reason: {rejection_reason}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
    
    # Check photo count
    photo_count = get_user_photo_count(employee_id)
    remaining = MAX_PHOTOS_PER_USER - photo_count
    
    if remaining <= 0:
        st.warning(f"⚠️ You have reached the maximum upload limit of {MAX_PHOTOS_PER_USER} photos.")
        st.info(f"You have uploaded {photo_count} photo(s). Delete a photo to upload a new one.")
        return
    
    st.markdown(f'<div class="section-note">JPG or PNG, title required. You can upload {remaining} more photo(s). ({photo_count}/{MAX_PHOTOS_PER_USER} uploaded)</div>', unsafe_allow_html=True)
    
    # Use user-specific keys to prevent cross-user state persistence
    title_key = f"title_input_{employee_id}"
    uploader_key = f"file_uploader_{employee_id}"
    theme_key = f"theme_select_{employee_id}"
    
    title = st.text_input("Photo Title", key=title_key)
    theme = st.selectbox("Select Theme", THEMES, index=0, key=theme_key)
    uploaded_file = st.file_uploader("Select a JPG or PNG image", type=["jpg", "jpeg", "png"], key=uploader_key)

    if st.button("Upload", key=f"upload_btn_{employee_id}"):
        if not title.strip():
            st.warning("Title is required.")
            return
        if not theme:
            st.warning("Please select a theme.")
            return
        if not uploaded_file:
            st.warning("Please choose a file.")
            return
        
        # Double-check photo count before uploading
        current_count = get_user_photo_count(employee_id)
        if current_count >= MAX_PHOTOS_PER_USER:
            st.error(f"You have reached the maximum upload limit of {MAX_PHOTOS_PER_USER} photos.")
            return
        
        # Enforce one photo per theme (pending/approved count; rejected can be replaced)
        user_photos = photos_df[photos_df["uploader"].astype(str).str.upper() == employee_id.upper()].copy()
        non_rejected = user_photos[user_photos["status"] != "rejected"] if "status" in user_photos.columns else user_photos
        if len(non_rejected) >= MAX_PHOTOS_PER_USER:
            st.error(f"You have reached the maximum upload limit of {MAX_PHOTOS_PER_USER} photos.")
            return
        theme_taken = non_rejected[non_rejected["theme"] == theme] if "theme" in non_rejected.columns else pd.DataFrame()
        if not theme_taken.empty:
            st.error("You have already uploaded a photo for this theme. Each user can submit one photo per theme (max 2 total).")
            return
        
        save_photo(uploaded_file, title, employee_id, theme)
        st.success(f"Photo '{title.strip()}' uploaded successfully! ⏳ It is pending admin approval and will be visible to others once approved.")
        # Clear the form after successful upload
        if title_key in st.session_state:
            del st.session_state[title_key]
        if uploader_key in st.session_state:
            del st.session_state[uploader_key]
        if theme_key in st.session_state:
            del st.session_state[theme_key]
        st.rerun()


def gallery_section(employee_id: str = "") -> None:
    """Show gallery of uploaded photos (without uploader names) during Upload Phase. Only shows approved photos."""
    photos_df, _ = load_data()
    is_admin = employee_id.upper() == ADMIN_USERNAME.upper() if employee_id else False
    
    # Filter to show only approved photos to regular users, all photos to admin
    if is_admin:
        display_df = photos_df.copy()
    else:
        display_df = photos_df[photos_df["status"] == "approved"].copy()
    
    if display_df.empty:
        if is_admin:
            st.info("No photos uploaded yet.")
        else:
            st.info("No approved photos available yet.")
        return
    
    st.markdown('<div class="section-title">Uploaded Photos</div>', unsafe_allow_html=True)
    if is_admin:
        st.markdown('<div class="section-note">All submitted entries. Admin: Delete buttons are available below each photo.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-note">All approved entries (uploader names hidden for anonymity).</div>', unsafe_allow_html=True)
    
    # Display in a simple grid (3 columns per row)
    cols_per_row = 3
    photo_rows = [
        display_df.iloc[i : i + cols_per_row] for i in range(0, len(display_df), cols_per_row)
    ]
    
    for row_df in photo_rows:
        cols = st.columns(len(row_df))
        for col, (_, row) in zip(cols, row_df.iterrows()):
            photo_id = row["photo_id"]
            
            with col:
                st.markdown('<div class="photo-card">', unsafe_allow_html=True)
                photo_image = get_photo_image(row)
                if photo_image:
                    st.image(photo_image, caption=None)
                else:
                    st.warning("Image file missing.")
                st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                st.caption(f"Theme: {row.get('theme', 'Unspecified')}")
                
                # Show status badge for admin
                if is_admin:
                    status = row.get("status", "approved")
                    if status == "pending":
                        st.markdown('<div style="color: #f59e0b; font-weight: bold; margin: 0.5rem 0;">⏳ Pending</div>', unsafe_allow_html=True)
                    elif status == "rejected":
                        st.markdown('<div style="color: #ef4444; font-weight: bold; margin: 0.5rem 0;">❌ Rejected</div>', unsafe_allow_html=True)
                
                # Show delete button for admin
                if is_admin:
                    if st.button("🗑️ Delete", key=f"delete-{photo_id}", use_container_width=True):
                        delete_photo(photo_id)
                        st.success(f"Photo '{row['title']}' deleted successfully.")
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)


def rating_section(employee_id: str) -> None:
    """Voting section - only shown during Voting Phase, with anonymity. Only shows approved photos."""
    st.markdown('<div class="section-title">Vote for Photos</div>', unsafe_allow_html=True)
    photos_df, ratings_df = load_data()
    is_admin = employee_id.upper() == ADMIN_USERNAME.upper()

    # Filter to show only approved photos
    approved_df = photos_df[photos_df["status"] == "approved"].copy()
    
    if approved_df.empty:
        st.info("No approved photos available for voting.")
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
    user_vote = ratings_df[ratings_df["user_id"] == employee_id]
    current_photo_id = user_vote["photo_id"].iloc[0] if not user_vote.empty else None

    # Display in a simple grid (3 columns per row)
    cols_per_row = 3
    photo_rows = [
        approved_df.iloc[i : i + cols_per_row] for i in range(0, len(approved_df), cols_per_row)
    ]

    for row_df in photo_rows:
        cols = st.columns(len(row_df))
        for col, (_, row) in zip(cols, row_df.iterrows()):
            photo_id = row["photo_id"]

            with col:
                st.markdown('<div class="photo-card">', unsafe_allow_html=True)
                photo_image = get_photo_image(row)
                if photo_image:
                    st.image(photo_image, caption=None)
                else:
                    st.warning("Image file missing.")
                st.markdown(f'<div class="photo-title">{row["title"]}</div>', unsafe_allow_html=True)
                st.caption(f"Theme: {row.get('theme', 'Unspecified')}")
                # Uploader name NOT displayed for anonymity

                is_current = current_photo_id == photo_id
                button_label = "You voted here" if is_current else "Move your vote here" if current_photo_id else "Vote for this photo"
                disabled = is_current

                if st.button(button_label, key=f"vote-{photo_id}", use_container_width=True, disabled=disabled):
                    save_rating(photo_id, employee_id, 1)
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


def show_rules_modal() -> bool:
    """Display contest rules modal. Returns True if user has acknowledged."""
    if "rules_acknowledged" not in st.session_state:
        st.session_state.rules_acknowledged = False
    
    # If already acknowledged, return True
    if st.session_state.rules_acknowledged:
        return True
    
    # Show rules in an expandable section with prominent styling
    st.markdown("""
    <style>
    /* Hide any empty containers at the top */
    .block-container > div:first-child:empty {
        display: none !important;
    }
    .rules-container {
        background: linear-gradient(135deg, rgba(79,70,229,0.1) 0%, rgba(124,58,237,0.1) 100%);
        border: 2px solid #4f46e5;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 12px 32px rgba(79, 70, 229, 0.15);
    }
    .contest-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: #4f46e5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .contest-subtitle {
        font-size: 1.2rem;
        color: #475569;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .rules-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 1.5rem;
        text-align: center;
        border-bottom: 3px solid #4f46e5;
        padding-bottom: 1rem;
    }
    .rules-list {
        margin: 1.5rem 0;
        font-size: 1rem;
    }
    .rules-list ol {
        padding-left: 1.5rem;
    }
    .rules-list li {
        margin: 1rem 0;
        line-height: 1.8;
        color: #0f172a;
    }
    .rules-list strong {
        color: #4f46e5;
        font-size: 1.05rem;
    }
    .warning-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1.5rem 0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show rules prominently - all in one HTML block to avoid empty containers
    st.markdown("""
    <div class="rules-container">
    <div class="contest-title">Income Tax Photography League</div>
    <div class="contest-subtitle">In-House Photo Contest</div>
    
    <div class="rules-title">📋 Rules for Departmental Photo Competition</div>
    
    <div class="rules-list">
    <ol>
    <li>The competition is open to entire <strong>AAYKAR KUTUMB</strong>.</li>
    
    <li><strong>Theme:</strong><br>
    Each participant may submit photographs under the following themes:<br>
    &nbsp;&nbsp;&nbsp;i. "Happy Department is an Efficient Department"<br>
    &nbsp;&nbsp;&nbsp;ii. "New Income Tax Act"</li>
    
    <li><strong>Number of Entries:</strong><br>
    A maximum of two (2) photographs per participant is permitted (one per theme).</li>
    
    <li><strong>Photo Quality:</strong><br>
    • Photographs must be clear, sharp, and of good visual quality.<br>
    • Blurred, pixelated, or poorly lit photographs will not be considered.</li>
    
    <li><strong>Watermark Requirement:</strong><br>
    • Each photograph must carry the original watermark of the device (mobile phone/camera) from which it has been taken.<br>
    • Edited or removed watermarks will lead to disqualification.</li>
    
    <li><strong>Originality:</strong><br>
    • Photographs must be original and taken by the participant.<br>
    • Use of stock images or images taken from other sources is strictly prohibited.</li>
    
    <li><strong>Editing:</strong><br>
    • Minor adjustments (cropping, brightness, contrast) are permitted.<br>
    • Heavy editing, filters, or digital manipulation are not allowed.</li>
    
    <li><strong>Submission:</strong><br>
    • Photographs must be submitted in the prescribed manner and within the stipulated timeline, as communicated separately.</li>
    
    <li><strong>Disqualification:</strong><br>
    • Non-compliance with any of the above rules will result in disqualification.</li>
    
    <li><strong>Decision of Jury:</strong><br>
    • The decision of HQ Coordination shall be final and binding on all participants.</li>
    </ol>
    </div>
    
    <div class="warning-box">
    <strong>⚠️ Important:</strong> Please read all rules carefully before proceeding. By continuing, you acknowledge that you have read, understood, and agree to comply with all the rules and conditions stated above.
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Acknowledgment checkbox
    agreed = st.checkbox("✅ **I have read and understood all the rules and conditions. I agree to comply with them.**", key="rules_checkbox")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("I Agree and Continue", type="primary", use_container_width=True, disabled=not agreed):
            st.session_state.rules_acknowledged = True
            st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.stop()
    
    return False


def main() -> None:
    st.set_page_config(page_title="Photo Contest", page_icon="📸", layout="centered")
    inject_css()
    
    # Show rules modal first - must acknowledge before proceeding
    if not show_rules_modal():
        return  # Stop execution until rules are acknowledged

    ensure_structure()

    # Display main page title (on ALL pages - before and after login)
    st.markdown("""
    <div class="main-page-title">
        <h1>Income Tax Photography League</h1>
        <h2>In-House Photo Contest</h2>
    </div>
    """, unsafe_allow_html=True)

    user_info = require_user()
    if not user_info:
        # Show login message with proper styling to prevent text cutoff
        st.markdown("""
        <div style="padding: 1rem; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; margin: 1rem 0;">
            <strong>⚠️ Please login to continue.</strong>
        </div>
        """, unsafe_allow_html=True)
        return
    
    employee_id = user_info.get("employee_id", "")
    is_admin = user_info.get("is_admin", False) or (employee_id.upper() == ADMIN_USERNAME.upper())
    
    # Logout button
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.authenticated_user = {}
        st.rerun()
    
    # Cloudinary Status Indicator
    st.sidebar.divider()
    st.sidebar.header("Storage Status")
    if CLOUDINARY_AVAILABLE and is_cloudinary_configured():
        st.sidebar.success("✅ Cloudinary Active")
        st.sidebar.caption("Photos stored in cloud (unlimited)")
        try:
            init_cloudinary()
            secrets = st.secrets.get("cloudinary", {})
            cloud_name = secrets.get("cloud_name", "N/A")
            st.sidebar.caption(f"Cloud: {cloud_name}")
        except:
            pass
    else:
        st.sidebar.warning("⚠️ Cloudinary Not Configured")
        st.sidebar.caption("Using base64 storage (~10-20 photos max)")
        if not CLOUDINARY_AVAILABLE:
            st.sidebar.caption("Cloudinary package not installed")
        else:
            st.sidebar.caption("Add credentials in Streamlit Secrets")
    
    # Get current phase from toggle (admin only)
    voting_phase = phase_toggle(employee_id if is_admin else "")
    
    # Show admin controls (End Voting button and Reset Contest button)
    if is_admin:
        end_voting_button(employee_id)
        reset_contest_button(employee_id)
    
    voting_ended = get_voting_ended()

    # Show moderation section for admin (always visible, regardless of phase)
    if is_admin:
        moderation_section(employee_id)
        st.divider()

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
        rating_section(employee_id)
        # Leaderboard is HIDDEN during voting to prevent influence
    else:
        # Upload Phase: Show upload and gallery, hide voting and leaderboard
        st.info("📤 **Upload Phase Active** - Upload your photos. Voting will begin after the admin enables voting phase.")
        st.divider()
        upload_section(employee_id)
        st.divider()
        gallery_section(employee_id)
        # Leaderboard is HIDDEN during upload phase


if __name__ == "__main__":
    main()

