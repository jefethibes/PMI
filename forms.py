from wtforms import StringField, Form, validators, PasswordField, TextAreaField
from wtforms.fields.html5 import EmailField


class Chamados(Form):
    titulo = StringField('Título:', [validators.length(min=5, max=30, message='Título muito pequeno!')])
    comentario = TextAreaField('Comentario:', [validators.length(min=10, max=100, message='Comentário muito pequeno!')])


class Login(Form):
    usuario = StringField('Usuário', [validators.length(min=3, max=15, message='Login inválido!')])
    senha = PasswordField('Senha', [validators.length(min=5, max=20, message='Senha inválida!')])


class CriarUsuario(Form):
    usuario = StringField('Usuário:', [validators.length(min=3, max=15, message='Usuario muito curto!')])
    senha = PasswordField('Senha:', [validators.length(min=5, max=20, message='Senha muito curta!')])
    nome = StringField('Nome:', [validators.length(min=2, max=20, message='Nome muito curto!')])
    sobrenome = StringField('Sobrenome:', [validators.length(min=1, max=50, message='Sobrenome muito curto!')])
    email = EmailField('E-mail:', [validators.length(min=5, max=50, message='E-mail inválido!')])


class Encerramento(Form):
    comentario = TextAreaField('Comentario de encerramento:', [validators.length(min=10, max=100, message='Comentário muito pequeno!')])


class AlteraUsuario(Form):
    usuario = StringField('Usuário:', [validators.length(min=3, max=15, message='Usuario muito curto!')])
    nome = StringField('Nome:', [validators.length(min=2, max=20, message='Nome muito curto!')])
    sobrenome = StringField('Sobrenome:', [validators.length(min=1, max=50, message='Sobrenome muito curto!')])
    email = EmailField('E-mail:', [validators.length(min=5, max=50, message='E-mail inválido!')])

