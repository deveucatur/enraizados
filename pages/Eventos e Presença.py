import streamlit as st
from database import Evento, Presenca, Adolescente, Visitante, session
import pandas as pd
import datetime

st.header("Eventos e Presença")

def criar_evento():
    st.subheader("Criar Novo Evento")
    with st.form("Criar Evento"):
        nome_evento = st.text_input("Nome do Evento")
        data_evento = st.date_input("Data do Evento", value=datetime.date.today())
        submit = st.form_submit_button("Criar Evento")

        if submit:
            novo_evento = Evento(nome=nome_evento, data=data_evento)
            session.add(novo_evento)
            session.commit()
            st.success(f"Evento '{nome_evento}' criado com sucesso!")

if st.button("Registrar Presenças"):
    # Criar um conjunto de IDs dos presentes para facilitar a verificação
    presentes_ids = {adolescente.id for adolescente in presentes}
    
    # Registrar presença dos presentes e ausentes
    for adolescente in adolescentes:
        presente = adolescente.id in presentes_ids
        nova_presenca = Presenca(
            adolescente_id=adolescente.id,
            evento_id=evento_selecionado.id,
            presente=presente
        )
        session.add(nova_presenca)

    # Registrar visitantes
    for visitante_data in visitantes:
        novo_visitante = Visitante(
            nome=visitante_data['nome'],
            telefone=visitante_data['telefone'],
            convidado_por=visitante_data['convidado_por_id'],
            evento_id=evento_selecionado.id  # Certifique-se de incluir o evento_id
        )
        session.add(novo_visitante)

    # Encerrar o evento para novos registros
    evento_selecionado.encerrado = True
    session.commit()
    st.success("Presenças registradas e evento encerrado com sucesso!")


def historico_eventos():
    st.subheader("Histórico de Eventos")
    eventos = session.query(Evento).order_by(Evento.data.desc()).all()
    for evento in eventos:
        with st.expander(f"{evento.nome} - {evento.data.strftime('%d/%m/%Y')}"):
            presencas = session.query(Presenca).filter_by(evento_id=evento.id).all()
            data = []
            for presenca in presencas:
                adolescente = session.query(Adolescente).filter_by(id=presenca.adolescente_id).first()
                data.append({
                    'Nome': adolescente.nome,
                    'Presente': 'Sim' if presenca.presente else 'Não'
                })
            df = pd.DataFrame(data)
            st.table(df)

            # Mostrar visitantes deste evento
            visitantes = session.query(Visitante).filter_by(evento_id=evento.id).all()
            if visitantes:
                st.write("**Visitantes:**")
                data_visitantes = []
                for visitante in visitantes:
                    convidado_por = session.query(Adolescente).filter_by(id=visitante.convidado_por).first()
                    data_visitantes.append({
                        'Nome': visitante.nome,
                        'Telefone': visitante.telefone,
                        'Convidado por': convidado_por.nome if convidado_por else 'N/A'
                    })
                df_visitantes = pd.DataFrame(data_visitantes)
                st.table(df_visitantes)

# Adicionar o campo 'presente' na tabela Presenca
def atualizar_presenca_model():
    from sqlalchemy import Column, Boolean
    if not hasattr(Presenca, 'presente'):
        Presenca.presente = Column(Boolean)
        Presenca.__table__.create(session.bind, checkfirst=True)

atualizar_presenca_model()
criar_evento()
registrar_presenca()
historico_eventos()
