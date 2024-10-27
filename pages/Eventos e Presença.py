import streamlit as st
from database import Evento, Presenca, Adolescente, session
import pandas as pd

st.header("Registro de Presença")

def criar_evento():
    with st.form("Criar Evento"):
        nome_evento = st.text_input("Nome do Evento")
        data_evento = st.date_input("Data do Evento")
        submit = st.form_submit_button("Criar Evento")

        if submit:
            novo_evento = Evento(nome=nome_evento, data=data_evento)
            session.add(novo_evento)
            session.commit()
            st.success("Evento criado com sucesso!")

criar_evento()

def registrar_presenca():
    eventos = session.query(Evento).all()
    adolescentes = session.query(Adolescente).all()

    evento_selecionado = st.selectbox("Selecione o Evento", eventos, format_func=lambda x: x.nome)
    presentes = st.multiselect("Selecione os Presentes", adolescentes, format_func=lambda x: x.nome)

    if st.button("Registrar Presenças"):
        for adolescente in presentes:
            nova_presenca = Presenca(adolescente_id=adolescente.id, evento_id=evento_selecionado.id)
            session.add(nova_presenca)
        session.commit()
        st.success("Presenças registradas com sucesso!")

registrar_presenca()
