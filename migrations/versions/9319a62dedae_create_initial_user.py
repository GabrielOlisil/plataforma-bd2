"""create_initial_user

Revision ID: 9319a62dedae
Revises: 09f6f124f969
Create Date: 2025-09-08 16:01:47.592273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9319a62dedae'
down_revision = '09f6f124f969'
branch_labels = None
depends_on = None


import sqlalchemy as sa
from alembic import op
import bcrypt

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
            INSERT INTO app_user (funcionario_id, senha) VALUES (:funcionario_id, :senha)
        """),
        {"funcionario_id": funcionario_id, "senha": hashed}
    )


def downgrade():
    conn = op.get_bind()
    # Remover dados criados no upgrade
    conn.execute(
        sa.text("""
            DELETE FROM app_user WHERE funcionario_id IN 
            (SELECT id FROM funcionario WHERE email = :email)
        """),
        {"email": "admin@exemplo.com"}
    )
    conn.execute(
        sa.text("DELETE FROM funcionario WHERE email = :email"),
        {"email": "admin@exemplo.com"}
    )