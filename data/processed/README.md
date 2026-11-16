# Datos procesados

Salidas de F2 y su documentación generada por F3. Son los únicos archivos versionados de esta carpeta: `.gitignore` excluye cualquier otro CSV.

| Archivo | Lo genera | Unidad de análisis | Dimensiones | Contenido |
|---|---|---|---|---|
| `04LicitacionesEne_procesado.csv` | `F2/F2_Preprocesamiento.ipynb` | Oferta por ítem | 45.741 × 17 | Variables analíticas convertidas, tamaño en escala ordinal (`TamanoProveedorOrdinal`) y banderas de duplicado potencial y de valor extremo en CLP |
| `04LicitacionesEne_brecha_por_licitacion.csv` | `F2/F2_Preprocesamiento.ipynb` | Licitación | 2.292 × 24 | Suma de ofertas ganadoras, brecha frente al monto estimado, estado de la comparación y coincidencia |
| `diccionario_f3.csv` | `F3/F3_Nucleo_Algoritmico.ipynb` | Columna | 41 filas | Archivo, columna, tipo, unidad de análisis y regla de cada columna de los dos archivos anteriores |
| `parametros_f3.csv` | `F3/F3_Nucleo_Algoritmico.ipynb` | Parámetro | 8 filas | Escala del tamaño, tolerancia de coincidencia y límites del IQR ajustados sobre los montos CLP |

**Formato:** separador `;`, codificación UTF-8 con BOM (`utf-8-sig`) y saltos de línea `\n`. Al leerlos, el CSV no conserva los tipos: fechas, montos y la escala ordinal se reconstruyen con el diccionario.

```python
pd.read_csv("data/processed/04LicitacionesEne_procesado.csv", sep=";", encoding="utf-8-sig")
```

**Datos personales:** no contienen RUT, nombres ni columnas de texto libre. `cargar_csv` excluye los identificadores al leer y F2 exporta una lista explícita de columnas, comprobada por `validar_procesado()`. `NroLicitacion` es el código público de la licitación (por ejemplo, `1050283-1-LE25`), no un RUT.

## Regenerarlos

1. Descarga el archivo original en `data/raw/` (ver [`data/raw/README.md`](../raw/README.md)).
2. Ejecuta `F2/F2_Preprocesamiento.ipynb`: escribe los dos primeros archivos.
3. Ejecuta `F3/F3_Nucleo_Algoritmico.ipynb`: comprueba que su pipeline reproduce ambos archivos y escribe el diccionario y los parámetros.

Con el mismo archivo de entrada, F2 produce archivos idénticos (mismo SHA-256) en cada ejecución. Si después de ejecutar aparecen modificados en `git status`, cambió la entrada o el código.
