# TT-POSGRADO

## Análisis de Sentimientos Basado en Aspectos (ABSA) para el Sector Turístico

Este repositorio contiene el prototipo funcional desarrollado para mi Trabajo de Titulación de Maestría en Inteligencia Artificial Aplicada en la UTPL. El sistema utiliza modelos de lenguaje de gran escala (LLMs) para transformar reseñas no estructuradas en inteligencia estratégica para la gestión de destinos turísticos.

Este repositorio alberga el prototipo funcional para mi Trabajo de Titulación de Maestría en Inteligencia Artificial Aplicada. El sistema implementa un Pipeline Híbrido que extrae sentimientos granulares de reseñas turísticas, combinando el razonamiento de Gemini 2.5 Flash con un motor de reglas morfológicas bilingües.

## Descripción del Proyecto

A diferencia del análisis de sentimientos tradicional que ofrece una visión global, este sistema aplica ABSA (Aspect-Based Sentiment Analysis) para desglosar la experiencia del visitante en dimensiones específicas como Seguridad, Infraestructura, Gastronomía y Atención.

El motor principal es Gemini 2.5 Flash, seleccionado por su alta precisión en tareas de razonamiento Zero-Shot y su capacidad para procesar contextos multilingües y multiculturales.

### Características Principales

* Análisis Bimodal: Procesa datos de plataformas masivas (Google Reviews) y foros de discusión social (Reddit).
* Motor Híbrido de Clasificación: Combina la potencia generativa de la IA con un sistema de reglas morfológicas bilingües para garantizar la precisión en 8 categorías estratégicas.
* Extracción de Evidencia: El modelo no solo califica, sino que extrae la cita textual exacta que justifica cada sentimiento.
* Dashboard Interactivo: Visualizaciones avanzadas mediante diagramas Sunburst, análisis temporal de quejas y detección de fortalezas/debilidades.
* Resiliencia Técnica: Implementación de Exponential Backoff para manejar límites de cuota de la API y procesamiento por lotes (batching).

## Instalación y Configuración
### Clonar el repositorio:
git clone 
https://github.com/adpardo1/TT-POSGRADO.git

cd TT-POSGRADO
### Crear un entorno virtual:
python -m venv venv
source venv/bin/activate  
#### En Windows: venv\Scripts\activate
### Instalar dependencias:
pip install -r requirements.txt
### Configurar la API Key:
Necesitarás una clave de Google AI Studio (Gemini API). El prototipo permite ingresarla directamente en la interfaz de configuración.
## Uso del Prototipo
Para lanzar la aplicación web:

streamlit run TSIS2.py

Una vez en la interfaz:
* Carga tu archivo (CSV o Excel) con las reseñas.
* Configura el tamaño del lote (recomendado $n=10$).
* Inicia el análisis y explora los resultados.

## Estructura del Corpus Analizado

El sistema fue validado con un corpus de 9,864 registros:
* Google Reviews (Loja): 9,569 reseñas locales.
* Reddit (Ecuador): 295 interacciones internacionales para capturar la percepción del turista extranjero.

## Arquitectura y Metodología del Sistema
1. Ingesta y Configuración
El proceso comienza con la carga de datasets en formato CSV o Excel. A través de la interfaz, el usuario gestiona las credenciales y los parámetros de procesamiento.
2. Estructura Técnica y Proceso de Inferencia
El núcleo del prototipo sigue una lógica secuencial para transformar el texto no estructurado en datos categorizados.

El núcleo del prototipo sigue una lógica secuencial para transformar el texto no estructurado en datos categorizados.

Figura 1. Diagrama de flujo del sistema: desde la carga de datos hasta la visualización final.
![Estructura técnica del prototipo](https://github.com/user-attachments/assets/b56955e3-91d1-47cd-a939-102b8fb8d9b0)


En esta etapa, se ejecutan las siguientes fases:

Fase 1 (Extracción): El modelo realiza una inferencia para extraer aspectos y sentimientos granulares.

Fase 2 y 3 (Clasificación y Consolidación): Se aplica un clustering semántico seguido de un sistema de reglas bilingües para normalizar los hallazgos en las 8 categorías estratégicas.
3. Visualización de Resultados y Dashboard
La fase final convierte los datos procesados (como los 6,778 registros finales) en conocimiento visual interactivo.

Jerarquía de Opiniones: Mediante diagramas Sunburst se explora la relación entre categorías y sentimientos.

![Vista General](https://github.com/user-attachments/assets/4729722f-e8a7-4a4e-aeff-3d6810efeb55)

Análisis Temporal: Se visualiza la evolución de la percepción del turista a lo largo del tiempo.

![Evolucion Temporal](https://github.com/user-attachments/assets/4c17c275-c1fc-4357-9df5-d1e1590e2a18)

Detección de Fortalezas y Debilidades: Identificación automática de los puntos críticos y activos mejor valorados.

![Graficas](https://github.com/user-attachments/assets/6d61019f-9019-4ec4-b81e-e6b8f0d709e2)

## Stack Tecnológico y Arquitectura del Código

El prototipo ha sido desarrollado bajo un enfoque modular, priorizando la eficiencia en el manejo de memoria y la resiliencia en las llamadas a la API de Google.

Lenguaje: Python 3.9+

Framework Web: Streamlit (Interfaz reactiva y gestión de estado con st.session_state)

Motor de IA: Google GenAI SDK (Gemini 2.5 Flash)

Procesamiento de Datos: Pandas (Estructuración de DataFrames y normalización de fechas con errors='coerce')

Visualización: Plotly Express (Gráficos interactivos Sunburst y de series temporales)

Componentes Clave del Script (TSIS2.py):
Sistema de Reglas Híbrido (categorizar_por_reglas): Una función basada en diccionarios de lexemas bilingües que actúa como respaldo (fallback) cuando la clasificación de la IA es ambigua, garantizando que el 100% de los aspectos extraídos se asignen a una de las 8 categorías estratégicas.

Pipeline de Inferencia (proceso_completo_analisis): Gestiona el flujo de datos en tres etapas: extracción mediante batching, clustering semántico de términos únicos y consolidación final del reporte.

Limpieza de Respuesta (limpiar_json): Implementación de expresiones regulares (Regex) para asegurar que la salida del LLM sea un JSON válido, incluso ante posibles alucinaciones de formato.


### Licencia

Este proyecto se distribuye bajo la licencia MIT. Para más detalles, consulta el archivo LICENSE.


### Autor
Angel David Pardo Correa Maestría en Inteligencia Artificial Aplicada - UTPL.

adpardo1@utpl.edu.ec


## Licencia

Este proyecto está bajo la **Licencia MIT**. Esto significa que eres libre de usar, copiar, modificar y distribuir el código, siempre que se mantenga la nota de derechos de autor y el texto de la licencia en las copias.

Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.
