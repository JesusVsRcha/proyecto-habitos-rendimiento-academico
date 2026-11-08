import numpy as np
import pandas as pd
import streamlit as st

from datos import ESTRES, NUMERICAS, TIEMPO, cargar_datos, presupuesto_24, tabla_iqr

df = cargar_datos()
st.title("Hábitos diarios y rendimiento académico")
st.caption("Avance 2 · Problema y datos · Contexto académico 2023–2024")
st.write("La distribución del tiempo entre estudio, descanso y otras actividades puede "
         "relacionarse con el rendimiento académico. Exploramos estas asociaciones "
         "mediante GPA, sin atribuir relaciones causales.")
st.subheader("Pregunta de investigación")
st.info("¿En qué medida los hábitos diarios de los estudiantes se relacionan con su "
        "rendimiento académico, medido mediante GPA, durante el año académico 2023–2024?")

st.subheader("Problema, variables y contexto")
x, y, t = st.columns([2, 1, 1])
with x:
    st.markdown("**X · Variables explicativas**")
    st.markdown("\n".join(f"- `{columna}`" for columna in [*TIEMPO, "Stress_Level"]))
with y:
    st.markdown("**Y · Rendimiento académico**")
    st.write("GPA: variable cuantitativa que representa el rendimiento académico.")
with t:
    st.markdown("**T · Contexto temporal**")
    st.write("Año académico 2023–2024, definido en el proyecto.")
    st.caption("El CSV no contiene fechas ni seguimiento individual; el periodo no puede verificarse desde sus columnas.")

st.subheader("Dataset y calidad")
st.write("**Fuente:** Student Lifestyle Dataset · `student_lifestyle_dataset.csv`. "
         "**Unidad de observación:** un estudiante.")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Estudiantes", f"{len(df):,}".replace(",", "."))
c2.metric("Columnas originales", df.shape[1])
c3.metric("Valores nulos", int(df.isna().sum().sum()))
c4.metric("Registros duplicados", int(df.duplicated().sum()))
filas = []
for columna in df.columns:
    tipo = "Identificador (excluido de X)" if columna == "Student_ID" else (
        "Categórica ordinal" if columna == "Stress_Level" else "Cuantitativa continua")
    filas.append({"Variable": columna, "Tipo conceptual": tipo,
                  "Tipo Pandas": str(df[columna].dtype), "Nulos": int(df[columna].isna().sum())})
st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
st.write(f"Identificadores repetidos: **{int(df['Student_ID'].duplicated().sum())}**. "
         f"Categorías de estrés observadas: **{', '.join(n for n in ESTRES if n in set(df['Stress_Level']))}**.")
no_finitos = int((~np.isfinite(df[NUMERICAS].to_numpy())).sum())
negativos = int((df[TIEMPO] < 0).sum().sum())
st.write(f"Valores numéricos no finitos: **{no_finitos}**. Horas negativas: **{negativos}**.")
with st.expander("Vista previa del CSV original"):
    st.dataframe(df.head(10), hide_index=True, width="stretch")

st.subheader("Valores atípicos mediante IQR")
st.caption("Criterio: valores menores que Q1 − 1,5 × IQR o mayores que Q3 + 1,5 × IQR; IQR = Q3 − Q1.")
st.dataframe(tabla_iqr(df).round(3), hide_index=True, width="stretch")
st.markdown("**Decisiones de limpieza**\n\n"
            "- Se conserva el CSV y todos sus registros, incluidos los valores atípicos: no existe evidencia de que sean errores.\n"
            "- Se verifican columnas, tipos numéricos y categorías de estrés al cargar los datos.\n"
            "- `Student_ID` se utiliza únicamente como identificador, sin incluirlo como predictor ni en las correlaciones.\n"
            "- Los grupos de horas se calculan solo para el análisis; no se guardan cambios en el dataset.")

st.subheader("Un presupuesto diario cerrado de 24 horas")
cumplen = int(presupuesto_24(df).sum())
if cumplen == len(df):
    st.success(f"Las cinco variables de tiempo suman 24 horas para los {len(df):,} estudiantes.".replace(",", "."))
else:
    st.warning(f"{cumplen} de {len(df)} estudiantes cumplen el presupuesto de 24 horas.")
st.write("Estudio, actividades extracurriculares, sueño, socialización y actividad física "
         "completan el día. Aumentar una actividad deja menos tiempo para las demás: "
         "las variables temporales no son completamente independientes.")
st.caption("Comprobación por estudiante con tolerancia de 10⁻⁹ horas para el redondeo de punto flotante. Continúe con EDA en el menú lateral.")
