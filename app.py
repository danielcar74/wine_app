
import ssl
import httpx

# Tenta forçar o Python a não verificar os certificados de segurança da rede
ssl._create_default_https_context = ssl._create_unverified_context

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
        with st.form("form_novo_vinho", clear_on_submit=True):
            # O campo SKU sumiu daqui! A rotina faz sozinha.
            nome = st.text_input("Nome do Vinho*")
            produtor = st.text_input("Nome do Produtor")
            tipo = st.selectbox("Tipo", ["Tinto", "Branco", "Rosé", "Espumante", "Laranja", "Sobremesa"])
            pais = st.text_input("País")
            regiao = st.text_input("Região do produtor")
            uva = st.text_input("Uvas")
            preco_venda_atual = st.number_input("Preço de Venda (R$)*", min_value=0.0, format="%.2f")
            
            
            submit_button = st.form_submit_button("Cadastrar Vinho")
            
            if submit_button:
                if nome and preco > 0:
                    try:
                        # 1. O CÉREBRO DO SKU: Busca o último cadastrado
                        # Ordena de Z a A e pega só o primeiro (limit 1)
                        resp_sku = supabase.table("produtos").select("sku").order("sku", desc=True).limit(1).execute()
                        
                        if not resp_sku.data:
                            novo_sku = "A00001" # Se a tabela estiver vazia, é o primeiro!
                        else:
                            ultimo_sku = resp_sku.data[0]["sku"] # Ex: "A00004"
                            numero = int(ultimo_sku.replace("A", "")) # Tira a letra e vira número (4)
                            novo_sku = f"A{numero + 1:05d}" # Soma 1 e devolve os zeros (A00005)
                        
                        # 2. Prepara o pacote com o SKU gerado automaticamente
                        novo_vinho = {
                            "sku": novo_sku,
                            "nome": nome,
                            "produtor": produtor,
                            "tipo": tipo,
                            "pais": pais,
                            "região": regiao,
                            "uva": uva,
                            "preco_venda_atual": preco_venda_atual,
                            "estoque_total": 0
                        }
                        
                        # 3. Salva no banco
                        supabase.table("produtos").insert(novo_vinho).execute()
                        st.success(f"Vinho '{nome}' cadastrado com o código {novo_sku}!")
                        st.rerun() # Atualiza a tela
                        
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.warning("Preencha o Nome e Preço corretamente.")

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
