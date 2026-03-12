import streamlit as st
import pandas as pd
import json
import time
import re
import plotly.express as px
from google import genai
from google.genai import types

# ============================================
#  CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Gemini ABSA",
    page_icon="",
    layout="wide"
)

# Inicializar estado si no existe
if "clean_df" not in st.session_state:
    st.session_state.clean_df = None

# ============================================
#  SIDEBAR: CONFIGURACIÓN
# ============================================
st.sidebar.header(" Configuración")
api_key = st.sidebar.text_input("Tu API Key de Gemini", type="password")

st.sidebar.markdown("---")
st.sidebar.header(" Control")
batch_size = st.sidebar.slider("Tamaño del Lote", 5, 100, 50, help="Procesar de 20 en 20 es seguro para la API.")
max_rows = st.sidebar.number_input("Filas a cargar", 10, 10000, 500, help="Límite para pruebas rápidas.")

client = None
if api_key:
    client = genai.Client(api_key=api_key)

# ============================================
#  LÓGICA DE BACKEND (IA + REGLAS)
# ============================================

def limpiar_json(texto):
    """Limpia la respuesta del LLM para obtener JSON válido."""
    texto = re.sub(r"```json\s*|\s*```", "", str(texto)).strip()
    start = texto.find('[')
    end = texto.rfind(']')
    if start != -1 and end != -1:
        texto = texto[start:end+1]
    try: return json.loads(texto)
    except: return []

def categorizar_por_reglas(aspecto):
    """
    SISTEMA HÍBRIDO MULTILINGÜE (Español + Inglés):
    Detecta raíces de palabras para unificar categorías aunque la IA falle.
    """
    a = aspecto.lower()
    
    reglas = {
        "Gastronomía": [
            'comida', 'sabor', 'restaurante', 'cena', 'desayuno', 'rico', 'plato', 'menu', 'café', 'bebida', 'almuerzo', 'delicios',
            'food', 'meal', 'taste', 'tasty', 'breakfast', 'lunch', 'dinner', 'drink', 'eat', 'restaurant'
        ],
        "Seguridad": [
            'seguridad', 'robo', 'peligro', 'miedo', 'policía', 'ladron', 'oscuro', 'inseguro', 'matar', 'delincuencia', 'robado',
            'security', 'safe', 'unsafe', 'rob', 'stolen', 'thief', 'theft', 'danger', 'police', 'scary', 'dark'
        ],
        "Precio": [
            'precio', 'costo', 'caro', 'barato', 'dolar', 'pagar', 'economico', 'valor', 'cobran',
            'price', 'cost', 'expensive', 'cheap', 'dollar', 'pay', 'value', 'money', 'budget'
        ],
        "Infraestructura": [
            'habitacion', 'cama', 'baño', 'ducha', 'hotel', 'limpi', 'suci', 'agua', 'luz', 'wifi', 'pared', 'piso', 'lugar', 'sitio', 'mantenim',
            'room', 'bed', 'bath', 'shower', 'hotel', 'clean', 'dirty', 'water', 'light', 'wifi', 'wall', 'floor', 'place', 'spot', 'facility'
        ],
        "Atención": [
            'atencion', 'personal', 'gente', 'amable', 'grosero', 'servicio', 'recepcion', 'guia', 'trato', 'staff', 'dueñ',
            'service', 'staff', 'people', 'kind', 'rude', 'reception', 'guide', 'host', 'friendly', 'helpful'
        ],
        "Naturaleza": [
            'paisaje', 'vista', 'naturaleza', 'parque', 'arbol', 'sendero', 'rio', 'cascada', 'montaña', 'aire', 'jardin',
            'landscape', 'view', 'nature', 'park', 'tree', 'trail', 'river', 'waterfall', 'mountain', 'air', 'garden', 'hike'
        ],
        "Transporte": [
            'taxi', 'bus', 'transporte', 'llegar', 'carro', 'trafico', 'camino', 'calle', 'acceso', 'aeropuerto', 'uber',
            'taxi', 'bus', 'transport', 'arrive', 'car', 'traffic', 'road', 'street', 'access', 'airport', 'uber'
        ],
        "Ubicación": [
            'ubicacion', 'centro', 'cerca', 'lejos', 'zona', 'barrio',
            'location', 'center', 'near', 'far', 'zone', 'area', 'neighborhood'
        ]
    }
    
    for categoria, keywords in reglas.items():
        if any(root in a for root in keywords):
            return categoria
            
    return "Otros"

def proceso_completo_analisis(df, text_col, date_col, client, batch_size):
    """
    Pipeline Completo: Extracción -> Clustering IA -> Validación Reglas -> Tabla Final
    """
    # --- FASE 1: EXTRACCIÓN ---
    status = st.empty()
    bar = st.progress(0)
    status.info("1/3 Extrayendo aspectos con Gemini...")
    
    extraction_results = {}
    
    # Prompt optimizado para traducción implícita
    prompt_extract = """
    Analiza las reseñas turísticas (Español/Inglés). INPUT: {text_batch}
    
    TAREA: Extraer una lista JSON estricta.
    1. "id": El ID numérico exacto del input.
    2. "analysis": Lista de objetos con:
       - "aspecto": (1-3 palabras). Si está en inglés, TRADÚCELO al español (Ej: 'Price'->'Precio').
       - "sentimiento": "Positivo", "Negativo" o "Neutro".
       - "evidencia": Cita corta del texto.
    
    EJEMPLO:
    [ {{"id": 0, "analysis": [{{"aspecto": "Precio", "sentimiento": "Positivo", "evidencia": "very cheap"}}]}} ]
    """
    
    df = df.reset_index(drop=True)
    df['temp_id'] = df.index.astype(int)
    
    # Procesamiento de Fechas
    df['fecha_normalizada'] = pd.NaT
    if date_col and date_col != "Ninguna":
        # Coerce: Si falla (ej: "11/03/2021DD"), lo convierte en NaT (vacío) en vez de romper el código
        df['fecha_normalizada'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
    
    all_raw_aspects = set()
    total = len(df)
    
    for i in range(0, total, batch_size):
        batch = df.iloc[i:i+batch_size]
        batch_input = [{"id": int(r['temp_id']), "text": str(r[text_col])[:600]} for _, r in batch.iterrows()]
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_extract.format(text_batch=json.dumps(batch_input, ensure_ascii=False)),
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = limpiar_json(response.text)
            
            if isinstance(data, list):
                for item in data:
                    if 'id' in item:
                        extraction_results[item['id']] = item.get('analysis', [])
                        for sub in item.get('analysis', []):
                            if 'aspecto' in sub: all_raw_aspects.add(sub['aspecto'].lower().strip())
        except Exception as e:
            print(f"Error silencioso en lote {i}: {e}")
        bar.progress(min((i + batch_size) / total, 1.0))

    # --- 2. CLUSTERING CON IA ---
    status.info(f"2/3 Categorizando {len(all_raw_aspects)} términos únicos...")
    mapping_dict = {}
    
    if all_raw_aspects:
        unique_list = list(all_raw_aspects)
        prompt_cluster = f"""
        Mapea estos términos a: ["Gastronomía", "Seguridad", "Infraestructura", "Atención", "Precio", "Naturaleza", "Transporte", "Ubicación"].
        Si es ambiguo usa "Otros".
        LISTA: {json.dumps(unique_list[:800])}
        SALIDA JSON: {{ "termino": "CATEGORIA" }}
        """
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_cluster,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            mapping_dict = limpiar_json(resp.text)
        except: pass

    # --- 3. CONSOLIDACIÓN ---
    status.info("3/3 Generando reporte final...")
    clean_rows = []
    
    for idx, analysis_list in extraction_results.items():
        try: txt = df.loc[df['temp_id'] == idx, text_col].iloc[0]
        except: txt = ""
        
        # Recuperar fecha normalizada
        fecha = df.loc[df['temp_id'] == idx, 'fecha_normalizada'].iloc[0]
        
        for item in analysis_list:
            raw = item.get('aspecto', 'N/A').strip()
            raw_low = raw.lower()
            
            # Prioridad 1: IA Clustering
            cat = mapping_dict.get(raw_low, None)
            # Prioridad 2: Reglas Bilingües
            if not cat or cat == "Otros":
                cat = categorizar_por_reglas(raw_low)
            
            clean_rows.append({
                "ID": idx, "Aspecto": raw.title(),
                "Categoría": cat, "Sentimiento": item.get('sentimiento', 'Neutro'),
                "Evidencia": item.get('evidencia', ''),
                "Fecha": fecha
            })
            
    status.empty()
    bar.empty()
    return pd.DataFrame(clean_rows)

# ============================================
#  INTERFAZ PRINCIPAL
# ============================================
st.title(" ANALISIS DE SENTIMIENTOS BASADO EN ASPECTOS")
st.markdown("Sistema inteligente para análisis de opiniones turísticas.")

up = st.file_uploader("Sube tu archivo (CSV/Excel)", type=["csv", "xlsx"])

if up:
    if up.name.endswith('.csv'): df = pd.read_csv(up).head(max_rows)
    else: df = pd.read_excel(up).head(max_rows)
    
    st.dataframe(df.head(3), use_container_width=True)
    
    # Selectores de Columnas
    c1, c2 = st.columns(2)
    with c1:
        text_col = st.selectbox(" Columna de Comentarios:", df.columns)
    with c2:
        # Intenta autodetectar columna de fecha
        date_candidates = ["Ninguna"] + list(df.columns)
        default_idx = 0
        for i, col in enumerate(date_candidates):
            if 'date' in col.lower() or 'fecha' in col.lower() or 'time' in col.lower():
                default_idx = i
                break
        date_col = st.selectbox(" Columna de Fecha (Opcional):", date_candidates, index=default_idx)
    
    # Botón Principal
    if st.button(" Iniciar Análisis Completo", type="primary"):
        if not api_key:
            st.error(" Falta la API Key en la barra lateral.")
        else:
            with st.spinner("Ejecutando pipeline de IA..."):
                final_df = proceso_completo_analisis(df, text_col, date_col, client, batch_size)
                st.session_state.clean_df = final_df
                if not final_df.empty:
                    st.success(f"¡Éxito! Se extrajeron {len(final_df)} aspectos.")
                else:
                    st.error("No se encontraron datos.")

# ============================================
#  PESTAÑAS DE RESULTADOS
# ============================================
if st.session_state.clean_df is not None and not st.session_state.clean_df.empty:
    st.divider()
    df_viz = st.session_state.clean_df
    
    # TABS
    tab_data, tab_dash, tab_time = st.tabs([" Datos Limpios", " Dashboard Global", " Análisis Temporal"])
    
    # --- TAB 1: DATOS ---
    with tab_data:
        st.dataframe(df_viz, use_container_width=True)
        csv = df_viz.to_csv(index=False).encode('utf-8')
        st.download_button(" Descargar CSV", csv, "resultados_absa.csv", "text/csv")
        
    # --- TAB 2: DASHBOARD GLOBAL ---
    with tab_dash:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#####  Jerarquía de Opiniones")
            fig_sun = px.sunburst(
                df_viz, path=['Categoría', 'Sentimiento', 'Aspecto'],
                color='Sentimiento',
                color_discrete_map={"Positivo":"#2ecc71", "Negativo":"#e74c3c", "Neutro":"#95a5a6", "Otros": "#bdc3c7"}
            )
            st.plotly_chart(fig_sun, use_container_width=True)
        with col_g2:
            st.markdown("#####  Volumen por Categoría")
            fig_bar = px.histogram(df_viz, y="Categoría", color="Sentimiento", barmode="group", orientation='h',
                                   color_discrete_map={"Positivo":"#2ecc71", "Negativo":"#e74c3c", "Neutro":"#95a5a6"})
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        # Top Fortalezas y Debilidades
        c_pos, c_neg = st.columns(2)
        with c_pos:
            st.markdown("#####  Fortalezas (Top 10)")
            df_pos = df_viz[df_viz['Sentimiento']=='Positivo']['Aspecto'].value_counts().head(10).reset_index()
            if not df_pos.empty:
                fig_p = px.bar(df_pos, x='count', y='Aspecto', orientation='h', color_discrete_sequence=['#2ecc71'])
                fig_p.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_p, use_container_width=True)
        
        with c_neg:
            st.markdown("#####  Puntos de Dolor (Top 10)")
            df_neg = df_viz[df_viz['Sentimiento']=='Negativo']['Aspecto'].value_counts().head(10).reset_index()
            if not df_neg.empty:
                fig_n = px.bar(df_neg, x='count', y='Aspecto', orientation='h', color_discrete_sequence=['#e74c3c'])
                fig_n.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_n, use_container_width=True)

    # --- TAB 3: ANÁLISIS TEMPORAL (NUEVO) ---
    with tab_time:
        st.subheader(" Evolución en el Tiempo")
        
        # Verificar fechas válidas
        if df_viz['Fecha'].isnull().all():
            st.warning(" No seleccionaste una columna de fecha válida o el formato no es reconocible.")
        else:
            # Preparar datos: Agrupar por Mes
            df_time = df_viz.dropna(subset=['Fecha']).copy()
            df_time['Mes'] = df_time['Fecha'].dt.to_period('M').astype(str)
            
            # 1. Línea de Sentimientos
            st.markdown("#####  Evolución del Sentimiento")
            time_sent = df_time.groupby(['Mes', 'Sentimiento']).size().reset_index(name='Cantidad')
            fig_line = px.line(
                time_sent, x='Mes', y='Cantidad', color='Sentimiento',
                markers=True,
                color_discrete_map={"Positivo":"#2ecc71", "Negativo":"#e74c3c", "Neutro":"#95a5a6"}
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            # 2. Área de Categorías Negativas (Pain Points)
            st.markdown("#####  Tendencia de Quejas por Categoría")
            negativos = df_time[df_time['Sentimiento'] == 'Negativo']
            if not negativos.empty:
                time_cat = negativos.groupby(['Mes', 'Categoría']).size().reset_index(name='Quejas')
                fig_area = px.area(
                    time_cat, x='Mes', y='Quejas', color='Categoría',
                    title="¿Qué problemas están creciendo?"
                )
                st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.info("¡No hay quejas suficientes para graficar tendencias! ")
                