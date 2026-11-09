# Documento de hallazgos · EA3

_Generado automáticamente el 2026-11-08 22:49 (hora de Colombia) a partir de la ejecución del notebook._

## Pregunta de negocio
**¿Qué grandes temas aparecen en los fragmentos de informes sobre el conflicto armado colombiano, para que un centro de memoria histórica organice su archivo en colecciones temáticas y decida qué líneas pedagógicas y de atención a víctimas priorizar?**

- **Quién la necesita:** el equipo de archivo y pedagogía de un centro de memoria histórica (o una ONG de víctimas)
- **Qué decisión apoya:** cómo agrupar los documentos en colecciones y a qué temas dedicar primero recursos

## Respuesta corta
Los 2,883 fragmentos de informes se organizan en **9 grandes temas**.
Los tres más frecuentes reúnen el **42 %** del archivo:
**G6 · source, farc, violencia** (16.8 %), **G0 · humanos, derechos humanos, derechos** (12.7 %), **G2 · armados, grupos, grupos armados** (12.4 %).

| Tema (nombre automático) | Fragmentos | Palabras que lo definen |
|---|---|---|
| G6 · source, farc, violencia | 485 (16.8 %) | source, farc, violencia, paramilitares, conflicto, grupos, estado, seguridad |
| G0 · humanos, derechos humanos, derechos | 366 (12.7 %) | humanos, derechos humanos, derechos, violaciones, violaciones derechos, conflicto, armado, conflicto armado |
| G2 · armados, grupos, grupos armados | 358 (12.4 %) | armados, grupos, grupos armados, ilegales, armados ilegales, amenazas, desplazamiento, forzado |
| G3 · source, paz, victimas | 358 (12.4 %) | source, paz, victimas, conflicto, memoria, reparacion, mujeres, verdad |
| G7 · estructurales, causas, causas estructurales | 340 (11.8 %) | estructurales, causas, causas estructurales, estructurales conflicto, repeticion, social, conflicto, exclusion |
| G8 · ci, pdf, 365 | 266 (9.2 %) | ci, pdf, 365, 365 ci, 1306, 1306 ci, conflicto, violencia |
| G5 · desaparicion, familiares, testimonios | 255 (8.8 %) | desaparicion, familiares, testimonios, desaparicion forzada, forzada, victimas, familias, casos |
| G4 · 119, 119 ci, ci | 241 (8.4 %) | 119, 119 ci, ci, pdf, tierras, conflicto, comunidades, violencia |
| G1 · sexual, violencia sexual, violencia | 214 (7.4 %) | sexual, violencia sexual, violencia, mujeres, victimas, armados, testimonios, victimas violencia |

Los nombres salen de las palabras más importantes de cada grupo. El equipo de archivo debe revisarlos y ponerles un nombre definitivo.

## Hallazgos principales
1. **Temas dominantes.** El tema más grande (G6 · source, farc, violencia) concentra el 16.8 % de los fragmentos, y el más pequeño (G1 · sexual, violencia sexual, violencia) el 7.4 %. El archivo no está repartido por igual: unos temas tienen mucho más material que otros.
2. **¿Cuántos temas?** Se probaron de 2 a 12 grupos. Con 9 se obtuvo la mejor separación entre las opciones útiles para organizar un archivo (silueta 0.048).
3. **Textos típicos de cada tema** (los más cercanos al centro del grupo):
- **G0:** _El informe señala que la Armada de Colombia experimentó profundas transformaciones institucionales en respuesta a los desafíos derivados del conflicto armado interno. Entre los hallazgos principales se destaca la adaptac…_
- **G1:** _Los testimonios recopilados reflejan que la violencia sexual fue utilizada de manera sistemática por actores armados como mecanismo de control, castigo y dominación sobre las mujeres. Se registraron casos de violación, a…_
- **G2:** _El informe describe que el desplazamiento forzado en el Bajo Cauca se ha dado tanto de forma masiva como de manera silenciosa y fragmentada. Las amenazas directas, la presencia de grupos armados ilegales y la violencia s…_
- **G3:** _Desde su fundación, CODHES se ha propuesto contribuir en todas las iniciativas que permitan el cierre del conflicto armado y la construcción de una paz sostenible. Su enfoque ha sido buscar la paz como principio estructu…_
- **G4:** _Informe 119-CI-00339…_
- **G5:** _Entre 1998 y 2005, el informe registra varios casos de desaparición forzada en Usme. Destaca el caso de la familia Muñoz, cuyo hijo adolescente fue desaparecido en octubre de 2002 tras haber sido presuntamente señalado d…_
- **G6:** _En Caicedo, la FARC utilizó el territorio para control y desplazamiento, imponiendo conductas a la población y exacciones forzosas. Durante la década de 1990, las AUC realizaron incursiones desde Santa Fe, formando grupo…_
- **G7:** _El informe identifica como causas estructurales del conflicto armado factores como la desigualdad socioeconómica, la ausencia efectiva del Estado, la exclusión de sectores vulnerables y la falta de acceso a servicios bás…_
- **G8:** _Hoy en día Puerto Gaitán se caracteriza por una economía de enclave basada principalmente en la industria petrolera【4:7†365-CI-00931.pdf】.…_

![Elección de k](../figuras/eleccion_k.png)
![Mapa de temas](../figuras/mapa_grupos.png)
![Tamaño de los temas](../figuras/tamano_grupos.png)

## ¿Qué tan confiables son los resultados?
- **Silueta = 0.048** (va de -1 a 1): grupos débiles: muchos textos están en la frontera entre dos temas. En textos es normal que la silueta sea baja: un mismo informe habla de varios temas a la vez (por ejemplo, desplazamiento **y** despojo de tierras), así que muchos fragmentos quedan cerca de la frontera entre dos grupos.
- **Davies-Bouldin = 4.31:** más bajo es mejor. Sirve para comparar entre valores de k, no tiene un umbral absoluto.
- Los grupos se describen con palabras clave y ejemplos que una persona puede revisar, así que la agrupación es **verificable**.
- **Limitaciones:**
  - K-means asigna cada texto a **un solo** tema, aunque en la realidad tenga varios.
  - Supone grupos de forma "redonda" y de tamaño parecido.
  - TF-IDF cuenta palabras, pero no entiende su significado: dos fragmentos que dicen lo mismo con palabras distintas pueden quedar separados.
  - Los fragmentos son extractos cortos y el dataset no cubre todos los informes existentes.

## Recomendaciones
1. **G6 · source, farc, violencia** (16.8 % del archivo): crear una colección temática con sus 485 fragmentos y usar sus textos típicos como punto de partida de una guía pedagógica o de una ruta de consulta para víctimas e investigadores.
2. **G0 · humanos, derechos humanos, derechos** (12.7 % del archivo): crear una colección temática con sus 366 fragmentos y usar sus textos típicos como punto de partida de una guía pedagógica o de una ruta de consulta para víctimas e investigadores.
3. **G2 · armados, grupos, grupos armados** (12.4 % del archivo): crear una colección temática con sus 358 fragmentos y usar sus textos típicos como punto de partida de una guía pedagógica o de una ruta de consulta para víctimas e investigadores.
4. Hacer que un equipo humano **revise una muestra de cada grupo** antes de publicar las colecciones, y ajuste los nombres y los textos mal ubicados.
5. Usar el modelo guardado (`.pkl`) para **clasificar automáticamente los fragmentos nuevos** en el tema más cercano a medida que crezca el archivo, y volver a entrenarlo cuando se agreguen muchos documentos.
6. Priorizar las líneas pedagógicas y de atención en los temas más grandes, sin descuidar los pequeños: pueden representar hechos menos documentados que merecen más investigación.
