import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Dashboard Gimnasio", page_icon="🏋️", layout="wide")
if "ok" not in st.session_state: st.session_state.ok=False
if not st.session_state.ok:
    st.title("🏋️ Dashboard Gimnasio")
    pwd=st.text_input("Contraseña",type="password")
    if st.button("Ingresar"):
        if pwd=="1234":
            st.session_state.ok=True; st.rerun()
        else: st.error("Contraseña incorrecta")
    st.stop()

@st.cache_data
def data():
    np.random.seed(1); n=10000
    fechas=pd.date_range("2022-01-01","2025-12-31")
    planes=["Básico","Premium","VIP"]; gen=["Masculino","Femenino"]
    df=pd.DataFrame({
      "Fecha_Registro":np.random.choice(fechas,n),
      "Edad":np.random.randint(18,70,n),
      "Género":np.random.choice(gen,n),
      "Plan":np.random.choice(planes,n,p=[.5,.3,.2]),
      "Visitas_Mes":np.random.randint(0,31,n),
      "Gasto_Mensual":np.round(np.random.normal(120,25,n),2),
      "Antigüedad_Meses":np.random.randint(1,61,n)
    })
    p=((df["Visitas_Mes"]<6)|(df["Antigüedad_Meses"]<4))
    df["Churn"]=np.where(p,np.random.choice(["Abandonó","Activo"],n,p=[.65,.35]),
                           np.random.choice(["Abandonó","Activo"],n,p=[.15,.85]))
    return df
df=data()
st.sidebar.header("Filtros")
plan=st.sidebar.multiselect("Plan",df.Plan.unique(),default=list(df.Plan.unique()))
gen=st.sidebar.multiselect("Género",df["Género"].unique(),default=list(df["Género"].unique()))
ch=st.sidebar.multiselect("Churn",df.Churn.unique(),default=list(df.Churn.unique()))
f=df[df.Plan.isin(plan)&df["Género"].isin(gen)&df.Churn.isin(ch)]
tot=len(f); act=(f.Churn=="Activo").sum(); abd=(f.Churn=="Abandonó").sum(); tasa=abd/tot*100 if tot else 0
c1,c2,c3,c4=st.columns(4)
c1.metric("Clientes",tot); c2.metric("Activos",act); c3.metric("Abandonos",abd); c4.metric("Tasa",f"{tasa:.1f}%")
c5,c6,c7=st.columns(3)
c5.metric("Visitas Prom.",f"{f.Visitas_Mes.mean():.1f}")
c6.metric("Ingreso Prom.",f"${f.Gasto_Mensual.mean():.2f}")
c7.metric("Antigüedad",f"{f.Antigüedad_Meses.mean():.1f}")
st.subheader("Estadística cuantitativa"); st.dataframe(f.describe())
st.subheader("Frecuencia por Plan"); st.dataframe(f.Plan.value_counts())
st.subheader("Frecuencia Churn"); st.dataframe(f.Churn.value_counts())
x=st.selectbox("Eje X",f.columns)
y=st.selectbox("Eje Y",[c for c in f.columns if c!=x])
t=st.selectbox("Gráfico",["Dispersión","Barras","Histograma","Caja"])
if t=="Dispersión": fig=px.scatter(f,x=x,y=y,color="Churn")
elif t=="Barras": fig=px.bar(f,x=x,color="Churn")
elif t=="Histograma": fig=px.histogram(f,x=x,color="Churn")
else: fig=px.box(f,x=x,y=y,color="Churn")
st.plotly_chart(fig,use_container_width=True)
a,b=st.columns(2)
with a: st.plotly_chart(px.pie(f,names="Churn",title="Churn"),use_container_width=True)
with b: st.plotly_chart(px.histogram(f,x="Edad",color="Churn"),use_container_width=True)
a,b=st.columns(2)
with a: st.plotly_chart(px.scatter(f,x="Visitas_Mes",y="Gasto_Mensual",color="Churn",size="Antigüedad_Meses"),use_container_width=True)
with b: st.plotly_chart(px.box(f,x="Plan",y="Gasto_Mensual",color="Plan"),use_container_width=True)
st.subheader("Datos"); st.dataframe(f,use_container_width=True)
