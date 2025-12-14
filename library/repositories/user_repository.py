from library.repositories.base_repository import BaseRepository
from library.models.user import User

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username):
        return self.model.query.filter_by(username=username).first()

    def get_by_email(self, email):
        return self.model.query.filter_by(email_address=email).first()

    def get_admins(self):
        return self.model.query.filter_by(is_admin=True).all()