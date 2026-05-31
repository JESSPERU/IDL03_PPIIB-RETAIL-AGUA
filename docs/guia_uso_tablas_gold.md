# Guía de uso y diccionario de datos — Capa Gold

## Proyecto: Predicción de demanda para retail de agua

Este documento describe el uso funcional de las tablas Gold exportadas desde Supabase. La capa Gold es la fuente final para análisis, dashboard y Machine Learning.

**Principio general:** Bronze conserva el dato crudo, Silver limpia y tipa, y Gold consolida información lista para negocio, visualización y modelo predictivo.


---

## 1. Resumen ejecutivo de tablas

| Tabla | Tipo | Filas | Columnas | Uso principal |
|---|---:|---:|---:|---|
| `dim_producto` | Dimensión | 3 | 13 | Segmentar ventas, inventario y predicciones por producto, categoría, volumen y formato. |
| `dim_tiempo` | Dimensión | 366 | 22 | Analizar demanda por fecha, mes, feriado, quincena, temporada y clima. |
| `fact_ventas_diarias` | Hecho | 3123 | 13 | Dashboard comercial: unidades vendidas, ventas monetarias, precio promedio, descuentos y transacciones. |
| `fact_inventario` | Hecho | 1098 | 13 | Dashboard logístico: stock apertura, cierre, mínimo, quiebres y stock bajo. |
| `fact_marketing` | Hecho | 672 | 10 | Medir relación entre Ads, clics, conversiones y demanda. |
| `ml_dataset` | ML entrenamiento | 1098 | 39 | Entrenar el modelo predictivo de demanda diaria por SKU. |
| `ml_score_input` | ML scoring | 3 | 33 | Entrada del modelo; no contiene la variable objetivo. |
| `ml_score_output` | ML resultado | 0 | 15 | Salida para dashboard: demanda predicha, stock recomendado y alertas. |
| `ml_feature_importance` | ML explicabilidad | 0 | 7 | Explicar qué variables influyen en la predicción. |

---

## 2. Cómo se relacionan las tablas


Modelo recomendado para dashboard:
- `fact_ventas_diarias` se relaciona con `dim_producto` por `id_sku`.
- `fact_ventas_diarias` se relaciona con `dim_tiempo` por `fecha`.
- `fact_inventario` se relaciona con `dim_producto` por `id_sku` y con `dim_tiempo` por `fecha`.
- `fact_marketing` se relaciona con `dim_tiempo` por `fecha`.
- `ml_score_output` se relaciona con `dim_producto` por `id_sku` y con `dim_tiempo` por `fecha_objetivo`.

Tablas para Machine Learning:
- `ml_dataset`: entrenamiento histórico; contiene la variable objetivo `cantidad_vendida_total`.
- `ml_score_input`: entrada futura o planificada; no contiene la variable objetivo.
- `ml_score_output`: salida del modelo; se llena después de ejecutar el scoring.
- `ml_feature_importance`: explicabilidad; se llena después del entrenamiento.


---

## 3. Guía de uso por tabla

### `dim_producto`

**Tipo:** Dimensión  

**Filas:** 3  

**Descripción:** Catálogo enriquecido de productos/SKU.  

**Uso principal:** Segmentar ventas, inventario y predicciones por producto, categoría, volumen y formato.  

**Ejemplos de análisis:** ventas por categoría, comparación de bidón vs botella, volumen vendido por formato, stock de seguridad por producto.

**Columnas principales:**

- `id_sku`: Identificador único del SKU/producto. (Clave de producto).
- `descripcion`: Descripción del producto. (Atributo producto).
- `categoria`: Categoría del producto. (Atributo producto / Feature).
- `volumen_litros`: Volumen del producto en litros. (Atributo producto / Feature).
- `unidad_medida`: Unidad de medida. (Atributo producto).
- `formato_envase`: Formato de envase del producto. (Atributo producto / Feature).
- `costo_unitario_base`: Costo base unitario del producto. (Atributo producto).
- `precio_lista`: Precio de lista referencial. (Atributo producto).
- `stock_seguridad`: Stock de seguridad definido para el producto. (Parámetro inventario).
- `lead_time_dias`: Días estimados de reposición o abastecimiento. (Parámetro logístico).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `fecha_modificacion`: Fecha de última modificación o carga. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `dim_tiempo`

**Tipo:** Dimensión  

**Filas:** 366  

**Descripción:** Calendario enriquecido con variables climáticas y estacionalidad.  

**Uso principal:** Analizar demanda por fecha, mes, feriado, quincena, temporada y clima.  

**Ejemplos de análisis:** demanda por mes, por feriado, por quincena, por temporada, correlación con temperatura y ola de calor.

**Columnas principales:**

- `fecha`: Fecha diaria del registro. (Clave temporal).
- `anio`: Año de la fecha. (Atributo calendario).
- `mes`: Mes numérico. (Feature calendario).
- `trimestre`: Trimestre del año. (Feature calendario).
- `numero_dia_semana`: Número del día de la semana. (Feature calendario).
- `nombre_dia`: Nombre del día de la semana. (Atributo calendario).
- `es_fin_de_semana`: Indica si la fecha cae en fin de semana. (Feature calendario).
- `es_feriado`: Indica si la fecha es feriado. (Feature calendario).
- `nombre_feriado`: Nombre del feriado, si aplica. (Atributo calendario).
- `es_quincena`: Indica si la fecha cae en periodo de quincena. (Feature calendario).
- `es_fin_mes`: Indica si la fecha corresponde a fin de mes. (Feature calendario).
- `temporada`: Temporada o estación comercial. (Feature calendario).
- `temperatura_promedio_celsius`: Temperatura promedio diaria. (Feature clima).
- `temperatura_maxima_celsius`: Temperatura máxima diaria. (Feature clima).
- `temperatura_minima_celsius`: Temperatura mínima diaria. (Feature clima).
- `humedad_porcentaje`: Porcentaje de humedad diaria. (Feature clima).
- `precipitacion_mm`: Precipitación diaria en milímetros. (Feature clima).
- `alerta_ola_calor`: Indica si hubo o se espera ola de calor. (Feature clima / Alerta).
- `fuente_clima`: Fuente del dato climático. (Atributo clima).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `fecha_modificacion`: Fecha de última modificación o carga. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `fact_ventas_diarias`

**Tipo:** Hecho  

**Filas:** 3123  

**Descripción:** Ventas reales agregadas por fecha, SKU, canal y campaña.  

**Uso principal:** Dashboard comercial: unidades vendidas, ventas monetarias, precio promedio, descuentos y transacciones.  

**Ejemplos de análisis:** unidades vendidas por día, ventas monetarias, precio promedio, descuentos, transacciones por canal/campaña.

**Columnas principales:**

- `fecha`: Fecha diaria del registro. (Clave temporal).
- `id_sku`: Identificador único del SKU/producto. (Clave de producto).
- `id_canal`: Identificador del canal de venta. (Clave de canal).
- `id_campana`: Identificador de campaña publicitaria. (Clave de campaña).
- `cantidad_vendida_total`: Cantidad total vendida. En ml_dataset es la variable objetivo a predecir. (Target / Métrica).
- `venta_total`: Importe total vendido. (Métrica monetaria).
- `precio_unitario_promedio`: Precio promedio aplicado en las ventas del día. (Feature / Métrica).
- `descuento_total`: Monto total de descuento aplicado. (Métrica / Feature).
- `porcentaje_descuento_promedio`: Porcentaje promedio de descuento. (Métrica / Feature).
- `numero_transacciones`: Campo `numero_transacciones`. (Campo).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `fecha_modificacion`: Fecha de última modificación o carga. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `fact_inventario`

**Tipo:** Hecho  

**Filas:** 1098  

**Descripción:** Fotografía diaria de inventario por SKU.  

**Uso principal:** Dashboard logístico: stock apertura, cierre, mínimo, quiebres y stock bajo.  

**Ejemplos de análisis:** días con stock bajo, quiebre de stock, comparación stock apertura vs ventas, evaluación de reposición.

**Columnas principales:**

- `fecha`: Fecha diaria del registro. (Clave temporal).
- `id_sku`: Identificador único del SKU/producto. (Clave de producto).
- `stock_inicial_sistema`: Stock inicial registrado por el sistema. (Métrica inventario).
- `ingresos_almacen`: Unidades ingresadas al almacén. (Métrica inventario / Feature).
- `stock_apertura`: Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. (Feature inventario).
- `stock_disponible_cierre`: Stock al cierre del día. No debe usarse como feature predictiva del mismo día para evitar fuga de datos. (Métrica inventario / Diagnóstico).
- `stock_minimo`: Nivel mínimo de stock para alertas. (Parámetro inventario).
- `costo_unitario`: Costo unitario del producto para inventario. (Métrica costo).
- `quiebre_stock_flag`: Indica si hubo quiebre de stock. (Alerta inventario).
- `flag_stock_bajo`: Indica si el stock estuvo por debajo del mínimo. (Alerta inventario).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `fecha_modificacion`: Fecha de última modificación o carga. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `fact_marketing`

**Tipo:** Hecho  

**Filas:** 672  

**Descripción:** Métricas diarias de publicidad digital por campaña.  

**Uso principal:** Medir relación entre Ads, clics, conversiones y demanda.  

**Ejemplos de análisis:** inversión Ads diaria, clics, impresiones, conversiones, relación Ads vs demanda.

**Columnas principales:**

- `fecha`: Fecha diaria del registro. (Clave temporal).
- `id_campana`: Identificador de campaña publicitaria. (Clave de campaña).
- `plataforma_origen`: Plataforma de Ads: Meta, Google, TikTok u otra. (Atributo marketing).
- `inversion_usd`: Inversión publicitaria diaria en dólares. (Métrica marketing).
- `impresiones`: Cantidad de impresiones publicitarias. (Métrica marketing).
- `clics`: Cantidad de clics generados por la campaña. (Métrica marketing).
- `conversiones_atribuidas`: Conversiones atribuidas a la campaña. (Métrica marketing).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `fecha_modificacion`: Fecha de última modificación o carga. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `ml_dataset`

**Tipo:** ML entrenamiento  

**Filas:** 1098  

**Descripción:** Sábana histórica consolidada con target y features.  

**Uso principal:** Entrenar el modelo predictivo de demanda diaria por SKU.  

**Uso ML:** entrenamiento del modelo. La variable objetivo es `cantidad_vendida_total`. No usar `stock_disponible_cierre` como feature predictiva del mismo día porque puede generar fuga de datos.

**Columnas principales:**

- `fecha`: Fecha diaria del registro. (Clave temporal).
- `id_sku`: Identificador único del SKU/producto. (Clave de producto).
- `categoria`: Categoría del producto. (Atributo producto / Feature).
- `volumen_litros`: Volumen del producto en litros. (Atributo producto / Feature).
- `formato_envase`: Formato de envase del producto. (Atributo producto / Feature).
- `cantidad_vendida_total`: Cantidad total vendida. En ml_dataset es la variable objetivo a predecir. (Target / Métrica).
- `stock_apertura`: Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. (Feature inventario).
- `ingresos_almacen`: Unidades ingresadas al almacén. (Métrica inventario / Feature).
- `stock_disponible_cierre`: Stock al cierre del día. No debe usarse como feature predictiva del mismo día para evitar fuga de datos. (Métrica inventario / Diagnóstico).
- `stock_minimo`: Nivel mínimo de stock para alertas. (Parámetro inventario).
- `precio_unitario_promedio`: Precio promedio aplicado en las ventas del día. (Feature / Métrica).
- `descuento_total`: Monto total de descuento aplicado. (Métrica / Feature).
- `porcentaje_descuento_promedio`: Porcentaje promedio de descuento. (Métrica / Feature).
- `inversion_ads_total`: Inversión total de Ads agregada por día. (Feature marketing).
- `clics_total`: Clics totales agregados por día. (Feature marketing).
- `impresiones_total`: Impresiones totales agregadas por día. (Feature marketing).
- `conversiones_total`: Conversiones totales agregadas por día. (Feature marketing).
- `temperatura_promedio_celsius`: Temperatura promedio diaria. (Feature clima).
- `temperatura_maxima_celsius`: Temperatura máxima diaria. (Feature clima).
- `humedad_porcentaje`: Porcentaje de humedad diaria. (Feature clima).
- `precipitacion_mm`: Precipitación diaria en milímetros. (Feature clima).
- `alerta_ola_calor`: Indica si hubo o se espera ola de calor. (Feature clima / Alerta).
- `numero_dia_semana`: Número del día de la semana. (Feature calendario).
- `mes`: Mes numérico. (Feature calendario).
- `trimestre`: Trimestre del año. (Feature calendario).
- `es_fin_de_semana`: Indica si la fecha cae en fin de semana. (Feature calendario).
- `es_feriado`: Indica si la fecha es feriado. (Feature calendario).
- `es_quincena`: Indica si la fecha cae en periodo de quincena. (Feature calendario).
- `es_fin_mes`: Indica si la fecha corresponde a fin de mes. (Feature calendario).
- `temporada`: Temporada o estación comercial. (Feature calendario).
- `ventas_lag1`: Ventas del SKU en el día anterior. (Feature histórica).
- `ventas_lag7`: Ventas del SKU hace 7 días. (Feature histórica).
- `ventas_roll7`: Promedio móvil de ventas de los últimos 7 días. (Feature histórica).
- `ads_lag1`: Inversión Ads del día anterior. (Feature marketing rezagada).
- `ads_lag3`: Inversión Ads de hace 3 días. (Feature marketing rezagada).
- `riesgo_demanda_censurada`: Indica posible demanda no observada por falta de stock. (Alerta ML).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `fecha_modificacion`: Fecha de última modificación o carga. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `ml_score_input`

**Tipo:** ML scoring  

**Filas:** 3  

**Descripción:** Datos futuros o planificados para que el modelo prediga.  

**Uso principal:** Entrada del modelo; no contiene la variable objetivo.  

**Uso ML:** contiene los datos que se entregan al modelo para predecir. No debe incluir `cantidad_vendida_total`.

**Columnas principales:**

- `id_score_input`: Identificador del registro de entrada para scoring. (Clave técnica ML).
- `fecha_objetivo`: Fecha para la cual se desea generar la predicción. (Clave temporal futura).
- `id_sku`: Identificador único del SKU/producto. (Clave de producto).
- `categoria`: Categoría del producto. (Atributo producto / Feature).
- `volumen_litros`: Volumen del producto en litros. (Atributo producto / Feature).
- `formato_envase`: Formato de envase del producto. (Atributo producto / Feature).
- `stock_apertura`: Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. (Feature inventario).
- `ingresos_almacen`: Unidades ingresadas al almacén. (Métrica inventario / Feature).
- `precio_unitario_estimado`: Precio estimado que se usará para predecir. (Feature futura).
- `descuento_estimado`: Descuento planificado o estimado para la predicción. (Feature futura).
- `inversion_ads_planificada`: Inversión publicitaria planificada para la fecha objetivo. (Feature futura).
- `clics_estimados`: Clics estimados para la predicción. (Feature futura).
- `impresiones_estimadas`: Impresiones estimadas para la predicción. (Feature futura).
- `temperatura_promedio_estimada`: Temperatura promedio estimada para la predicción. (Feature futura clima).
- `temperatura_maxima_estimada`: Temperatura máxima estimada para la predicción. (Feature futura clima).
- `humedad_porcentaje_estimada`: Humedad estimada para la predicción. (Feature futura clima).
- `precipitacion_mm_estimada`: Precipitación estimada para la predicción. (Feature futura clima).
- `alerta_ola_calor`: Indica si hubo o se espera ola de calor. (Feature clima / Alerta).
- `numero_dia_semana`: Número del día de la semana. (Feature calendario).
- `mes`: Mes numérico. (Feature calendario).
- `trimestre`: Trimestre del año. (Feature calendario).
- `es_fin_de_semana`: Indica si la fecha cae en fin de semana. (Feature calendario).
- `es_feriado`: Indica si la fecha es feriado. (Feature calendario).
- `es_quincena`: Indica si la fecha cae en periodo de quincena. (Feature calendario).
- `es_fin_mes`: Indica si la fecha corresponde a fin de mes. (Feature calendario).
- `temporada`: Temporada o estación comercial. (Feature calendario).
- `ventas_lag1`: Ventas del SKU en el día anterior. (Feature histórica).
- `ventas_lag7`: Ventas del SKU hace 7 días. (Feature histórica).
- `ventas_roll7`: Promedio móvil de ventas de los últimos 7 días. (Feature histórica).
- `ads_lag1`: Inversión Ads del día anterior. (Feature marketing rezagada).
- `ads_lag3`: Inversión Ads de hace 3 días. (Feature marketing rezagada).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `ml_score_output`

**Tipo:** ML resultado  

**Filas:** 0  

**Descripción:** Predicciones generadas por el modelo.  

**Uso principal:** Salida para dashboard: demanda predicha, stock recomendado y alertas.  

**Uso ML/dashboard:** almacena predicciones, intervalos, stock recomendado y alertas de quiebre/sobrestock. Está vacía antes de ejecutar el scoring.

**Columnas principales:**

- `id_score_output`: Identificador del resultado de predicción. (Clave técnica ML).
- `fecha_prediccion`: Fecha y hora en que se generó la predicción. (Auditoría ML).
- `fecha_objetivo`: Fecha para la cual se desea generar la predicción. (Clave temporal futura).
- `id_sku`: Identificador único del SKU/producto. (Clave de producto).
- `cantidad_predicha`: Demanda estimada por el modelo. (Predicción).
- `intervalo_bajo`: Límite inferior estimado de la demanda. (Predicción).
- `intervalo_alto`: Límite superior estimado de la demanda. (Predicción).
- `stock_apertura`: Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. (Feature inventario).
- `stock_recomendado`: Stock sugerido con margen de seguridad. (Recomendación).
- `riesgo_quiebre_stock`: Indica si el stock proyectado es menor a la demanda predicha. (Alerta predictiva).
- `riesgo_sobrestock`: Indica si el stock proyectado supera ampliamente la demanda predicha. (Alerta predictiva).
- `modelo_version`: Versión del modelo que generó el resultado. (Control ML).
- `comentario_negocio`: Texto interpretativo de la predicción. (Explicación de negocio).
- `fecha_creacion`: Fecha de creación del registro. (Auditoría).
- `usuario_modificacion`: Usuario o proceso que modificó el registro. (Auditoría).

### `ml_feature_importance`

**Tipo:** ML explicabilidad  

**Filas:** 0  

**Descripción:** Importancia de variables del modelo entrenado.  

**Uso principal:** Explicar qué variables influyen en la predicción.  

**Uso ML/dashboard:** muestra las variables más influyentes del modelo. Está vacía antes de entrenar el modelo.

**Columnas principales:**

- `id_importance`: Identificador de importancia de variable. (Clave técnica ML).
- `modelo_version`: Versión del modelo que generó el resultado. (Control ML).
- `feature_name`: Nombre de la variable usada por el modelo. (Explicabilidad).
- `importance_value`: Peso o importancia relativa de la variable. (Explicabilidad).
- `ranking`: Orden de importancia de la variable. (Explicabilidad).
- `fecha_entrenamiento`: Fecha de entrenamiento del modelo. (Auditoría ML).
- `usuario_ejecucion`: Usuario que ejecutó el proceso. (Auditoría).


---

## 4. Diccionario de datos consolidado

El diccionario completo, con columnas, tipos inferidos, rol, descripción y nulos, se entrega también en formato CSV: `diccionario_datos_gold.csv`.


### Diccionario — `dim_producto`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `id_sku` | TEXT | Clave de producto | Identificador único del SKU/producto. | 0 |
| `descripcion` | TEXT | Atributo producto | Descripción del producto. | 0 |
| `categoria` | TEXT | Atributo producto / Feature | Categoría del producto. | 0 |
| `volumen_litros` | NUMERIC | Atributo producto / Feature | Volumen del producto en litros. | 0 |
| `unidad_medida` | TEXT | Atributo producto | Unidad de medida. | 0 |
| `formato_envase` | TEXT | Atributo producto / Feature | Formato de envase del producto. | 0 |
| `costo_unitario_base` | NUMERIC | Atributo producto | Costo base unitario del producto. | 0 |
| `precio_lista` | NUMERIC | Atributo producto | Precio de lista referencial. | 0 |
| `stock_seguridad` | INTEGER | Parámetro inventario | Stock de seguridad definido para el producto. | 0 |
| `lead_time_dias` | INTEGER | Parámetro logístico | Días estimados de reposición o abastecimiento. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `fecha_modificacion` | DATE/TIMESTAMP | Auditoría | Fecha de última modificación o carga. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `dim_tiempo`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `fecha` | DATE/TIMESTAMP | Clave temporal | Fecha diaria del registro. | 0 |
| `anio` | INTEGER | Atributo calendario | Año de la fecha. | 0 |
| `mes` | INTEGER | Feature calendario | Mes numérico. | 0 |
| `trimestre` | INTEGER | Feature calendario | Trimestre del año. | 0 |
| `numero_dia_semana` | INTEGER | Feature calendario | Número del día de la semana. | 0 |
| `nombre_dia` | TEXT | Atributo calendario | Nombre del día de la semana. | 0 |
| `es_fin_de_semana` | BOOLEAN | Feature calendario | Indica si la fecha cae en fin de semana. | 0 |
| `es_feriado` | BOOLEAN | Feature calendario | Indica si la fecha es feriado. | 0 |
| `nombre_feriado` | TEXT | Atributo calendario | Nombre del feriado, si aplica. | 354 |
| `es_quincena` | BOOLEAN | Feature calendario | Indica si la fecha cae en periodo de quincena. | 0 |
| `es_fin_mes` | BOOLEAN | Feature calendario | Indica si la fecha corresponde a fin de mes. | 0 |
| `temporada` | TEXT | Feature calendario | Temporada o estación comercial. | 0 |
| `temperatura_promedio_celsius` | NUMERIC | Feature clima | Temperatura promedio diaria. | 0 |
| `temperatura_maxima_celsius` | NUMERIC | Feature clima | Temperatura máxima diaria. | 0 |
| `temperatura_minima_celsius` | NUMERIC | Feature clima | Temperatura mínima diaria. | 0 |
| `humedad_porcentaje` | NUMERIC | Feature clima | Porcentaje de humedad diaria. | 0 |
| `precipitacion_mm` | NUMERIC | Feature clima | Precipitación diaria en milímetros. | 0 |
| `alerta_ola_calor` | BOOLEAN | Feature clima / Alerta | Indica si hubo o se espera ola de calor. | 0 |
| `fuente_clima` | TEXT | Atributo clima | Fuente del dato climático. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `fecha_modificacion` | DATE/TIMESTAMP | Auditoría | Fecha de última modificación o carga. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `fact_inventario`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `fecha` | DATE/TIMESTAMP | Clave temporal | Fecha diaria del registro. | 0 |
| `id_sku` | TEXT | Clave de producto | Identificador único del SKU/producto. | 0 |
| `stock_inicial_sistema` | INTEGER | Métrica inventario | Stock inicial registrado por el sistema. | 0 |
| `ingresos_almacen` | INTEGER | Métrica inventario / Feature | Unidades ingresadas al almacén. | 0 |
| `stock_apertura` | INTEGER | Feature inventario | Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. | 0 |
| `stock_disponible_cierre` | INTEGER | Métrica inventario / Diagnóstico | Stock al cierre del día. No debe usarse como feature predictiva del mismo día para evitar fuga de datos. | 0 |
| `stock_minimo` | INTEGER | Parámetro inventario | Nivel mínimo de stock para alertas. | 0 |
| `costo_unitario` | NUMERIC | Métrica costo | Costo unitario del producto para inventario. | 0 |
| `quiebre_stock_flag` | BOOLEAN | Alerta inventario | Indica si hubo quiebre de stock. | 0 |
| `flag_stock_bajo` | BOOLEAN | Alerta inventario | Indica si el stock estuvo por debajo del mínimo. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `fecha_modificacion` | DATE/TIMESTAMP | Auditoría | Fecha de última modificación o carga. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `fact_marketing`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `fecha` | DATE/TIMESTAMP | Clave temporal | Fecha diaria del registro. | 0 |
| `id_campana` | TEXT | Clave de campaña | Identificador de campaña publicitaria. | 0 |
| `plataforma_origen` | TEXT | Atributo marketing | Plataforma de Ads: Meta, Google, TikTok u otra. | 0 |
| `inversion_usd` | NUMERIC | Métrica marketing | Inversión publicitaria diaria en dólares. | 0 |
| `impresiones` | INTEGER | Métrica marketing | Cantidad de impresiones publicitarias. | 0 |
| `clics` | INTEGER | Métrica marketing | Cantidad de clics generados por la campaña. | 0 |
| `conversiones_atribuidas` | INTEGER | Métrica marketing | Conversiones atribuidas a la campaña. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `fecha_modificacion` | DATE/TIMESTAMP | Auditoría | Fecha de última modificación o carga. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `fact_ventas_diarias`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `fecha` | DATE/TIMESTAMP | Clave temporal | Fecha diaria del registro. | 0 |
| `id_sku` | TEXT | Clave de producto | Identificador único del SKU/producto. | 0 |
| `id_canal` | TEXT | Clave de canal | Identificador del canal de venta. | 0 |
| `id_campana` | TEXT | Clave de campaña | Identificador de campaña publicitaria. | 0 |
| `cantidad_vendida_total` | INTEGER | Target / Métrica | Cantidad total vendida. En ml_dataset es la variable objetivo a predecir. | 0 |
| `venta_total` | NUMERIC | Métrica monetaria | Importe total vendido. | 0 |
| `precio_unitario_promedio` | NUMERIC | Feature / Métrica | Precio promedio aplicado en las ventas del día. | 0 |
| `descuento_total` | NUMERIC | Métrica / Feature | Monto total de descuento aplicado. | 0 |
| `porcentaje_descuento_promedio` | NUMERIC | Métrica / Feature | Porcentaje promedio de descuento. | 0 |
| `numero_transacciones` | INTEGER | Campo | Campo `numero_transacciones` de la tabla `fact_ventas_diarias`. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `fecha_modificacion` | DATE/TIMESTAMP | Auditoría | Fecha de última modificación o carga. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `ml_dataset`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `fecha` | DATE/TIMESTAMP | Clave temporal | Fecha diaria del registro. | 0 |
| `id_sku` | TEXT | Clave de producto | Identificador único del SKU/producto. | 0 |
| `categoria` | TEXT | Atributo producto / Feature | Categoría del producto. | 0 |
| `volumen_litros` | NUMERIC | Atributo producto / Feature | Volumen del producto en litros. | 0 |
| `formato_envase` | TEXT | Atributo producto / Feature | Formato de envase del producto. | 0 |
| `cantidad_vendida_total` | INTEGER | Target / Métrica | Cantidad total vendida. En ml_dataset es la variable objetivo a predecir. | 0 |
| `stock_apertura` | INTEGER | Feature inventario | Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. | 0 |
| `ingresos_almacen` | INTEGER | Métrica inventario / Feature | Unidades ingresadas al almacén. | 0 |
| `stock_disponible_cierre` | INTEGER | Métrica inventario / Diagnóstico | Stock al cierre del día. No debe usarse como feature predictiva del mismo día para evitar fuga de datos. | 0 |
| `stock_minimo` | INTEGER | Parámetro inventario | Nivel mínimo de stock para alertas. | 0 |
| `precio_unitario_promedio` | NUMERIC | Feature / Métrica | Precio promedio aplicado en las ventas del día. | 0 |
| `descuento_total` | NUMERIC | Métrica / Feature | Monto total de descuento aplicado. | 0 |
| `porcentaje_descuento_promedio` | NUMERIC | Métrica / Feature | Porcentaje promedio de descuento. | 0 |
| `inversion_ads_total` | NUMERIC | Feature marketing | Inversión total de Ads agregada por día. | 0 |
| `clics_total` | INTEGER | Feature marketing | Clics totales agregados por día. | 0 |
| `impresiones_total` | INTEGER | Feature marketing | Impresiones totales agregadas por día. | 0 |
| `conversiones_total` | INTEGER | Feature marketing | Conversiones totales agregadas por día. | 0 |
| `temperatura_promedio_celsius` | NUMERIC | Feature clima | Temperatura promedio diaria. | 0 |
| `temperatura_maxima_celsius` | NUMERIC | Feature clima | Temperatura máxima diaria. | 0 |
| `humedad_porcentaje` | NUMERIC | Feature clima | Porcentaje de humedad diaria. | 0 |
| `precipitacion_mm` | NUMERIC | Feature clima | Precipitación diaria en milímetros. | 0 |
| `alerta_ola_calor` | BOOLEAN | Feature clima / Alerta | Indica si hubo o se espera ola de calor. | 0 |
| `numero_dia_semana` | INTEGER | Feature calendario | Número del día de la semana. | 0 |
| `mes` | INTEGER | Feature calendario | Mes numérico. | 0 |
| `trimestre` | INTEGER | Feature calendario | Trimestre del año. | 0 |
| `es_fin_de_semana` | BOOLEAN | Feature calendario | Indica si la fecha cae en fin de semana. | 0 |
| `es_feriado` | BOOLEAN | Feature calendario | Indica si la fecha es feriado. | 0 |
| `es_quincena` | BOOLEAN | Feature calendario | Indica si la fecha cae en periodo de quincena. | 0 |
| `es_fin_mes` | BOOLEAN | Feature calendario | Indica si la fecha corresponde a fin de mes. | 0 |
| `temporada` | TEXT | Feature calendario | Temporada o estación comercial. | 0 |
| `ventas_lag1` | INTEGER | Feature histórica | Ventas del SKU en el día anterior. | 0 |
| `ventas_lag7` | INTEGER | Feature histórica | Ventas del SKU hace 7 días. | 0 |
| `ventas_roll7` | NUMERIC | Feature histórica | Promedio móvil de ventas de los últimos 7 días. | 0 |
| `ads_lag1` | NUMERIC | Feature marketing rezagada | Inversión Ads del día anterior. | 0 |
| `ads_lag3` | NUMERIC | Feature marketing rezagada | Inversión Ads de hace 3 días. | 0 |
| `riesgo_demanda_censurada` | BOOLEAN | Alerta ML | Indica posible demanda no observada por falta de stock. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `fecha_modificacion` | DATE/TIMESTAMP | Auditoría | Fecha de última modificación o carga. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `ml_score_input`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `id_score_input` | INTEGER | Clave técnica ML | Identificador del registro de entrada para scoring. | 0 |
| `fecha_objetivo` | DATE/TIMESTAMP | Clave temporal futura | Fecha para la cual se desea generar la predicción. | 0 |
| `id_sku` | TEXT | Clave de producto | Identificador único del SKU/producto. | 0 |
| `categoria` | TEXT | Atributo producto / Feature | Categoría del producto. | 0 |
| `volumen_litros` | NUMERIC | Atributo producto / Feature | Volumen del producto en litros. | 0 |
| `formato_envase` | TEXT | Atributo producto / Feature | Formato de envase del producto. | 0 |
| `stock_apertura` | INTEGER | Feature inventario | Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. | 0 |
| `ingresos_almacen` | INTEGER | Métrica inventario / Feature | Unidades ingresadas al almacén. | 0 |
| `precio_unitario_estimado` | NUMERIC | Feature futura | Precio estimado que se usará para predecir. | 0 |
| `descuento_estimado` | NUMERIC | Feature futura | Descuento planificado o estimado para la predicción. | 0 |
| `inversion_ads_planificada` | NUMERIC | Feature futura | Inversión publicitaria planificada para la fecha objetivo. | 0 |
| `clics_estimados` | INTEGER | Feature futura | Clics estimados para la predicción. | 0 |
| `impresiones_estimadas` | INTEGER | Feature futura | Impresiones estimadas para la predicción. | 0 |
| `temperatura_promedio_estimada` | NUMERIC | Feature futura clima | Temperatura promedio estimada para la predicción. | 0 |
| `temperatura_maxima_estimada` | NUMERIC | Feature futura clima | Temperatura máxima estimada para la predicción. | 0 |
| `humedad_porcentaje_estimada` | NUMERIC | Feature futura clima | Humedad estimada para la predicción. | 0 |
| `precipitacion_mm_estimada` | NUMERIC | Feature futura clima | Precipitación estimada para la predicción. | 0 |
| `alerta_ola_calor` | BOOLEAN | Feature clima / Alerta | Indica si hubo o se espera ola de calor. | 0 |
| `numero_dia_semana` | INTEGER | Feature calendario | Número del día de la semana. | 0 |
| `mes` | INTEGER | Feature calendario | Mes numérico. | 0 |
| `trimestre` | INTEGER | Feature calendario | Trimestre del año. | 0 |
| `es_fin_de_semana` | BOOLEAN | Feature calendario | Indica si la fecha cae en fin de semana. | 0 |
| `es_feriado` | BOOLEAN | Feature calendario | Indica si la fecha es feriado. | 0 |
| `es_quincena` | BOOLEAN | Feature calendario | Indica si la fecha cae en periodo de quincena. | 0 |
| `es_fin_mes` | BOOLEAN | Feature calendario | Indica si la fecha corresponde a fin de mes. | 0 |
| `temporada` | TEXT | Feature calendario | Temporada o estación comercial. | 0 |
| `ventas_lag1` | INTEGER | Feature histórica | Ventas del SKU en el día anterior. | 0 |
| `ventas_lag7` | INTEGER | Feature histórica | Ventas del SKU hace 7 días. | 0 |
| `ventas_roll7` | NUMERIC | Feature histórica | Promedio móvil de ventas de los últimos 7 días. | 0 |
| `ads_lag1` | NUMERIC | Feature marketing rezagada | Inversión Ads del día anterior. | 0 |
| `ads_lag3` | NUMERIC | Feature marketing rezagada | Inversión Ads de hace 3 días. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `ml_score_output`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `id_score_output` | TEXT | Clave técnica ML | Identificador del resultado de predicción. | 0 |
| `fecha_prediccion` | DATE/TIMESTAMP | Auditoría ML | Fecha y hora en que se generó la predicción. | 0 |
| `fecha_objetivo` | DATE/TIMESTAMP | Clave temporal futura | Fecha para la cual se desea generar la predicción. | 0 |
| `id_sku` | TEXT | Clave de producto | Identificador único del SKU/producto. | 0 |
| `cantidad_predicha` | TEXT | Predicción | Demanda estimada por el modelo. | 0 |
| `intervalo_bajo` | TEXT | Predicción | Límite inferior estimado de la demanda. | 0 |
| `intervalo_alto` | TEXT | Predicción | Límite superior estimado de la demanda. | 0 |
| `stock_apertura` | TEXT | Feature inventario | Stock disponible al inicio del día. Es válido como feature porque existe antes de la venta. | 0 |
| `stock_recomendado` | TEXT | Recomendación | Stock sugerido con margen de seguridad. | 0 |
| `riesgo_quiebre_stock` | TEXT | Alerta predictiva | Indica si el stock proyectado es menor a la demanda predicha. | 0 |
| `riesgo_sobrestock` | TEXT | Alerta predictiva | Indica si el stock proyectado supera ampliamente la demanda predicha. | 0 |
| `modelo_version` | TEXT | Control ML | Versión del modelo que generó el resultado. | 0 |
| `comentario_negocio` | TEXT | Explicación de negocio | Texto interpretativo de la predicción. | 0 |
| `fecha_creacion` | DATE/TIMESTAMP | Auditoría | Fecha de creación del registro. | 0 |
| `usuario_modificacion` | TEXT | Auditoría | Usuario o proceso que modificó el registro. | 0 |

### Diccionario — `ml_feature_importance`

| Columna | Tipo inferido | Rol | Descripción | Nulos |
|---|---|---|---|---:|
| `id_importance` | TEXT | Clave técnica ML | Identificador de importancia de variable. | 0 |
| `modelo_version` | TEXT | Control ML | Versión del modelo que generó el resultado. | 0 |
| `feature_name` | TEXT | Explicabilidad | Nombre de la variable usada por el modelo. | 0 |
| `importance_value` | TEXT | Explicabilidad | Peso o importancia relativa de la variable. | 0 |
| `ranking` | TEXT | Explicabilidad | Orden de importancia de la variable. | 0 |
| `fecha_entrenamiento` | DATE/TIMESTAMP | Auditoría ML | Fecha de entrenamiento del modelo. | 0 |
| `usuario_ejecucion` | TEXT | Auditoría | Usuario que ejecutó el proceso. | 0 |

---

## 5. Recomendaciones de uso


1. Para Power BI, Streamlit o Looker, usar principalmente `dim_producto`, `dim_tiempo`, `fact_ventas_diarias`, `fact_inventario`, `fact_marketing` y `ml_score_output`.
2. Para entrenamiento del modelo, usar `ml_dataset`.
3. Para predicciones futuras, alimentar `ml_score_input` y ejecutar el script de scoring para llenar `ml_score_output`.
4. Para explicabilidad, mostrar `ml_feature_importance` en el dashboard.
5. Evitar prometer tiempo real absoluto. Esta arquitectura está pensada para actualización programada o incremental.
6. Mantener `stock_apertura` como feature válida y no usar `stock_disponible_cierre` como variable predictiva del mismo día.
