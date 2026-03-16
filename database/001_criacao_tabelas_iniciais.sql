
-- 1. Tabela de Produtos (O Catálogo)
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    produtor VARCHAR (255) NOT NULL,
    tipo VARCHAR(50),
    pais VARCHAR(100),
    regiao VARCHAR(100),
    uva_principal VARCHAR(100),
    preco_venda_atual DECIMAL(10, 2) NOT NULL,
    estoque_total INTEGER DEFAULT 0
);

-- 2. Tabela de Clientes (O CRM)
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_contato TIMESTAMP
);

-- 3. Tabela de Entradas (Para calcular Ciclo de Pagamento e Estoque Parado)
CREATE TABLE entradas_estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER REFERENCES produtos(id),
    data_entrada DATE NOT NULL,
    quantidade_comprada INTEGER NOT NULL,
    quantidade_disponivel INTEGER NOT NULL,
    custo_unitario DECIMAL(10, 2) NOT NULL,
    prazo_pagamento_fornecedor_dias INTEGER NOT NULL
);

-- 4. Tabela de Vendas (Cabeçalho do Pedido)
CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(10, 2) NOT NULL,
    prazo_recebimento_cliente_dias INTEGER NOT NULL
);

-- 5. Tabela de Itens da Venda (Para saber exatamente qual vinho saiu)
CREATE TABLE itens_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER REFERENCES vendas(id),
    produto_id INTEGER REFERENCES produtos(id),
    quantidade INTEGER NOT NULL,
    preco_praticado DECIMAL(10, 2) NOT NULL
);