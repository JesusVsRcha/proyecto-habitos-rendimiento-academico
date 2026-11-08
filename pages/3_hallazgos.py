import plotly.express as px
import streamlit as st

from datos import (
    AZUL, TIEMPO, cargar_datos, mostrar_grafico, presupuesto_24,
    resumen_actividad, resumen_estres, resumen_estudio,
)

df = cargar_datos()
st.title("Principales hallazgos")
st.caption(f"Resultados calculados desde el CSV completo: {len(df)} estudiantes. El filtro de EDA aplica solo a esa página.")
r_estudio = df[TIEMPO[0]].corr(df["GPA"])
r_actividad = df[TIEMPO[4]].corr(df["GPA"])
r_sueno = df[TIEMPO[2]].corr(df["GPA"])
estres = resumen_estres(df)
actividad = resumen_actividad(df).set_index("Grupo")

with st.container(border=True):
    st.subheader("1 · Las horas de estudio presentan la mayor asociación individual con GPA")
    st.write(f"Pearson **r = {r_estudio:.3f}**: asociación positiva fuerte y la mayor "
             "entre las variables cuantitativas de hábitos consideradas. No implica causalidad.")
    estudio = resumen_estudio(df)
    fig = px.line(estudio, x="Grupo", y="GPA promedio", markers=True, text="GPA promedio",
                  color_discrete_sequence=[AZUL], labels={"Grupo": "Horas de estudio por día"},
                  title="Progresión del GPA promedio según horas de estudio")
    fig.update_traces(texttemplate="%{y:.3f}", textposition="top center")
    mostrar_grafico(fig, "hallazgo_estudio", 420)
    st.dataframe(estudio.round(3), hide_index=True, width="stretch")
    st.caption("Intervalos: [5, 6], (6, 7], (7, 8], (8, 9] y (9, 10].")
    st.write("**Interpretación:** el GPA promedio aumenta progresivamente en los grupos con más horas de estudio.")

with st.container(border=True):
    st.subheader("2 · Las cinco variables de tiempo forman un presupuesto cerrado de 24 horas")
    cumplen = int(presupuesto_24(df).sum())
    st.write(f"**{cumplen} de {len(df)} estudiantes** cumplen la suma de 24 horas "
             "entre estudio, actividades extracurriculares, sueño, socialización y actividad física.")
    st.write("**Interpretación:** aumentar una actividad reduce el tiempo disponible para las otras. "
             "Las variables temporales presentan dependencia estructural y no deben analizarse "
             "como completamente independientes.")

with st.container(border=True):
    st.subheader("3 · El estrés alto coincide con mayor GPA y más horas de estudio")
    if {"Low", "High"}.issubset(estres.index):
        low, high = estres.loc["Low"], estres.loc["High"]
        diferencia = high["Estudio (h/día)"] - low["Estudio (h/día)"]
        st.write(f"High: GPA **{high['GPA promedio']:.3f}** y estudio **{high['Estudio (h/día)']:.3f} h/día**. "
                 f"Low: GPA **{low['GPA promedio']:.3f}** y estudio **{low['Estudio (h/día)']:.3f} h/día**. "
                 f"La diferencia es de **{diferencia:.3f} horas de estudio diarias** (aproximadamente 2,9).")
    st.write("**Interpretación:** las diferencias en estudio cambian la interpretación de la asociación "
             "entre estrés y GPA. No podemos concluir que el estrés cause mejores notas.")

with st.container(border=True):
    st.subheader("4 · Actividad física y GPA deben interpretarse dentro de la distribución del tiempo")
    st.write(f"Pearson entre actividad física y GPA: **r = {r_actividad:.3f}**.")
    for grupo in ["0–2 h", "Más de 6 h"]:
        fila = actividad.loc[grupo]
        st.write(f"**{grupo} de actividad física:** {int(fila['Estudiantes'])} estudiantes · "
                 f"GPA **{fila['GPA promedio']:.3f}** · Estudio **{fila['Estudio (h/día)']:.3f} h/día**.")
    st.write("**Interpretación:** quienes realizan más actividad física también dedican menos horas "
             "al estudio. El presupuesto fijo de 24 horas permite interpretar el patrón como "
             "distribución del tiempo; no demuestra daño causado por el ejercicio.")

with st.container(border=True):
    st.subheader("5 · La cantidad de sueño no presenta una asociación lineal clara con GPA")
    st.write(f"Pearson **r = {r_sueno:.3f}**, cercano a cero. Dentro de este dataset no aparece "
             "una asociación lineal clara entre cantidad de sueño y GPA.")
    st.write("**Interpretación:** este resultado no significa que el sueño no sea importante. "
             "No evalúa su calidad, posibles relaciones no lineales ni efectos causales.")

st.subheader("Síntesis del EDA")
st.info("El rendimiento académico está fuertemente asociado con las horas destinadas al estudio. "
        "Sin embargo, los hábitos diarios forman parte de un presupuesto fijo de 24 horas, por lo "
        "que variables como actividad física, sueño y socialización no deben analizarse de manera "
        "completamente independiente. Algunas relaciones aparentemente llamativas, como el mayor "
        "GPA en estudiantes con estrés alto, cambian de interpretación cuando se consideran "
        "simultáneamente las diferencias en las horas de estudio.")
izquierda, derecha = st.columns(2)
with izquierda:
    st.subheader("Limitaciones")
    st.markdown("- Correlación no implica causalidad.\n"
                "- Dataset basado en autorreporte.\n"
                "- Mide cantidad de horas, pero no calidad del estudio.\n"
                "- Pueden existir variables no observadas: motivación, disciplina o método de estudio.\n"
                "- No existe una serie temporal individual por estudiante.\n"
                "- Las variables temporales tienen dependencia estructural porque suman 24 horas.")
with derecha:
    st.subheader("Implicancias para el Avance 3")
    st.markdown("- Las horas de estudio serán una variable importante.\n"
                "- Considerar interacciones entre hábitos.\n"
                "- No analizar las variables temporales como completamente independientes.\n"
                "- Tratar correctamente `Stress_Level`, considerando su orden Low, Moderate, High.\n"
                "- Evaluar durante el modelado si las relaciones observadas se mantienen.")
