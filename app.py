import streamlit as st

st.set_page_config(page_title="Gestão de Adolescentes", layout="wide")

st.title("Sistema de Gestão para Grupo de Adolescentes")

st.sidebar.title("Navegação")
page = st.sidebar.selectbox("Selecione a página", ["Cadastro", "Presença", "Aniversariantes", "Relatórios"])

if page == "Cadastro":
    import pages.cadastro
elif page == "Presença":
    import pages.presenca
elif page == "Aniversariantes":
    import pages.aniversariantes
elif page == "Relatórios":
    import pages.relatorios
