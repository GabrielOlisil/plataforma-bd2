from flask import Flask, session, request, redirect, url_for, render_template
from sqlalchemy.orm import sessionmaker

from models import Base, Funcionario, Endereco, Localidade
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine("mysql+pymysql://root:alunoifro@127.0.0.1:3306/test")

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)


@app.route('/')
def index():
    return render_template('index.html', nome="John Doe")