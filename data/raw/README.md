# Datos originales

El archivo fuente del proyecto (raw), `04LicitacionesEne.csv`, no se versiona (está excluido en `.gitignore`). Cada integrante lo descarga y lo deja en esta carpeta.

| Dato | Valor |
|---|---|
| Archivo del proyecto | `04LicitacionesEne.csv` (45.741 filas, 72 columnas, separador `;`, codificación `latin-1`) |
| Fuente pública oficial | [`Municipalidades.7z`](https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Municipalidades.7z) de Mercado Público (ChileCompra), licitaciones por sector, primer semestre de 2025. Contiene `04LicitacionesEne.csv`, `04LicitacionesFeb.csv` y `04LicitacionesMar.csv` |
| Copia exacta del proyecto (cuenta UNAB) | [04LicitacionesEne.zip en OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) (solo integrantes del grupo y docente con cuenta institucional UNAB) |

## Relación entre la fuente pública y el archivo del proyecto

El archivo del proyecto proviene del `04LicitacionesEne.csv` publicado en `Municipalidades.7z`, con dos diferencias:

1. **Se quitaron las columnas `Proveedor` y `ProveedorRUT`** (identificadores directos de los oferentes). El archivo público tiene 74 columnas; el del proyecto, 72.
2. **El grupo hizo esa eliminación en Excel**, que volvió a escribir el archivo. Excel no cambió filas ni columnas, pero sí el formato de algunos valores: las fechas perdieron los segundos (`11:07:00` → `11:07`), los códigos largos pasaron a notación científica (`2152204004001` → `2,15E+12`), algunos ceros a la izquierda se perdieron (`00798` → `798`), algunos montos se redondearon (`15756302,999999998` → `15756303`) y algunos textos se convirtieron en fecha (`10-2025` → `oct-25`).

Por eso el archivo público y el del proyecto tienen SHA-256 distintos (ver la tabla de abajo). Las cifras del análisis no cambian, y `pytest` lo comprueba (ver Opción B): con el archivo público, el pipeline de F3 entrega las mismas 2.257 licitaciones comparables y las mismas 1.254 coincidencias; solo 7 de 2.292 licitaciones difieren en `MontoTotalGanadoras`, en menos de una parte en 10⁻⁹, por el redondeo de Excel. Al leer, `cargar_csv()` descarta `Proveedor` y `ProveedorRUT` mediante `es_columna_privada()`.

## Cómo obtenerlo

### Opción A — Copia exacta del proyecto (cuenta UNAB)

Reproduce byte a byte las salidas versionadas en `data/processed/`.

1. Abre el [enlace de OneDrive](https://uandresbelloedu-my.sharepoint.com/:u:/g/personal/o_salgadosanhueza1_uandresbello_edu/IQCmmeS9mqScQ7om4C8pptK-AawF-4DLpDESncr5zrz-5uM?e=L8yMs7) con tu cuenta institucional UNAB y usa **Descargar**.
2. Descomprime `04LicitacionesEne.zip` y deja el CSV directamente en `data/raw/04LicitacionesEne.csv`.
3. Verifica su SHA-256 (sección siguiente).

### Opción B — Fuente pública oficial (sin cuenta)

Permite revisar el origen de los datos y comprobar, con `pytest`, que el archivo público entrega las mismas cifras del análisis. No sirve para ejecutar F2 y F3: los notebooks verifican el SHA-256 de la copia del proyecto, que es lo que garantiza que se reproducen byte a byte las salidas versionadas en `data/processed/`.

1. Descarga [`Municipalidades.7z`](https://chc-lic-files.mercadopublico.cl/sector/2025/Sem1/Municipalidades.7z) y extrae `04LicitacionesEne.csv` (requiere un descompresor de 7z, por ejemplo 7-Zip).
2. Compara su SHA-256 con la fila «Fuente pública» de la tabla de abajo.
3. Para comprobar la equivalencia, déjalo en `data/raw/04LicitacionesEne.csv` y ejecuta `pytest` desde la raíz. La prueba `test_fuente_publica_entrega_las_mismas_cifras` ([`tests/test_regresion_f2.py`](../../tests/test_regresion_f2.py)) pasa el archivo público por el pipeline y lo compara con `data/processed/`: las mismas 2.292 licitaciones con el mismo estado de brecha, 2.257 comparables y 1.254 coincidencias; solo difieren los montos redondeados por Excel (menos de una parte en 10⁻⁹) y las fechas, que no intervienen en la brecha (decisión 19 en [`docs/decisiones.md`](../../docs/decisiones.md)).

El portal de datos abiertos de ChileCompra (`datos-abiertos.chilecompra.cl`) entrega otro archivo, con otro esquema y otro SHA-256; no es la fuente de este proyecto.

### Qué ocurre en cada caso

El código identifica el archivo por su SHA-256 (`identificar_raw()` en `src/preprocesamiento.py`):

| Paso | Copia del proyecto (Opción A) | Archivo público (Opción B) | Sin archivo |
|---|---|---|---|
| F1 | Corre y contrasta el encabezado (72 columnas) | Corre; omite el contraste con un aviso | Corre; avisa que falta |
| F2 y F3 | Corren y reproducen `data/processed/` byte a byte | Se detienen con un mensaje que explica la Opción A | Se detienen con las instrucciones de descarga |
| F4 | Corre con las comprobaciones contra `data/raw` (secciones 3 y 8) | Corre desde `data/processed/`; omite esas comprobaciones con un aviso | Igual que con el archivo público |
| `pytest` | Pasa la regresión exacta contra F2; omite la de equivalencia | Pasa la de equivalencia; omite la regresión exacta | Omite ambas; pasan las demás |

### Por qué no se versiona el raw ni una muestra

Además de `Proveedor` y `ProveedorRUT`, las columnas de texto libre contienen datos de terceros: en `NombreOferta` hay razones sociales (4.672 filas), RUT (272), correos (134) y teléfonos (194); en `EspecificacionesProveedor`, RUT (217), correos (460) y teléfonos (1.740); y `Descripcion` incluye nombres de funcionarios. `cargar_csv()` descarta `EspecificacionesProveedor` al leer y ninguna de estas columnas se exporta: las salidas versionadas solo tienen columnas numéricas, de fecha y categóricas. Anonimizar el texto libre no es confiable, por lo que tampoco se versiona una muestra.

Cuidados, sobre todo en Windows:

- **No abras y guardes el CSV con Excel.** Excel lo vuelve a escribir y altera el contenido, como ocurrió con la versión del proyecto descrita arriba, aunque pandas lo siga leyendo sin error. Si necesitas mirarlo, ciérralo sin guardar.
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
| Copia del proyecto, tal como viene en el zip de OneDrive (CRLF) | `480d475e356997e6a98429106bfadc0e7646890bb7e9553d03c5bd087aa3ed04` |
| Copia del proyecto con saltos de línea Unix (LF) | `ec308de2f2785fea3cf3304b200e350b8e9b9a92f3bd828d9bf0e152c7a041bf` |
| Fuente pública, `04LicitacionesEne.csv` extraído de `Municipalidades.7z` (CRLF) | `1b17e13f16d0b17ccd356bc9f47322a9302b415ad12151fc70106b21277fab22` |
| Fuente pública con saltos de línea Unix (LF) | `9e1a0589a4baf07909bc04e72a5b026574e02e11203e4908ed75d582526b2909` |

Las dos primeras filas tienen el mismo contenido y pandas las lee igual; lo mismo ocurre con las dos últimas. Cualquier otro valor indica que el archivo fue modificado o que es una versión distinta: bórralo y descárgalo de nuevo.

Para comprobar los comprimidos antes de extraerlos: el zip de OneDrive tiene SHA-256 `6b02ece3198802e0be733b93e3456b032e3811da69c8412a740af76992c57420` y `Municipalidades.7z` (publicado el 23 de abril de 2025), `fd49de170dba09c0cf17c2a0606bd04405dd461426676c080d2d533dfff5b8e3`.

### Verificación automática en Python (`src/preprocesamiento.py`)

El proyecto valida automáticamente el archivo ignorando los retornos de carro `\r` (produciendo `ec308de2f2785fea3cf3304b200e350b8e9b9a92f3bd828d9bf0e152c7a041bf` tanto en Windows CRLF como en macOS/Linux LF):

```python
from pathlib import Path
from src.preprocesamiento import verificar_hash_raw

verificar_hash_raw(Path("data/raw/04LicitacionesEne.csv"))
```
