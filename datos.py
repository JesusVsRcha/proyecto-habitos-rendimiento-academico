"""Carga y cálculos compartidos. Nunca modifica el CSV original."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent
CSV = RAIZ / "data" / "raw" / "student_lifestyle_dataset.csv"
TIEMPO = [
    "Study_Hours_Per_Day", "Extracurricular_Hours_Per_Day",
    "Sleep_Hours_Per_Day", "Social_Hours_Per_Day",
    "Physical_Activity_Hours_Per_Day",
]
NUMERICAS = TIEMPO + ["GPA"]
ESTRES = ["Low", "Moderate", "High"]
NOMBRES = dict(zip(NUMERICAS, ["Estudio", "Extracurricular", "Sueño", "Socialización", "Actividad física", "GPA"]))
COLORES = {"Low": "#0d9488", "Moderate": "#d97706", "High": "#6366f1"}
AZUL = "#2563eb"
GRUPOS_ACTIVIDAD = ["0–2 h", "2–4 h", "4–6 h", "Más de 6 h"]
GRUPOS_ESTUDIO = ["5–6 h", "6–7 h", "7–8 h", "8–9 h", "9–10 h"]


@st.cache_data(show_spinner=False)
def _leer_csv(ruta: str, version: tuple[int, int]) -> pd.DataFrame:
    # La fecha de modificación y el tamaño invalidan la caché al cambiar el CSV.
    df = pd.read_csv(ruta)
    faltantes = set(["Student_ID", *NUMERICAS, "Stress_Level"]) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(faltantes))}")
    for columna in ["Student_ID", *NUMERICAS]:
        df[columna] = pd.to_numeric(df[columna], errors="raise")
    desconocidos = set(df["Stress_Level"].dropna()) - set(ESTRES)
    if desconocidos:
        raise ValueError(f"Categorías de estrés desconocidas: {desconocidos}")
    return df


def cargar_datos() -> pd.DataFrame:
    try:
        estado = CSV.stat()
        return _leer_csv(str(CSV), (estado.st_mtime_ns, estado.st_size))
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"No se pudo cargar {CSV.name}: {error}")
        st.stop()


def resumen_estres(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Stress_Level").agg(
        Estudiantes=("GPA", "size"),
        **{"GPA promedio": ("GPA", "mean"),
           "Estudio (h/día)": (TIEMPO[0], "mean"),
           "Sueño (h/día)": (TIEMPO[2], "mean"),
           "Actividad física (h/día)": (TIEMPO[4], "mean")},
    ).reindex([nivel for nivel in ESTRES if nivel in set(df["Stress_Level"])])


def resumen_actividad(df: pd.DataFrame) -> pd.DataFrame:
    grupos = pd.cut(df[TIEMPO[4]], [0, 2, 4, 6, np.inf],
                    labels=GRUPOS_ACTIVIDAD, include_lowest=True)
    return df.assign(Grupo=grupos).groupby("Grupo", observed=False).agg(
        Estudiantes=("GPA", "size"),
        **{"GPA promedio": ("GPA", "mean"), "Estudio (h/día)": (TIEMPO[0], "mean")},
    ).reset_index()


def resumen_estudio(df: pd.DataFrame) -> pd.DataFrame:
    grupos = pd.cut(df[TIEMPO[0]], [5, 6, 7, 8, 9, 10],
                    labels=GRUPOS_ESTUDIO, include_lowest=True)
    return df.assign(Grupo=grupos).groupby("Grupo", observed=False).agg(
        Estudiantes=("GPA", "size"), **{"GPA promedio": ("GPA", "mean")},
    ).reset_index()


def tabla_iqr(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for columna in NUMERICAS:
        q1, q3 = df[columna].quantile([0.25, 0.75])
        inferior, superior = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        filas.append({"Variable": columna, "Límite inferior": inferior,
                      "Límite superior": superior,
                      "Valores atípicos": int(((df[columna] < inferior) | (df[columna] > superior)).sum())})
    return pd.DataFrame(filas)


def presupuesto_24(df: pd.DataFrame) -> pd.Series:
    # Tolerancia numérica para la representación binaria de decimales.
    return pd.Series(np.isclose(df[TIEMPO].sum(axis=1, min_count=5), 24,
                               atol=1e-9, rtol=0), index=df.index)


def mostrar_grafico(fig, clave: str, altura: int = 460) -> None:
    fig.update_layout(height=altura, font=dict(size=13),
                      margin=dict(l=35, r=35, t=65, b=45))
    st.plotly_chart(fig, width="stretch", key=clave,
                    config={"displaylogo": False})
