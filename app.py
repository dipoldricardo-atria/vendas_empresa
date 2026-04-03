import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Comercial Tech", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Substitua pelo link que você copiou no Passo 1
URL_PLANILHA = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA"

conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler os dados da nuvem
def buscar_dados(aba):
    return conn.read(spreadsheet=URL_PLANILHA, worksheet=aba)

# --- SISTEMA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def tela_login():
    st.title("🚀 Portal Comercial - Tech")
    with st.sidebar:
        st.subheader("Login de Acesso")
        email = st.text_input("E-mail Corporativo")
        senha = st.text_input("Senha", type="password")
        if st.button("Acessar Painel"):
            df_users = buscar_dados("usuarios")
            # Verifica se e-mail e senha batem
            usuario = df_users[(df_users['email'] == email) & (df_users['senha'].astype(str) == senha)]
            if not usuario.empty:
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = usuario.iloc[0]
                st.rerun()
            else:
                st.error("Credenciais inválidas")

if not st.session_state['logged_in']:
    tela_login()
else:
    u = st.session_state['user_info']
    st.sidebar.success(f"Logado: {u['nome']}")
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- MENU DE NAVEGAÇÃO ---
    opcoes = ["Dashboard", "Cadastrar Venda", "Baixa de Pagamentos"] if u['perfil'] == "Admin" else ["Minhas Comissões"]
    menu = st.sidebar.radio("Navegação", opcoes)

    # --- ABA: DASHBOARD ---
    if menu == "Dashboard":
        st.title("📊 Painel de Controle (Diretoria)")
        st.divider() # Linha divisória segura
        
        df_v = buscar_dados("vendas")
        if not df_v.empty:
            total_fat = df_v[df_v['status'] == 'Pago']['valor'].sum()
            st.metric("Faturamento Total Realizado", f"R$ {total_fat:,.2f}")
            st.dataframe(df_v, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada na planilha ainda.")

    # --- ABA: CADASTRAR VENDA ---
    elif menu == "Cadastrar Venda":
        st.subheader("Inserir Novo Contrato")
        with st.form("nova_venda"):
            cliente = st.text_input("Nome do Cliente")
            v_total = st.number_input("Valor Total do Projeto", min_value=0.0)
            v_entrada = st.number_input("Valor de Entrada", min_value=0.0)
            parcelas = st.number_input("Nº de Parcelas Restantes", min_value=1, step=1)
            data_venda = st.date_input("Data da Venda", date.today())
            
            if st.form_submit_button("Gerar e Sincronizar"):
                # Aqui o sistema gera os dados e você cola na planilha
                st.success("Dados gerados! Para salvar na nuvem, você deve inserir no Google Sheets.")
                st.info("Nota: No Streamlit Cloud, a escrita direta exige configuração de API JSON.")