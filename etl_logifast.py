from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# 1. CONFIGURAÇÕES E CREDENCIAIS
# ==========================================
# Insira abaixo a senha do seu MySQL Workbench
SENHA_MYSQL = "SUA_SENHA_AQUI"
DB_NAME = "logifast_db"

print("🔄 [ETL] Iniciando o pipeline de dados da LogiFast Retail...")

# Semente de aleatoriedade para garantir que os dados sejam reprodutíveis
np.random.seed(42)
random.seed(42)

NUM_REGISTROS = 1500  # Quantidade de vendas simuladas

# ==========================================
# 2. GERAÇÃO DA DIMENSÃO: CLIENTES
# ==========================================
bairros_sp = [
    'Centro', 'Moema', 'Pinheiros', 'Tatuapé',
    'Itaquera', 'Santo Amaro', 'Lapa', 'Santana'
]
clientes_ids = [f'CLI{str(i).zfill(4)}' for i in range(1, 201)]

df_clientes = pd.DataFrame({
    'cliente_id': clientes_ids,
    'regiao_sp': [random.choice(bairros_sp) for _ in range(200)],
    'tipo_cliente': np.random.choice(['Varejo', 'Atacado'], size=200, p=[0.8, 0.2])
})

# ==========================================
# 3. GERAÇÃO DA DIMENSÃO: PRODUTOS
# ==========================================
categorias = {
    'Eletrônicos': [('Fone Bluetooth', 150.0), ('Carregador Rápido', 80.0), ('Smartwatch', 350.0)],
    'Alimentos/Laticínios': [('Kit Iogurtes Premium', 45.0), ('Queijo Artesanal 500g', 38.0), ('Manteiga Extra', 22.0)],
    'Acessórios': [('Mochila Impermeável', 180.0), ('Suporte Celular Moto', 55.0), ('Capa Protetora', 30.0)]
}

produtos_data = []
prod_id_counter = 1
for cat, prods in categorias.items():
    for nome, preco in prods:
        produtos_data.append({
            'produto_id': f'PROD{str(prod_id_counter).zfill(3)}',
            'nome_produto': nome,
            'categoria': cat,
            'preco_unitario': preco
        })
        prod_id_counter += 1

df_produtos = pd.DataFrame(produtos_data)

# ==========================================
# 4. GERAÇÃO DA TABELA FATO: VENDAS
# ==========================================
data_inicio = datetime(2026, 1, 1)
datas_pedido = [
    data_inicio + timedelta(days=random.randint(0, 290), hours=random.randint(8, 20))
    for _ in range(NUM_REGISTROS)
]

pedidos_data = []
for i in range(NUM_REGISTROS):
    prod = df_produtos.sample(1).iloc[0]
    # Laticínios costumam ter maior volume por pedido
    qtd = random.randint(1, 10) if prod['categoria'] == 'Alimentos/Laticínios' else random.randint(1, 3)
    dt_ped = datas_pedido[i]

    status = np.random.choice(['Entregue', 'Cancelado', 'Em Trânsito'], p=[0.88, 0.07, 0.05])

    if status == 'Entregue':
        tempo_entrega_h = round(random.uniform(1.5, 48.0), 2)
        dt_ent = dt_ped + timedelta(hours=tempo_entrega_h)
    else:
        tempo_entrega_h = None
        dt_ent = None

    pedidos_data.append({
        'pedido_id': f'PED{str(i + 1).zfill(5)}',
        'cliente_id': random.choice(clientes_ids),
        'produto_id': prod['produto_id'],
        'quantidade': qtd,
        'valor_total': round(qtd * prod['preco_unitario'], 2),
        'data_pedido': dt_ped.strftime('%Y-%m-%d %H:%M:%S'),
        'data_entrega': dt_ent.strftime('%Y-%m-%d %H:%M:%S') if dt_ent else None,
        'tempo_entrega_horas': tempo_entrega_h,
        'status_pedido': status
    })

df_vendas = pd.DataFrame(pedidos_data)
print("✅ [ETL] Dados gerados e transformados com sucesso em memória!")

# ==========================================
# 5. CARGA DOS DADOS NO MYSQL (LOAD)
# ==========================================
try:
    # Cria a string de conexão usando PyMySQL
    connection_string = f'mysql+pymysql://root:{SUASENHAAQUI}@localhost:3306/{DB_NAME}'
    engine = create_engine(connection_string)

    # Inserção nas tabelas respeitando a estrutura do banco
    df_clientes.to_sql('dim_clientes', con=engine, if_exists='append', index=False)
    df_produtos.to_sql('dim_produtos', con=engine, if_exists='append', index=False)
    df_vendas.to_sql('fato_vendas', con=engine, if_exists='append', index=False)

    print("🚀 [ETL] Carga finalizada com sucesso! Tabelas populadas no MySQL.")

except Exception as e:
    print(f"❌ [ETL] Erro durante a conexão ou carga no MySQL: {e}")
    