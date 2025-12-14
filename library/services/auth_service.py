from library.repositories.user_repository import UserRepository
from library.models.user import User

class AuthService:
    user_repo = UserRepository()

    @staticmethod
    def register_user(username, email, password):
        # Yeni kullanıcı nesnesi oluştur
        user = User(username=username, email_address=email, password=password)
        # Repository aracılığıyla kaydet
        return AuthService.user_repo.add(user)

    @staticmethod
    def check_user_login(username, password):
        # Repository'den kullanıcıyı bul
        user = AuthService.user_repo.get_by_username(username)

        # Şifre kontrolü (Model içindeki metodu kullanmaya devam ediyoruz)
        if user and user.check_password_correction(attempted_password=password):
            return user
        return None