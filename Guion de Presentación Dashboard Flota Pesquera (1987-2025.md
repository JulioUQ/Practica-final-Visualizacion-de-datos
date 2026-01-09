Este es un guion estructurado y cronometrado para un video de entre **5 minutos**, diseñado para cubrir todos los puntos de evaluación exigidos.

He separado el guion en dos columnas conceptuales: **Lo que haces en pantalla** (Visual) y **Lo que dices** (Audio).

---

# 🎬 Guion de Presentación: Dashboard Flota Pesquera (1987-2025)

**Tiempo estimado:** 5:00 - 5:30 minutos.
**Tono:** Profesional, analítico y claro.

---

### 1. Introducción y Contexto (0:00 - 0:45)

_Objetivo: Presentar el proyecto y el conjunto de datos (15% Datos)._

| **Acción en Pantalla**                                                                                    | **Guion (Audio)**                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Vista:** Tab "Panorama General". **Acción:** Scroll suave para mostrar título y métricas principales.] | "Hola, soy [Tu Nombre] y presento mi proyecto de visualización sobre la **Flota Pesquera Española**. He analizado un histórico de **38 años (1987-2025)** con más de **27.000 buques** registrados."                                                                                                                                                                                                                                                        |
| **[Vista:** Señalar el título y luego hacer un gesto hacia la pantalla completa.]"                        | **[Punto 4: Originalidad]** A diferencia de los informes estáticos y agregados que suele publicar la Unión Europea, este dashboard aporta un valor diferencial: permite la **exploración granular a nivel de buque** y la interactividad en tiempo real, democratizando el acceso a datos complejos."                                                                                                                                                       |
| **[Vista:** Señalar métricas "Buques Totales" y "Edad Media".]                                            | "El objetivo no era solo pintar datos, sino responder a una pregunta crítica: **¿Cómo ha cambiado el modelo productivo pesquero en España?** "**[Punto 1: Objetivo Medible]** Me fijé un objetivo medible y concreto para este análisis: **cuantificar la evolución de la potencia media (kW) por Comunidad Autónoma**, para determinar si la reducción del número de barcos ha implicado realmente una disminución de la capacidad extractiva industrial." |

---

### 2. Proceso de Creación y Calidad del Dato (0:45 - 1:40)

_Objetivo: Explicar decisiones de diseño y limpieza (20% Proceso)._

| **Acción en Pantalla**                                                                   | **Guion (Audio)**                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Vista:** Clic en Tab **"Control de Calidad"**. Scroll por las secciones de limpieza.] | "Antes de visualizar, realicé un riguroso proceso de limpieza que he documentado en esta pestaña específica para garantizar la transparencia."                                                                                                                                                                                                                                                                             |
| **[Vista:** Señalar sección "Imputación de Valores Anómalos".]                           | "Una decisión de diseño clave fue no eliminar los registros con valores cero en potencia o eslora, ya que perderíamos información histórica. En su lugar, apliqué una técnica de **Imputación KNN (K-Nearest Neighbors)** con un `k=15`. Esto me permitió reconstruir los datos faltantes basándome en los 15 barcos más similares, manteniendo la integridad estadística del dataset sin introducir sesgos artificiales." |
| **[Vista:** Señalar gráficos de Outliers.]                                               | "También validé los outliers. Como vemos en los Boxplots, existen buques muy grandes que son atípicos pero reales (grandes arrastreros), por lo que decidí mantenerlos en el análisis."                                                                                                                                                                                                                                    |

---

### 3. Evolución Temporal y Preguntas Clave (1:40 - 2:40)

_Objetivo: Responder preguntas analíticas mediante la interacción (20% Preguntas)._

| **Acción en Pantalla**                                                                      | **Guion (Audio)**                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Vista:** Clic en Tab **"Panorama General"** o **"Evolución"**. Enfocar gráfico de Edad.] | "**[Punto 2: Priorización Variables/Contexto]** Para la narrativa, he priorizado dos variables clave que dan contexto social a los datos: la **Edad del Buque** y el **Tipo de Arte**."                                                                                                                                |
| **[Vista:** Señalar dato de "Edad Media" (aprox 32-34 años).]                               | "Operacionalicé la pregunta _'¿Hay relevo generacional?'_ mediante la métrica de **Edad Media**. El dato de más de 30 años de media no es solo un número técnico; cuenta una historia social de **envejecimiento del sector**, falta de inversión y dificultad para atraer a jóvenes pescadores a una flota antigua."  |
| **[Vista:** Ir a Tab **"Evolución Temporal"**. Ver líneas de altas vs bajas.]               | "**[Punto 5: Operacionalización]** Aquí respondemos a la pregunta de la sostenibilidad. Usé un **gráfico de líneas de doble eje** para contrastar el descenso de buques (cantidad) frente al aumento de potencia (capacidad). La métrica es clara: menos familias viviendo de la pesca, pero barcos más industriales." |

---

### 4. Distribución Geográfica e Interactividad (2:40 - 3:40)

_Objetivo: Demostrar interactividad y diseño UX (15% Interactividad + 20% Vivo)._

| **Acción en Pantalla**                                                                                                  | **Guion (Audio)**                                                                                                                                                                                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **[Vista:** Clic en Tab **"Distribución Geográfica"**. Seleccionar métrica "Potencia Media" en el selector.]            | "Para entender el territorio, diseñé este mapa interactivo con **Folium**. He integrado un selector que permite cambiar la métrica al instante. Si cambio a 'Potencia Media', el mapa se redibuja."                                                                                                                                        |
| **[Vista:** Pasar ratón por Galicia (muchos barcos, poca potencia media) vs País Vasco (menos barcos, mucha potencia).] | "Observen la interactividad. Al segmentar por **Comunidad Autónoma**, vemos la disparidad social y económica: Galicia mantiene el tejido social con mucha flota de pequeña escala (artes menores), mientras que el País Vasco apuesta por una flota industrial de altura. El mapa permite validar esta hipótesis visualmente en segundos." |
| **[Vista:** Scroll al **Treemap**. Hacer clic en una Comunidad para hacer drill-down.]                                  | "Para profundizar, utilicé un Treemap. Este gráfico es vital porque permite ver la jerarquía: Comunidad > Puerto. Si hago clic aquí, puedo ver cómo un solo puerto puede concentrar gran parte del arqueo de una región, algo que un gráfico de barras simple ocultaría."                                                                  |

---

### 5. Análisis Avanzado: Clustering (3:40 - 4:30)

_Objetivo: Mostrar profundidad técnica y decisiones analíticas._

| **Acción en Pantalla**                                                       | **Guion (Audio)**                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Vista:** Clic en Tab **"Tipologías (Clustering)"**. Mover el gráfico 3D.] | "Finalmente, para aportar un nivel de análisis superior al de los informes oficiales, implementé técnicas de **Machine Learning (K-Means)**." **¿Qué tipos de barcos existen realmente según sus físicas?** Para ello, utilicé un algoritmo de aprendizaje no supervisado, **K-Means**."                                                                         |
| **[Vista:** Señalar el gráfico del "Codo" y luego el Scatter 3D.]            | "Utilizando el método del codo, determiné que 4 clusters era la división óptima. En este gráfico 3D interactivo, podemos ver claramente los grupos separados: desde la inmensa nube de artes menores (pequeños y poco potentes) hasta los grandes buques industriales (en morado) que se separan del resto. Esto valida que la flota está altamente polarizada." |
|                                                                              | "En lugar de usar solo las categorías administrativas, he agrupado los buques por similitud técnica. Este **Scatter Plot 3D** operacionaliza la segmentación de la flota, revelando 4 tipologías reales de operación que permiten diseñar políticas públicas más precisas que las basadas en promedios generales."                                               |

---

### 6. Reflexión Final y Cierre (4:30 - 5:15)

_Objetivo: Conclusiones y autocrítica (10% Reflexión)._

| **Acción en Pantalla**                                                | **Guion (Audio)**                                                                                                                                                              |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **[Vista:** Clic en Tab **"Conclusiones"**. Mostrar recomendaciones.] | "Para cerrar, la visualización nos permite concluir que la flota española sufre un **envejecimiento progresivo** (media de 32 años) y una **hiper-especialización regional**." |
| **[Vista:** Mostrar filtros laterales (Sidebar) brevemente.]          | "En cuanto a mi aprendizaje:                                                                                                                                                   |

Y hemos contado la historia social del envejecimiento de la flota." | | **[Vista:** Plano general del dashboard.] | "Este proyecto demuestra que la visualización de datos no es solo estética, sino una herramienta analítica para entender la realidad socioeconómica del sector primario. Gracias." |

1. **Técnico:** He aprendido a integrar modelos de Scikit-learn (KMeans/KNN) directamente en el flujo de visualización de Streamlit.
2. **Limitaciones:** La principal dificultad fue la integración de los Shapefiles geográficos, ya que algunos nombres de comunidades no coincidían con el CSV, lo que tuve que solucionar mediante un mapeo manual en el código.
3. **Futuro:** Me habría gustado integrar datos de capturas económicas para correlacionar potencia con rentabilidad, pero esos datos no eran públicos." |
   | **[Vista:** Plano general del Dashboard.] | "En definitiva, esta herramienta transforma una tabla plana de 27.000 filas en una historia interactiva sobre la transformación naval de España. Muchas gracias." |

---

### 💡 Consejos para la grabación:

1. **Preparación de Pantalla:**

- Ejecuta `streamlit run dashboard_flota.py`.
- Pon el navegador en pantalla completa (F11).
- Asegúrate de que el Zoom del navegador esté al 100% o 110% para que las letras se lean bien en el video.
- Ten cargados los datos (que la caché `st.cache_data` ya haya funcionado) para que no haya tiempos de espera en el video.

2. **Sobre los Filtros Laterales:**

- Aunque no dedico una sección exclusiva a hablar de ellos en el guion (por tiempo), **úsalos** durante la demo. Por ejemplo, cuando estés en "Distribución Geográfica", filtra por "Arrastre" en la barra lateral para que se vea cómo el mapa cambia dinámicamente. Eso suma puntos en _Interactividad_.

3. **Accesibilidad:**

- Menciona sutilmente (o asegúrate de que se vea) que los colores elegidos (escalas `Reds`, `Blues`, `Set2`) son distintos y fáciles de diferenciar, lo cual es una buena práctica de diseño.
### Tips para "vender" la respuesta a los comentarios:

1. **Usa la voz:** Cuando digas frases como _"A diferencia de los informes estáticos..."_ o _"Siguiendo el plan de control de calidad..."_, enfatiza ligeramente el tono. Estás haciendo un guiño auditivo al profesor diciéndole: "He leído tu corrección y aquí está la solución".
    
2. **Pausas visuales:** Cuando hables de los **Outliers** o del **KNN**, quédate un segundo extra en la pestaña de "Control de Calidad". Deja que el profesor lea que has escrito "Imputación con KNN" en el texto de la web (que está en tu código). Eso demuestra que el cambio es real, no solo retórica.
    
3. **La variable social:** Asegúrate de que cuando hables de la "Edad del buque", tu tono sea un poco más narrativo/preocupado, ya que estás hablando de problemas sociales (falta de relevo generacional), contrastando con el tono técnico del resto.