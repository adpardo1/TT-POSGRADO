# TT-POSGRADO

## Análisis de Sentimientos Basado en Aspectos (ABSA) para el Sector Turístico

Este repositorio contiene el prototipo funcional desarrollado para mi Trabajo de Titulación de Maestría en Inteligencia Artificial Aplicada en la UTPL. El sistema utiliza modelos de lenguaje de gran escala (LLMs) para transformar reseñas no estructuradas en inteligencia estratégica para la gestión de destinos turísticos.

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

streamlit run app.py

Una vez en la interfaz:
* Carga tu archivo (CSV o Excel) con las reseñas.
* Configura el tamaño del lote (recomendado $n=10$).
* Inicia el análisis y explora los resultados.

## Estructura del Corpus Analizado

El sistema fue validado con un corpus de 9,864 registros:
* Google Reviews (Loja): 9,569 reseñas locales.
* Reddit (Ecuador): 295 interacciones internacionales para capturar la percepción del turista extranjero.

### Licencia

Este proyecto se distribuye bajo la licencia MIT. Para más detalles, consulta el archivo LICENSE.


### Autor
Angel David Pardo Correa Maestría en Inteligencia Artificial Aplicada - UTPL.

adpardo1@utpl.edu.ec


## Licencia

Este proyecto está bajo la **Licencia MIT**. Esto significa que eres libre de usar, copiar, modificar y distribuir el código, siempre que se mantenga la nota de derechos de autor y el texto de la licencia en las copias.

Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.
