import streamlit as st
import pandas as pd

# --- Estilos personalizados ---
st.markdown(
    """
    <style>
    body {
        background-color: #fff5e6;
        color: #333;
    }
    .stApp {
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #cc5500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📑 Convenios con Prestadores")
st.write("Subí el Excel de convenios y la base de cruce para procesar los datos.")

# --- Subir archivos ---
file_convenios = st.file_uploader("Cargar Excel de convenios", type=["xlsx"])
file_cruce = st.file_uploader("Cargar Excel de cruce", type=["xlsx"])

if file_convenios and file_cruce:
    # Leer archivos
    df_conv = pd.read_excel(file_convenios, skiprows=5)  # ajusta skiprows según tu archivo
    df_cruce = pd.read_excel(file_cruce)

    st.subheader("Vista previa - Convenios")
    st.dataframe(df_conv.head())

    st.subheader("Vista previa - Base de Cruce")
    st.dataframe(df_cruce.head())

    # Merge (ejemplo: unir por código de práctica)
    df_merged = df_conv.merge(
        df_cruce,
        left_on="Practica/Rango/Unidad",
        right_on="CodigoOriginal",
        how="left"
    )

    st.subheader("Resultado del Cruce")
    st.dataframe(df_merged.head(20))

    # Descargar resultado
    @st.cache_data
    def convert_excel(df):
        return df.to_excel(index=False, engine="openpyxl")

    st.download_button(
        label="📥 Descargar resultado en Excel",
        data=convert_excel(df_merged),
        file_name="resultado_cruce.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
