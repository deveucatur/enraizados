from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

engine = create_engine('sqlite:///adolescentes.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Adolescente(Base):
    __tablename__ = 'adolescentes'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)  # Restringe nomes duplicados
    data_nascimento = Column(Date)
    telefone = Column(String)
    batizado_aguas = Column(Boolean)
    batizado_espirito = Column(Boolean)
    status = Column(String)


class Evento(Base):
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    data = Column(Date)

class Presenca(Base):
    __tablename__ = 'presencas'
    id = Column(Integer, primary_key=True)
    adolescente_id = Column(Integer, ForeignKey('adolescentes.id'))
    evento_id = Column(Integer, ForeignKey('eventos.id'))

Base.metadata.create_all(engine)
