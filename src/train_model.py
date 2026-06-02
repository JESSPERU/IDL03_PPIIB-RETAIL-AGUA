# ==========================================
# TRAIN MODEL
# Proyecto Retail Agua
# ==========================================

import pandas as pd
import numpy as np
import joblib

from datetime import datetime

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from sklearn.linear_model import LinearRegression

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.model_selection import TimeSeriesSplit

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# ==========================================
# 1. CARGAR DATASET
# ==========================================

df = pd.read_csv(
    "data/2.-Tablas Gold/ml_dataset.csv"
)

print(df.shape)

# ==========================================
# 2. PREPARACIÓN
# ==========================================

df["fecha"] = pd.to_datetime(
    df["fecha"]
)

columnas_eliminar = [
    "fecha",
    "fecha_creacion",
    "fecha_modificacion",
    "usuario_modificacion",
    "stock_disponible_cierre"
]

df = df.drop(
    columns=columnas_eliminar,
    errors="ignore"
)

target = "cantidad_vendida_total"

X = df.drop(
    columns=[target]
)

y = df[target]

# ==========================================
# 3. VARIABLES CATEGÓRICAS
# ==========================================

categoricas = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()

# ==========================================
# 4. PREPROCESAMIENTO
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categoricas
        )
    ],
    remainder="passthrough"
)

# ==========================================
# 5. COMPARACIÓN DE MODELOS
# ==========================================

tscv = TimeSeriesSplit(
    n_splits=5
)

modelos = {

    "Linear Regression":
        LinearRegression(),

    "Random Forest":
        RandomForestRegressor(
            n_estimators=100,
            random_state=42
        ),

    "Gradient Boosting":
        GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
}

resultados = []

for nombre, algoritmo in modelos.items():

    maes = []
    rmses = []
    r2s = []

    for train_idx, test_idx in tscv.split(X):

        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        modelo = Pipeline([
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                algoritmo
            )
        ])

        modelo.fit(
            X_train,
            y_train
        )

        pred = modelo.predict(
            X_test
        )

        maes.append(
            mean_absolute_error(
                y_test,
                pred
            )
        )

        rmses.append(
            np.sqrt(
                mean_squared_error(
                    y_test,
                    pred
                )
            )
        )

        r2s.append(
            r2_score(
                y_test,
                pred
            )
        )

    resultados.append([
        nombre,
        np.mean(maes),
        np.mean(rmses),
        np.mean(r2s)
    ])

resultado_df = pd.DataFrame(
    resultados,
    columns=[
        "Modelo",
        "MAE",
        "RMSE",
        "R2"
    ]
)

resultado_df = resultado_df.sort_values(
    "R2",
    ascending=False
)

print(resultado_df)

# ==========================================
# 6. MODELO GANADOR
# ==========================================

modelo_final = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )
    )
])

modelo_final.fit(
    X,
    y
)

print(
    "Modelo final entrenado."
)

# ==========================================
# 7. EXPORTAR MODELO
# ==========================================

joblib.dump(
    modelo_final,
    "models/modelo_demanda.pkl"
)

print(
    "PKL generado correctamente."
)

# ==========================================
# 8. FEATURE IMPORTANCE
# ==========================================

feature_names = (
    modelo_final
    .named_steps["preprocessor"]
    .get_feature_names_out()
)

importancias = (
    modelo_final
    .named_steps["model"]
    .feature_importances_
)

fi = pd.DataFrame({
    "feature_name": feature_names,
    "importance_value": importancias
})

fi = fi.sort_values(
    "importance_value",
    ascending=False
).reset_index(drop=True)

fi["ranking"] = fi.index + 1

fi["modelo_version"] = (
    "RandomForest_v1"
)

fi["fecha_entrenamiento"] = (
    datetime.now()
)

fi["usuario_ejecucion"] = (
    "train_model.py"
)

fi.insert(
    0,
    "id_importance",
    range(
        1,
        len(fi)+1
    )
)

fi.to_csv(
    "data/2.-Tablas Gold/ml_feature_importance.csv",
    index=False
)

print(
    "Feature importance exportado."
)