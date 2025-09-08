from functools import wraps

from flask import Flask, session, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import  SQLAlchemy
from flask_migrate import Migrate
import bcrypt
import secrets
from datetime import  UTC, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:alunoifro@127.0.0.1:3306/test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db: SQLAlchemy = SQLAlchemy(app)

migrate = Migrate(app, db)


def check_password(hashed: bytes, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

from models import Funcionario, Endereco, Localidade, Session, User



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            flash('Você precisa estar logado para acessar esta página.')
            return redirect(url_for('login'))

        session_obj = Session.query.filter_by(session_token=token).first()
        if not session_obj:
            flash('Sessão inválida. Faça login novamente.')
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    return decorated_function




@app.route('/logout')
def logout():
    token = session.pop('token', None)
    if token:
        session_db = Session.query.filter_by(session_token=token).first()
        if session_db:
            db.session.delete(session_db)
            db.session.commit()

    flash('Deslogado com sucesso.')
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    senha = request.form.get('senha')

    func = Funcionario.query.filter_by(email=email).first()

    if not func or not func.user:
        print('Usuário ou senha inválidos')
        flash('Usuário ou senha inválidos')
        return redirect(url_for('login'), 400)

    if not check_password(func.user.senha, senha):
        print('Usuário ou senha inválidos')
        flash('Usuário ou senha inválidos')
        return redirect(url_for('login'), 400)

    # Remove sessão antiga (se existir)
    old_session = Session.query.filter_by(user_id=func.user.id).first()
    if old_session:
        db.session.delete(old_session)
        db.session.commit()

    # Cria nova sessão
    session_db = Session(user_id=func.user.id)
    db.session.add(session_db)
    db.session.commit()

    session['token'] = session_db.session_token

    return redirect(url_for('home'))






@app.route('/', methods=['GET'])
@login_required
def home():


    return 'Pra ver aqui tem que tar logado'






@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    email = request.form.get('email')
    senha = request.form.get('senha')
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')

    # Cria Funcionario
    funcionario = Funcionario(email=email, nome=nome, cpf=cpf)
    db.session.add(funcionario)
    db.session.commit()

    # Cria User com senha hasheada
    hashed_senha = hash_password(senha)
    user = User(funcionario_id=funcionario.id, senha=hashed_senha)
    db.session.add(user)
    db.session.commit()

    flash('Usuário criado com sucesso!')
    return redirect(url_for('login'))


