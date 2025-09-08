from datetime import datetime, timedelta, UTC
import secrets

from main import  db

class Funcionario(db.Model):
    __tablename__ = 'funcionario'

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    nome = db.Column(db.String(100), nullable=False)

    endereco = db.relationship('Endereco', back_populates='funcionario', uselist=False, cascade='all, delete-orphan')
    user = db.relationship('AppUser', back_populates='funcionario', uselist=False, cascade='all, delete-orphan')

class Endereco(db.Model):
    __tablename__ = 'endereco'

    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(100), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.Integer, nullable=False)

    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), unique=True, nullable=False)
    localidade_id = db.Column(db.Integer, db.ForeignKey('localidade.id'), nullable=False)

    funcionario = db.relationship('Funcionario', back_populates='endereco')
    localidade = db.relationship('Localidade', back_populates='enderecos')


class Localidade(db.Model):
    __tablename__ = 'localidade'

    id = db.Column(db.Integer, primary_key=True)
    cep = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)

    enderecos = db.relationship('Endereco', back_populates='localidade', cascade='all, delete-orphan')


class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    senha = db.Column(db.LargeBinary(60), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), unique=True, nullable=False)
    funcionario = db.relationship('Funcionario', back_populates='user')


class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    user = db.relationship('AppUser', backref='sessions')

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.session_token = secrets.token_hex(32)





