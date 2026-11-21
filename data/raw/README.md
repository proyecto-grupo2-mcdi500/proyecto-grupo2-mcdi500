# Datos originales

El archivo de entrada `04LicitacionesEne.csv` no se versiona (está excluido en `.gitignore`). Cada integrante lo descarga y lo deja en esta carpeta.

| Dato | Valor |
|---|---|
| Archivo | `04LicitacionesEne.csv` (45.741 filas, 72 columnas, separador `;`, codificación `latin-1`) |
| Descarga pública (recomendada) | [ChileCompra — Datos Abiertos (`ordenes-y-licitaciones`)](https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones), apartado **Licitaciones**, año **2025**, mes **Enero** (sector Municipalidades) |
| Acceso público | Libre desde el portal oficial de ChileCompra (no requiere cuenta UNAB) |
| Espejo alternativo (cuenta UNAB) | [04LicitacionesEne.zip en OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) (solo integrantes del grupo y docente con cuenta institucional UNAB) |

## Cómo obtenerlo

### Opción A — Portal público oficial de ChileCompra (sin cuenta UNAB)

1. Abre [ChileCompra — Datos Abiertos (`ordenes-y-licitaciones`)](https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones).
2. Selecciona **Licitaciones** → año **2025** → mes **Enero** (sector **Municipalidades**, archivo `04LicitacionesEne.zip`).
3. Descarga y descomprime `04LicitacionesEne.zip`.
4. Deja el CSV exactamente en `data/raw/04LicitacionesEne.csv`.
5. Comprueba que tenga exactamente el mismo SHA-256 indicado abajo (`ec308de2f2785fea3cf3304b200e350b8e9b9a92f3bd828d9bf0e152c7a041bf` en LF / sin `\r`).

### Opción B — Espejo en OneDrive (solo cuenta UNAB)

1. Abre el [enlace de OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) con tu cuenta institucional UNAB y usa **Descargar**.
2. Descomprime `04LicitacionesEne.zip` y deja el CSV directamente en `data/raw/04LicitacionesEne.csv`.
3. Verifica su SHA-256 (ambas fuentes entregan exactamente el mismo archivo y hash).

Cuidados, sobre todo en Windows:

- **No abras y guardes el CSV con Excel.** Excel lo vuelve a escribir y puede alterar el contenido, aunque pandas lo siga leyendo sin error. Si necesitas mirarlo, ciérralo sin guardar.
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
| CSV tal como viene en el zip (saltos de línea de Windows, CRLF) | `480d475e356997e6a98429106bfadc0e7646890bb7e9553d03c5bd087aa3ed04` |
| Mismo contenido con saltos de línea Unix (LF) | `ec308de2f2785fea3cf3304b200e350b8e9b9a92f3bd828d9bf0e152c7a041bf` |

Ambas tienen el mismo contenido y pandas las lee igual. Cualquier otro valor indica que el archivo fue modificado (por ejemplo, guardado con Excel) o que es una versión anterior: bórralo y descárgalo de nuevo.

Para comprobar el zip antes de descomprimirlo, su SHA-256 es `6b02ece3198802e0be733b93e3456b032e3811da69c8412a740af76992c57420`.

### Verificación automática en Python (`src/preprocesamiento.py`)

El proyecto valida automáticamente el archivo ignorando los retornos de carro `\r` (produciendo `ec308de2f2785fea3cf3304b200e350b8e9b9a92f3bd828d9bf0e152c7a041bf` tanto en Windows CRLF como en macOS/Linux LF):

```python
from pathlib import Path
from src.preprocesamiento import verificar_hash_raw

verificar_hash_raw(Path("data/raw/04LicitacionesEne.csv"))
```
