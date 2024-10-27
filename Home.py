import streamlit as st
from database import Adolescente, Evento, session
import pandas as pd
import datetime
from sqlalchemy import func

st.set_page_config(page_title="Enraizados - Home", page_icon=":seedling:", layout="wide")

# CSS para estilização personalizada
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Crie um arquivo 'styles.css' com as estilizações desejadas
local_css("styles.css")

# Cabeçalho Principal
st.image("logo.png", width=150)
st.title("🌱 Enraizados")


# Seções de Propósito e Visão
st.header("Propósito e Visão")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Propósito")
    st.write("Ser enraizados em Cristo, apaixonados pelo Espírito Santo e ensinar os outros a fazer o mesmo.")

with col2:
    st.subheader("Visão a Longo Prazo")
    st.write("Criar uma geração que se torna referência em espiritualidade e liderança, inspirando outros a seguir o mesmo caminho.")

# Seção de Eventos
st.header("Eventos")
events = [
    {
        "nome": "Enraizados (Toda Quinta-feira)",
        "descricao": "Um espaço semanal para ensino profundo, oração, e comunhão entre os adolescentes. Cada mês pode ter um tema diferente, como 'Identidade em Cristo', 'O poder do Espírito Santo', etc."
    },
    {
        "nome": "Encontro das Preciosas (Outubro)",
        "descricao": "Um evento específico para meninas, focando em identidade, autoestima em Cristo, e o valor delas aos olhos de Deus."
    },
    {
        "nome": "Forjados em Cristo (Novembro)",
        "descricao": "Focado nos meninos, este evento trata sobre ser forjado como servo de Deus, com temas como liderança, caráter e propósito."
    },
    {
        "nome": "Gincana Roots (Março)",
        "descricao": "Uma gincana divertida e interativa para promover união e comunhão entre os adolescentes, com atividades que integram aprendizado espiritual e recreação."
    },
    {
        "nome": "Acampa Roots (Julho)",
        "descricao": "Acampamento anual para crescimento espiritual intenso, com momentos de adoração, estudos, e atividades ao ar livre, ideal para criar laços mais profundos entre o grupo."
    }
]

for event in events:
    with st.expander(f"📅 {event['nome']}"):
        st.write(event["descricao"])

# Dados do Sistema
st.header("Dados do Sistema")

# Número de adolescentes
total_adolescentes = session.query(Adolescente).count()

# Aniversariantes da semana
hoje = datetime.date.today()
dia_semana = hoje.weekday()  # 0 é segunda-feira
inicio_semana = hoje - datetime.timedelta(days=dia_semana)
fim_semana = inicio_semana + datetime.timedelta(days=6)

aniversariantes_semana = session.query(Adolescente).filter(
    func.strftime("%m-%d", Adolescente.data_nascimento) >= inicio_semana.strftime("%m-%d"),
    func.strftime("%m-%d", Adolescente.data_nascimento) <= fim_semana.strftime("%m-%d")
).all()

# Eventos da semana
eventos_semana = session.query(Evento).filter(
    Evento.data >= inicio_semana,
    Evento.data <= fim_semana
).all()

# Exibir métricas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Adolescentes", total_adolescentes, delta=None)

with col2:
    st.metric("Aniversariantes da Semana", len(aniversariantes_semana), delta=None)

with col3:
    st.metric("Eventos nesta Semana", len(eventos_semana), delta=None)

# Listar aniversariantes
if aniversariantes_semana:
    st.subheader("🎂 Aniversariantes da Semana")
    for adolescente in aniversariantes_semana:
        st.write(f"- {adolescente.nome} ({adolescente.data_nascimento.strftime('%d/%m')})")
else:
    st.write("Nenhum aniversariante nesta semana.")

# Listar eventos da semana
if eventos_semana:
    st.subheader("📆 Eventos desta Semana")
    for evento in eventos_semana:
        st.write(f"- {evento.nome} ({evento.data.strftime('%d/%m/%Y')})")
else:
    st.write("Nenhum evento nesta semana.")

# Rodapé com uma mensagem
st.markdown("---")
st.write("💒 **Igreja Assembleia de Deus - Ministério de Adolescentes El-Shaday**")
