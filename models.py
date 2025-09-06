from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase, MappedColumn, relationship
from typing import List

class Base(DeclarativeBase):
    pass

class Funcionario(Base):
    __tablename__ = 'funcionario'

    id: Mapped[int] = MappedColumn(primary_key=True)
    cpf: Mapped[str] = MappedColumn(String(14))
    email: Mapped[str] = MappedColumn(String(100))
    nome: Mapped[str] = MappedColumn(String(100))
    endereco: Mapped['Endereco'] = relationship('Endereco',back_populates="funcionario", uselist=False, cascade="all, delete-orphan")

class Endereco(Base):

    __tablename__ = 'endereco'
    id:Mapped[int] = MappedColumn(primary_key=True)

    rua: Mapped[str] = MappedColumn(String(100))
    bairro: Mapped[str] = MappedColumn(String(100))
    numero: Mapped[int] = MappedColumn(Integer)

    funcionario_id: Mapped[int] = MappedColumn(ForeignKey('funcionario.id'), unique=True)
    localidade_id: Mapped[int] = MappedColumn(ForeignKey('localidade.id'))

    funcionario: Mapped['Funcionario'] = relationship("Funcionario", back_populates="endereco")
    localidade: Mapped['Localidade'] = relationship("Localidade", back_populates="enderecos")


class Localidade(Base):
    __tablename__ = 'localidade'

    id: Mapped[int] = MappedColumn(primary_key=True)
    cep: Mapped[str] = MappedColumn(String(10))
    cidade: Mapped[str] = MappedColumn(String(10))
    estado: Mapped[str] = MappedColumn(String(2))
    enderecos: Mapped[List['Endereco']] = relationship('Endereco', back_populates='localidade')