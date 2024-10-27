import streamlit as st
from database import Adolescente, session
import pandas as pd
from sqlalchemy import func

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
            # Verificar se já existe um usuário com o mesmo nome
            existe = session.query(Adolescente).filter(func.lower(Adolescente.nome) == nome.lower()).first()
            if existe:
                st.error("Já existe um adolescente cadastrado com este nome.")
            else:
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
                st.rerun()

def exibir_adolescentes():
    st.subheader("Lista de Adolescentes")

    # Filtros
    filtro_nome = st.text_input("Filtrar por nome")
    filtro_status = st.selectbox("Filtrar por status", ["Todos", "Ativo", "Inativo"])

    query = session.query(Adolescente)
    if filtro_nome:
        query = query.filter(Adolescente.nome.ilike(f"%{filtro_nome}%"))
    if filtro_status != "Todos":
        query = query.filter_by(status=filtro_status)

    data = pd.read_sql(query.statement, session.bind)
    if data.empty:
        st.info("Nenhum adolescente encontrado com os filtros aplicados.")
        return

    # Adicionar colunas para editar e excluir
    data['Editar'] = 'Editar'
    data['Excluir'] = 'Excluir'

    # Exibir tabela interativa
    st.table(data[['id', 'nome', 'data_nascimento', 'telefone', 'batizado_aguas', 'batizado_espirito', 'status']])

    # Selecionar adolescente para editar ou excluir
    adolescente_id = st.number_input("Digite o ID do Adolescente para Editar/Excluir", min_value=0, step=1)
    acao = st.selectbox("Ação", ["Selecionar", "Editar", "Excluir"])

    if acao == "Editar" and adolescente_id > 0:
        editar_adolescente(adolescente_id)
    elif acao == "Excluir" and adolescente_id > 0:
        excluir_adolescente(adolescente_id)

def editar_adolescente(adolescente_id):
    adolescente = session.query(Adolescente).filter_by(id=adolescente_id).first()
    if adolescente:
        with st.form(f"Editar Adolescente {adolescente.nome}"):
            nome = st.text_input("Nome", value=adolescente.nome)
            data_nascimento = st.date_input("Data de Nascimento", value=adolescente.data_nascimento)
            telefone = st.text_input("Telefone", value=adolescente.telefone)
            batizado_aguas = st.selectbox(
                "Batizado nas Águas", ["Sim", "Não"], index=0 if adolescente.batizado_aguas else 1
            ) == "Sim"
            batizado_espirito = st.selectbox(
                "Batizado no Espírito Santo", ["Sim", "Não"], index=0 if adolescente.batizado_espirito else 1
            ) == "Sim"
            status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if adolescente.status == "Ativo" else 1)
            submit = st.form_submit_button("Salvar")

            if submit:
                # Verificar se o novo nome já existe em outro registro
                existe = session.query(Adolescente).filter(
                    func.lower(Adolescente.nome) == nome.lower(), Adolescente.id != adolescente_id
                ).first()
                if existe:
                    st.error("Já existe um adolescente cadastrado com este nome.")
                else:
                    adolescente.nome = nome
                    adolescente.data_nascimento = data_nascimento
                    adolescente.telefone = telefone
                    adolescente.batizado_aguas = batizado_aguas
                    adolescente.batizado_espirito = batizado_espirito
                    adolescente.status = status
                    session.commit()
                    st.success("Adolescente atualizado com sucesso.")
                    st.rerun()
    else:
        st.error("Adolescente não encontrado.")

def excluir_adolescente(adolescente_id):
    adolescente = session.query(Adolescente).filter_by(id=adolescente_id).first()
    if adolescente:
        confirmar = st.checkbox(f"Confirmar exclusão de {adolescente.nome}")
        if confirmar:
            session.delete(adolescente)
            session.commit()
            st.success("Adolescente excluído com sucesso.")
            st.rerun()
    else:
        st.error("Adolescente não encontrado.")

adicionar_adolescente()
exibir_adolescentes()
