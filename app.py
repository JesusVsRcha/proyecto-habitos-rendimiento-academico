"""Punto de entrada y navegación del Avance 2."""
import streamlit as st

st.set_page_config(page_title="Hábitos diarios y rendimiento académico", page_icon="📊", layout="wide")
st.markdown("""
<style>
    .block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 3rem; }
</style>
""", unsafe_allow_html=True)
st.sidebar.title("Hábitos y GPA")
st.sidebar.caption("Ciencia de Datos · Avance 2")
pagina = st.navigation([
    st.Page("pages/1_problema_datos.py", title="1 · Problema y datos", default=True),
    st.Page("pages/2_eda.py", title="2 · EDA"),
    st.Page("pages/3_hallazgos.py", title="3 · Hallazgos"),
])
pagina.run()
