# Hábitos diarios y rendimiento académico

Proyecto de Ciencia de Datos desarrollado para el **Avance 2: Análisis Exploratorio de Datos (EDA)**.

## Pregunta de investigación

**¿En qué medida los hábitos diarios de los estudiantes se relacionan con su rendimiento académico, medido mediante GPA, durante el año académico 2023–2024?**

## Dataset

Se utiliza el **Student Lifestyle Dataset** con:

- 2.000 estudiantes.
- 8 columnas originales.
- 0 valores nulos.
- 0 registros duplicados.
- Unidad de observación: un estudiante.

El archivo original se conserva en:

```text
data/raw/student_lifestyle_dataset.csv
```

`Student_ID` se utiliza únicamente como identificador y se excluye de los predictores y correlaciones.

## Variables

### X — Variables explicativas

- `Study_Hours_Per_Day`
- `Extracurricular_Hours_Per_Day`
- `Sleep_Hours_Per_Day`
- `Social_Hours_Per_Day`
- `Physical_Activity_Hours_Per_Day`
- `Stress_Level`

### Y — Variable objetivo

- `GPA`

### T — Contexto temporal

- Año académico 2023–2024.
- El CSV no contiene fechas ni seguimiento temporal individual por estudiante.

## Principales hallazgos del EDA

1. Las horas de estudio presentan la mayor asociación individual con GPA (`r ≈ 0,734`).
2. Las cinco variables de tiempo suman 24 horas para todos los estudiantes, por lo que forman un presupuesto diario cerrado.
3. El grupo con estrés alto presenta mayor GPA, pero también dedica considerablemente más horas al estudio.
4. La actividad física presenta una asociación negativa moderada con GPA, pero también coincide con menos horas de estudio; debe interpretarse dentro de la distribución del tiempo.
5. Las horas de sueño no presentan una asociación lineal clara con GPA (`r ≈ 0`).

Estos resultados muestran **asociaciones y no relaciones causales**.

## Estructura del repositorio

```text
proyecto-habitos-rendimiento-academico/
├── app.py
├── datos.py
├── data/
│   └── raw/
│       └── student_lifestyle_dataset.csv
├── pages/
│   ├── 1_problema_datos.py
│   ├── 2_eda.py
│   └── 3_hallazgos.py
├── tests/
│   └── verificar.py
├── requirements.txt
├── INICIAR_STREAMLIT.bat
├── .streamlit/
│   └── config.toml
├── .vscode/
│   └── settings.json
├── .gitignore
└── README.md
```

## Instalación

Se recomienda utilizar Python 3.10 o superior.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecutar Streamlit

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

También puede utilizarse el archivo:

```text
INICIAR_STREAMLIT.bat
```

que prepara el entorno y ejecuta la aplicación automáticamente en Windows.

## Verificación

Para comprobar estructura, datos, cálculos científicos, navegación, gráficos y filtros:

```powershell
.\.venv\Scripts\python.exe tests\verificar.py
```

La verificación comprueba, entre otros puntos:

- forma del dataset `(2000, 8)`;
- ausencia de nulos y duplicados;
- outliers mediante IQR;
- presupuesto de 24 horas;
- correlaciones principales;
- resultados por nivel de estrés y actividad física;
- las tres páginas de Streamlit;
- los cinco gráficos del EDA;
- funcionamiento del filtro interactivo;
- conservación del CSV original.

## Aplicación Streamlit

La aplicación contiene tres páginas:

1. **Problema y datos** — pregunta, X/Y/T, calidad, outliers y estructura de 24 horas.
2. **EDA** — cinco visualizaciones y filtro interactivo por nivel de estrés.
3. **Hallazgos** — síntesis de resultados, limitaciones e implicancias para el modelado posterior.

## Dependencias

Las versiones utilizadas se encuentran fijadas en `requirements.txt`:

- Streamlit
- pandas
- NumPy
- Plotly
