"""Verificación reproducible de los resultados y de la interfaz Streamlit."""
import hashlib
import itertools
import json
import os
import py_compile
import sys
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_PROYECTO))

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from datos import (
    CSV, ESTRES, RAIZ, TIEMPO, presupuesto_24, resumen_actividad,
    resumen_estres, resumen_estudio, tabla_iqr,
)


def sin_excepciones(app):
    assert not app.exception, [error.message for error in app.exception]


def metricas(app):
    return {metrica.label: metrica.value for metrica in app.metric}


def verificar():
    original = hashlib.sha256(CSV.read_bytes()).hexdigest()
    for archivo in [RAIZ / "app.py", RAIZ / "datos.py", *sorted((RAIZ / "pages").glob("*.py"))]:
        assert archivo.name == archivo.name.lower(), archivo.name
        py_compile.compile(str(archivo), doraise=True)
    df = pd.read_csv(CSV)
    assert df.shape == (2000, 8)
    assert df.isna().sum().sum() == 0
    assert df.duplicated().sum() == 0
    assert presupuesto_24(df).all()
    assert tabla_iqr(df)["Valores atípicos"].tolist() == [0, 0, 0, 0, 5, 4]
    np.testing.assert_allclose(
        df[TIEMPO].corrwith(df["GPA"]),
        [0.73, -0.03, 0, -0.09, -0.34], atol=0.006,
    )
    estres = resumen_estres(df)
    np.testing.assert_allclose(estres["GPA promedio"], [2.817, 3.025, 3.262], atol=0.001)
    np.testing.assert_allclose(estres["Estudio (h/día)"], [5.474, 6.970, 8.385], atol=0.001)
    np.testing.assert_allclose(estres["Sueño (h/día)"], [8.064, 7.948, 7.046], atol=0.001)
    np.testing.assert_allclose(estres["Actividad física (h/día)"], [5.582, 4.337, 3.961], atol=0.001)
    actividad = resumen_actividad(df)
    assert actividad["Estudiantes"].tolist() == [423, 557, 508, 512]
    np.testing.assert_allclose(actividad["GPA promedio"], [3.259, 3.162, 3.080, 2.983], atol=0.001)
    np.testing.assert_allclose(actividad["Estudio (h/día)"], [8.412, 7.804, 7.280, 6.540], atol=0.001)
    estudio = resumen_estudio(df)
    assert estudio["Estudiantes"].sum() == len(df)
    np.testing.assert_allclose(estudio["GPA promedio"], [2.821, 2.962, 3.121, 3.293, 3.429], atol=0.001)
    print("OK: sintaxis, CSV, IQR, presupuesto de 24 horas y resultados científicos.")

    # Ejecutar desde otra carpeta comprueba que la carga no depende del cwd.
    anterior = Path.cwd()
    os.chdir(RAIZ / "pages")
    try:
        app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=30).run()
        sin_excepciones(app)
        assert [pagina["page_name"] for pagina in app._registered_pages.values()] == [
            "1 · Problema y datos", "2 · EDA", "3 · Hallazgos",
        ]
        assert metricas(app)["Estudiantes"] == "2.000"
        assert metricas(app)["Columnas originales"] == "8"
        print("OK: página de problema y datos; tres páginas registradas en navegación.")

        app.switch_page("pages/2_eda.py").run()
        sin_excepciones(app)
        assert len(app.get("plotly_chart")) == 5
        completos = [grafico.proto.spec for grafico in app.get("plotly_chart")]
        figuras = [json.loads(spec) for spec in completos]
        assert len(figuras[0]["data"]) == 2  # Histograma + boxplot marginal.
        assert len(figuras[1]["data"]) == 2  # Scatter + tendencia.
        assert figuras[2]["data"][0]["texttemplate"] == "%{text:.2f}"
        assert figuras[3]["layout"]["xaxis"]["categoryarray"] == ESTRES
        assert len(figuras[4]["data"]) == 2  # GPA y estudio con unidades distintas.
        for cantidad in range(1, 4):
            for seleccion in itertools.combinations(ESTRES, cantidad):
                app.multiselect[0].set_value(list(seleccion)).run()
                sin_excepciones(app)
                assert len(app.get("plotly_chart")) == 5
                filtrado = df.loc[df["Stress_Level"].isin(seleccion)]
                m = metricas(app)
                assert m["Estudiantes seleccionados"] == str(len(filtrado))
                assert m["GPA promedio"] == f"{filtrado['GPA'].mean():.3f}"
                assert m["Estudio promedio"] == f"{filtrado[TIEMPO[0]].mean():.3f} h"
                r = filtrado[TIEMPO[0]].corr(filtrado["GPA"])
                specs = [grafico.proto.spec for grafico in app.get("plotly_chart")]
                assert f"{r:.3f}" in json.loads(specs[1])["layout"]["title"]["text"]
                if len(seleccion) < 3:
                    assert all(nuevo != completo for nuevo, completo in zip(specs, completos))
                tablas = app.dataframe
                pd.testing.assert_frame_equal(tablas[1].value, resumen_estres(filtrado).round(3).rename_axis("Nivel de estrés"))
                pd.testing.assert_frame_equal(tablas[2].value, resumen_actividad(filtrado).round(3))
        app.multiselect[0].set_value([]).run()
        sin_excepciones(app)
        assert len(app.get("plotly_chart")) == 0
        assert app.warning
        assert metricas(app)["Estudiantes seleccionados"] == "0"
        app.multiselect[0].set_value(ESTRES).run()
        sin_excepciones(app)
        assert len(app.get("plotly_chart")) == 5
        print("OK: cinco gráficos, tablas filtradas y las ocho combinaciones del filtro, incluida la selección vacía.")

        app.switch_page("pages/3_hallazgos.py").run()
        sin_excepciones(app)
        assert len(app.get("plotly_chart")) == 1
        assert len([titulo for titulo in app.subheader if titulo.value[:1] in '12345']) == 5
        pd.testing.assert_frame_equal(app.dataframe[0].value, estudio.round(3))
        app.switch_page("pages/1_problema_datos.py").run()
        sin_excepciones(app)
        assert metricas(app)["Estudiantes"] == "2.000"
        print("OK: hallazgos y regreso a la primera página sin excepciones.")
    finally:
        os.chdir(anterior)
    assert hashlib.sha256(CSV.read_bytes()).hexdigest() == original
    print("OK: CSV conservado sin modificaciones. Verificación completa.")


if __name__ == "__main__":
    verificar()
