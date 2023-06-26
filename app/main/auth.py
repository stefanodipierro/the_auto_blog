# auth.py
from .models import User
from app import login_manager  # Import login_manager from app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


