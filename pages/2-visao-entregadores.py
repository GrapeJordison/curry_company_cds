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

st.set_page_config(page_title='Visão Entregadores', page_icon='🏍', layout='wide')

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

    # 9. Limpeza coluna Time_taken tirando (min)
    df['Time_taken(min)'] = (df['Time_taken(min)'].apply(lambda x:x
                                                  .split('(min)')[1]))
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df


def top_delivers(df, ascendancy):
    df7 = (df.loc[:, ['Delivery_person_ID','Time_taken(min)','City']]
             .groupby(['City', 'Delivery_person_ID']).mean()
             .sort_values(['City', 'Time_taken(min)'], ascending=ascendancy)
             .reset_index())
    
    df7_1 = df7.loc[df7['City'] == 'Metropolitian', :].head(10)
    df7_2 = df7.loc[df7['City'] == 'Urban', :].head(10)
    df7_3 = df7.loc[df7['City'] == 'Semi-Urban', :].head(10)
    
    df7 = pd.concat([df7_1, df7_2, df7_3]).reset_index(drop=True)
    
    return df7

# ============ Inicio estrutura lógica ===============
# ====================================================
# Import dataset
# ====================================================
df_raw = pd.read_csv('../datasets/train.csv')

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

st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container():
        
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        
        
        with col1:
            # A maior idade dos entregadores
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            # A menor idade dos entregadores
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)

        with col3:
            # A melhor condição do veículo
            melhor_condicao = df.loc[:, 'Vehicle_condition'].min()
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4:
            # A pior condição do veículo
            pior_condicao = df.loc[:, 'Vehicle_condition'].max()
            col4.metric('Pior condição', pior_condicao)
            
    
    with st.container():
        st.markdown("""---""")
        st.title(' Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('###### A avaliação média por entregador.')
            # Seleção de colunas e linhas

            df3 = (df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                     .groupby('Delivery_person_ID').mean().reset_index())

            st.dataframe(df3)      
        
        with col2:
            st.markdown('###### A avaliação média e o desvio padrão por tipo de tráfego.')
            # FUNÇÃO de agregação "agg"
            df4 = ( df.loc[:, ['Road_traffic_density','Delivery_person_Ratings']]
                      .groupby('Road_traffic_density')
                      .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudança de nome das colunas
            df4.columns = ['delivery_mean', 'delivery_std']

            # Reset do index
            df4 = df4.reset_index()

            st.dataframe(df4)
            
            st.markdown('###### A avaliação média e o desvio padrão por condições climáticas.')
            # FUNÇÃO de agregação "agg"
            # .agg ( { <coluna que recebe a operação: uma lista de operação a ser aplicado})

            df5 = (df.loc[:, ['Weatherconditions','Delivery_person_Ratings']]
                     .groupby('Weatherconditions')
                     .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudança de nome das colunas
            df5.columns = ['delivery_mean', 'delivery_std']

            # Reset do index
            df5 = df5.reset_index()

            st.dataframe(df5)


    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Os 10 entregadores mais rápidos por cidade.')
            df7 = top_delivers(df, ascendancy=True)
            st.dataframe(df7)

        with col2:
            st.markdown(' ##### Os 10 entregadores mais lentos por cidade.')
            df7 = top_delivers(df, ascendancy=False)
            st.dataframe(df7)



            

            




