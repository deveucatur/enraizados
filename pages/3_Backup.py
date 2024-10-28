import streamlit as st
from database import Base, engine, session, Adolescente, Evento, Presenca, Visitante
import json
import os
import requests
import datetime
import base64

# Carregar o token do GitHub das secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

st.write(GITHUB_TOKEN)

# Configurações do GitHub
GITHUB_USER = "deveucatur"
GITHUB_REPO = "enraizados"
BACKUP_FILE = "backup_dados.json"
BRANCH = "main"

def exportar_dados():
    # Obter todos os dados das tabelas
    adolescentes = session.query(Adolescente).all()
    eventos = session.query(Evento).all()
    presencas = session.query(Presenca).all()
    visitantes = session.query(Visitante).all()

    # Função para converter objetos ORM em dicionários com apenas colunas
    def to_dict(obj):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

    # Converter para formatos serializáveis em JSON
    dados = {
        "adolescentes": [to_dict(a) for a in adolescentes],
        "eventos": [to_dict(e) for e in eventos],
        "presencas": [to_dict(p) for p in presencas],
        "visitantes": [to_dict(v) for v in visitantes],
    }

    # Converter para JSON
    json_dados = json.dumps(dados, indent=4, default=str)
    return json_dados

def codificar_conteudo(conteudo):
    conteudo_bytes = conteudo.encode('utf-8')
    conteudo_base64 = base64.b64encode(conteudo_bytes).decode('utf-8')
    return conteudo_base64

def fazer_commit_github(conteudo, mensagem_commit):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{BACKUP_FILE}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Verificar se o arquivo já existe
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None

    data = {
        "message": mensagem_commit,
        "content": conteudo,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha

    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code in (200, 201):
        st.success("Backup feito com sucesso e enviado para o GitHub!")
    else:
        st.error(f"Erro ao fazer o commit no GitHub: {response.json()}")

def restaurar_dados():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{BACKUP_FILE}?ref={BRANCH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        conteudo_base64 = response.json()["content"]
        conteudo_json = base64.b64decode(conteudo_base64).decode('utf-8')
        dados = json.loads(conteudo_json)

        # Limpar as tabelas existentes
        session.query(Presenca).delete()
        session.query(Visitante).delete()
        session.query(Adolescente).delete()
        session.query(Evento).delete()
        session.commit()

        # Função para filtrar apenas colunas do modelo
        def filter_columns(model, data):
            model_columns = set(c.name for c in model.__table__.columns)
            # Opcional: Remover 'id' se não quiser definir manualmente
            # model_columns.discard('id')
            return {k: v for k, v in data.items() if k in model_columns}

        # Restaurar dados
        for item in dados["adolescentes"]:
            item = filter_columns(Adolescente, item)
            novo_adolescente = Adolescente(**item)
            session.add(novo_adolescente)

        for item in dados["eventos"]:
            item = filter_columns(Evento, item)
            novo_evento = Evento(**item)
            session.add(novo_evento)

        for item in dados["presencas"]:
            item = filter_columns(Presenca, item)
            nova_presenca = Presenca(**item)
            session.add(nova_presenca)

        for item in dados["visitantes"]:
            item = filter_columns(Visitante, item)
            novo_visitante = Visitante(**item)
            session.add(novo_visitante)

        session.commit()
        st.success("Dados restaurados com sucesso!")
    else:
        st.error(f"Erro ao recuperar o backup do GitHub: {response.json()}")

def backup_recuperacao():
    st.title("Backup e Recuperação do Banco de Dados")

    opcao = st.selectbox("Selecione a ação", ["Backup do Banco de Dados", "Restaurar Banco de Dados"])

    if opcao == "Backup do Banco de Dados":
        st.write("Esta ação irá exportar todos os dados do banco de dados para um arquivo JSON e fazer o commit no GitHub.")
        if st.button("Fazer Backup"):
            json_dados = exportar_dados()
            conteudo_base64 = codificar_conteudo(json_dados)
            mensagem_commit = f"Backup automático em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            fazer_commit_github(conteudo_base64, mensagem_commit)

    elif opcao == "Restaurar Banco de Dados":
        st.write("Esta ação irá restaurar o banco de dados a partir do arquivo JSON no GitHub.")
        if st.button("Restaurar Dados"):
            restaurar_dados()

backup_recuperacao()
