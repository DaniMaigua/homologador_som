import streamlit as st
import pandas as pd
import os
from io import BytesIO

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
st.write("Subí el Excel de convenios. La base de cruce se carga solo una vez por el administrador.")

# --- Ruta donde se guarda la base ---
BASE_FILE = "base_cruce.csv"

# --- Zona admin ---
st.sidebar.subheader("🔐 Zona de administrador")
password = st.sidebar.text_input("Contraseña admin", type="password")

if password == "admin123":  # Cambiá esta clave
    st.sidebar.write("✅ Acceso concedido")

    file_cruce = st.sidebar.file_uploader("Cargar nueva base de cruce", type=["xlsx"])
    if file_cruce:
        df_cruce = pd.read_excel(file_cruce)
        df_cruce.to_csv(BASE_FILE, index=False)  # Guardamos la base
        st.sidebar.success("Base de cruce actualizada con éxito.")

# --- Verificar si hay base guardada ---
if os.path.exists(BASE_FILE):
    df_cruce = pd.read_csv(BASE_FILE)
    df_cruce.columns = df_cruce.columns.str.strip()
    st.sidebar.success("Base de cruce lista para usar.")
else:
    df_cruce = None
    st.sidebar.error("No hay base de cruce cargada por el administrador.")

# --- Carga de convenios ---
file_convenios = st.file_uploader("📂 Cargar Excel de convenios", type=["xlsx"])

if file_convenios:
    if df_cruce is not None:
        # --- Leer primeras 5 filas como cabecera ---
        df_header = pd.read_excel(file_convenios, nrows=5, header=None)

        # --- Leer el resto como tabla ---
        df_conv = pd.read_excel(file_convenios, skiprows=5)

        st.subheader("Vista previa - Convenios (con datos originales)")
        st.dataframe(df_conv)

        # --- Merge: cruce con base ---
        df_merged = df_conv.merge(
            df_cruce,
            left_on="Practica/Rango/Unidad",
            right_on="Codigo SOM",
            how="left"
        )

        # Renombrar columnas del cruce
        df_merged = df_merged.rename(columns={
            "Codigo NNM": "Codigo NNM (Cruce)",
            "Descripcion NNM": "Descripcion NNM (Cruce)"
        })

        # Mostrar resultado al usuario
        st.subheader("Resultado del Cruce")
        st.dataframe(df_merged)

        # --- Función para exportar respetando las 5 filas iniciales ---
        @st.cache_data
        def convert_excel_with_header(header, df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                # Guardamos la cabecera manualmente
                header.to_excel(writer, index=False, header=False)
                # Guardamos la tabla debajo
                df.to_excel(writer, index=False, startrow=len(header))
            return output.getvalue()

        # --- Obtener nodo y prestador de celdas B3 y C3 ---
        try:
            nodo = str(df_header.iloc[2, 1]).strip()  # B3
            prestador = str(df_header.iloc[2, 2]).strip()  # C3
            nombre_archivo = f"resultado_cruce_{nodo}{prestador}.xlsx"
        except Exception:
            nombre_archivo = "resultado_cruce.xlsx"  # fallback

        # Botón de descarga
        st.download_button(
            label="📥 Descargar resultado en Excel",
            data=convert_excel_with_header(df_header, df_merged),
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("⚠️ No se puede procesar porque falta la base de cruce.")
