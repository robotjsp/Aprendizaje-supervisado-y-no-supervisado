"""Agrupamiento (clustering) de textos con K-means.

Flujo, igual que las demás clases del curso:

    preparar_datos  -> textos válidos y sin repetir
    vectorizar      -> texto -> números (TF-IDF -> SVD -> normalizar)
    evaluar_k       -> prueba varios k y calcula inercia, silueta, Davies-Bouldin, Calinski-Harabasz
    elegir_k        -> regla documentada para escoger k
    entrenar        -> K-means con el k elegido (guarda el .pkl con fecha)
    describir       -> tamaño, palabras clave y ejemplos de cada grupo

¿Por qué TF-IDF -> SVD -> normalizar?
- K-means mide DISTANCIAS, así que la escala importa. TF-IDF da a cada texto
  un vector de largo 1 (todos en la misma escala), así un texto largo no
  "pesa" más que uno corto.
- TF-IDF crea miles de columnas casi vacías. SVD (también llamado LSA) las
  resume en unas pocas "dimensiones de tema" y quita ruido.
- Al volver a normalizar, la distancia entre textos equivale a qué tan
  distinto es su contenido (similitud coseno).
"""
from __future__ import annotations

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer


class AgrupadorTextos:
    """Descubre grupos de textos parecidos sin usar una variable objetivo.

    Args:
        columna_texto: columna con los textos a agrupar.
        rango_k: valores de k (número de grupos) que se comparan.
        k_minimo_negocio: menor k útil para el negocio (menos grupos no sirven para organizar).
        n_componentes: dimensiones que conserva SVD.
        max_features, min_df, max_df, ngram_range, stop_words: parámetros de TF-IDF.
        n_init: veces que K-means reinicia con centroides distintos (se queda con el mejor).
        random_state: semilla para que el resultado se pueda repetir.
        directorio_modelos: carpeta donde se guarda el .pkl.
    """

    def __init__(
        self,
        columna_texto: str = "texto",
        rango_k: range = range(2, 13),
        k_minimo_negocio: int = 4,
        n_componentes: int = 100,
        max_features: int = 5000,
        min_df: int = 3,
        max_df: float = 0.5,
        ngram_range: tuple[int, int] = (1, 2),
        stop_words: list[str] | None = None,
        n_init: int = 10,
        random_state: int = 42,
        directorio_modelos: str | Path = "entrenamiento",
    ) -> None:
        self.columna_texto = columna_texto
        self.rango_k = list(rango_k)
        self.k_minimo_negocio = k_minimo_negocio
        self.n_componentes = n_componentes
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        self.stop_words = stop_words
        self.n_init = n_init
        self.random_state = random_state
        self.directorio_modelos = Path(directorio_modelos)

        self.textos: pd.Series | None = None
        self.vectorizador: Pipeline | None = None
        self.X: np.ndarray | None = None
        self.varianza_explicada: float | None = None
        self.tabla_k: pd.DataFrame | None = None
        self.k: int | None = None
        self.modelo: KMeans | None = None
        self.etiquetas: np.ndarray | None = None
        self.metricas: dict[str, float] | None = None
        self.ruta_modelo: Path | None = None

    # ------------------------------------------------------------------ #
    def preparar_datos(self, df: pd.DataFrame) -> pd.Series:
        """Quita textos vacíos o repetidos: un texto repetido formaría un grupo artificial."""
        if self.columna_texto not in df.columns:
            raise KeyError(f"Falta la columna {self.columna_texto}.")
        textos = df[self.columna_texto].fillna("").astype(str).str.strip()
        validos = textos[textos != ""]
        unicos = validos.drop_duplicates()
        print(f"[preparar_datos] {len(textos)} filas -> {len(validos)} con texto -> {len(unicos)} textos únicos.")
        self.textos = unicos
        return unicos

    def vectorizar(self, textos: pd.Series) -> np.ndarray:
        n_comp = min(self.n_componentes, len(textos) - 1)
        self.vectorizador = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=self.max_features, min_df=self.min_df, max_df=self.max_df,
                                      ngram_range=self.ngram_range, stop_words=self.stop_words,
                                      strip_accents="unicode", lowercase=True)),
            ("svd", TruncatedSVD(n_components=n_comp, random_state=self.random_state)),
            ("normalizar", Normalizer(copy=False)),
        ])
        self.X = self.vectorizador.fit_transform(textos)
        self.varianza_explicada = float(self.vectorizador.named_steps["svd"].explained_variance_ratio_.sum())
        vocab = len(self.vectorizador.named_steps["tfidf"].vocabulary_)
        print(f"[vectorizar] vocabulario={vocab} términos -> {n_comp} dimensiones SVD "
              f"(conservan {self.varianza_explicada:.1%} de la variación).")
        return self.X

    # ------------------------------------------------------------------ #
    def _kmeans(self, k: int) -> KMeans:
        return KMeans(n_clusters=k, n_init=self.n_init, random_state=self.random_state)

    def evaluar_k(self) -> pd.DataFrame:
        """Entrena K-means para cada k y guarda sus métricas."""
        filas = []
        for k in self.rango_k:
            km = self._kmeans(k).fit(self.X)
            filas.append({
                "k": k,
                "inercia": km.inertia_,
                "silueta": silhouette_score(self.X, km.labels_, random_state=self.random_state),
                "Davies-Bouldin": davies_bouldin_score(self.X, km.labels_),
                "Calinski-Harabasz": calinski_harabasz_score(self.X, km.labels_),
                "grupo más pequeño": int(np.bincount(km.labels_).min()),
            })
        self.tabla_k = pd.DataFrame(filas).set_index("k")
        print(f"[evaluar_k] se compararon k = {self.rango_k[0]} … {self.rango_k[-1]}.")
        return self.tabla_k

    def elegir_k(self) -> int:
        """Regla: entre los k útiles para el negocio (k >= k_minimo_negocio), el de mayor silueta.

        Si dos k tienen casi la misma silueta (diferencia < 0.005) se prefiere el más pequeño:
        menos grupos son más fáciles de explicar y gestionar.
        """
        candidatos = self.tabla_k.loc[self.tabla_k.index >= self.k_minimo_negocio]
        mejor = candidatos["silueta"].max()
        self.k = int(candidatos.index[candidatos["silueta"] >= mejor - 0.005].min())
        print(f"[elegir_k] k elegido = {self.k} (silueta {self.tabla_k.loc[self.k, 'silueta']:.3f}).")
        return self.k

    def entrenar(self, k: int | None = None) -> KMeans:
        k = k or self.k
        self.modelo = self._kmeans(k).fit(self.X)
        self.k = k
        self.etiquetas = self.modelo.labels_
        self.metricas = {
            "inercia": float(self.modelo.inertia_),
            "silueta": float(silhouette_score(self.X, self.etiquetas, random_state=self.random_state)),
            "davies_bouldin": float(davies_bouldin_score(self.X, self.etiquetas)),
            "calinski_harabasz": float(calinski_harabasz_score(self.X, self.etiquetas)),
        }
        self.directorio_modelos.mkdir(parents=True, exist_ok=True)
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.ruta_modelo = self.directorio_modelos / f"{fecha}_KMeans_k{k}.pkl"
        with self.ruta_modelo.open("wb") as archivo:
            pickle.dump({"vectorizador": self.vectorizador, "kmeans": self.modelo}, archivo)
        print(f"[entrenar] K-means k={k}; silueta={self.metricas['silueta']:.3f}; "
              f"modelo guardado en {self.ruta_modelo}")
        return self.modelo

    # ------------------------------------------------------------------ #
    def palabras_clave(self, n: int = 8) -> dict[int, list[str]]:
        """Palabras más importantes del centro de cada grupo (devueltas al espacio TF-IDF)."""
        svd = self.vectorizador.named_steps["svd"]
        vocab = self.vectorizador.named_steps["tfidf"].get_feature_names_out()
        centros = svd.inverse_transform(self.modelo.cluster_centers_)
        return {g: list(vocab[np.argsort(centros[g])[::-1][:n]]) for g in range(self.k)}

    def nombres_grupos(self, n: int = 3) -> dict[int, str]:
        """Nombre automático de cada grupo con sus 3 palabras más fuertes."""
        return {g: f"G{g} · " + ", ".join(p[:n]) for g, p in self.palabras_clave(n).items()}

    def perfil(self) -> pd.DataFrame:
        tamanos = np.bincount(self.etiquetas, minlength=self.k)
        distancias = self.modelo.transform(self.X)[np.arange(len(self.X)), self.etiquetas]
        largo = self.textos.str.split().str.len().to_numpy()
        tabla = pd.DataFrame({
            "grupo": range(self.k),
            "nombre": [self.nombres_grupos()[g] for g in range(self.k)],
            "textos": tamanos,
            "% del total": (tamanos / tamanos.sum() * 100).round(1),
            "palabras promedio": [round(float(largo[self.etiquetas == g].mean()), 1) for g in range(self.k)],
            "cohesión (dist. media al centro)": [round(float(distancias[self.etiquetas == g].mean()), 3)
                                                 for g in range(self.k)],
            "palabras clave": [", ".join(p) for p in self.palabras_clave(8).values()],
        })
        return tabla.sort_values("textos", ascending=False).reset_index(drop=True)

    def ejemplos(self, n: int = 2, largo: int = 160) -> pd.DataFrame:
        """Los textos más cercanos al centro de cada grupo: los más 'típicos'."""
        distancias = self.modelo.transform(self.X)
        filas = []
        for g in range(self.k):
            idx = np.where(self.etiquetas == g)[0]
            for i in idx[np.argsort(distancias[idx, g])][:n]:
                filas.append({"grupo": g, "texto típico": self.textos.iloc[i][:largo] + "…"})
        return pd.DataFrame(filas)

    def asignaciones(self) -> pd.DataFrame:
        return pd.DataFrame({self.columna_texto: self.textos.to_numpy(), "grupo": self.etiquetas})

    # ------------------------------------------------------------------ #
    def ejecutar(self, df: pd.DataFrame) -> dict[str, Any]:
        print("[ejecutar][1/5] preparar_datos")
        textos = self.preparar_datos(df)
        print("[ejecutar][2/5] vectorizar")
        self.vectorizar(textos)
        print("[ejecutar][3/5] evaluar_k")
        self.evaluar_k()
        print("[ejecutar][4/5] elegir_k")
        self.elegir_k()
        print("[ejecutar][5/5] entrenar")
        self.entrenar()
        print("[ejecutar] flujo completo terminado.")
        return {"k": self.k, "metricas": self.metricas, "tabla_k": self.tabla_k,
                "perfil": self.perfil(), "ruta_modelo": self.ruta_modelo}
