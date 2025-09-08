"""create_default_user

Revision ID: b4fbc2fbb3ca
Revises: 72f21bb82197
Create Date: 2025-09-08 16:13:07.955251

"""
from alembic import op
import sqlalchemy as sa
import bcrypt

# revision identifiers, used by Alembic.
revision = 'b4fbc2fbb3ca'
down_revision = '72f21bb82197'
branch_labels = None
depends_on = None


def upgrade():
    # Criar hash da senha para inserir
    senha = "senha123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)

    conn = op.get_bind()

    # Verificar se o funcionário já existe
    funcionario_id = conn.execute(
        sa.text("SELECT id FROM funcionario WHERE email = :email"),
        {"email": "admin@exemplo.com"}
    ).scalar()

    if not funcionario_id:
        # Inserir Funcionario
        conn.execute(
            sa.text("""
                INSERT INTO funcionario (cpf, email, nome) 
                VALUES (:cpf, :email, :nome)
            """),
            {"cpf": "00000000000", "email": "admin@exemplo.com", "nome": "Administrador"}
        )

        # Buscar id do funcionário recém criado
        funcionario_id = conn.execute(
            sa.text("SELECT id FROM funcionario WHERE email = :email"),
            {"email": "admin@exemplo.com"}
        ).scalar()

        # Inserir AppUser com a senha hasheada
        conn.execute(
            sa.text("""
                INSERT INTO app_user (funcionario_id, senha) 
                VALUES (:funcionario_id, :senha)
            """),
            {"funcionario_id": funcionario_id, "senha": hashed}
        )


def downgrade():
    conn = op.get_bind()

    # Remover AppUser criado
    conn.execute(
        sa.text("""
            DELETE FROM app_user 
            WHERE funcionario_id IN (
                SELECT id FROM funcionario WHERE email = :email
            )
        """),
        {"email": "admin@exemplo.com"}
    )

    # Remover Funcionario criado
    conn.execute(
        sa.text("DELETE FROM funcionario WHERE email = :email"),
        {"email": "admin@exemplo.com"}
    )