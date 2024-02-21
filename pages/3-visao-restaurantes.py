# bibliotecas necessárias

import pandas as pd
# cálculo distância entre pontos geográficos
from haversine import haversine 
# gráfico
import plotly.express as px
import plotly.graph_objects as go
# framework web dahsboard
import streamlit  as st

import datetime as dt

from PIL import Image
# mapa
import folium
# mapa no streamlit
from streamlit_folium import folium_static

import numpy as np

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽', layout='wide')

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
    lins = df['Festival'] != 'NaN'
    df = df.loc[lins, :]

    # 9. Limpeza coluna Time_taken tirando (min)
    df['Time_taken(min)'] = (df['Time_taken(min)'].apply(lambda x:x
                                                  .split('(min)')[1]))
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df



def distance(df, fig):
    if fig == False:
        # Colunas
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude']
        
        # Calculando distâncias em km e criando coluna da distância
        df['distance'] = df.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        
        avg_distance = np.round(df['distance'].mean(),2)
        return avg_distance

    else:
        # Colunas
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude']
        
        # Calculando distâncias em km e criando coluna da distância
        df['Distance_delivery_location'] = (df.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),                      (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1))
                        
        avg_distance = (df.loc[:, ['City', 'Distance_delivery_location']]
                           .groupby('City')
                           .mean()
                           .reset_index())
        
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['Distance_delivery_location'], pull=[0, 0.1, 0])])

        return fig



def avg_std_time_delivery(df, operation, festival):
    """ 
        Esta função calcula o tempo médio e o descio padrão do tempo de entrega.
        Parâmetros:
            Input: 
                - df: Dataframe com os dados necessários para o cálculo
                - op: Tipo de operação que pode ser calculado
                    'avg_time': calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo
            Output:
                - df: Dataframe com 2 colunas e 1 linha
    """
    df6 = (df.loc[:, ['Time_taken(min)','Festival']]
             .groupby('Festival')
             .agg({'Time_taken(min)': ['mean','std']}))
    df6.columns = ['avg_time','std_time']
    df6 = df6.reset_index()
    df6 = np.round(df6.loc[df6['Festival'] == festival, operation],2)
    
    return df6



def avg_std_time_graph(df):            
    #Seleção de linhas e colunas
    cols = ['Time_taken(min)','City']
    
    # Calculando
    df4 = df.loc[:, cols].groupby(['City']).agg({'Time_taken(min)':['mean', 'std']})
    
    # Renomeando as colunas
    df4.columns = ['avg_time','std_time']
    
    # Resetando index
    df4 = df4.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df4['City'], y=df4['avg_time'], error_y=dict(type='data', array=df4['std_time'])))

    fig.update_layout(barmode='group')

    return fig


def avg_std_time_on_traffic(df):

    #Seleção de linhas e colunas
    cols = ['Time_taken(min)','City','Road_traffic_density']
    
    # Calculando
    df5 = df.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']})
    
    # Renomeando as colunas
    df5.columns = ['avg_time','std_time']
    
    # Resetando index
    df5 = df5.reset_index()
    
    
    fig = px.sunburst(df5, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint= np.average(df5['std_time']))
    
    return fig


# ============ Inicio estrutura lógica ===============
# ====================================================
# Import dataset
# ====================================================
df_raw = pd.read_csv('train.csv')

# Fazendo uma cópia do dataframe lido:
df = df_raw.copy()

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

# Filtro de data
linhas_selecionadas2 = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas2, :]

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

# Filtro de trânsito
linhas_selecionadas3 = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas3, :]

st.sidebar.markdown("""---""")

st.sidebar.markdown(' ### Powered by Comunidade DS')


# ====================================================
# Layout Sreamlit
# ====================================================

st.header('Marketplace - Visão Restaurantes')

st.dataframe(df)

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container():
        st.markdown('Overall Metrics')

        col1, col2, col3 = st.columns(3)
        
        with col1:
            df1 = df.loc[:, 'Delivery_person_ID'].nunique()
            st.markdown('Entregadores')
            col1.metric('Qtde', df1)
            
        with col2:            
            st.markdown('Distância média: Cidade X Restaurante')
            avg_distance = distance(df, fig = False)
            col2.metric('Qtde', avg_distance)

        with col3:
            st.markdown('Tempo de entrega médio com festival')    
            df6 = avg_std_time_delivery(df, 'avg_time', 'Yes ')  
            col3.metric('Qtde', df6)

    with st.container():

        col1, col2, col3 = st.columns(3)
       
        with col1:
            st.markdown('Desvio padrão com festival')
            df6 = avg_std_time_delivery(df, 'std_time', 'Yes ')  
            col1.metric('Qtde', df6)

            
        with col2:
            st.markdown('Tempo de entrega médio sem festival')
            df6 = avg_std_time_delivery(df, 'avg_time', 'No ')  
            col2.metric('Qtde', df6)

           
        with col3:
            st.markdown('Desvio padrão sem festival')
            df6 = avg_std_time_delivery(df, 'std_time', 'No ')  
            col3.metric('Qtde', df6)    
        
    with st.container():

        st.markdown("""---""")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('###### Distribuição do tempo por cidade')
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('###### Tempo médio por tipo de entrega (tabela)')
            #Seleção de linhas e colunas
            cols = ['Time_taken(min)','Type_of_order']
            # Calculando
            df4 = df.loc[:, cols].groupby('Type_of_order').mean().reset_index()
            st.dataframe(df4, use_container_width=True)
       
    with st.container():
        st.markdown("""---""")
        st.markdown('##### Distribuição do Tempo')

        col1, col2 = st.columns(2)
        with col1:

            st.markdown('##### Distribuição da média por cidade')
            fig = distance(df, fig=True)
            st.plotly_chart(fig, use_container_width=True)
                    
        with col2:
            st.markdown('##### Tempo de entrega médio por cidade e tipo de trafego (Sunburst)')
            fig = avg_std_time_on_traffic(df)            
            st.plotly_chart(fig, use_container_width=True)





