import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

# 1. Carregar os dados corrigidos (CSV)
def carregar_dados():
    veiculos = pd.read_csv('corrigido_broken_database_1.csv')
    marcas = pd.read_csv('corrigido_broken_database_2.csv')

    # Renomear a coluna 'id_marca_' para 'id_marca'
    veiculos = veiculos.rename(columns={'id_marca_': 'id_marca'})

    return veiculos, marcas

# 2. Análises para o relatório
def realizar_analises(veiculos, marcas):
    # Combinar as tabelas
    tabela_consolidada = veiculos.merge(marcas, left_on='id_marca', right_on='id_marca')
    
    # Análise 1: Marca com maior volume de vendas
    vendas_por_marca = tabela_consolidada.groupby('marca')['vendas'].sum()
    maior_vendas_marca = vendas_por_marca.idxmax()
    maior_vendas_valor = vendas_por_marca.max()

    # Análise 2: Veículo com maior e menor receita
    tabela_consolidada['receita'] = tabela_consolidada['vendas'] * tabela_consolidada['valor_do_veiculo']
    veiculo_maior_receita = tabela_consolidada.loc[tabela_consolidada['receita'].idxmax()]
    veiculo_menor_receita = tabela_consolidada.loc[tabela_consolidada['receita'].idxmin()]

    # Análise 3: Faixas de preço
    tabela_consolidada['faixa_preco'] = (tabela_consolidada['valor_do_veiculo'] // 10000) * 10000
    faixas_preco = tabela_consolidada.groupby('faixa_preco')['vendas'].sum()

    # Análise 4: Menores tickets médios por marca
    ticket_medio = tabela_consolidada.groupby('marca')['valor_do_veiculo'].mean()
    menores_tickets = ticket_medio.nsmallest(3)

    # Análise 5: Veículos mais vendidos
    mais_vendidos = tabela_consolidada.nlargest(5, 'vendas')

    # Análise 6: Receita total por marca
    receita_por_marca = tabela_consolidada.groupby('marca')['receita'].sum()

    return {
        "maior_vendas": (maior_vendas_marca, maior_vendas_valor),
        "maior_receita": veiculo_maior_receita,
        "menor_receita": veiculo_menor_receita,
        "faixas_preco": faixas_preco,
        "menores_tickets": menores_tickets,
        "mais_vendidos": mais_vendidos,
        "receita_por_marca": receita_por_marca
    }

# 3. Gerar gráficos
def gerar_graficos(faixas_preco, menores_tickets, receita_por_marca):
    # Gráfico de faixas de preço
    plt.figure(figsize=(8, 5))
    faixas_preco.plot(kind='bar', color='skyblue')
    plt.title('Vendas por Faixa de Preço')
    plt.xlabel('Faixa de Preço (R$)')
    plt.ylabel('Total de Vendas')
    plt.savefig('grafico_faixas_preco.png')
    plt.close()

    # Gráfico de menores tickets médios
    plt.figure(figsize=(8, 5))
    menores_tickets.plot(kind='bar', color='salmon')
    plt.title('Menores Tickets Médios por Marca')
    plt.xlabel('Marca')
    plt.ylabel('Ticket Médio (R$)')
    plt.savefig('grafico_menores_tickets.png')
    plt.close()

    # Gráfico de receita total por marca
    plt.figure(figsize=(8, 5))
    receita_por_marca.plot(kind='bar', color='lightgreen')
    plt.title('Receita Total por Marca')
    plt.xlabel('Marca')
    plt.ylabel('Receita Total (R$)')
    plt.savefig('grafico_receita_por_marca.png')
    plt.close()

# 4. Gerar tabela de veículos mais vendidos
def gerar_tabela_veiculos_mais_vendidos(mais_vendidos, c):
    data = [["Nome do Veículo", "Vendas"]]  # Cabeçalho da tabela
    for index, row in mais_vendidos.iterrows():
        data.append([row['nome'], row['vendas']])

    table = Table(data)
    table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))]))
    table.wrapOn(c, 100, 100)
    table.drawOn(c, 50, 100)  # Colocando a tabela na parte inferior

    return c

# 5. Gerar relatório PDF
def gerar_relatorio(analises):
    c = canvas.Canvas("relatorio_vendas.pdf", pagesize=letter)
    c.setFont("Helvetica", 12)
    
    # Título
    c.drawString(200, 750, "Relatório de Vendas - Análise Consolidada")

    # Análise 1
    c.drawString(50, 700, f"Marca com maior volume de vendas: {analises['maior_vendas'][0]} ({analises['maior_vendas'][1]} vendas)")

    # Análise 2
    c.drawString(50, 680, f"Veículo com maior receita: {analises['maior_receita']['nome']} (R$ {analises['maior_receita']['receita']})")
    c.drawString(50, 660, f"Veículo com menor receita: {analises['menor_receita']['nome']} (R$ {analises['menor_receita']['receita']})")

    # Gráficos de Análise
    c.drawString(50, 640, "Gráficos de Análise:")
    c.drawImage("grafico_faixas_preco.png", 50, 420, width=500, height=200)  # Ajustada a posição dos gráficos
    c.drawImage("grafico_menores_tickets.png", 50, 180, width=500, height=200)
    c.drawImage("grafico_receita_por_marca.png", 50, 640, width=500, height=200)

    # Adicionar Resumo de Insights
    c.setFont("Helvetica", 10)
    c.drawString(50, 120, "Resumo de Insights:")
    c.drawString(50, 100, f"A marca com maior volume de vendas é {analises['maior_vendas'][0]}, com {analises['maior_vendas'][1]} vendas.")
    c.drawString(50, 80, f"O veículo com maior receita foi {analises['maior_receita']['nome']}, com receita de R$ {analises['maior_receita']['receita']}.")

    # Adicionar nova página para a tabela de veículos mais vendidos
    c.showPage()  # Nova página no PDF

    # Adicionar tabela de veículos mais vendidos na nova página
    c = gerar_tabela_veiculos_mais_vendidos(analises["mais_vendidos"], c)

    c.save()
    print("Relatório gerado: relatorio_vendas.pdf")

# 6. Fluxo Principal
def main():
    veiculos, marcas = carregar_dados()
    analises = realizar_analises(veiculos, marcas)
    gerar_graficos(analises["faixas_preco"], analises["menores_tickets"], analises["receita_por_marca"])
    gerar_relatorio(analises)

if __name__ == "__main__":
    main()
