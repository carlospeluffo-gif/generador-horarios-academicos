import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import plotly.express as px
from datetime import datetime, timedelta

# ========================================================
# 1. CONFIGURACIÓN Y CONSTANTES (MODELO MATEMÁTICO)
# ========================================================
st.set_page_config(page_title="UPRM Auto-Scheduler Thesis Ed.", page_icon="🧬", layout="wide")

# Definición de Bloques de Tiempo Estándar (Patrones UPRM)
# Esto reduce el espacio de búsqueda y garantiza horarios realistas.
BLOQUES_TIEMPO = {
    # Patrón Lunes-Miércoles-Viernes (3 Créditos - 50 min)
    'LWV_0730': {'id': 0, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '07:30', 'fin': '08:20', 'label': 'LWV 7:30-8:20'},
    'LWV_0830': {'id': 1, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '08:30', 'fin': '09:20', 'label': 'LWV 8:30-9:20'},
    'LWV_0930': {'id': 2, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '09:30', 'fin': '10:20', 'label': 'LWV 9:30-10:20'},
    'LWV_1030': {'id': 3, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '10:30', 'fin': '11:20', 'label': 'LWV 10:30-11:20'},
    'LWV_1130': {'id': 4, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '11:30', 'fin': '12:20', 'label': 'LWV 11:30-12:20'},
    'LWV_1230': {'id': 5, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '12:30', 'fin': '13:20', 'label': 'LWV 12:30-1:20'},
    'LWV_1330': {'id': 6, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '13:30', 'fin': '14:20', 'label': 'LWV 1:30-2:20'},
    'LWV_1430': {'id': 7, 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': '14:30', 'fin': '15:20', 'label': 'LWV 2:30-3:20'},
    
    # Patrón Martes-Jueves (3 Créditos - 1h 20min)
    'MJ_0730': {'id': 8, 'dias': ['Ma', 'Ju'], 'inicio': '07:30', 'fin': '08:50', 'label': 'MJ 7:30-8:50'},
    'MJ_0900': {'id': 9, 'dias': ['Ma', 'Ju'], 'inicio': '09:00', 'fin': '10:20', 'label': 'MJ 9:00-10:20'},
    # Hora Universal (10:30 - 12:00) generalmente se evita, pero la ponemos disponible con penalización alta si se desea
    'MJ_1230': {'id': 10, 'dias': ['Ma', 'Ju'], 'inicio': '12:30', 'fin': '13:50', 'label': 'MJ 12:30-1:50'},
    'MJ_1400': {'id': 11, 'dias': ['Ma', 'Ju'], 'inicio': '14:00', 'fin': '15:20', 'label': 'MJ 2:00-3:20'},
    'MJ_1530': {'id': 12, 'dias': ['Ma', 'Ju'], 'inicio': '15:30', 'fin': '16:50', 'label': 'MJ 3:30-4:50'}
}

# Clases de 4 créditos suelen tener laboratorios o combinaciones, 
# para este demo asumiremos que se ajustan a bloques de 3 créditos + 1 hora extra o bloques especiales.
# Para simplificar el MVP, usaremos los bloques estándar.

def str_to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

# ========================================================
# 2. ESTRUCTURAS DE DATOS (GENOTIPO)
# ========================================================

class Seccion:
    """Representa una instancia única de una clase (e.g. MATE3031 Sección 001)"""
    def __init__(self, id_seccion, curso_info, numero_seccion):
        self.id = id_seccion
        self.codigo = curso_info['CODIGO']
        self.nombre = curso_info['NOMBRE']
        self.creditos = curso_info['CREDITOS']
        self.cupo = curso_info['CUPO']
        self.tipo_salon = curso_info['TIPO_SALON']
        # Limpiar lista de candidatos
        raw_cands = str(curso_info['CANDIDATOS']).split(',')
        self.candidatos = [c.strip() for c in raw_cands if len(c.strip()) > 1]
        self.num_seccion = f"{numero_seccion:03d}"

class Gen:
    """
    Un Gen representa la asignación de RECURSOS a una SECCIÓN específica.
    Gen = [Sección, Profesor, BloqueTiempo, Salón]
    """
    def __init__(self, seccion, profesor, bloque_key, salon):
        self.seccion = seccion
        self.profesor = profesor        # String (Nombre)
        self.bloque_key = bloque_key    # Key del dict BLOQUES_TIEMPO
        self.salon = salon              # Objeto (Diccionario del salón)

class Cromosoma:
    """Un individuo completo (Un Horario Completo)"""
    def __init__(self, genes):
        self.genes = genes
        self.fitness = 0.0
        self.conflictos_hard = []
        self.conflictos_soft = []

    def calcular_fitness(self, profesores_db):
        """
        Función Objetivo f(H) = w_f * Violaciones_Hard + w_s * Violaciones_Soft
        Objetivo: Maximizar Fitness (o minimizar costo). Aquí usaremos un score que empieza en 0 y resta.
        """
        score = 0
        self.conflictos_hard = []
        self.conflictos_soft = []
        
        PENALTY_HARD = 1000
        PENALTY_SOFT = 10

        # Estructuras auxiliares para detectar choques rápidamente
        # Mapa: (Dia, Minuto) -> Lista de ocupación
        # Para hacerlo eficiente, usaremos buckets por bloque de tiempo.
        
        profesor_ocupacion = {} # {NombreProf: [(BloqueID, Curso)]}
        salon_ocupacion = {}    # {CodigoSalon: [(BloqueID, Curso)]}

        for gen in self.genes:
            bloque = BLOQUES_TIEMPO[gen.bloque_key]
            
            # 1. RESTRICCIÓN FUERTE: Capacidad del Salón
            if gen.salon['CAPACIDAD'] < gen.seccion.cupo:
                score -= PENALTY_HARD
                self.conflictos_hard.append(f"Capacidad: {gen.seccion.codigo}-{gen.seccion.num_seccion} ({gen.seccion.cupo}) excede salón {gen.salon['CODIGO']} ({gen.salon['CAPACIDAD']})")

            # 2. RESTRICCIÓN FUERTE: Tipo de Salón
            # Normalización simple para comparar
            req_tipo = str(gen.seccion.tipo_salon).lower().strip()
            sal_tipo = str(gen.salon['TIPO']).lower().strip()
            if req_tipo != "general" and req_tipo != sal_tipo:
                 score -= PENALTY_HARD
                 self.conflictos_hard.append(f"Tipo Salón: {gen.seccion.codigo} requiere {req_tipo}, asignado a {gen.salon['CODIGO']} ({sal_tipo})")

            # 3. RESTRICCIÓN FUERTE: Choque de Horario (Profesor)
            if gen.profesor != "TBA":
                if gen.profesor not in profesor_ocupacion: profesor_ocupacion[gen.profesor] = []
                
                # Verificar choques con clases ya procesadas
                for b_id_ocupado, curso_ocupado in profesor_ocupacion[gen.profesor]:
                    # Si los bloques se solapan en días y horas
                    if bloques_solapan(bloque, BLOQUES_TIEMPO[b_id_ocupado]):
                        score -= PENALTY_HARD
                        self.conflictos_hard.append(f"Choque Prof: {gen.profesor} tiene {gen.seccion.codigo} y {curso_ocupado} al mismo tiempo.")
                        break # Solo penalizar una vez por par
                
                profesor_ocupacion[gen.profesor].append((gen.bloque_key, gen.seccion.codigo))

            # 4. RESTRICCIÓN FUERTE: Choque de Horario (Salón)
            sid = gen.salon['CODIGO']
            if sid not in salon_ocupacion: salon_ocupacion[sid] = []
            for b_id_ocupado, curso_ocupado in salon_ocupacion[sid]:
                if bloques_solapan(bloque, BLOQUES_TIEMPO[b_id_ocupado]):
                    score -= PENALTY_HARD
                    self.conflictos_hard.append(f"Choque Salón: {sid} ocupado por {gen.seccion.codigo} y {curso_ocupado}.")
                    break
            salon_ocupacion[sid].append((gen.bloque_key, gen.seccion.codigo))
            
            # 5. RESTRICCIÓN SUAVE: Preferencia de Candidatos
            # Si el profesor asignado NO está en la lista de candidatos preferidos (pero es apto teóricamente)
            # En este modelo, asumimos que solo asignamos candidatos válidos, pero si forzamos uno externo:
            if gen.seccion.candidatos and gen.profesor not in gen.seccion.candidatos and gen.profesor != "TBA":
                 score -= PENALTY_SOFT * 5 # Penalidad media
                 self.conflictos_soft.append(f"Preferencia: {gen.profesor} no es candidato ideal para {gen.seccion.codigo}")

        # 6. RESTRICCIONES SUAVES GLOBALES (Carga Académica)
        for prof, ocupaciones in profesor_ocupacion.items():
            # Calcular carga total (aprox 3 creditos por curso)
            carga = len(ocupaciones) * 3 
            info_prof = profesores_db.get(prof)
            if info_prof:
                if carga > info_prof['Carga_Max']:
                    score -= PENALTY_SOFT * (carga - info_prof['Carga_Max'])
                    self.conflictos_soft.append(f"Sobrecarga: {prof} tiene {carga} crds (Max: {info_prof['Carga_Max']})")
                if carga < info_prof['Carga_Min']:
                    score -= PENALTY_SOFT
                    self.conflictos_soft.append(f"Subcarga: {prof} tiene {carga} crds (Min: {info_prof['Carga_Min']})")

        self.fitness = score
        return score

def bloques_solapan(b1, b2):
    """Retorna True si dos bloques de tiempo tienen conflicto"""
    # 1. Verificar intersección de días
    dias1 = set(b1['dias'])
    dias2 = set(b2['dias'])
    if not dias1.intersection(dias2):
        return False # No coinciden días
    
    # 2. Verificar intersección de horas
    start1, end1 = str_to_minutes(b1['inicio']), str_to_minutes(b1['fin'])
    start2, end2 = str_to_minutes(b2['inicio']), str_to_minutes(b2['fin'])
    
    # Lógica de solapamiento: (Start1 < End2) y (Start2 < End1)
    if (start1 < end2) and (start2 < end1):
        return True
    
    return False

# ========================================================
# 3. ALGORITMO GENÉTICO
# ========================================================

def generar_poblacion_inicial(secciones, salones, size=50):
    poblacion = []
    keys_bloques = list(BLOQUES_TIEMPO.keys())
    
    for _ in range(size):
        genes = []
        for sec in secciones:
            # Asignación Aleatoria Inteligente
            # 1. Elegir profesor de candidatos (o TBA si vacio)
            prof = random.choice(sec.candidatos) if sec.candidatos else "TBA"
            
            # 2. Elegir un bloque de tiempo
            bloque = random.choice(keys_bloques)
            
            # 3. Elegir un salón que cumpla capacidad (Heurística inicial)
            salones_posibles = [s for s in salones if s['CAPACIDAD'] >= sec.cupo]
            if not salones_posibles: salones_posibles = salones # Fallback
            salon = random.choice(salones_posibles)
            
            genes.append(Gen(sec, prof, bloque, salon))
        
        poblacion.append(Cromosoma(genes))
    return poblacion

def torneo_seleccion(poblacion, k=3):
    seleccionados = random.sample(poblacion, k)
    return max(seleccionados, key=lambda x: x.fitness)

def cruce(padre1, padre2):
    """Cruce Uniforme: cada gen (sección) se hereda de P1 o P2"""
    genes_hijo = []
    for g1, g2 in zip(padre1.genes, padre2.genes):
        # 50% probabilidad de heredar de cada uno
        gen_nuevo = copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2)
        genes_hijo.append(gen_nuevo)
    return Cromosoma(genes_hijo)

def mutacion(individuo, salones, tasa_mutacion=0.1):
    keys_bloques = list(BLOQUES_TIEMPO.keys())
    for gen in individuo.genes:
        if random.random() < tasa_mutacion:
            tipo_mutacion = random.choice(['tiempo', 'salon', 'profesor'])
            
            if tipo_mutacion == 'tiempo':
                gen.bloque_key = random.choice(keys_bloques)
            elif tipo_mutacion == 'salon':
                # Intentar buscar salón válido
                salones_ok = [s for s in salones if s['CAPACIDAD'] >= gen.seccion.cupo]
                gen.salon = random.choice(salones_ok) if salones_ok else random.choice(salones)
            elif tipo_mutacion == 'profesor':
                if gen.seccion.candidatos:
                    gen.profesor = random.choice(gen.seccion.candidatos)

def ejecutar_ga(secciones, salones, profesores_db, pop_size, generaciones, mutacion_rate, progress_bar, status_txt):
    poblacion = generar_poblacion_inicial(secciones, salones, pop_size)
    
    # Evaluar inicial
    best_overall = None
    
    for gen_idx in range(generaciones):
        for ind in poblacion:
            ind.calcular_fitness(profesores_db)
        
        # Ordenar
        poblacion.sort(key=lambda x: x.fitness, reverse=True)
        mejor_actual = poblacion[0]
        
        if best_overall is None or mejor_actual.fitness > best_overall.fitness:
            best_overall = copy.deepcopy(mejor_actual)
        
        # Visualización progreso
        progress_bar.progress((gen_idx + 1) / generaciones)
        status_txt.markdown(f"**Generación {gen_idx+1}:** Fitness: {mejor_actual.fitness:.2f} | Conflictos Hard: {len(mejor_actual.conflictos_hard)}")
        
        # Elitismo (pasar el mejor directo)
        nueva_poblacion = [best_overall]
        
        # Crear descendencia
        while len(nueva_poblacion) < pop_size:
            p1 = torneo_seleccion(poblacion)
            p2 = torneo_seleccion(poblacion)
            hijo = cruce(p1, p2)
            mutacion(hijo, salones, mutacion_rate)
            nueva_poblacion.append(hijo)
            
        poblacion = nueva_poblacion

    return best_overall

# ========================================================
# 4. INTERFAZ Y PROCESAMIENTO
# ========================================================

def cargar_datos(uploaded_file):
    try:
        # Leer todas las hojas
        xls = pd.ExcelFile(uploaded_file)
        df_cursos = pd.read_excel(xls, 'Cursos')
        df_profes = pd.read_excel(xls, 'Profesores')
        df_salones = pd.read_excel(xls, 'Salones')
        
        # Normalizar columnas (quitar espacios, mayusculas)
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        df_profes.columns = [c.strip() for c in df_profes.columns] # Case sensitive titles often in pandas
        df_profes.columns = [c.title() for c in df_profes.columns] # Standarize to Title Case
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]

        # 1. Procesar Profesores a Diccionario
        # Esperamos columnas: Nombre, Carga_Min, Carga_Max
        profes_db = {}
        for _, row in df_profes.iterrows():
            nombre = row.get('Nombre', 'Unknown').strip()
            profes_db[nombre] = {
                'Carga_Min': row.get('Carga_Min', 0),
                'Carga_Max': row.get('Carga_Max', 12),
            }
            
        # 2. Procesar Salones a Lista de Dicts
        # Esperamos CODIGO, CAPACIDAD, TIPO
        salones_list = df_salones.to_dict('records')
        
        # 3. Procesar Cursos y EXPANDIR secciones
        secciones_list = []
        id_counter = 0
        for _, row in df_cursos.iterrows():
            qty = int(row.get('CANTIDAD_SECCIONES', 1))
            for i in range(qty):
                # Crear objeto sección
                s = Seccion(id_counter, row, i+1)
                secciones_list.append(s)
                id_counter += 1
                
        return secciones_list, profes_db, salones_list, None
        
    except Exception as e:
        return None, None, None, str(e)

def main():
    st.title("🎓 UPRM Course Scheduler - Thesis Edition")
    st.markdown("""
    Esta aplicación implementa un **Algoritmo Genético** para resolver el problema de *Timetabling* universitario.
    Se basa en la minimización de una función de costo sujeta a restricciones fuertes ($R_f$) y suaves ($R_s$).
    """)
    
    with st.sidebar:
        st.header("1. Carga de Datos")
        file = st.file_uploader("Subir Excel (Cursos, Profesores, Salones)", type=['xlsx'])
        
        st.header("2. Parámetros GA")
        pop_size = st.slider("Tamaño Población", 20, 200, 50)
        generaciones = st.slider("Generaciones", 10, 500, 100)
        mutacion_rate = st.slider("Tasa Mutación", 0.0, 0.5, 0.1)
        
        run_btn = st.button("🧬 Ejecutar Algoritmo", type="primary", disabled=not file)

    if file:
        secciones, profes_db, salones, err = cargar_datos(file)
        if err:
            st.error(f"Error leyendo archivo: {err}")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Secciones a Programar", len(secciones))
            c2.metric("Profesores Disponibles", len(profes_db))
            c3.metric("Salones Disponibles", len(salones))
            
            if run_btn:
                st.divider()
                st.subheader("Optimización en Progreso...")
                bar = st.progress(0)
                status = st.empty()
                
                # EJECUCIÓN DEL ALGORITMO
                start_time = datetime.now()
                mejor_horario = ejecutar_ga(secciones, salones, profes_db, pop_size, generaciones, mutacion_rate, bar, status)
                end_time = datetime.now()
                
                st.success(f"Optimización finalizada en {(end_time-start_time).total_seconds():.2f} segundos.")
                
                # MOSTRAR RESULTADOS
                st.divider()
                
                # Preparar DataFrame Final
                data_rows = []
                for g in mejor_horario.genes:
                    b_info = BLOQUES_TIEMPO[g.bloque_key]
                    data_rows.append({
                        'Curso': g.seccion.codigo,
                        'Sección': g.seccion.num_seccion,
                        'Nombre': g.seccion.nombre,
                        'Profesor': g.profesor,
                        'Días': "".join(b_info['dias']),
                        'Horario': f"{b_info['inicio']} - {b_info['fin']}",
                        'Salón': g.salon['CODIGO'],
                        'BloqueID': b_info['id'] # Para ordenar
                    })
                
                df_res = pd.DataFrame(data_rows).sort_values(by=['Curso', 'Sección'])
                
                tab1, tab2, tab3 = st.tabs(["📅 Horario Tabla", "⚠️ Reporte de Conflictos", "📊 Análisis"])
                
                with tab1:
                    st.dataframe(df_res[['Curso', 'Sección', 'Profesor', 'Días', 'Horario', 'Salón']], use_container_width=True)
                    
                    csv = df_res.to_csv(index=False).encode('utf-8')
                    st.download_button("Descargar CSV", csv, "horario_uprm.csv", "text/csv")
                
                with tab2:
                    c_hard = len(mejor_horario.conflictos_hard)
                    c_soft = len(mejor_horario.conflictos_soft)
                    
                    col_h, col_s = st.columns(2)
                    col_h.metric("Conflictos Fuertes (Deben ser 0)", c_hard, delta_color="inverse")
                    col_s.metric("Conflictos Suaves (Avisos)", c_soft, delta_color="off")
                    
                    if c_hard > 0:
                        st.error("Se encontraron violaciones críticas:")
                        for c in mejor_horario.conflictos_hard:
                            st.write(f"- {c}")
                    else:
                        st.success("✅ ¡El horario es FACTIBLE (cero choques críticos)!")
                        
                    with st.expander("Ver advertencias suaves"):
                        for c in mejor_horario.conflictos_soft:
                            st.write(f"- {c}")
                            
                with tab3:
                    # Visualización Gráfica (Heatmap simple de ocupación de salones)
                    st.write("Ocupación de Salones")
                    df_chart = df_res.groupby('Salón').count().reset_index()
                    fig = px.bar(df_chart, x='Salón', y='Curso', title="Cantidad de Clases por Salón")
                    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
