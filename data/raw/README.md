# Datos originales

El archivo original `04LicitacionesEne.csv` **no se versiona** en este repositorio: contiene el nombre y el RUT de los proveedores, y parte de ellos corresponde a personas naturales. Está excluido en `.gitignore` y cada integrante lo descarga a su copia local de esta carpeta.

Los notebooks no modifican este archivo: trabajan sobre una copia en memoria y guardan sus salidas en `data/processed/`.

| Dato | Valor |
|---|---|
| Archivo | `04LicitacionesEne.csv` (45.741 filas, 74 columnas, separador `;`, codificación `latin-1`) |
| Descarga | [04LicitacionesEne.zip en OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQC4FsRVSA7FQZ_vVtA7HW9gAXYbDcGX6o_MVfe2-Uywd70?e=cu6AXI) |
| Acceso | Solo los integrantes del grupo y el docente, con su cuenta institucional UNAB |
| Fuente declarada | [ChileCompra — Datos Abiertos](https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones), sector Municipalidades, enero de 2025 |

## Cómo obtenerlo

1. Abre el enlace de descarga con tu cuenta UNAB y usa **Descargar**.
2. Descomprime `04LicitacionesEne.zip`.
3. Deja el CSV en esta carpeta, con esta ruta exacta: `data/raw/04LicitacionesEne.csv`.
4. Verifica que sea la versión del proyecto (sección siguiente).

Cuidados, sobre todo en Windows:

- **No abras y guardes el CSV con Excel.** Excel lo vuelve a escribir con otro separador y altera el contenido, aunque pandas lo siga leyendo sin error. Si necesitas mirarlo, ciérralo sin guardar.
- **No lo dejes dentro de una subcarpeta.** *Extraer todo* crea `04LicitacionesEne\04LicitacionesEne.csv`; mueve el CSV para que quede directamente en `data\raw\`.
- **Revisa el nombre.** Si el navegador lo descargó como `04LicitacionesEne (1).zip`, el CSV interior igual se llama `04LicitacionesEne.csv`; no le cambies el nombre.

## Verificar la versión (SHA-256)

Desde la raíz del repositorio:

```bash
# macOS / Linux
shasum -a 256 data/raw/04LicitacionesEne.csv

# Windows (Git Bash)
sha256sum data/raw/04LicitacionesEne.csv
```

```powershell
# Windows (PowerShell)
Get-FileHash data\raw\04LicitacionesEne.csv -Algorithm SHA256
```

El resultado debe ser uno de estos (PowerShell lo muestra en mayúsculas; es el mismo valor):

| Versión | SHA-256 |
|---|---|
| CSV tal como viene en el zip (saltos de línea de Windows, CRLF) | `8bfe41efd05c4507146c87147b8207c7d415325f367e15d5878128fb35e155d3` |
| Mismo contenido con saltos de línea Unix (LF), la versión que estuvo en Git | `912409d5e7119b0866de35fb86dccb37df949ef1f6406882dbe7817a7a3b6282` |

Ambas tienen el mismo contenido y pandas las lee igual. Cualquier otro valor indica que el archivo fue modificado (por ejemplo, guardado con Excel): bórralo y descárgalo de nuevo.

Para comprobar el zip antes de descomprimirlo, su SHA-256 es `f3d11a392056d1468c60763ee787e601373ae52d45ab77c224e2f83d4f10f50d`.
