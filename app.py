import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="PedidosYa Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("PedidosYa Control Tower")

st.caption("Versión 1.0")

with st.sidebar:

    pagina = option_menu(

        None,

        [

            "Resumen Ejecutivo",

            "Operación ST",

            "Loss Tree",

            "Analytics",

            "Configuración"

        ],

        icons=[

            "speedometer2",

            "boxes",

            "bar-chart",

            "graph-up",

            "gear"

        ],

        default_index=0

    )

if pagina=="Resumen Ejecutivo":

    st.header("Dashboard Ejecutivo")

elif pagina=="Operación ST":

    st.header("Operación ST")

elif pagina=="Loss Tree":

    st.header("Loss Tree")

elif pagina=="Analytics":

    st.header("Analytics")

elif pagina=="Configuración":

    st.header("Configuración")
