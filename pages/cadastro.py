import streamlit as st
from database import Adolescente, session
import pandas as pd

st.header("Cadastro de Adolescentes")

def adicionar_adolescente():
    with st.form("Adicionar Adolescente"):
        nome = st.text_input("Nome")
        data_nascimento = st.date_input("Data de Nascimento")
        telefone = st.text_input("Telefone")
        batizado_aguas = st.selectbox("Batizado nas Águas", ["Sim", "Não"]) == "Sim"
        batizado_espirito = st.selectbox("Batizado no Espírito Santo", ["Sim", "Não"]) == "Sim"
        status = st.selectbox("Status", ["Ativo", "Inativo"])
        submit = st.form_submit_button("Adicionar")

        if submit:
            novo_adolescente = Adolescente(
                nome=nome,
                data_nascimento=data_nascimento,
                telefone=telefone,
                batizado_aguas=batizado_aguas,
                batizado_espirito=batizado_espirito,
                status=status
            )
            session.add(novo_adolescente)
            session.commit()
            st.success("Adolescente adicionado com sucesso!")

adicionar_adolescente()

# Exibir dados
def exibir_adolescentes():
    st.subheader("Lista de Adolescentes")
    query = session.query(Adolescente)
    data = pd.read_sql(query.statement, session.bind)
    st.dataframe(data)

exibir_adolescentes()
