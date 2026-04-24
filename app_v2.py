
import ssl
import httpx
import pandas as pd
import math

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
# TELA 1: CATÁLOGO
# ==========================================
if menu == "🍷 Catálogo":
    st.title("🍷 Gestão de Catálogo")
    
    # Cria duas abas visuais na tela
    aba_manual, aba_planilha = st.tabs(["✍️ Cadastro Manual", "📦 Importação em Massa"])
    
    # ------------------------------------------
    # ABA 1: CADASTRO MANUAL (Seu código atual adaptado)
    # ------------------------------------------
    with aba_manual:
        st.subheader("Adicionar Novo Vinho")
        with st.form("form_novo_vinho", clear_on_submit=True):
            nome = st.text_input("Nome do Vinho*")
            produtor = st.text_input("Produtor*")
            tipo = st.selectbox("Tipo", ["Tinto", "Branco", "Rosé", "Espumante", "Laranja", "Sobremesa"])
            uva = st.text_input("Uva Principal")
            pais = st.text_input("País")
            regiao = st.text_input("Região")
            preco_venda_atual = st.number_input("Preço de Venda (R$)*", min_value=0.0, format="%.2f")
            custo = st.number_input (   "Preço de custo (R$)*", min_value=0.0, format="%.2f")
            prazo_fornecedor_dias = st.number_input("Prazo do fornecedor (dias)*", min_value=0, step=1,format="%d")
            
            submit_button = st.form_submit_button("Cadastrar Vinho")
            
            if submit_button:
                if nome and produtor and preco_venda_atual > 0:
                    try:
                        resp_sku = supabase.table("produtos").select("sku").order("sku", desc=True).limit(1).execute()
                        novo_sku = "A00001" if not resp_sku.data else f"A{int(resp_sku.data[0]['sku'].replace('A', '')) + 1:05d}"
                        
                        novo_vinho = {
                            "sku": novo_sku, "nome": nome, "produtor": produtor, "tipo": tipo,
                            "uva": uva, "pais": pais, "regiao": regiao, 
                            "preco_venda_atual": preco_venda_atual, "custo": custo, "prazo_fornecedor_dias": prazo_fornecedor_dias,
                            "estoque_total": 0
                        }
                        
                        supabase.table("produtos").insert(novo_vinho).execute()
                        st.success(f"Vinho '{nome}' cadastrado com o código {novo_sku}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.warning("Preencha Nome, Produtor e Preço corretamente.")

    # ------------------------------------------
    # ABA 2: IMPORTAÇÃO DE PLANILHA (Novo recurso)
    # ------------------------------------------
    with aba_planilha:
        st.subheader("Upload de Planilha (.xlsx)")
        st.markdown("**Regra:** A planilha deve ter cabeçalhos exatos na primeira linha: `nome`, `produtor`, `tipo`, `uva`, `pais`, `regiao`, `preco_venda_atual`, `estoque_total`,`custo`, `prazo_fornecedor_dias`.")
        
        arquivo_excel = st.file_uploader("Arraste seu arquivo Excel aqui", type=['xlsx'])
        
        if arquivo_excel is not None:
            try:
                # 1. Lê a planilha transformando em um DataFrame do Pandas
                df = pd.read_excel(arquivo_excel)
                
                # 2. Mostra uma prévia dos dados na tela para o usuário conferir
                st.write("Prévia dos dados encontrados:")
                st.dataframe(df.head())
                
                if st.button("Processar e Salvar no Banco"):
                    # 3. Validação de segurança básica das colunas obrigatórias
                    colunas_obrigatorias = ['nome', 'produtor', 'preco_venda_atual']
                    if not all(coluna in df.columns for coluna in colunas_obrigatorias):
                        st.error(f"Erro: A planilha deve conter pelo menos as colunas: {', '.join(colunas_obrigatorias)}")
                    else:
                        with st.spinner("Gerando SKUs e inserindo no banco..."):
                            # Descobre qual é o último SKU do banco para continuar a contagem
                            resp_sku = supabase.table("produtos").select("sku").order("sku", desc=True).limit(1).execute()
                            ultimo_numero = 0 if not resp_sku.data else int(resp_sku.data[0]['sku'].replace('A', ''))
                            
                            lote_vinhos = []
                            
                            # 4. Varre cada linha da planilha para montar os pacotes
                            # O preenchimento de 'fillna("")' evita que vazios quebrem o banco
                            df = df.fillna("") 
                            
                            for index, linha in df.iterrows():
                                ultimo_numero += 1
                                novo_sku = f"A{ultimo_numero:05d}"
                                
                                vinho = {
                                    "sku": novo_sku,
                                    "nome": str(linha['nome']),
                                    "produtor": str(linha['produtor']),
                                    "tipo": str(linha['tipo']) if 'tipo' in df.columns else "",
                                    "uva": str(linha['uva']) if 'uva' in df.columns else "",
                                    "pais": str(linha['pais']) if 'pais' in df.columns else "",
                                    "regiao": str(linha['regiao']) if 'regiao' in df.columns else "",
                                    "preco_venda_atual": float(linha['preco_venda_atual']),
                                    "estoque_total": int(linha['estoque_total']) if 'estoque_total' in df.columns and linha['estoque_total'] != "" else 0,
                                    "custo": int(linha['custo']) if 'custo' in df.columns and linha['custo'] != "" else 0,
                                    "prazo_fornecedor_dias": int(linha['prazo_fornecedor_dias'])if 'prazo_fornecedor_dias' in df.columns and linha ['prazo_fornecedor_dias'] != "" else 0
                                        }
                                lote_vinhos.append(vinho)
                            
                            # 5. BATCH INSERT: Manda a lista inteira de uma vez para o Supabase
                            supabase.table("produtos").insert(lote_vinhos).execute()
                            
                            st.success(f"✅ Sucesso! {len(lote_vinhos)} vinhos foram adicionados ao estoque.")
                            # Botão para limpar a tela e recarregar
                            if st.button("Atualizar Tela"):
                                st.rerun()
                                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a planilha: {e}")

# ==========================================
# TELA 2: CLIENTES
# ==========================================
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
#    st.info("A tela de cadastro de clientes será construída aqui.")
    
    # Cria duas abas visuais na tela
    aba_manual, aba_planilha = st.tabs(["✍️ Cadastro Manual", "📦 Importação em Massa"])
    
    # ------------------------------------------
    # ABA 1: CADASTRO MANUAL (Seu código atual adaptado)
    # ------------------------------------------
    with aba_manual:
        st.subheader("Adicionar Novo Cliente")
        with st.form("form_novo_cliente", clear_on_submit=True):
            nome_cli = st.text_input("Nome do Cliente*")
            email = st.text_input("E-mail*")
            telefone = st.text_input("Telefone")
            apelido = st.text_input("Apelido")
            endereco = st.text_input("Endereço")
            bairro = st.text_input("Bairro")
            cidade = st.text_input("Cidade")
            vip = st.bool_input("VIP*")
            
            submit_button = st.form_submit_button("Cadastrar Cliente")
            
            if submit_button:
                if nome_cli:
                    try:
                        resp_sku = supabase.table("clientes").select("cod_cli").order("cod_cli", desc=True).limit(1).execute()
                        novo_cod_cli = "A00001" if not resp_cod_cli.data else f"A{int(resp_cod_cli.data[0]['cod_cli'].replace('A', '')) + 1:05d}"
                        
                        novo_cli = {
                            "cod_cli": novo_cod_cli,
                            "nome_cli": nome_cli,
                            "email": email,
                            "telefone": telefone,
                            "apelido": apelido,
                            "endereco": endereco,
                            "bairro": bairro,
                            "cidade": cidade,
                            "vip": vip
                        }
                        
                        supabase.table("clientes").insert(novo_cli).execute()
                        st.success(f"Cliente '{nome}' cadastrado com o código {novo_cod_cli}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.warning("Preencha nome do cliente corretamente.")

    # ------------------------------------------
    # ABA 2: IMPORTAÇÃO DE PLANILHA (Novo recurso)
    # ------------------------------------------
    with aba_planilha:
        st.subheader("Upload de Planilha (.xlsx)")
        st.markdown("**Regra:** A planilha deve ter cabeçalhos exatos na primeira linha: `nome_cli`, èmail`, `telefone`, `apelido`, `endereco`, `bairro`, `cidade`, `vip`.")
        
        arquivo_excel = st.file_uploader("Arraste seu arquivo Excel aqui", type=['xlsx'])
        
        if arquivo_excel is not None:
            try:
                # 1. Lê a planilha transformando em um DataFrame do Pandas
                df = pd.read_excel(arquivo_excel)
                
                # 2. Mostra uma prévia dos dados na tela para o usuário conferir
                st.write("Prévia dos dados encontrados:")
                st.dataframe(df.head())
                
                if st.button("Processar e Salvar no Banco"):
                    # 3. Validação de segurança básica das colunas obrigatórias
                    colunas_obrigatorias = ['nome_cli', 'email', 'vip']
                    if not all(coluna in df.columns for coluna in colunas_obrigatorias):
                        st.error(f"Erro: A planilha deve conter pelo menos as colunas: {', '.join(colunas_obrigatorias)}")
                    else:
                        with st.spinner("Gerando SKUs e inserindo no banco..."):
                            # Descobre qual é o último SKU do banco para continuar a contagem
                            resp_sku = supabase.table("clientes").select("sku").order("sku", desc=True).limit(1).execute()
                            ultimo_numero = 0 if not resp_sku.data else int(resp_sku.data[0]['sku'].replace('A', ''))
                            
                            pasta_clientes = []
                            
                            # 4. Varre cada linha da planilha para montar os pacotes
                            # O preenchimento de 'fillna("")' evita que vazios quebrem o banco
                            df = df.fillna("") 
                            
                            for index, linha in df.iterrows():
                                ultimo_numero += 1
                                novo_cli = f"A{ultimo_numero:05d}"
                                
                                cliente = {
                                    "cod_cli": novo_cod_cli,
                                    "nome": str(linha['nome']),
                                    "email": str(linha['email']),
                                    "telefone": str(linha['telefone']) if 'tipo' in df.columns else "",
                                    "apelido": str(linha['apelido']) if 'apelido' in df.columns else "",
                                    "endereco": str(linha['endereco']) if 'endereco' in df.columns else "",
                                    "bairro": str(linha['bairro']) if 'bairro' in df.columns else "",
                                    "cidade": float(linha['cidade']) if 'cidade' in df.columns and linha['cidade'] != "" else 0,
                                    "vip": int(linha['vip'])
                                        }
                                pasta_clientes.append(clientes)
                            
                            # 5. BATCH INSERT: Manda a lista inteira de uma vez para o Supabase
                            supabase.table("clientes").insert(pasta_clientes).execute()
                            
                            st.success(f"✅ Sucesso! {len(pasta_clientes)} clientes foram adicionados ao estoque.")
                            # Botão para limpar a tela e recarregar
                            if st.button("Atualizar Tela"):
                                st.rerun()
                                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a planilha: {e}")


# ==========================================
# TELA 3: VENDAS
# ==========================================
elif menu == "🛒 Vendas":
    st.title("🛒 Registro de Vendas")
    st.info("O painel de registro de saídas será construído aqui.")
