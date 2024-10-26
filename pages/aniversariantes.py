import streamlit as st
from database import Adolescente, session
import pandas as pd
import datetime

st.header("Aniversariantes do Mês")

def aniversariantes_do_mes():
    mes_atual = datetime.datetime.now().month
    query = session.query(Adolescente).filter(
        func.strftime("%m", Adolescente.data_nascimento) == f"{mes_atual:02d}"
    )
    data = pd.read_sql(query.statement, session.bind)
    st.dataframe(data)

aniversariantes_do_mes()
