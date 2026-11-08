import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from datos import (
    AZUL, COLORES, ESTRES, NOMBRES, NUMERICAS, TIEMPO,
    cargar_datos, mostrar_grafico, resumen_actividad, resumen_estres,
)

df = cargar_datos()
st.title("Análisis exploratorio de datos")
st.write("Cinco visualizaciones para explorar el GPA y los hábitos diarios. "
         "Todos los gráficos, tablas y métricas de esta página responden al filtro lateral.")
st.sidebar.subheader("Filtros del EDA")
seleccion = st.sidebar.multiselect("Nivel de estrés", ESTRES, default=ESTRES, key="filtro_estres")
datos = df.loc[df["Stress_Level"].isin(seleccion)].copy()
st.sidebar.metric("Estudiantes seleccionados", len(datos))
st.caption(f"Muestra analizada: {len(datos)} de {len(df)} estudiantes · "
           f"Estrés: {', '.join(n for n in ESTRES if n in seleccion) or 'ninguno'}.")
if datos.empty:
    st.warning("Seleccione al menos un nivel de estrés para mostrar el análisis.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("GPA promedio", f"{datos['GPA'].mean():.3f}")
c2.metric("Estudio promedio", f"{datos[TIEMPO[0]].mean():.3f} h")
c3.metric("Sueño promedio", f"{datos[TIEMPO[2]].mean():.3f} h")
c4.metric("Actividad física", f"{datos[TIEMPO[4]].mean():.3f} h")
with st.expander("Estadísticas descriptivas de la selección"):
    st.dataframe(datos[NUMERICAS].rename(columns=NOMBRES).describe().round(3), width="stretch")

st.header("1 · Distribución del GPA")
fig = px.histogram(datos, x="GPA", nbins=30, marginal="box",
                   color_discrete_sequence=[AZUL], title="Distribución del rendimiento académico")
fig.update_layout(yaxis_title="Número de estudiantes")
mostrar_grafico(fig, "distribucion_gpa")
st.write(f"**Interpretación:** el GPA promedio de la selección es **{datos['GPA'].mean():.3f}**. "
         "En el dataset completo se concentra alrededor de 3,1 y no muestra una asimetría extrema. "
         "El histograma y el boxplot permiten comparar la selección con ese patrón general.")

st.header("2 · Horas de estudio y GPA")
r_estudio = datos[TIEMPO[0]].corr(datos["GPA"])
fig = px.scatter(datos, x=TIEMPO[0], y="GPA", opacity=0.35,
                 color_discrete_sequence=[AZUL], labels={TIEMPO[0]: "Horas de estudio por día"},
                 title=f"Estudio y GPA · Pearson r = {r_estudio:.3f}")
validos = datos[[TIEMPO[0], "GPA"]].dropna()
if len(validos) >= 2 and validos[TIEMPO[0]].nunique() > 1:
    pendiente, intercepto = np.polyfit(validos[TIEMPO[0]], validos["GPA"], 1)
    linea_x = np.linspace(validos[TIEMPO[0]].min(), validos[TIEMPO[0]].max(), 100)
    fig.add_trace(go.Scatter(x=linea_x, y=pendiente * linea_x + intercepto,
                            mode="lines", name="Tendencia lineal", line=dict(color="#d97706", width=3)))
mostrar_grafico(fig, "estudio_gpa")
st.write(f"**Interpretación:** Pearson en la selección es **{r_estudio:.3f}**. "
         "En los datos completos (r ≈ 0,73), existe una asociación positiva fuerte "
         "entre estudio y GPA. La línea resume la tendencia observada; no demuestra causalidad.")

st.header("3 · Matriz de correlación de Pearson")
matriz = datos[NUMERICAS].corr()
etiquetas = [NOMBRES[columna] for columna in NUMERICAS]
fig = go.Figure(go.Heatmap(
    z=matriz.to_numpy(), x=etiquetas, y=etiquetas,
    zmin=-1, zmax=1, zmid=0, colorscale="RdBu",
    text=matriz.to_numpy(), texttemplate="%{text:.2f}",
    hovertemplate="%{x} / %{y}: %{z:.3f}<extra></extra>", colorbar=dict(title="Pearson r"),
))
fig.update_layout(title="Correlaciones de la muestra seleccionada")
mostrar_grafico(fig, "matriz_pearson", 540)
relaciones = matriz["GPA"]
st.write("**Interpretación:** asociaciones con GPA en la selección: "
         + "; ".join(f"{NOMBRES[c]} **{relaciones[c]:+.3f}**" for c in TIEMPO) + ". "
         "En el dataset completo destacan estudio (+0,73) y actividad física (−0,34); "
         "las demás asociaciones lineales con GPA son débiles o cercanas a cero. "
         "Student_ID está excluido y Stress_Level se analiza por categorías.")

st.header("4 · GPA según nivel de estrés")
fig = px.box(datos, x="Stress_Level", y="GPA", color="Stress_Level",
             category_orders={"Stress_Level": ESTRES}, color_discrete_map=COLORES,
             labels={"Stress_Level": "Nivel de estrés"}, title="GPA por nivel de estrés", points="outliers")
fig.update_layout(showlegend=False)
mostrar_grafico(fig, "estres_gpa")
estres = resumen_estres(datos)
st.dataframe(estres.round(3).rename_axis("Nivel de estrés"), width="stretch")
if {"Low", "High"}.issubset(estres.index):
    diferencia = estres.loc["High", "Estudio (h/día)"] - estres.loc["Low", "Estudio (h/día)"]
    st.write(f"**Interpretación:** High presenta GPA promedio **{estres.loc['High', 'GPA promedio']:.3f}**, "
             f"frente a **{estres.loc['Low', 'GPA promedio']:.3f}** en Low; "
             f"también estudia **{diferencia:.3f} horas diarias más**. "
             "Esta comparación no demuestra que el estrés mejore las notas.")
else:
    st.write("**Interpretación:** la tabla y el boxplot muestran solo los niveles seleccionados. "
             "Para comparar High con Low, incluya ambos en el filtro. En el dataset completo "
             "High tiene mayor GPA y dedica más tiempo al estudio; no puede atribuirse causalidad al estrés.")

st.header("5 · Actividad física, horas de estudio y GPA")
actividad = resumen_actividad(datos)
fig = make_subplots(rows=1, cols=2, subplot_titles=("GPA promedio", "Horas de estudio promedio"), shared_xaxes=True)
for columna, variable, color in [(1, "GPA promedio", AZUL), (2, "Estudio (h/día)", "#0d9488")]:
    fig.add_trace(go.Scatter(
        x=actividad["Grupo"].astype(str).tolist(), y=actividad[variable],
        mode="lines+markers+text", text=actividad[variable].round(3),
        textposition="top center", line=dict(color=color, width=3),
        name=variable, customdata=actividad["Estudiantes"],
        hovertemplate="%{x}<br>Promedio: %{y:.3f}<br>Estudiantes: %{customdata}<extra></extra>",
        connectgaps=False,
    ), row=1, col=columna)
    fig.update_xaxes(title_text="Actividad física diaria", row=1, col=columna)
fig.update_yaxes(title_text="GPA", row=1, col=1)
fig.update_yaxes(title_text="Horas/día", row=1, col=2)
fig.update_layout(title="Distribución del tiempo: actividad física y estudio", showlegend=False)
mostrar_grafico(fig, "actividad_estudio_gpa")
st.dataframe(actividad.round(3), hide_index=True, width="stretch")
st.caption("Intervalos cerrados a la derecha: [0, 2], (2, 4], (4, 6] y (6, ∞). "
           "Los paneles utilizan unidades distintas, indicadas en cada eje.")
st.write("**Interpretación:** en el dataset completo, al aumentar el grupo de actividad física, "
         "disminuyen tanto el GPA promedio como las horas promedio de estudio. "
         "Los paneles muestran si este patrón se mantiene en la selección. Las cinco variables "
         "temporales suman 24 horas: el patrón puede reflejar un intercambio en la distribución "
         "del tiempo y no demuestra que el ejercicio perjudique las notas.")
