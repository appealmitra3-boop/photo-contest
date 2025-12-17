# Photo Contest Application

A Streamlit-based photo contest application with user authentication, voting system, and admin controls.

## Features

- **User Authentication**: Username/password login with self-registration
- **Photo Upload**: Users can upload up to 2 photos each
- **Voting System**: Anonymous voting with results hidden during voting phase
- **Admin Controls**: Admin can manage contest phases and delete photos
- **Leaderboard**: Results displayed after voting ends

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Deployment

This app is configured for Streamlit Cloud deployment.

### Streamlit Cloud Deployment Steps:

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set main file to `app.py`
7. Click "Deploy"

### Important Notes:

- Data files (`data/` folder) will be created automatically on first run
- Photos will be stored in the `photos/` folder
- Admin username is configured via Streamlit Secrets (recommended) or hardcoded in `app.py`

## Configuration

- Admin username: Set via Streamlit Secrets or modify `ADMIN_USERNAME` in `app.py`
- Max photos per user: 2 (configurable in `app.py`)

## Usage

1. Register a new account or login
2. Upload photos (max 2 per user)
3. Admin enables voting phase
4. Users vote for their favorite photos
5. Admin ends voting to reveal results

