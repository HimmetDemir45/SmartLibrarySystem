from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from library.models import User
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField

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

# İSİM DEĞİŞİKLİĞİ: PurchaseItemForm -> BorrowBookForm
class BorrowBookForm(FlaskForm):
    submit = SubmitField(label='Ödünç al!')

# İSİM DEĞİŞİKLİĞİ: SellItemForm -> ReturnBookForm
class ReturnBookForm(FlaskForm):
    submit = SubmitField(label='Geri ver!')

# --- KİTAP EKLEME FORMU (Sadece Admin Görecek) ---
class AddBookForm(FlaskForm):
    name = StringField(label='Kitap Adı:', validators=[DataRequired()])
    author = StringField(label='Yazar:', validators=[DataRequired()])
    category = StringField(label='Kategori:', validators=[DataRequired()])
    barcode = StringField(label='Barkod:', validators=[Length(min=12, max=12), DataRequired()])
    description = TextAreaField(label='Açıklama:', validators=[DataRequired()])
    image = FileField('Kitap Kapağı', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField(label='Kitabı Kütüphaneye Ekle')