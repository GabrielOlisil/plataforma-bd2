"""create initial user

Revision ID: aa175f0a1f30
Revises: 56893875a758
Create Date: 2025-09-08 11:45:12.279473

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import bcrypt

# revision identifiers, used by Alembic.
revision = 'aa175f0a1f30'
down_revision = '56893875a758'
branch_labels = None
depends_on = None

def upgrade():

    # Criar hash da senha para inserir
    senha = "senha123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)

    conn = op.get_bind()

    # Inserir Funcionario
    conn.execute(
        sa.text("""
            INSERT INTO funcionario (cpf, email, nome) VALUES (:cpf, :email, :nome)
        """),
        {"cpf": "00000000000", "email": "admin@exemplo.com", "nome": "Administrador"}
    )

    # Buscar id do funcionário recém criado
    funcionario_id = conn.execute(
        sa.text("SELECT id FROM funcionario WHERE email = :email"),
        {"email": "admin@exemplo.com"}
    ).scalar()

    # Inserir User com a senha hasheada
    conn.execute(
        sa.text("""
            INSERT INTO user (funcionario_id, senha) VALUES (:funcionario_id, :senha)
        """),
        {"funcionario_id": funcionario_id, "senha": hashed}
    )


def downgrade():
    # Remover dados criados no upgrade
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM user WHERE funcionario_id IN (SELECT id FROM funcionario WHERE email = :email)"), {"email": "admin@exemplo.com"})
    conn.execute(sa.text("DELETE FROM funcionario WHERE email = :email"), {"email": "admin@exemplo.com"})
