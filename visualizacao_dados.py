import streamlit as sl
import pandas as pd
import plotly.express as px
from datetime import datetime

df = pd.read_csv('dataset_mercado.csv')

#função que classifica se o produto está valido, vencendo o vencido
def statusValidade(data):
    if data < datetime.today():
        return 'Vencido'
    elif data.month == datetime.today().month and data.year == datetime.today().year:
        return 'Vencendo'
    else:
        return 'Válido'

#conversão para datetime pois dtypes estava retornando Object
df['validade'] = pd.to_datetime(df["validade"])

#calculo do valor total de cada produto
df['valor total'] = df['valor'] * df['estoque']

#adiciona coluna com status da validade
df['status validade'] = df['validade'].apply(statusValidade)

#agrupar por status da validade depois soma a coluna valor total do grupo
#reset index apenas adiciona coluna index padrao do datafram resetado no inicio
dfGroup = df.groupby('status validade')['valor total'].sum().reset_index()

listaProdutos = df.groupby('status validade')['produto'].apply(
    lambda prod: ',<br>'.join(
        [', '.join(prod[i:i+3]) for i in range(0, len(prod), 3)]
    )
)

#adiciona a coluna de lista de produtos no agrupamento
dfGroup = dfGroup.merge(listaProdutos, on='status validade')

#renomeia a coluna
dfGroup.rename(columns={'produto': 'lista produtos'}, inplace=True)

#soma de todos totais (100% no grafico pizza)
total = sum(df['valor total'])

#cores para o gráfico
cores = {
    'Válido': 'green',
    'Vencendo': 'gold',
    'Vencido': 'red'
}

#construção do grafico
##attr
## dataframe            = agrupamentos
## names                = nome da coluna que define as categorias
## values               = nome da coluna que define o tamanho dos pedaços
## title                = titulo do grafico
## color                = coluna pelo qual será dividido as cores
## color_discrete_map   = dicionario de cores personalizado
## custom_data          = colunas passados para trabalhar no hover
## hover_name           = coluna onde tem valor para titulo no hover tooltip
## hole                 = valor para transformar gráfico pizza em donut
fig = px.pie(
    data_frame=dfGroup,
    names="status validade",
    values="valor total",
    title="Distribuição do Valor Total em Estoque por Status de Validade",
    color="status validade",
    color_discrete_map=cores,
    custom_data=["valor total", "lista produtos"],
    hover_name='status validade',
    hole=0.4
)

#Atualiza layout geral do gráfico
## title        = atualizando tamanho do titulo do gráfico
## legend       = atualizando tamanho da legenda do gráfico
## annotations  = Colocando anotação na posição desejada
fig.update_layout(
    title=dict(font=dict(size=24)),
    legend=dict(font=dict(size=24)),
    annotations=[
        dict(
            text=f"<b>Valor Total:</b> R$ {total:,.2f}",
            x=0,
            y=1.15,
            showarrow=False,
            font=dict(size=20),
        )
    ],
)

# Modifica estilos de cada fatia
## textfont         = atualiza tamanho da fonte dentro da fatia
## textinfo         = escolhe o que será mostrado em cada fatia
## hovertemplate    = define o que será mostrado no hover tooltip
## hoverlabel       = atualiza tamanho da fonte do titulo do hover
fig.update_traces(
    textfont=dict(size=18),
    textinfo="percent",
    hovertemplate="<b>%{label}</b><br><br>" +
                  "<b>Valor total:</b> R$ %{customdata[0][0]}<br>" +
                  "<b>Produtos:</b> %{customdata[0][1]}<extra></extra>",
    hoverlabel=dict(font_size=16),
)

#Plota o gráfico
## use_container_width = atributo necessário quando há mais de um gráfico na tela
##q garante o gráfico não ficar cortado ou mal posicionado
sl.plotly_chart(fig, use_container_width=True)

### EXECUTAR STREAMLIT PARA VER O GRÁFICO
### streamlit run visualizacao_dados.py