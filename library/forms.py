from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError,Regexp
from flask_wtf.file import FileField, FileAllowed
from library.models import User, Author, Category
from wtforms_sqlalchemy.fields import QuerySelectField

# QuerySelectField için gerekli sorgu fonksiyonları
def get_authors():
    """Tüm yazarları çekmek için sorgu fonksiyonu."""
    return Author.query.all()

def get_categories():
    """Tüm kategorileri çekmek için sorgu fonksiyonu."""
    return Category.query.all()

class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Kullanıcı adı alınmış! Lütfen farklı bir kullanıcı adı deneyin')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email adresi zaten kullanılıyor! Lütfen farklı bir email adresi deneyin')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class BorrowBookForm(FlaskForm):
    submit = SubmitField(label='Ödünç al!')


class ReturnBookForm(FlaskForm):
    submit = SubmitField(label='Geri ver!')

# --- KİTAP EKLEME FORMU (Sadece Admin Görecek) ---
# ...
class AddBookForm(FlaskForm):
    name = StringField(label='Kitap Adı:', validators=[DataRequired()])
    # QuerySelectField ile değiştiriyoruz. Yazarları çekmek için get_authors fonksiyonunu kullanacak.
    author = QuerySelectField(label='Yazar:', query_factory=get_authors, allow_blank=False, get_label='name')
    # Kategorileri çekmek için get_categories fonksiyonunu kullanacak.
    category = QuerySelectField(label='Kategori:', query_factory=get_categories, allow_blank=False, get_label='name')
    barcode = StringField(label='Barkod:', validators=[
        Length(min=12, max=12, message="Barkod tam 12 hane olmalıdır."),
        DataRequired(),
        Regexp('^[0-9]*$', message="Barkod sadece rakamlardan oluşabilir.")
    ])
    description = TextAreaField(label='Açıklama:', validators=[DataRequired()])
    image = FileField('Kitap Kapağı', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField(label='Kitabı Kütüphaneye Ekle')


# --- YAZAR VE KATEGORİ YÖNETİM FORMLARI (ADMIN) ---

class AdminForm(FlaskForm):
    """Admin paneli için temel form."""
    name = StringField(label='İsim:', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField(label='Kaydet')


class AddAuthorForm(AdminForm):
    """Yazar Ekleme/Düzenleme Formu."""
    pass # name ve submit alanlarını AdminForm'dan miras alır


class AddCategoryForm(AdminForm):
    """Kategori Ekleme/Düzenleme Formu."""
    pass # name ve submit alanlarını AdminForm'dan miras alır

class EditBookForm(FlaskForm):
    """Kitap Düzenleme Formu (Validasyon için)"""
    name = StringField(label='Kitap Adı:', validators=[DataRequired()])
    # Not: Servis katmanınız string beklediği için şimdilik StringField kullanıyoruz.
    author = StringField(label='Yazar:', validators=[DataRequired()])
    category = StringField(label='Kategori:', validators=[DataRequired()])
    barcode = StringField(label='Barkod:', validators=[
        Length(min=12, max=12, message="Barkod tam 12 hane olmalıdır."),
        DataRequired(),
        Regexp('^[0-9]*$', message="Barkod sadece rakamlardan oluşabilir.")
    ])
    description = TextAreaField(label='Açıklama:', validators=[DataRequired()])
    image = FileField('Kitap Kapağı', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField(label='Değişiklikleri Kaydet')


# 1. E-posta İsteme Formu
class RequestResetForm(FlaskForm):
    email = StringField('E-posta Adresi',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Şifre Sıfırlama Linki Gönder')

    def validate_email(self, email):
        user = User.query.filter_by(email_address=email.data).first()
        if user is None:
            raise ValidationError('Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.')

# 2. Yeni Şifre Belirleme Formu
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Yeni Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifreyi Onayla',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Şifreyi Güncelle')