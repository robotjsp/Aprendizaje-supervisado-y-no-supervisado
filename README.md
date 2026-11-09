# EA3 · Temas en los informes del conflicto armado (K-means)

Un notebook ejecutable descarga un dataset de Hugging Face, prepara los textos, entrena un modelo **no supervisado (K-means)** y genera dos cosas:
- un resumen automático en `.txt`;
- el **documento de hallazgos** (`HALLAZGOS.md`).

GitHub Actions lo ejecuta con cada `push` a `main`.

## Integrante

| Nombre | Rol |
|---|---|
| _[Escribe aquí tu nombre completo]_ | Desarrollo completo (grupo de una persona) |

## Pregunta de negocio

> **¿Qué grandes temas aparecen en los fragmentos de informes sobre el conflicto armado colombiano, para que un centro de memoria histórica organice su archivo en colecciones temáticas y decida qué líneas pedagógicas y de atención a víctimas priorizar?**

- **Quién la necesita:** el equipo de archivo y pedagogía de un centro de memoria histórica, o una ONG de víctimas.
- **Qué decisión apoya:** cómo agrupar los documentos en colecciones y a qué temas dedicar primero recursos de pedagogía, investigación y atención.

## Dataset

| | |
|---|---|
| **Identificador** | `jdavit/colombian-conflict-SQA` |
| **Enlace** | https://huggingface.co/datasets/jdavit/colombian-conflict-SQA |
| **Configuración / splits** | `default` · `train` (~2.895 filas) + `test` (30 filas), unidos |
| **Columna usada** | `context`: fragmentos reales de informes sobre el conflicto |
| **Licencia** | CC-BY-4.0 |

**¿Por qué permite responder la pregunta?** Los fragmentos tratan de masacres, desplazamiento, desaparición, despojo, memoria y otros temas, pero **nadie les puso una etiqueta de tema**. Descubrir esos grupos sin etiquetas es justamente lo que hace el aprendizaje no supervisado.

Las columnas `question` y `answer` no entran al modelo. La respuesta la escribió una IA, así que no es el texto original del informe; la pregunta solo se usa después para describir los grupos.

## ¿Por qué no supervisado y por qué K-means?

- **No supervisado:** no hay una variable objetivo que predecir. Queremos **descubrir** qué temas existen.
- **K-means:**
  - Produce grupos fáciles de explicar: cada grupo tiene un centro, y sus palabras más importantes le dan nombre.
  - Funciona bien con muchos textos.
  - El modelo guardado sirve para **asignar automáticamente** a un tema los documentos nuevos.

### Cómo funciona K-means, paso a paso

1. Se decide **k**, el número de grupos.
2. Se ubican k **centroides** iniciales. Con `k-means++` quedan repartidos lejos unos de otros.
3. Cada texto se asigna al **centroide más cercano**.
4. Cada centroide se **mueve al promedio** de los textos de su grupo.
5. Se repiten los pasos 3 y 4 hasta que los grupos dejan de cambiar.
6. Como el resultado depende del punto de partida, se repite todo `n_init` veces y se queda con la versión de menor **inercia**: la suma de las distancias al cuadrado de cada texto a su centroide.

### Parámetros principales

| Parámetro | Valor | Qué significa |
|---|---|---|
| `n_clusters` (k) | elegido con evidencia (ver abajo) | cuántos grupos se forman |
| `init` | `k-means++` (predeterminado) | cómo se ubican los centroides iniciales |
| `n_init` | 10 | cuántas veces se reinicia para no quedarse con una mala solución |
| `max_iter` | 300 (predeterminado) | máximo de repeticiones de los pasos 3 y 4 |
| `random_state` | 42 | semilla: el resultado sale igual en cada ejecución |

- **Ventajas:** es simple, rápido y fácil de explicar, y asigna nuevos textos al instante.
- **Limitaciones:**
  - Hay que elegir k.
  - Cada texto pertenece a **un solo** grupo.
  - Supone grupos de forma "redonda" y tamaño parecido.
  - Es sensible a la escala de las variables y a los valores extremos.

### Cómo se eligió k

Se entrenó K-means con k = 2 … 12 y se compararon cuatro métricas:
- **Inercia:** se busca el codo.
- **Silueta:** va de -1 a 1; más alta es mejor.
- **Davies-Bouldin:** más bajo es mejor.
- **Calinski-Harabasz:** más alto es mejor.

**Regla:** entre los k útiles para el negocio (**k ≥ 4**, porque con 2 o 3 grupos no se organiza un archivo), se elige el de **mayor silueta**. Si dos casi empatan, gana el k más pequeño. Ver `figuras/eleccion_k.png`.

## Preprocesamiento y escalado

| Paso | Problema que resuelve |
|---|---|
| Validar: tabla de calidad con métrica y decisión | saber cuántos vacíos, duplicados o espacios extra hay |
| Normalizar espacios y quitar duplicados | los textos repetidos formarían grupos artificiales |
| Quitar contextos vacíos y repetidos | sin texto no hay nada que agrupar; varias preguntas comparten el mismo fragmento |
| **TF-IDF** (`max_df=0.5`, `min_df=3`, palabras vacías en español, palabras sueltas y pares) | convierte el texto en números y quita peso a las palabras que aparecen en todas partes |
| **SVD** (100 dimensiones) | resume miles de columnas en 100 "ejes de tema" y quita ruido |
| **Normalizer** (largo 1) | **escalado**: K-means usa distancias, así que todos los textos deben estar en la misma escala para que un texto largo no quede "lejos" solo por su tamaño |

No hay división entre entrenamiento y prueba, porque en el aprendizaje no supervisado no existe una respuesta correcta con la cual comparar.

## Estructura

```
src/clases_po/
  hf_loader.py              HFDatasetLoader: conexión automática a Hugging Face
  preparador_conflicto.py   PreparadorConflicto: validar y limpiar
  agrupador_textos.py       AgrupadorTextos: TF-IDF -> SVD -> K-means, comparación de k, perfiles
  reporte_agrupamiento.py   ReporteAgrupamiento: resumen .txt y HALLAZGOS.md
src/actividades/
  EA3_Agrupamiento.ipynb    Notebook con todo el flujo y sus resultados
  reportes/EA3_resumen_modelo.txt   Resumen automático
  reportes/HALLAZGOS.md             Documento de hallazgos (generado con los resultados)
  figuras/                  eleccion_k.png, mapa_grupos.png, tamano_grupos.png
.github/workflows/ejecutar-ea3.yml
```

## Uso

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyarrow openpyxl
cd src/actividades
jupyter nbconvert --to notebook --execute --inplace EA3_Agrupamiento.ipynb
```

También se puede abrir `src/actividades/EA3_Agrupamiento.ipynb` en VS Code o Jupyter, elegir el kernel `.venv` y pulsar **Run All**.

## GitHub Actions

`.github/workflows/ejecutar-ea3.yml` se activa **automáticamente con cada `push` a `main`**. Hace lo siguiente:
1. Instala las dependencias.
2. Ejecuta el notebook, que obtiene el dataset, construye el DataFrame, preprocesa, entrena y evalúa K-means y genera el `.txt` y los hallazgos.
3. Publica el artefacto **`resumen-ea3`** (reportes, figuras, modelo y notebook).
4. Hace commit de los resultados con `[skip ci]`.

**Ejecución exitosa:** _[pega aquí el enlace]_

## Evidencias

| Evidencia | Ubicación |
|---|---|
| Pregunta de negocio y DataFrame | Notebook: introducción y Etapa 1 |
| Preprocesamiento antes y después | Notebook, Etapa 2 (calidad, registro, tabla de texto → TF-IDF → SVD) |
| Elección de k, métricas y escenarios | Notebook, Etapa 3; `figuras/eleccion_k.png` |
| Perfil de cada grupo y visualización | Notebook, Etapa 4; `figuras/mapa_grupos.png` y `figuras/tamano_grupos.png` |
| Resumen automático | `src/actividades/reportes/EA3_resumen_modelo.txt` y artefacto `resumen-ea3` |
| **Documento de hallazgos** | [`src/actividades/reportes/HALLAZGOS.md`](src/actividades/reportes/HALLAZGOS.md) |
