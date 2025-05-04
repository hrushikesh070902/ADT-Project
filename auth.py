from models import User

def authenticate(email, password):
    """
    Look up a User by email/password in the database.
    Returns the User object on success, or None on failure.
    """
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        return user
    return None
