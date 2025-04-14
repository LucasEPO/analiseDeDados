import streamlit as sl
import pandas as pd
import plotly.express as px
import seaborn as sns

PERIODOS_DIA = ['Manhã', 'Tarde', 'Noite', 'Madrugada']
CORES = {
    'Manhã': 'yellow',
    'Tarde': 'orangered',
    'Noite': 'midnightblue',
    'Madrugada': 'gray'
}

df = sns.load_dataset('taxis')

# Funcao para definir qual periodo a corrida aconteceu
def get_period(hour):
    if 5 <= hour < 12:
        return PERIODOS_DIA[0]
    elif 12 <= hour < 18:
        return PERIODOS_DIA[1]
    elif 18 <= hour < 24:
        return PERIODOS_DIA[2]
    else:
        return PERIODOS_DIA[3]

# Cria a coluna periodo dia utilizando a funcao passando o hora
df['periodo dia'] = df['pickup'].dt.hour.apply(get_period)

# Cria um filtro na sidebar do tipo multiselect para selecionar o periodo do dia
periodoFiltro = sl.sidebar.multiselect(
    label='Período do dia:',
    options=PERIODOS_DIA,
    default=PERIODOS_DIA,
)

# Garante que não vai dar erro caso nenhum periodo seja selecionado
if len(periodoFiltro) > 0:
    #aplica o filtro de periodo
    dfFiltrado = df[df['periodo dia'].isin(periodoFiltro)]
else:
    dfFiltrado = df

# Pega a menor e a maior data na coluna pickup do dataset
min_data = dfFiltrado['pickup'].min().date()
max_data = dfFiltrado['pickup'].max().date()

dataRange = (min_data, max_data)

sl.sidebar.divider()

# Checkbox que serve para voltar rapidamente para todas as datas selecionadas
## a depender da escolha dela o filtro de data ativa ou desativa
todasDatas = sl.sidebar.checkbox(
    label='Todos as datas',
    value=True
)

# Filtro de data no sidebar
dataFiltro = sl.sidebar.date_input(
    label='Datas Entre:',
    value=dataRange,
    min_value=min_data,
    max_value=max_data,
    disabled= todasDatas
)

sl.sidebar.divider()

# Texto no rodape da sidebar
sl.sidebar.markdown(
    """
    <div style='font-size: 0.8em; opacity: 0.6; text-align: right; padding-top: 380px;'>
        Criado por <b>Lucas Eduardo</b>
    </div>
    """,
    unsafe_allow_html=True
)

# Garante que nao vai ter problemas enquanto seleciona o filtro
if not todasDatas:
    if len(dataFiltro) == 2:
        dataFiltroInicio, dataFiltroFim = dataFiltro
    elif len(dataFiltro) == 1:
        dataFiltroInicio = dataFiltro[0]
        dataFiltroFim = max_data
else:
    dataFiltroInicio, dataFiltroFim = dataRange

# Aplica o filtro de data
dfFiltrado = dfFiltrado[df['pickup'].dt.date.between(dataFiltroInicio, dataFiltroFim)]

# fig1 = grafico de dispersão
## attr
## data_frame           = dados a serem exibidos
## x                    = coluna no eixo x
## y                    = coluna no eixo y
## color                = coluna pelo qual sera dividido as cores
## color_discrete_map   = dicionario de cores
## trendline            = tipo da linha de tendencia
## title                = titulo do grafico
## labels               = rotulos dos eixos
fig1 = px.scatter(
    data_frame = dfFiltrado,
    x = 'distance',
    y = 'fare',
    color = 'periodo dia',
    color_discrete_map=CORES,
    trendline = 'ols',
    title = 'Relação tarifa por distância e periodo do dia',
    labels = {'fare': 'Tarifa', 'distance': 'Distancia da Corrida'}
)

# Mostra as linhas tracegadas para o hover
fig1.update_xaxes(showspikes=True)
fig1.update_yaxes(showspikes=True)

# Cria coluna hora para fig2
dfFiltrado['hora'] = pd.to_datetime(dfFiltrado['pickup']).dt.hour
# Agrupa por horas e bairros de origem guardando na coluna qtd corridas
dfHoras = dfFiltrado.groupby(['hora', 'pickup_borough']).size().reset_index(name='qtd corridas')

# fig2 = grafico de linha
## attr
## data_frame           = dados a serem exibidos
## x                    = coluna no eixo x
## y                    = coluna no eixo y
## color                = coluna pelo qual sera dividido as cores
## title                = titulo do grafico
## labels               = rotulos dos eixos
## template             = cores predefindas 
## height               = forca a altura máxima
fig2 = px.line(
    data_frame = dfHoras,
    x = 'hora',
    y = 'qtd corridas',
    color = 'pickup_borough',
    title = 'Volume de corridas por hora e por região',
    labels = {
        'hora': 'Hora do Dia',
        'qtd corridas': 'Quantidade de Corridas',
        'pickup_borough': 'Região'
    },
    template = 'plotly_dark',
    height = 300
)

# Garante q o template de hover n tenha nada
fig2.update_traces(
    hovertemplate = None,
)

# Atualiza o layout para q no eixo x as horas sejam marcadas de uma por uma
## define o tipo de hover para mostrar um hover unico para todas linhas em um x
fig2.update_layout(
    xaxis = dict(dtick=1),
    hovermode = 'x unified'
)

# Agrupa por bairro de origem e periodo do dia, guarda numa coluna qtd corridas e ordena por ela
dfCounts = dfFiltrado.groupby(['pickup_borough', 'periodo dia']).size().reset_index(name='qtd corridas').sort_values('qtd corridas', ascending=True)
#  Soma o total de corridas por bairro de origem e ordena do menor para o maior e guarda a ordem dos bairros
ordemRegioes = dfCounts.groupby('pickup_borough')['qtd corridas'].sum().sort_values().index
# Transforma a coluna 'pickup_borough' em uma categoria ordenada com base na ordem calculada
dfCounts['pickup_borough'] = pd.Categorical(dfCounts['pickup_borough'], categories=ordemRegioes, ordered=True)
# Ordena com base na nova ordem de categorias
dfCounts = dfCounts.sort_values('pickup_borough')

# fig3 = grafico de linha
## attr
## data_frame           = dados a serem exibidos
## x                    = coluna no eixo x
## y                    = coluna no eixo y
## color                = coluna pelo qual sera dividido as cores
## color_discrete_map   = dicionario de cores
## title                = titulo do grafico
## labels               = rotulos dos eixos
## barmode              = estilo de distribuicao das grupos q formam as barras
fig3 = px.bar(
    data_frame = dfCounts,
    x = 'qtd corridas',
    y = 'pickup_borough',
    color = 'periodo dia',
    color_discrete_map = CORES,
    orientation = 'h',
    title = 'Total de corridas por região e periodo de dia',
    labels = {'pickup_borough': 'Bairro de Origem', 'qtd corridas': 'Quantidade de Corridas'},
    barmode = 'group'
)

# Soma a coluna de passageiros quando estao numa mesma zona de origem
dfPassageiros = dfFiltrado.groupby('pickup_zone')['passengers'].sum().reset_index()

# fig2 = grafico de linha
## attr
## data_frame           = dados a serem exibidos
## x                    = coluna no eixo x
## y                    = coluna no eixo y
## title                = titulo do grafico
## color                = coluna pelo qual sera dividido as cores
## template             = cores predefindas 
## labels               = rotulos dos eixos
fig4 = px.bar(
    dfPassageiros,
    x = 'pickup_zone',
    y = 'passengers',
    title = 'Total de Passageiros por Zona de Origem',
    color = 'pickup_zone', 
    template = 'plotly_dark',
    labels = {'passengers': 'Total de Passageiros', 'pickup_zone': 'Zona de Origem'}
)

# Atualiza o layout removendo a legenda deste grafico
fig4.update_layout(showlegend=False)

# Plot de graficos
# Plota a fig 2
sl.plotly_chart(fig2, use_container_width=True)
# Divide em 2 colunas
col1, col2 = sl.columns(2)
# Plota a fig 4
sl.plotly_chart(fig4, use_container_width=True)
# Adiciona um divisor na pag
sl.divider()
# Mostra o dataframe filtrado
dfFiltrado

# Plota os graficos fig1 e fig3 nas colunas que foram separadas
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig3, use_container_width=True)