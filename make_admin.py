from library import app, db
from library.models import User

with app.app_context():
    # Buraya Admin yapmak istediğin kullanıcının adını yaz
    username_to_make_admin = "PostmanKullanicisi"

    user = User.query.filter_by(username=username_to_make_admin).first()

    if user:
        user.is_admin = True
        db.session.commit()
        print(f"BAŞARILI: {user.username} artık bir Admin!")
    else:
        print("HATA: Kullanıcı bulunamadı. İsmi doğru yazdığına emin ol.")