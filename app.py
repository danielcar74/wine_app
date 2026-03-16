import streamlit as st
from supabase import create_client, Client

# 1. Configuração visual da página
st.set_page_config(page_title="Gestão de Vinhos", page_icon="🍷", layout="wide")
st.title("🍷 Meu App de Vinhos")
st.write("Bem-vindo ao sistema de gestão de estoque e vendas!")

# 2. Credenciais do Supabase (Substitua pelas suas)
SUPABASE_URL = "COLE_SUA_URL_AQUI"
SUPABASE_KEY = "COLE_SUA_CHAVE_ANON_AQUI"

# 3. Função para conectar no banco (o cache evita que ele conecte toda hora e fique lento)
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# 4. A Mágica: Conectando e puxando os dados
try:
    supabase: Client = init_connection()
    st.success("✅ Conectado ao banco de dados com sucesso!")

    st.divider() # Cria uma linha separadora na tela
    st.subheader("📦 Meu Catálogo de Vinhos")

    # Isso é o equivalente a fazer um "SELECT * FROM produtos"
    resposta = supabase.table("produtos").select("*").execute()

    # Se tiver dados, mostra como uma tabela interativa na tela
    if resposta.data:
        st.dataframe(resposta.data, use_container_width=True)
    else:
        st.info("O catálogo está vazio. Vá no Supabase e cadastre seu primeiro vinho para vê-lo aqui!")

except Exception as e:
    st.error(f"Erro ao conectar no banco: {e}")