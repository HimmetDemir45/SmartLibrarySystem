from library.repositories.user_repository import UserRepository
from library.models.user import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

logger = logging.getLogger(__name__)

class AuthService:
    user_repo = UserRepository()

    @staticmethod
    def register_user(username, email, password):
        try:
            # Yeni kullanıcı nesnesi oluştur - varsayılan bakiye 100 TL
            user = User(username=username, email_address=email, password=password, budget=100)
            # Repository aracılığıyla kaydet
            return AuthService.user_repo.add(user)
        except IntegrityError as e:
            logger.error(f"Kullanıcı kayıt hatası (duplicate): {str(e)}")
            raise ValueError("Bu kullanıcı adı veya email zaten kullanılıyor.")
        except SQLAlchemyError as e:
            logger.error(f"Kullanıcı kayıt hatası: {str(e)}")
            raise

    @staticmethod
    def check_user_login(username, password):
        try:
            # Repository'den kullanıcıyı bul
            user = AuthService.user_repo.get_by_username(username)

            # Şifre kontrolü (Model içindeki metodu kullanmaya devam ediyoruz)
            if user and user.check_password_correction(attempted_password=password):
                return user
            return None
        except SQLAlchemyError as e:
            logger.error(f"Kullanıcı giriş hatası: {str(e)}")
            return None