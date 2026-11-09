"""Resumen .txt y documento de hallazgos (.md) del modelo de agrupamiento.

Todo el contenido sale de un ``AgrupadorTextos`` ya ejecutado: si cambian los
datos, cambian el resumen y los hallazgos.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import sklearn


def lectura_silueta(s: float) -> str:
    """Traduce la silueta a palabras (escala de -1 a 1)."""
    if s >= 0.5:
        return "grupos muy bien separados"
    if s >= 0.25:
        return "grupos razonablemente separados"
    if s >= 0.1:
        return "grupos reconocibles pero con fronteras difusas (normal en textos)"
    if s > 0:
        return "grupos débiles: muchos textos están en la frontera entre dos temas"
    return "no hay una estructura de grupos clara"


class ReporteAgrupamiento:
    def __init__(self, pregunta: dict, info_dataset: dict, df_crudo: pd.DataFrame,
                 calidad: pd.DataFrame, registro: pd.DataFrame, agrupador, tipos_por_grupo: pd.DataFrame | None = None):
        self.pregunta = pregunta
        self.info = info_dataset
        self.df_crudo = df_crudo
        self.calidad = calidad
        self.registro = registro
        self.ag = agrupador
        self.tipos = tipos_por_grupo
        self.fecha = datetime.now(ZoneInfo("America/Bogota"))

    # ------------------------------------------------------------------ #
    def resumen_txt(self, ruta: str | Path = "reportes/EA3_resumen_modelo.txt") -> Path:
        ag, m = self.ag, self.ag.metricas
        tfidf = ag.vectorizador.named_steps["tfidf"]
        svd = ag.vectorizador.named_steps["svd"]
        L, S = "=" * 78, "-" * 78
        lineas = [
            L,
            "RESUMEN AUTOMÁTICO · EA3 Aprendizaje no supervisado (K-means)",
            f"Fecha de ejecución: {self.fecha:%Y-%m-%d %H:%M:%S} (hora de Colombia) · scikit-learn {sklearn.__version__}",
            L, "",
            "1. PREGUNTA DE NEGOCIO", S,
            self.pregunta["pregunta"],
            f"Quién la necesita: {self.pregunta['quien']}",
            f"Qué decisión apoya: {self.pregunta['decision']}",
            "",
            "2. DATASET", S,
            f"Identificador: {self.info['dataset']}",
            f"Enlace: https://huggingface.co/datasets/{self.info['dataset']}",
            f"Configuración: {self.info.get('config') or 'default'} · splits: {self.info['splits']}",
            f"DataFrame crudo: {self.df_crudo.shape[0]} filas x {self.df_crudo.shape[1]} columnas "
            f"({', '.join(map(str, self.df_crudo.columns))})",
            "",
            "3. PREPROCESAMIENTO", S,
            "Validación (métrica y decisión):",
            self.calidad.to_string(index=False), "",
            "Registro de limpieza:",
            self.registro.to_string(index=False), "",
            f"Textos agrupados: {len(ag.textos)} fragmentos de informe (columna '{ag.columna_texto}') únicos y no vacíos.",
            f"TF-IDF: max_features={tfidf.max_features}, min_df={tfidf.min_df}, max_df={tfidf.max_df}, "
            f"ngram_range={tfidf.ngram_range}, stop_words=español, sin tildes · vocabulario={len(tfidf.vocabulary_)}",
            f"SVD (LSA): n_components={svd.n_components}, random_state={ag.random_state} · "
            f"conserva {ag.varianza_explicada:.1%} de la variación",
            "Normalizer (norma L2): todos los textos con la misma escala; la distancia mide diferencia de contenido.",
            "Sin división entrenamiento/prueba: no hay variable objetivo con la cual comparar (aprendizaje no supervisado).",
            "",
            "4. MODELO", S,
            "Tipo de aprendizaje: NO SUPERVISADO (descubre grupos sin etiquetas).",
            f"Algoritmo: KMeans(n_clusters={ag.k}, init='k-means++' (predeterminado), n_init={ag.n_init}, "
            f"max_iter=300 (predeterminado), random_state={ag.random_state})",
            f"Variables: vector de {svd.n_components} dimensiones que resume el texto de cada fragmento.",
            f"Elección de k: se compararon k = {ag.rango_k[0]}…{ag.rango_k[-1]}; regla = mayor silueta con "
            f"k >= {ag.k_minimo_negocio} (menos grupos no sirven para organizar un archivo); empate (<0.005) -> el menor k.",
            "",
            "Comparación de k:",
            ag.tabla_k.round(4).to_string(), "",
            "5. MÉTRICAS DEL MODELO ELEGIDO", S,
            f"k = {ag.k}",
            f"Silueta = {m['silueta']:.4f} -> {lectura_silueta(m['silueta'])}",
            f"Davies-Bouldin = {m['davies_bouldin']:.4f} (más bajo = grupos más compactos y separados)",
            f"Calinski-Harabasz = {m['calinski_harabasz']:.2f} (más alto = mejor separación)",
            f"Inercia = {m['inercia']:.2f} (suma de distancias al cuadrado al centro de cada grupo)",
            f"Modelo guardado: {ag.ruta_modelo}",
            "",
            "6. PERFIL DE LOS GRUPOS", S,
            ag.perfil().drop(columns=["palabras clave"]).to_string(index=False), "",
            "Palabras clave por grupo:",
            *[f"  G{g}: {', '.join(p)}" for g, p in ag.palabras_clave(10).items()],
            "",
        ]
        if self.tipos is not None:
            lineas += ["Tipo de pregunta por grupo (% de filas del grupo):", self.tipos.round(1).to_string(), ""]
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text("\n".join(lineas), encoding="utf-8")
        print(f"[resumen_txt] guardado en {ruta}")
        return ruta

    # ------------------------------------------------------------------ #
    def hallazgos_md(self, ruta: str | Path = "reportes/HALLAZGOS.md", carpeta_figuras: str = "../figuras") -> Path:
        ag, m = self.ag, self.ag.metricas
        perfil = ag.perfil()
        top = perfil.head(3)
        ejemplos = ag.ejemplos(1, 220)
        s = m["silueta"]

        temas = "\n".join(
            f"| {r['nombre']} | {r['textos']} ({r['% del total']} %) | {r['palabras clave']} |"
            for _, r in perfil.iterrows())
        ejemplo_txt = "\n".join(f"- **G{r['grupo']}:** _{r['texto típico']}_" for _, r in ejemplos.iterrows())
        recomendaciones = "\n".join(
            f"{i}. **{r['nombre']}** ({r['% del total']} % del archivo): crear una colección temática con sus "
            f"{r['textos']} fragmentos y usar sus textos típicos como punto de partida de una guía pedagógica o "
            "de una ruta de consulta para víctimas e investigadores."
            for i, (_, r) in enumerate(top.iterrows(), start=1))

        texto = f"""# Documento de hallazgos · EA3

_Generado automáticamente el {self.fecha:%Y-%m-%d %H:%M} (hora de Colombia) a partir de la ejecución del notebook._

## Pregunta de negocio
**{self.pregunta['pregunta']}**

- **Quién la necesita:** {self.pregunta['quien']}
- **Qué decisión apoya:** {self.pregunta['decision']}

## Respuesta corta
Los {len(ag.textos):,} fragmentos de informes se organizan en **{ag.k} grandes temas**.
Los tres más frecuentes reúnen el **{top['% del total'].sum():.0f} %** del archivo:
{", ".join(f"**{n}** ({p} %)" for n, p in zip(top['nombre'], top['% del total']))}.

| Tema (nombre automático) | Fragmentos | Palabras que lo definen |
|---|---|---|
{temas}

Los nombres salen de las palabras más importantes de cada grupo. El equipo de archivo debe revisarlos y ponerles un nombre definitivo.

## Hallazgos principales
1. **Temas dominantes.** El tema más grande ({top.iloc[0]['nombre']}) concentra el {top.iloc[0]['% del total']} % de los fragmentos, y el más pequeño ({perfil.iloc[-1]['nombre']}) el {perfil.iloc[-1]['% del total']} %. {"El archivo no está repartido por igual: unos temas tienen mucho más material que otros." if perfil.iloc[0]['% del total'] - perfil.iloc[-1]['% del total'] >= 5 else "El material está repartido de forma bastante pareja entre los temas."}
2. **¿Cuántos temas?** Se probaron de {ag.rango_k[0]} a {ag.rango_k[-1]} grupos. Con {ag.k} se obtuvo la mejor separación entre las opciones útiles para organizar un archivo (silueta {s:.3f}).
3. **Textos típicos de cada tema** (los más cercanos al centro del grupo):
{ejemplo_txt}

![Elección de k]({carpeta_figuras}/eleccion_k.png)
![Mapa de temas]({carpeta_figuras}/mapa_grupos.png)
![Tamaño de los temas]({carpeta_figuras}/tamano_grupos.png)

## ¿Qué tan confiables son los resultados?
- **Silueta = {s:.3f}** (va de -1 a 1): {lectura_silueta(s)}. En textos es normal que la silueta sea baja: un mismo informe habla de varios temas a la vez (por ejemplo, desplazamiento **y** despojo de tierras), así que muchos fragmentos quedan cerca de la frontera entre dos grupos.
- **Davies-Bouldin = {m['davies_bouldin']:.2f}:** más bajo es mejor. Sirve para comparar entre valores de k, no tiene un umbral absoluto.
- Los grupos se describen con palabras clave y ejemplos que una persona puede revisar, así que la agrupación es **verificable**.
- **Limitaciones:**
  - K-means asigna cada texto a **un solo** tema, aunque en la realidad tenga varios.
  - Supone grupos de forma "redonda" y de tamaño parecido.
  - TF-IDF cuenta palabras, pero no entiende su significado: dos fragmentos que dicen lo mismo con palabras distintas pueden quedar separados.
  - Los fragmentos son extractos cortos y el dataset no cubre todos los informes existentes.

## Recomendaciones
{recomendaciones}
{len(top) + 1}. Hacer que un equipo humano **revise una muestra de cada grupo** antes de publicar las colecciones, y ajuste los nombres y los textos mal ubicados.
{len(top) + 2}. Usar el modelo guardado (`.pkl`) para **clasificar automáticamente los fragmentos nuevos** en el tema más cercano a medida que crezca el archivo, y volver a entrenarlo cuando se agreguen muchos documentos.
{len(top) + 3}. Priorizar las líneas pedagógicas y de atención en los temas más grandes, sin descuidar los pequeños: pueden representar hechos menos documentados que merecen más investigación.
"""
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        print(f"[hallazgos_md] guardado en {ruta}")
        return ruta
