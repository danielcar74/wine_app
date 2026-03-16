import streamlit as st
from supabase import create_client, Client

# 1. Configuração visual da página
st.set_page_config(page_title="Gestão de Vinhos", page_icon="🍷", layout="wide")

# 2. Credenciais do Supabase
SUPABASE_URL = "https://rbshwryibzdxuzzbjcdx.supabase.co"
SUPABASE_KEY = "sb_publishable_vMCnLOxnqW4Y0nUvg6RLBw_rV3JT08Q"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# 3. Menu Lateral (A Navegação do App)
st.sidebar.title("Navegação")
menu = st.sidebar.radio("Escolha a tela:", ["🍷 Catálogo", "👥 Clientes", "🛒 Vendas"])

# ==========================================
# TELA 1: CATÁLOGO DE VINHOS
# ==========================================
if menu == "🍷 Catálogo":
    st.title("📦 Gestão do Catálogo")
    
    # Divide a tela em duas colunas (Esquerda menor, Direita maior)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Adicionar Novo Vinho")
        # Cria um formulário para empacotar os dados antes de enviar
        with st.form("form_novo_vinho", clear_on_submit=True):
            sku = st.text_input("SKU (Código único)*")
            nome = st.text_input("Nome do Vinho*")
            tipo = st.selectbox("Tipo", ["Tinto", "Branco", "Rosé", "Espumante", "Laranja", "Sobremesa"])
            pais = st.text_input("País")
            preco = st.number_input("Preço de Venda (R$)*", min_value=0.0, format="%.2f")
            
            # O botão que dispara a ação
            submit_button = st.form_submit_button("Cadastrar Vinho")
            
            if submit_button:
                if sku and nome and preco > 0:
                    # Empacota os dados do jeito que o Supabase espera (JSON)
                    novo_vinho = {
                        "sku": sku,
                        "nome": nome,
                        "tipo": tipo,
                        "pais": pais,
                        "preco_venda_atual": preco,
                        "estoque_total": 0
                    }
                    try:
                        # Comando de INSERT no banco
                        supabase.table("produtos").insert(novo_vinho).execute()
                        st.success(f"Vinho '{nome}' cadastrado!")
                        st.rerun() # Atualiza a tela para mostrar o vinho na tabela
                    except Exception as e:
                        st.error("Erro: O SKU já existe ou houve falha na conexão.")
                else:
                    st.warning("Preencha SKU, Nome e Preço corretamente.")

    with col2:
        st.subheader("Vinhos Cadastrados")
        try:
            # Comando de SELECT no banco
            resposta = supabase.table("produtos").select("sku, nome, tipo, pais, preco_venda_atual, estoque_total").execute()
            if resposta.data:
                # Exibe os dados em uma tabela interativa
                st.dataframe(resposta.data, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum vinho cadastrado. Use o formulário ao lado!")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

# ==========================================
# TELA 2: CLIENTES
# ==========================================
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
    st.info("A tela de cadastro de clientes será construída aqui.")

# ==========================================
# TELA 3: VENDAS
# ==========================================
elif menu == "🛒 Vendas":
    st.title("🛒 Registro de Vendas")
    st.info("O painel de registro de saídas será construído aqui.")