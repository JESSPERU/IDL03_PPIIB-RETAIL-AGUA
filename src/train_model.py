# ==========================================
# TRAIN MODEL
# Proyecto Retail Agua
# ==========================================

import pandas as pd
import joblib
from datetime import datetime

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import GradientBoostingRegressor

# ==========================================
# 1. CARGAR DATASET
# ==========================================

df = pd.read_csv("data/2.-Gold/ml_dataset.csv")

# ==========================================
# 2. FECHAS
# ==========================================

df["fecha"] = pd.to_datetime(df["fecha"])

# ==========================================
# 3. ELIMINAR COLUMNAS NO UTILIZABLES
# ==========================================

columnas_eliminar = [
    "fecha",
    "fecha_creacion",
    "fecha_modificacion",
    "usuario_modificacion",
    "stock_disponible_cierre"  # evitar data leakage
]

df = df.drop(columns=columnas_eliminar)

# ==========================================
# 4. TARGET
# ==========================================

target = "cantidad_vendida_total"

X = df.drop(columns=[target])
y = df[target]

# ==========================================
# 5. VARIABLES
# ==========================================

categoricas = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()

booleanas = X.select_dtypes(
    include=["bool"]
).columns.tolist()

numericas = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

# ==========================================
# 6. PREPROCESSOR
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
# 7. MODELO FINAL
# ==========================================

modelo = Pipeline([
    ("preprocessor", preprocessor),
    ("model", GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    ))
])

# ==========================================
# 8. ENTRENAMIENTO
# ==========================================

modelo.fit(X, y)

# ==========================================
# 9. GUARDAR PKL
# ==========================================

joblib.dump(
    modelo,
    "models/modelo_demanda.pkl"
)

print("Modelo guardado correctamente.")

# ==========================================
# 10. FEATURE IMPORTANCE
# ==========================================

feature_names = (
    modelo.named_steps["preprocessor"]
    .get_feature_names_out()
)

importancias = (
    modelo.named_steps["model"]
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

fi["modelo_version"] = "v1"

fi["fecha_entrenamiento"] = (
    datetime.now()
)

fi["usuario_ejecucion"] = "train_model.py"

fi.insert(
    0,
    "id_importance",
    range(1, len(fi)+1)
)

# ==========================================
# 11. EXPORTAR FEATURE IMPORTANCE
# ==========================================

fi.to_csv(
    "data/2.-Gold/ml_feature_importance.csv",
    index=False
)

print("Feature importance exportado.")
