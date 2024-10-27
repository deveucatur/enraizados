import streamlit as st
from database import Adolescente, Presenca, Evento, session
import pandas as pd
import matplotlib.pyplot as plt

st.header("Relatórios e Dashboards")

# Quantidade total de adolescentes
total_adolescentes = session.query(Adolescente).count()
st.metric("Total de Adolescentes", total_adolescentes)


# Percentual de batizados
st.subheader("Percentual de Batizados")
batizado_aguas = session.query(Adolescente).filter_by(batizado_aguas=True).count()
batizado_espirito = session.query(Adolescente).filter_by(batizado_espirito=True).count()
percent_aguas = (batizado_aguas / total_adolescentes) * 100 if total_adolescentes else 0
percent_espirito = (batizado_espirito / total_adolescentes) * 100 if total_adolescentes else 0
st.metric("Batizados nas Águas (%)", f"{percent_aguas:.2f}%")
st.metric("Batizados no Espírito Santo (%)", f"{percent_espirito:.2f}%")

# Frequência de presença por adolescente
st.subheader("Frequência de Presença")
presencas = session.query(Presenca).all()
eventos_totais = session.query(Evento).count()
frequencia = {}
for presenca in presencas:
    if presenca.adolescente_id not in frequencia:
        frequencia[presenca.adolescente_id] = 0
    frequencia[presenca.adolescente_id] += 1

dados_frequencia = []
for adolescente_id, freq in frequencia.items():
    adolescente = session.query(Adolescente).filter_by(id=adolescente_id).first()
    percentual = (freq / eventos_totais) * 100 if eventos_totais else 0
    dados_frequencia.append({
        'Nome': adolescente.nome,
        'Frequência (%)': percentual
    })

df_frequencia = pd.DataFrame(dados_frequencia)
st.dataframe(df_frequencia)
