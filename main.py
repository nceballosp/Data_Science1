import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------------------------
# Configuración
# -------------------------------------------------

st.set_page_config(
    page_title="Dashboard COVID Sintético",
    page_icon="🦠",
    layout="wide"
)

st.title("🦠 Dashboard Interactivo COVID-19")
st.markdown("### Simulación de datos sintéticos (10.000 registros)")

# -------------------------------------------------
# Generación de datos
# -------------------------------------------------

@st.cache_data
def generar_datos():

    np.random.seed(123)

    n = 10000

    ciudades = [
        "Bogotá",
        "Medellín",
        "Cali",
        "Barranquilla",
        "Cartagena",
        "Bucaramanga"
    ]

    sexos = ["Masculino", "Femenino"]

    estados = [
        "Recuperado",
        "Hospitalizado",
        "Fallecido"
    ]

    vacunas = [
        "Ninguna",
        "1 Dosis",
        "2 Dosis",
        "Refuerzo"
    ]

    fechas = pd.date_range(
        "2021-01-01",
        "2023-12-31"
    )

    df = pd.DataFrame({

        "Fecha": np.random.choice(fechas, n),

        "Edad": np.random.randint(1,95,n),

        "Ciudad": np.random.choice(ciudades,n),

        "Sexo": np.random.choice(sexos,n),

        "Estado": np.random.choice(
            estados,
            n,
            p=[0.80,0.15,0.05]
        ),

        "Vacunación": np.random.choice(
            vacunas,
            n,
            p=[0.15,0.20,0.35,0.30]
        ),

        "Días Hospitalizado": np.random.poisson(6,n),

        "Costo Atención": np.random.normal(
            3200,
            900,
            n
        ).round(2)

    })

    df["Costo Atención"] = df["Costo Atención"].clip(300)

    return df


df = generar_datos()

# -------------------------------------------------
# Barra lateral
# -------------------------------------------------

st.sidebar.header("Filtros")

ciudad = st.sidebar.multiselect(
    "Ciudad",
    df["Ciudad"].unique(),
    default=df["Ciudad"].unique()
)

sexo = st.sidebar.multiselect(
    "Sexo",
    df["Sexo"].unique(),
    default=df["Sexo"].unique()
)

estado = st.sidebar.multiselect(
    "Estado",
    df["Estado"].unique(),
    default=df["Estado"].unique()
)

vacuna = st.sidebar.multiselect(
    "Vacunación",
    df["Vacunación"].unique(),
    default=df["Vacunación"].unique()
)

df_filtrado = df[
    (df["Ciudad"].isin(ciudad)) &
    (df["Sexo"].isin(sexo)) &
    (df["Estado"].isin(estado)) &
    (df["Vacunación"].isin(vacuna))
]

# -------------------------------------------------
# Métricas Cuantitativas
# -------------------------------------------------

st.header("📊 Métricas Cuantitativas")

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Total Casos",
    len(df_filtrado)
)

c2.metric(
    "Edad Promedio",
    round(df_filtrado["Edad"].mean(),2)
)

c3.metric(
    "Costo Promedio",
    f"${df_filtrado['Costo Atención'].mean():,.0f}"
)

c4.metric(
    "Hospitalización Prom.",
    round(df_filtrado["Días Hospitalizado"].mean(),2)
)

# -------------------------------------------------
# Estadística descriptiva
# -------------------------------------------------

st.subheader("Estadística Descriptiva")

st.dataframe(
    df_filtrado.describe()
)

# -------------------------------------------------
# Estadística Cualitativa
# -------------------------------------------------

st.header("📌 Variables Cualitativas")

col1,col2 = st.columns(2)

with col1:

    st.write("Estado")

    tabla_estado = (
        df_filtrado["Estado"]
        .value_counts()
        .reset_index()
    )

    tabla_estado.columns=["Estado","Frecuencia"]

    st.dataframe(tabla_estado)

with col2:

    st.write("Ciudad")

    tabla_ciudad = (
        df_filtrado["Ciudad"]
        .value_counts()
        .reset_index()
    )

    tabla_ciudad.columns=["Ciudad","Frecuencia"]

    st.dataframe(tabla_ciudad)

# -------------------------------------------------
# Variables elegidas por usuario
# -------------------------------------------------

st.header("📈 Construcción dinámica de gráficos")

variables = df_filtrado.columns.tolist()

x = st.selectbox(
    "Variable eje X",
    variables
)

y = st.selectbox(
    "Variable eje Y",
    variables,
    index=1
)

tipo = st.selectbox(
    "Tipo de gráfico",
    [
        "Dispersión",
        "Barras",
        "Caja",
        "Histograma",
        "Línea"
    ]
)

if tipo=="Dispersión":

    fig = px.scatter(
        df_filtrado,
        x=x,
        y=y,
        color="Estado"
    )

elif tipo=="Barras":

    fig = px.bar(
        df_filtrado,
        x=x,
        color="Estado"
    )

elif tipo=="Caja":

    fig = px.box(
        df_filtrado,
        x=x,
        y=y,
        color="Estado"
    )

elif tipo=="Histograma":

    fig = px.histogram(
        df_filtrado,
        x=x,
        color="Estado"
    )

else:

    fig = px.line(
        df_filtrado.sort_values("Fecha"),
        x=x,
        y=y,
        color="Estado"
    )

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# Dashboard de análisis
# -------------------------------------------------

st.header("📊 Análisis Gráfico")

g1,g2 = st.columns(2)

with g1:

    fig1 = px.histogram(
        df_filtrado,
        x="Edad",
        nbins=30,
        color="Estado",
        title="Distribución de Edad"
    )

    st.plotly_chart(fig1,use_container_width=True)

with g2:

    fig2 = px.pie(
        df_filtrado,
        names="Estado",
        title="Estado de Pacientes"
    )

    st.plotly_chart(fig2,use_container_width=True)

g3,g4 = st.columns(2)

with g3:

    fig3 = px.box(
        df_filtrado,
        x="Estado",
        y="Costo Atención",
        color="Estado",
        title="Costo por Estado"
    )

    st.plotly_chart(fig3,use_container_width=True)

with g4:

    fig4 = px.scatter(
        df_filtrado,
        x="Edad",
        y="Costo Atención",
        color="Estado",
        size="Días Hospitalizado",
        hover_data=["Ciudad"],
        title="Edad vs Costo"
    )

    st.plotly_chart(fig4,use_container_width=True)

# -------------------------------------------------
# Tabla de datos
# -------------------------------------------------

st.header("Base de Datos")

st.dataframe(
    df_filtrado,
    use_container_width=True
)
