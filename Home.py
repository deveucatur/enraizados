import streamlit as st
from database import Adolescente, Presenca, Evento, Visitante, session
import pandas as pd
import datetime
from sqlalchemy import func
import plotly.express as px

st.set_page_config(page_title="Enraizados - Home", page_icon=":seedling:", layout="wide")

# CSS para estilização personalizada
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Crie um arquivo 'styles.css' com as estilizações desejadas
local_css("styles.css")

# Cabeçalho Principal
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






##DASHBORD##
st.header("📊 Dashboard Interativo")

# Obter o mês e ano atuais
mes_atual = datetime.datetime.now().month
ano_atual = datetime.datetime.now().year

st.subheader("Filtros")
col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox(
        "Selecione o Mês",
        list(range(1, 13)),
        format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'),
        index=mes_atual - 1
    )
with col2:
    anos_disponiveis = [ano_atual, ano_atual - 1]
    ano = st.selectbox(
        "Selecione o Ano",
        anos_disponiveis,
        index=0
    )

# Data inicial e final do filtro
data_inicio = datetime.date(ano, mes, 1)
if mes == 12:
    data_fim = datetime.date(ano + 1, 1, 1)
else:
    data_fim = datetime.date(ano, mes + 1, 1)


# Dados Filtrados
eventos_filtrados = session.query(Evento).filter(Evento.data >= data_inicio, Evento.data < data_fim).all()
eventos_ids = [evento.id for evento in eventos_filtrados]

presencas_filtradas = session.query(Presenca).filter(Presenca.evento_id.in_(eventos_ids)).all()

# Total de Adolescentes
total_adolescentes = session.query(Adolescente).count()

# Total de Eventos no Mês
total_eventos = len(eventos_filtrados)

# Presença Média no Mês
if total_eventos > 0:
    presencas_totais = sum(1 for p in presencas_filtradas if p.presente)
    media_presencas = presencas_totais / total_eventos
else:
    media_presencas = 0

# Visitantes no Mês
visitantes_mes = session.query(Visitante).filter(Visitante.evento_id.in_(eventos_ids)).count()

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Adolescentes", total_adolescentes)
col2.metric("Eventos no Mês", total_eventos)
col3.metric("Presença Média por Evento", f"{media_presencas:.1f}")
col4.metric("Visitantes no Mês", visitantes_mes)

# Gráfico de Presenças por Evento
st.subheader("Presenças por Evento")
dados_presencas = []
for evento in eventos_filtrados:
    presencas_evento = session.query(Presenca).filter_by(evento_id=evento.id).all()
    total_presentes = sum(1 for p in presencas_evento if p.presente)
    total_ausentes = sum(1 for p in presencas_evento if not p.presente)
    dados_presencas.append({
        'Evento': f"{evento.nome} ({evento.data.strftime('%d/%m')})",
        'Presentes': total_presentes,
        'Ausentes': total_ausentes
    })

df_presencas = pd.DataFrame(dados_presencas)

if not df_presencas.empty:
    fig = px.bar(
        df_presencas,
        x='Evento',
        y=['Presentes', 'Ausentes'],
        title="Presenças e Ausências por Evento",
        labels={'value': 'Quantidade', 'variable': 'Status'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Não há dados de presenças para o período selecionado.")

# Gráfico de Frequência por Adolescente
st.subheader("Frequência dos Adolescentes no Mês")
frequencia = {}
for presenca in presencas_filtradas:
    if presenca.adolescente_id not in frequencia:
        frequencia[presenca.adolescente_id] = {'Presenças': 0, 'Ausências': 0}
    if presenca.presente:
        frequencia[presenca.adolescente_id]['Presenças'] += 1
    else:
        frequencia[presenca.adolescente_id]['Ausências'] += 1

dados_frequencia = []
for adolescente_id, freq in frequencia.items():
    adolescente = session.query(Adolescente).filter_by(id=adolescente_id).first()
    total_presencas = freq['Presenças']
    total_ausencias = freq['Ausências']
    dados_frequencia.append({
        'Nome': adolescente.nome,
        'Presenças': total_presencas,
        'Ausências': total_ausencias
    })

df_frequencia = pd.DataFrame(dados_frequencia)

if not df_frequencia.empty:
    fig = px.bar(
        df_frequencia.sort_values('Presenças', ascending=False),
        x='Nome',
        y=['Presenças', 'Ausências'],
        title="Frequência de Presença por Adolescente",
        labels={'value': 'Quantidade', 'variable': 'Status'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Não há dados de frequência para o período selecionado.")

# Visitantes por Evento
st.subheader("Visitantes por Evento")
dados_visitantes = []
for evento in eventos_filtrados:
    visitantes_evento = session.query(Visitante).filter_by(evento_id=evento.id).count()
    dados_visitantes.append({
        'Evento': f"{evento.nome} ({evento.data.strftime('%d/%m')})",
        'Visitantes': visitantes_evento
    })

df_visitantes = pd.DataFrame(dados_visitantes)

if not df_visitantes.empty:
    fig = px.bar(
        df_visitantes,
        x='Evento',
        y='Visitantes',
        title="Número de Visitantes por Evento",
        labels={'Visitantes': 'Quantidade'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Não há dados de visitantes para o período selecionado.")

# Estilização
st.markdown("""
    <style>
        .css-18e3th9 {
            padding-top: 1rem;
        }
        .css-1d391kg {
            padding-top: 1rem;
        }
        .css-1lcbmhc {
            padding-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Rodapé com uma mensagem
st.markdown("---")
st.write("💒 **Igreja Assembleia de Deus - Ministério de Adolescentes El-Shaday**")
