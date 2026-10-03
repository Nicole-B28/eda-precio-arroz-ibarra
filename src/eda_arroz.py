import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos del productor
datos_productor = pd.read_excel(
    "data/precios-productor-ponderado.xlsx",
    sheet_name="Nacional",
    skiprows=6
)

# Eliminar columnas completamente vacías
datos_productor = datos_productor.dropna(axis=1, how="all")

# Filtrar solamente productos que contienen la palabra "Arroz"
arroz_productor = datos_productor[
    datos_productor["Producto"]
    .str.contains("Arroz", case=False, na=False)
]

# Mostrar productos de arroz encontrados
print("\nProductos de arroz encontrados:")
print(arroz_productor["Producto"].value_counts())

# Mostrar primeras filas del arroz
print("\nPrimeros registros de arroz:")
print(arroz_productor.head())

# Cargar datos de bodegas comerciales
datos_bodega = pd.read_excel(
    "data/precios-mercados-mayoristas-bodegas-comerciales.xlsx",
    sheet_name="Precios bodegas 12-26",
    skiprows=7
)

# Eliminar columnas completamente vacías
datos_bodega = datos_bodega.dropna(axis=1, how="all")

# Filtrar solamente productos que contienen la palabra arroz
arroz_bodega = datos_bodega[
    datos_bodega["Producto"]
    .str.contains("Arroz", case=False, na=False)
]

print("\nProductos de arroz encontrados en bodegas:")
print(arroz_bodega["Producto"].value_counts())

print("\nRegistros de arroz en Imbabura:")
print(
    arroz_bodega[
        arroz_bodega["Provincia"].str.upper() == "IMBABURA"
    ].head()
)

# ---------------------------------------------------------
# PREPARAR SERIES COMPARABLES DE ARROZ
# ---------------------------------------------------------

# Crear una versión estandarizada del nombre del producto
datos_productor["Producto_limpio"] = (
    datos_productor["Producto"]
    .str.lower()
    .str.strip()
)

datos_bodega["Producto_limpio"] = (
    datos_bodega["Producto"]
    .str.lower()
    .str.strip()
)

# Filtrar el producto comparable
productor_filtrado = datos_productor[
    datos_productor["Producto_limpio"] == "arroz pilado grano largo"
].copy()

bodega_ibarra = datos_bodega[
    (datos_bodega["Producto_limpio"] == "arroz pilado natural grano largo") &
    (datos_bodega["Provincia"].str.upper() == "IMBABURA")
].copy()

print("\nRegistros productor seleccionados:")
print(productor_filtrado.shape)

print("\nRegistros bodega Ibarra seleccionados:")
print(bodega_ibarra.shape)

# ---------------------------------------------------------
# CREAR FECHA A PARTIR DE AÑO Y MES
# ---------------------------------------------------------

meses = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}

# Convertir los meses a minúsculas
productor_filtrado["Mes_num"] = (
    productor_filtrado["Mes"]
    .str.lower()
    .str.strip()
    .map(meses)
)

bodega_ibarra["Mes_num"] = (
    bodega_ibarra["Mes"]
    .str.lower()
    .str.strip()
    .map(meses)
)

# Crear una fecha mensual
productor_filtrado["Fecha"] = pd.to_datetime(
    dict(
        year=productor_filtrado["Año"],
        month=productor_filtrado["Mes_num"],
        day=1
    )
)

bodega_ibarra["Fecha"] = pd.to_datetime(
    dict(
        year=bodega_ibarra["Año"],
        month=bodega_ibarra["Mes_num"],
        day=1
    )
)

print("\nFechas productor:")
print(productor_filtrado[["Fecha", "Producto", "Precio Promedio (USD/KG)"]].head())

print("\nColumnas exactas de la base de bodegas:")
print(bodega_ibarra.columns.tolist())

# ---------------------------------------------------------
# CREAR PROMEDIOS MENSUALES
# ---------------------------------------------------------

# Promedio mensual del precio al productor
productor_mensual = (
    productor_filtrado
    .groupby("Fecha", as_index=False)["Precio Promedio (USD/KG)"]
    .mean()
)

# Cambiar nombre de la columna para identificarla mejor
productor_mensual = productor_mensual.rename(
    columns={"Precio Promedio (USD/KG)": "Precio_Productor_USD_KG"}
)

# Promedio mensual del precio en bodegas de Ibarra
ibarra_mensual = (
    bodega_ibarra
    .groupby("Fecha", as_index=False)["Precio  Promedio (USD/Kg)"]
    .mean()
)

# Cambiar nombre de la columna
ibarra_mensual = ibarra_mensual.rename(
    columns={"Precio  Promedio (USD/Kg)": "Precio_Ibarra_USD_KG"}
)

print("\nPrecio mensual productor:")
print(productor_mensual.head())

print("\nPrecio mensual Ibarra:")
print(ibarra_mensual.head())

# ---------------------------------------------------------
# UNIR PRODUCTOR E IBARRA
# ---------------------------------------------------------

comparacion = pd.merge(
    productor_mensual,
    ibarra_mensual,
    on="Fecha",
    how="inner"
)

print("\nTabla comparativa:")
print(comparacion.head(10))

print("\nNúmero de meses comparables:")
print(len(comparacion))

# ---------------------------------------------------------
# CALCULAR BRECHA DE PRECIOS
# ---------------------------------------------------------

comparacion["Brecha_USD_KG"] = (
    comparacion["Precio_Ibarra_USD_KG"]
    - comparacion["Precio_Productor_USD_KG"]
)

comparacion["Brecha_Porcentual"] = (
    comparacion["Brecha_USD_KG"]
    / comparacion["Precio_Productor_USD_KG"]
) * 100

print("\nTabla con brecha de precios:")
print(comparacion.head(10))

# ---------------------------------------------------------
# PREGUNTA 1
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("PREGUNTA 1:")
print("¿El precio en Ibarra responde de forma inmediata a los cambios")
print("del precio al productor?")

print("\nRESPUESTA:")
print(
    "No de forma inmediata. Entre agosto de 2022 y julio de 2026, "
    "el precio al productor presenta variaciones frecuentes, mientras "
    "que el precio en las bodegas de Ibarra permanece estable durante "
    "varios meses y cambia de manera más escalonada. "
    "Esto sugiere que la transmisión del precio entre ambos niveles "
    "de la cadena no es inmediata ni proporcional."
)

print(
    "\nPor ejemplo, durante parte de 2024 el precio al productor disminuye "
    "aproximadamente desde USD 0.95/kg hasta USD 0.78/kg, mientras que "
    "el precio en Ibarra se mantiene alrededor de USD 1.50/kg."
)


# ---------------------------------------------------------
# GRÁFICA DE LA PREGUNTA 1
# ---------------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    comparacion["Fecha"],
    comparacion["Precio_Productor_USD_KG"],
    marker="o",
    label="Precio productor"
)

plt.plot(
    comparacion["Fecha"],
    comparacion["Precio_Ibarra_USD_KG"],
    marker="o",
    label="Precio bodega Ibarra"
)

plt.title(
    "Evolución del precio del arroz: productor vs. bodega Ibarra"
)

plt.xlabel("Fecha")
plt.ylabel("Precio promedio (USD/kg)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "resultados/01_transmision_precios.png",
    dpi=300
)

plt.show()


# ---------------------------------------------------------
# PREGUNTA 2
# ---------------------------------------------------------

# Encontrar el mes con la mayor brecha
fila_max_brecha = comparacion.loc[
    comparacion["Brecha_USD_KG"].idxmax()
]

fecha_max = fila_max_brecha["Fecha"]
precio_productor_max = fila_max_brecha["Precio_Productor_USD_KG"]
precio_ibarra_max = fila_max_brecha["Precio_Ibarra_USD_KG"]
brecha_max = fila_max_brecha["Brecha_USD_KG"]
brecha_porcentual_max = fila_max_brecha["Brecha_Porcentual"]

print("\n" + "=" * 80)
print("PREGUNTA 2:")
print("¿En qué periodo se produjo el mayor desacople entre el precio")
print("al productor y el precio de las bodegas de Ibarra?")

print("\nRESPUESTA:")
print(
    f"La mayor brecha se registró en {fecha_max.strftime('%B de %Y')}."
)

print(
    f"En ese mes, el precio al productor fue de USD {precio_productor_max:.2f}/kg, "
    f"mientras que en Ibarra fue de USD {precio_ibarra_max:.2f}/kg."
)

print(
    f"La diferencia fue de USD {brecha_max:.2f}/kg, equivalente a "
    f"{brecha_porcentual_max:.1f}% respecto al precio al productor."
)

# ---------------------------------------------------------
# GRÁFICA DE LA PREGUNTA 2
# ---------------------------------------------------------

top_brechas = comparacion.nlargest(
    10,
    "Brecha_USD_KG"
).copy()

top_brechas["Periodo"] = top_brechas["Fecha"].dt.strftime("%Y-%m")

top_brechas = top_brechas.sort_values("Brecha_USD_KG")

plt.figure(figsize=(10, 6))

plt.barh(
    top_brechas["Periodo"],
    top_brechas["Brecha_USD_KG"]
)

plt.title("10 meses con mayor brecha de precios")
plt.xlabel("Brecha entre Ibarra y productor (USD/kg)")
plt.ylabel("Periodo")
plt.tight_layout()

plt.savefig(
    "resultados/02_mayores_brechas.png",
    dpi=300
)

plt.show()


# ---------------------------------------------------------
# PREGUNTA 3
# ---------------------------------------------------------

rezagos = []

for mes_rezago in range(0, 7):

    correlacion = comparacion["Precio_Productor_USD_KG"].corr(
        comparacion["Precio_Ibarra_USD_KG"].shift(-mes_rezago)
    )

    rezagos.append({
        "Rezago_meses": mes_rezago,
        "Correlacion": correlacion
    })

rezagos_df = pd.DataFrame(rezagos)

mejor_fila = rezagos_df.loc[
    rezagos_df["Correlacion"].idxmax()
]

mejor_rezago = int(mejor_fila["Rezago_meses"])
mejor_correlacion = mejor_fila["Correlacion"]

print("\n" + "=" * 80)
print("PREGUNTA 3:")
print("¿Existe un rezago entre el cambio del precio al productor")
print("y el precio observado posteriormente en Ibarra?")

print("\nRESPUESTA:")
print(
    f"La mayor correlación se observa con un rezago de "
    f"{mejor_rezago} meses."
)

print(
    f"En ese punto, la correlación alcanza aproximadamente "
    f"{mejor_correlacion:.2f}."
)

print(
    "Esto sugiere que los movimientos del precio al productor "
    "podrían reflejarse con retraso en el precio observado en Ibarra."
)

print(
    "Sin embargo, esta relación es exploratoria y no demuestra causalidad."
)

# ---------------------------------------------------------
# GRÁFICA DE LA PREGUNTA 3
# ---------------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    rezagos_df["Rezago_meses"],
    rezagos_df["Correlacion"],
    marker="o"
)

plt.title("Correlación entre productor e Ibarra según meses de rezago")
plt.xlabel("Meses de rezago")
plt.ylabel("Correlación")
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "resultados/03_rezago_transmision.png",
    dpi=300
)

plt.show()


# ---------------------------------------------------------
# PREGUNTA 4
# ---------------------------------------------------------

# Calcular variaciones porcentuales mensuales
comparacion["Variacion_Productor"] = (
    comparacion["Precio_Productor_USD_KG"]
    .pct_change() * 100
)

comparacion["Variacion_Ibarra"] = (
    comparacion["Precio_Ibarra_USD_KG"]
    .pct_change() * 100
)

# Identificar meses en que ambos precios se movieron
# en la misma dirección
misma_direccion = (
    (
        (comparacion["Variacion_Productor"] > 0) &
        (comparacion["Variacion_Ibarra"] > 0)
    )
    |
    (
        (comparacion["Variacion_Productor"] < 0) &
        (comparacion["Variacion_Ibarra"] < 0)
    )
)

porcentaje_misma_direccion = (
    misma_direccion.iloc[1:].mean() * 100
)

print("\n" + "=" * 80)
print("PREGUNTA 4:")
print("¿Las subidas y bajadas del precio al productor")
print("se reflejan de la misma manera en Ibarra?")

print("\nRESPUESTA:")
print(
    f"Solo aproximadamente el {porcentaje_misma_direccion:.1f}% "
    "de los meses muestran movimientos en la misma dirección."
)

print(
    "Esto significa que una subida o bajada del precio al productor "
    "no necesariamente coincide en el mismo mes con un movimiento "
    "equivalente en el precio de Ibarra."
)

print(
    "El resultado refuerza la hipótesis de que la transmisión "
    "de precios puede presentar retrasos o comportamientos diferentes "
    "a lo largo de la cadena comercial."
)

# ---------------------------------------------------------
# GRÁFICA DE LA PREGUNTA 4
# ---------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.scatter(
    comparacion["Variacion_Productor"],
    comparacion["Variacion_Ibarra"]
)

plt.axhline(0, linestyle="--")
plt.axvline(0, linestyle="--")

plt.title(
    "Variación mensual del precio: productor vs. Ibarra"
)

plt.xlabel("Variación mensual del productor (%)")
plt.ylabel("Variación mensual en Ibarra (%)")

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "resultados/04_variaciones_productor_ibarra.png",
    dpi=300
)

plt.show()

# ---------------------------------------------------------
# PREGUNTA 5
# ---------------------------------------------------------

# Crear columna de año
comparacion["Año"] = comparacion["Fecha"].dt.year

# Calcular brecha promedio por año
brecha_anual = (
    comparacion
    .groupby("Año", as_index=False)["Brecha_USD_KG"]
    .mean()
)

# Identificar el año con mayor brecha promedio
fila_mayor_anual = brecha_anual.loc[
    brecha_anual["Brecha_USD_KG"].idxmax()
]

anio_mayor = int(fila_mayor_anual["Año"])
brecha_mayor_anual = fila_mayor_anual["Brecha_USD_KG"]

print("\n" + "=" * 80)
print("PREGUNTA 5:")
print("¿Fue 2025 un periodo excepcional en la ampliación")
print("de la brecha entre productor e Ibarra?")

print("\nRESPUESTA:")

print("\nBrecha promedio por año:")
print(brecha_anual)

print(
    f"\nEl año con la mayor brecha promedio fue {anio_mayor}, "
    f"con aproximadamente USD {brecha_mayor_anual:.2f}/kg."
)

print(
    "Esto permite identificar si el aumento observado en 2025 "
    "forma parte de un patrón normal o representa un periodo "
    "de separación especialmente alta entre ambos precios."
)

print(
    "Importante: 2022 y 2026 contienen periodos parciales, "
    "por lo que deben interpretarse con precaución."
)

print("\n" + "=" * 80)
print("PREGUNTA 5:")
print("¿La brecha entre productor e Ibarra se ha ampliado")
print("de forma sostenida en los últimos años?")

print("\nRESPUESTA:")
print(
    "Sí. Entre los años completos analizados, la brecha promedio "
    "pasó de aproximadamente USD 0.42/kg en 2023, "
    "a USD 0.63/kg en 2024 y USD 0.75/kg en 2025."
)

print(
    "Esto muestra una ampliación importante de la diferencia "
    "entre el precio al productor y el precio observado en Ibarra."
)

print(
    "El valor de 2026 también es elevado, pero debe interpretarse "
    "con cautela porque corresponde a un periodo parcial."
)

# ---------------------------------------------------------
# GRÁFICA DE LA PREGUNTA 5
# ---------------------------------------------------------

plt.figure(figsize=(9, 5))

plt.bar(
    brecha_anual["Año"].astype(str),
    brecha_anual["Brecha_USD_KG"]
)

plt.title(
    "Evolución de la brecha promedio anual: productor vs. Ibarra"
)

plt.xlabel("Año")
plt.ylabel("Brecha promedio (USD/kg)")
plt.tight_layout()

plt.savefig(
    "resultados/05_brecha_promedio_anual.png",
    dpi=300
)

plt.show()