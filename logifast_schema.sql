-- 1. Cria o banco de dados do projeto LogiFast Retail
CREATE DATABASE logifast_db;
USE logifast_db;

-- 2. Tabela de Dimensão: Clientes
CREATE TABLE dim_clientes (
    cliente_id VARCHAR(10) PRIMARY KEY,
    regiao_sp VARCHAR(100),
    tipo_cliente VARCHAR(50)
);

-- 3. Tabela de Dimensão: Produtos
CREATE TABLE dim_produtos (
    produto_id VARCHAR(10) PRIMARY KEY,
    nome_produto VARCHAR(100),
    categoria VARCHAR(50),
    preco_unitario DECIMAL(10,2)
);

-- 4. Tabela Fato: Vendas
CREATE TABLE fato_vendas (
    pedido_id VARCHAR(10) PRIMARY KEY,
    cliente_id VARCHAR(10),
    produto_id VARCHAR(10),
    quantidade INT,
    valor_total DECIMAL(10,2),
    data_pedido DATETIME,
    data_entrega DATETIME,
    tempo_entrega_horas DECIMAL(5,2),
    status_pedido VARCHAR(50),
    FOREIGN KEY (cliente_id) REFERENCES dim_clientes(cliente_id),
    FOREIGN KEY (produto_id) REFERENCES dim_produtos(produto_id)
);