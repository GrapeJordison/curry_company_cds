# bibliotecas necessárias
import pandas as pd
# cálculo distância entre pontos geográficos
from haversine import haversine 
# gráfico
import plotly.express as px
import streamlit  as st
import datetime as dt
from PIL import Image
# mapa
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

# ====================================================
# Import dataset
# ====================================================
df_raw = pd.read_csv('train.csv')

# Fazendo uma cópia do dataframe lido:
df = df_raw.copy()

# ====================================================
# Funções
# ====================================================

def clean_code(df):    
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoçao dos dados NaN
        2. Mudança do tipo de coluna de dados 
        3. Remoçao dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)    
    
        Input: Dataframe
        Output: Dataframe
    """
    
    # 1. Convertendo a coluna 'Delivery_person_Age' de texto para número:
    linhas_selecionadas = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_selecionadas, :].copy()
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    
    # 2. Convertendo a coluna 'Delivery_person_Ratings' de texto para número decimal (float):
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    
    # 3. Convertendo a coluna 'Order_Date' de texto para data:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    
    # 4. Convertendo a coluna 'multiple_deliveries' de texto para inteiro:
    linhas_selecionadas = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_selecionadas, :].copy()
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    
    # 5. Removendo os espaços dentro de strings/texto/object:
    # df = df.reset_index(drop=True) # drop=True tira a nova coluna index do df
    # for i in range (len(df)):
     # df.loc[i, 'ID'] = df.loc[i, 'ID'].strip()
    
    # 6. Removendo os espaços sem precisar usar o laço for:
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    # Esse comando executa quase que instantaneamente.
    
    # 7. Limpeza de dados de mais colunas:
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()

    
    # 8. Removaendo NaN
    linhas_selecionadas = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_selecionadas, :]
    linhas_selecionadas = df['City'] != 'NaN '
    df = df.loc[linhas_selecionadas, :]

    return df
    


def order_metric(df):
    """ Esta função recebe uma dataframe com um agrupamento de colunas e seleção de linhas e cria um gráfico de barras.     
    """
    # 1. Quantidade de pedidos por dia.
    # colunas
    cols = ['ID', 'Order_Date']
    # selecao de linhas
    df1 = df.loc[:, cols].groupby('Order_Date').count().reset_index()
    # desenhar o grafico de linhas - Bibliotecas Gráficos
    fig = px.bar(df1, x='Order_Date', y='ID')
    
    return fig

def traffic_order_share(df):             

    # selecao colunas e linhas
    df3 = (df.loc[:, ['ID', 'Road_traffic_density']]
             .groupby('Road_traffic_density')
             .count()
             .reset_index())
                    
    # Criando coluna dos percentuais
    df3['entregas_perc'] = df3['ID'] / df3['ID'].sum()
                    
    # Grafico de pizza
    fig = px.pie(df3, values='entregas_perc', names='Road_traffic_density')
    return fig


def traffic_order_city(df):
                
    # separando colunas e linhas
    df4 = (df.loc[:, ['ID', 'City', 'Road_traffic_density']]
             .groupby(['City','Road_traffic_density'])
             .count()
             .reset_index())
    
    # Grafico de Bolhas
    fig = px.scatter(df4, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig


def order_by_week(df):
    # criar coluna da semana
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
    # seleção das colunas e linhas
    df2 = (df.loc[:, ['ID','week_of_year']]
             .groupby('week_of_year')
             .count()
             .reset_index())
    # Gráfico de linhas
    fig = px.line(df2, x='week_of_year', y='ID')
    return fig

def order_share_by_week(df):
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    
    # Quantidade orders ids por semana
    df5_week = (df.loc[:, ['ID', 'week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index())
    
    # Quantidade de entregadores por semana
    df5_entregadores = (df.loc[:, ['Delivery_person_ID', 'week_of_year']]
                          .groupby('week_of_year')
                          .nunique()
                          .reset_index())
    
    # NOVIDADE função merge entre dataframes, inner aprender no curso SQL
    df5 = pd.merge(df5_week, df5_entregadores, how='inner')
    
    # Adicionando coluna da divisão
    df5['order_by_deliver'] = df5['ID'] / df5['Delivery_person_ID']
    
    # Grafico de linhas
    fig = px.line(df5, x="week_of_year", y="order_by_deliver")

    return fig


def country_maps(df):
    # Separando linhas e colunas
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df6 = (df.loc[:, cols]
             .groupby(['City', 'Road_traffic_density'])
             .median()
             .reset_index())
    
    # Desenhando o map
    map = folium.Map()
    
    for index, location_info in df6.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'], 
                     location_info['Delivery_location_longitude']], 
                      popup = location_info[['City','Road_traffic_density']
                    ]).add_to(map)
    
    folium_static(map, width=1024, height=600)

    
# ============ Inicio estrutura lógica ===============
# ====================================================
# Limpando os dados
# ====================================================

df = clean_code(df)

# ====================================================
# Inicio códigos Streamlit
# ====================================================

# ====================================================
# Barra Lateral Streamlit
# ====================================================

# Imagem da barra lateral
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

# Informações barra lateral
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=dt.datetime( 2022, 4, 13 ),
    min_value=dt.datetime( 2022, 2, 11 ),
    max_value=dt.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])


# Filtro de data
linhas_selecionadas2 = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas2, :]

# Filtro de trânsito
linhas_selecionadas3 = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas3, :]


st.sidebar.markdown("""---""")
    
st.sidebar.markdown(' ### Powered by Comunidade DS')

# ====================================================
# Layout Sreamlit
# ====================================================

st.header('Marketplace - Visão Empresa')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        # Order metric
        st.markdown('# Orders by day')        
        fig = order_metric(df)
        st.plotly_chart(fig, use_content_width=True)


    with st.container():       
        # Dividindo user container em duas colunas
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('# Quantidade de Pedidos por Tipo de Tráfego')
            fig = traffic_order_share(df)
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            st.markdown('# Comparação do volume de pedidos por cidade e tipo de tráfego')
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True)
                          
with tab2:
    with st.container():
        st.markdown('# Quantidade de Pedidos por Semana')
        fig = order_by_week(df)
        st.plotly_chart(fig, use_content_width=True)        
        
        
    with st.container():
        st.markdown('# A quantidade de pedidos por entregador por semana.')
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_content_width=True)

with tab3:
    st.markdown('# Localização central de cada cidade por tipo de tráfego')
    country_maps(df)

    












