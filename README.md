# Forum
A simple forum.

# Setup
    git clone https://github.com/ColdIV/forum.git
    virtualenv .env
    source .env/bin/activate
    # On Windows: 
    # .\.env\Scripts\activate
    cd .env
    pip3 install -r requirements.txt
    python3 app.py
    # Register admin on first run:
    python3 services/main_db.py
