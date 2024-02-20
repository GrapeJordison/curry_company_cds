
# Bibliotecas
import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Home",
    page_icon="🎲",
    layout='wide'
)

#image_path = '/home/user/Documents/repos/python/Jupyter-lab/'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

# Imagem da barra lateral
#image = Image.open('logo.png')
#st.sidebar.image(image, width=120)

# Informações barra lateral
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown(' ### Powered by Comunidade DS')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Enpresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Aconpanhamento dos indicadores semanais de crescinento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
    - @meigarom
    """)
