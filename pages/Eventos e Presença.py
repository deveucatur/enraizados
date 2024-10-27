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

def registrar_presenca():
    st.subheader("Registrar Presença")

    # Selecionar evento não encerrado
    eventos_abertos = session.query(Evento).filter_by(encerrado=False).all()
    if not eventos_abertos:
        st.info("Não há eventos abertos para registrar presença.")
        return

    evento_selecionado = st.selectbox(
        "Selecione o Evento",
        eventos_abertos,
        format_func=lambda x: f"{x.nome} - {x.data.strftime('%d/%m/%Y')}"
    )

    # Verificar se já foi registrada presença neste evento
    presencas_existentes = session.query(Presenca).filter_by(evento_id=evento_selecionado.id).first()
    if presencas_existentes:
        st.warning("A presença já foi registrada para este evento.")
        return

    adolescentes = session.query(Adolescente).filter_by(status="Ativo").all()
    presentes = st.multiselect(
        "Selecione os Presentes",
        adolescentes,
        format_func=lambda x: x.nome
    )

    # Visitantes
    st.subheader("Adicionar Visitantes")
    num_visitantes = st.number_input("Número de Visitantes", min_value=0, step=1)
    visitantes = []
    for i in range(int(num_visitantes)):
        with st.expander(f"Visitante {i+1}"):
            nome_visitante = st.text_input(f"Nome do Visitante {i+1}")
            telefone_visitante = st.text_input(f"Telefone do Visitante {i+1}")
            convidado_por = st.selectbox(
                f"Convidado por (Adolescente)",
                adolescentes,
                format_func=lambda x: x.nome,
                key=f"convidado_por_{i}"
            )
            visitantes.append({
                'nome': nome_visitante,
                'telefone': telefone_visitante,
                'convidado_por_id': convidado_por.id
            })
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
            else:
                st.write("Nenhum visitante neste evento.")


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
