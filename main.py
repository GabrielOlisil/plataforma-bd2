from functools import wraps

from dotenv import load_dotenv
from flask import Flask, session, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import  SQLAlchemy
from flask_migrate import Migrate
import bcrypt
import os

db_pass= os.getenv('DB_PASS')
db_host= os.getenv('DB_HOST')
db_database= os.getenv('DB_DATABASE')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://postgres:{db_pass}@{db_host}:5432/{db_database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

db: SQLAlchemy = SQLAlchemy(app)

migrate = Migrate(app, db)


def check_password(hashed: bytes, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

from models import Funcionario, Endereco, Localidade, Session, AppUser



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


@app.route('/list')
def list():
    funcionarios = Funcionario.query.all()
    return render_template('list.html', funcionarios=funcionarios)



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
    session['uid'] = func.user.id

    return redirect(url_for('home'))






@app.route('/', methods=['GET'])
@login_required
def home():
    uid = session['uid']

    funcionario = Funcionario.query.filter(Funcionario.user.has(AppUser.id==uid)).first()

    return render_template('index.html', funcionario=funcionario)






@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # dados básicos
    email = request.form.get('email')
    senha = request.form.get('senha')
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')

    # dados de endereço
    rua = request.form.get('rua')
    bairro = request.form.get('bairro')
    numero = request.form.get('numero')

    # dados de localidade
    cep = request.form.get('cep')
    cidade = request.form.get('cidade')
    estado = request.form.get('estado')

    try:
        # cria ou busca Localidade (evita duplicar se já existir)
        localidade = Localidade.query.filter_by(cep=cep).first()
        if not localidade:
            localidade = Localidade(cep=cep, cidade=cidade, estado=estado)
            db.session.add(localidade)
            db.session.flush()  # garante que tenha ID

        # cria Funcionario
        funcionario = Funcionario(email=email, nome=nome, cpf=cpf)
        db.session.add(funcionario)
        db.session.flush()

        # cria Endereco associado ao Funcionario + Localidade
        endereco = Endereco(
            rua=rua,
            bairro=bairro,
            numero=int(numero),
            funcionario_id=funcionario.id,
            localidade_id=localidade.id
        )
        db.session.add(endereco)

        # cria User com senha hasheada
        hashed_senha = hash_password(senha)
        user = AppUser(funcionario_id=funcionario.id, senha=hashed_senha)
        db.session.add(user)

        db.session.commit()

        flash('Usuário criado com sucesso!')
        return redirect(url_for('login'))

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao registrar: {str(e)}", "danger")
        return redirect(url_for('register'))


