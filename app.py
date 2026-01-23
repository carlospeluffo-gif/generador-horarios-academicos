import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA Y DOMINIO UPRM
# ==============================================================================

st.set_page_config(
    page_title="UPRM Scheduler Pro - AI Engine",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DEFINICIÓN DE BLOQUES DE TIEMPO (PATRONES REALES UPRM) ---
BLOQUES_TIEMPO = {
    # --- 3 CREDITOS (LWV 50min) ---
    'LWV_0730': {'id': 'LWV_0730', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 450, 'duracion': 50, 'label': 'LWV 7:30 - 8:20 AM'},
    'LWV_0830': {'id': 'LWV_0830', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 510, 'duracion': 50, 'label': 'LWV 8:30 - 9:20 AM'},
    'LWV_0930': {'id': 'LWV_0930', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 570, 'duracion': 50, 'label': 'LWV 9:30 - 10:20 AM'},
    'LWV_1030': {'id': 'LWV_1030', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 630, 'duracion': 50, 'label': 'LWV 10:30 - 11:20 AM (Hora Universal)'},
    'LWV_1130': {'id': 'LWV_1130', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 690, 'duracion': 50, 'label': 'LWV 11:30 - 12:20 PM'},
    'LWV_1230': {'id': 'LWV_1230', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 750, 'duracion': 50, 'label': 'LWV 12:30 - 1:20 PM'},
    'LWV_1330': {'id': 'LWV_1330', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 810, 'duracion': 50, 'label': 'LWV 1:30 - 2:20 PM'},
    'LWV_1430': {'id': 'LWV_1430', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 870, 'duracion': 50, 'label': 'LWV 2:30 - 3:20 PM'},
    'LWV_1530': {'id': 'LWV_1530', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 930, 'duracion': 50, 'label': 'LWV 3:30 - 4:20 PM'},
    'LWV_1630': {'id': 'LWV_1630', 'dias': ['Lu', 'Mi', 'Vi'], 'inicio': 990, 'duracion': 50, 'label': 'LWV 4:30 - 5:20 PM'},

    # --- 3 CREDITOS (MJ 1h 20min) ---
    'MJ_0730': {'id': 'MJ_0730', 'dias': ['Ma', 'Ju'], 'inicio': 450, 'duracion': 80, 'label': 'MJ 7:30 - 8:50 AM'},
    'MJ_0900': {'id': 'MJ_0900', 'dias': ['Ma', 'Ju'], 'inicio': 540, 'duracion': 80, 'label': 'MJ 9:00 - 10:20 AM'},
    'MJ_1030': {'id': 'MJ_1030', 'dias': ['Ma', 'Ju'], 'inicio': 630, 'duracion': 80, 'label': 'MJ 10:30 - 11:50 AM (Hora Universal)'},
    'MJ_1230': {'id': 'MJ_1230', 'dias': ['Ma', 'Ju'], 'inicio': 750, 'duracion': 80, 'label': 'MJ 12:30 - 1:50 PM'},
    'MJ_1400': {'id': 'MJ_1400', 'dias': ['Ma', 'Ju'], 'inicio': 840, 'duracion': 80, 'label': 'MJ 2:00 - 3:20 PM'},
    'MJ_1530': {'id': 'MJ_1530', 'dias': ['Ma', 'Ju'], 'inicio': 930, 'duracion': 80, 'label': 'MJ 3:30 - 4:50 PM'},
    'MJ_1700': {'id': 'MJ_1700', 'dias': ['Ma', 'Ju'], 'inicio': 1020, 'duracion': 80, 'label': 'MJ 5:00 - 6:20 PM'},
    
    # --- 4 CREDITOS / BLOQUES LARGOS ---
    'LMWJ_0730': {'id': 'LMWJ_0730', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 450, 'duracion': 50, 'label': 'LMWJ 7:30 - 8:20 (4 Cr)'},
    'LMWJ_0830': {'id': 'LMWJ_0830', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 510, 'duracion': 50, 'label': 'LMWJ 8:30 - 9:20 (4 Cr)'},
    'LMWJ_0930': {'id': 'LMWJ_0930', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 570, 'duracion': 50, 'label': 'LMWJ 9:30 - 10:20 (4 Cr)'},
    'LMWJ_1230': {'id': 'LMWJ_1230', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 750, 'duracion': 50, 'label': 'LMWJ 12:30 - 1:20 (4 Cr)'},
    'LMWJ_1330': {'id': 'LMWJ_1330', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 810, 'duracion': 50, 'label': 'LMWJ 1:30 - 2:20 (4 Cr)'},
    'LMWJ_1430': {'id': 'LMWJ_1430', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 870, 'duracion': 50, 'label': 'LMWJ 2:30 - 3:20 (4 Cr)'},
}

def mins_to_str(minutes):
    """Convierte minutos del día a formato HH:MM"""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

# ==============================================================================
# 2. MODELADO DE DATOS (CLASES ROBUSTAS)
# ==============================================================================

class Seccion:
    def __init__(self, uid, codigo, nombre, creditos, cupo, candidatos, tipo_salon_req):
        self.uid = uid
        self.codigo = str(codigo).strip().upper()
        self.nombre = str(nombre).strip()
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_salon_req).strip().upper()
        
        # Parseo robusto de candidatos (NORMALIZACIÓN A MAYÚSCULAS)
        if pd.isna(candidatos) or str(candidatos).strip() == '':
            self.candidatos = []
        else:
            # Dividir por comas, quitar espacios y convertir a MAYÚSCULAS
            self.candidatos = [str(c).strip().upper() for c in str(candidatos).split(',') if str(c).strip()]
    
    def __repr__(self):
        return f"{self.codigo} (ID:{self.uid})"

class Profesor:
    def __init__(self, nombre, carga_min, carga_max):
        # Nombre siempre en mayúsculas para evitar KeyErrors
        self.nombre = str(nombre).strip().upper()
        self.carga_min = float(carga_min)
        self.carga_max = float(carga_max)

class Salon:
    def __init__(self, codigo, capacidad, tipo):
        self.codigo = str(codigo).strip().upper()
        self.capacidad = int(capacidad)
        self.tipo = str(tipo).strip().upper()

class HorarioGen:
    def __init__(self, seccion, profesor_nombre, bloque_id, salon_obj):
        self.seccion = seccion
        self.profesor_nombre = profesor_nombre
        self.bloque_id = bloque_id
        self.salon_obj = salon_obj

# ==============================================================================
# 3. MOTOR DEL ALGORITMO GENÉTICO
# ==============================================================================

class SchedulerEngine:
    def __init__(self, secciones, profesores, salones):
        self.secciones = secciones
        # Mapa para acceso rápido a info del profesor
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        
        # Pre-cálculo de dominios factibles (Optimización)
        self.dominios_salones = {}
        for sec in secciones:
            validos = []
            for s in salones:
                if s.capacidad >= sec.cupo:
                    # Comparación flexible de tipos (GENERAL acepta todo, COMPUTOS solo COMPUTOS)
                    if sec.tipo_salon_req == 'GENERAL' or sec.tipo_salon_req == s.tipo:
                        validos.append(s)
            
            # Fallback: si no hay salones perfectos, usar todos (se penalizará después)
            self.dominios_salones[sec.uid] = validos if validos else salones

        self.bloques_3cr = [k for k, v in BLOQUES_TIEMPO.items() if 'LMWJ' not in k]
        self.bloques_4cr = [k for k, v in BLOQUES_TIEMPO.items() if 'LMWJ' in k]
        # Fallback si no hay bloques de 4cr definidos
        if not self.bloques_4cr: self.bloques_4cr = list(BLOQUES_TIEMPO.keys())

    def generar_individuo(self):
        genes = []
        for sec in self.secciones:
            # Seleccionar Profesor
            if sec.candidatos:
                prof = random.choice(sec.candidatos)
            else:
                prof = "TBA"
            
            # Seleccionar Bloque
            if sec.creditos >= 4:
                b_id = random.choice(self.bloques_4cr)
            else:
                b_id = random.choice(self.bloques_3cr)
                
            # Seleccionar Salón
            salon = random.choice(self.dominios_salones[sec.uid])
            
            genes.append(HorarioGen(sec, prof, b_id, salon))
        return genes

    def calcular_fitness(self, genes):
        score = 0
        hard_conflicts = []
        soft_conflicts = []
        
        ocupacion_profesores = {} 
        ocupacion_salones = {}    
        
        # Inicializamos carga SOLO con los profesores que existen en la DB
        carga_profesores = {p: 0 for p in self.profesores_dict}

        PENALTY_HARD_COLLISION = 10000
        PENALTY_HARD_CAPACITY = 5000
        PENALTY_SOFT_PREF = 50
        PENALTY_SOFT_LOAD = 100

        for gen in genes:
            bloque = BLOQUES_TIEMPO[gen.bloque_id]
            duracion = bloque['duracion']
            inicio = bloque['inicio']
            
            # 1. HARD: Capacidad Salón
            if gen.salon_obj.capacidad < gen.seccion.cupo:
                score -= PENALTY_HARD_CAPACITY
                hard_conflicts.append(f"[CAPACIDAD] {gen.seccion.codigo} ({gen.seccion.cupo}) > {gen.salon_obj.codigo} ({gen.salon_obj.capacidad})")

            # 2. HARD: Colisiones
            rango_tiempo = range(inicio, inicio + duracion)
            
            for dia in bloque['dias']:
                # Salón
                key_salon = (gen.salon_obj.codigo, dia)
                if key_salon not in ocupacion_salones: ocupacion_salones[key_salon] = []
                
                colision_salon = False
                for (t_ini, t_fin, curso_existente) in ocupacion_salones[key_salon]:
                    if max(inicio, t_ini) < min(inicio + duracion, t_fin):
                        colision_salon = True
                        other_course = curso_existente
                        break
                
                if colision_salon:
                    score -= PENALTY_HARD_COLLISION
                    hard_conflicts.append(f"[CHOQUE SALÓN] {gen.salon_obj.codigo} {dia} {mins_to_str(inicio)} ({gen.seccion.codigo} vs {other_course})")
                else:
                    ocupacion_salones[key_salon].append((inicio, inicio + duracion, gen.seccion.codigo))

                # Profesor
                if gen.profesor_nombre != "TBA":
                    key_prof = (gen.profesor_nombre, dia)
                    if key_prof not in ocupacion_profesores: ocupacion_profesores[key_prof] = []
                    
                    colision_prof = False
                    for (t_ini, t_fin, curso_existente) in ocupacion_profesores[key_prof]:
                         if max(inicio, t_ini) < min(inicio + duracion, t_fin):
                            colision_prof = True
                            other_course = curso_existente
                            break
                    
                    if colision_prof:
                        score -= PENALTY_HARD_COLLISION
                        hard_conflicts.append(f"[CHOQUE PROF] {gen.profesor_nombre} {dia} {mins_to_str(inicio)} ({gen.seccion.codigo} vs {other_course})")
                    else:
                        ocupacion_profesores[key_prof].append((inicio, inicio + duracion, gen.seccion.codigo))

            # 3. SOFT: Carga Académica (FIXED KEYERROR)
            if gen.profesor_nombre != "TBA":
                # Verificación de seguridad: Si el profe no está en la DB, lo iniciamos en 0 para no romper el código
                if gen.profesor_nombre not in carga_profesores:
                    carga_profesores[gen.profesor_nombre] = 0
                
                carga_profesores[gen.profesor_nombre] += gen.seccion.creditos
                
                if gen.seccion.candidatos and gen.profesor_nombre not in gen.seccion.candidatos:
                    score -= PENALTY_SOFT_PREF

        # Validar Cargas (Solo para profesores que sí existen en la DB)
        for prof_nombre, carga in carga_profesores.items():
            prof_obj = self.profesores_dict.get(prof_nombre)
            if prof_obj:
                if carga > prof_obj.carga_max:
                    score -= PENALTY_SOFT_LOAD * (carga - prof_obj.carga_max)
                    soft_conflicts.append(f"[SOBRECARGA] {prof_nombre}: {carga} crds (Max {prof_obj.carga_max})")
                elif carga < prof_obj.carga_min and carga > 0:
                    score -= (PENALTY_SOFT_LOAD / 2)
                    soft_conflicts.append(f"[SUBCARGA] {prof_nombre}: {carga} crds (Min {prof_obj.carga_min})")

        return score, hard_conflicts, soft_conflicts

    def cruce(self, padre1, padre2):
        genes_hijo = []
        for g1, g2 in zip(padre1, padre2):
            genes_hijo.append(copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2))
        return genes_hijo

    def mutacion(self, genes, rate=0.1):
        for gen in genes:
            if random.random() < rate:
                tipo = random.choice(['bloque', 'salon', 'prof'])
                
                if tipo == 'bloque':
                    valid_bloques = self.bloques_4cr if gen.seccion.creditos >= 4 else self.bloques_3cr
                    if valid_bloques: gen.bloque_id = random.choice(valid_bloques)
                
                elif tipo == 'salon':
                    gen.salon_obj = random.choice(self.dominios_salones[gen.seccion.uid])
                
                elif tipo == 'prof':
                    if gen.seccion.candidatos:
                        gen.profesor_nombre = random.choice(gen.seccion.candidatos)

    def evolucionar(self, pop_size=50, generaciones=100, mutacion_rate=0.1, progress_callback=None):
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        mejor_global = None
        mejor_fitness = -float('inf')
        history = []

        for gen_idx in range(generaciones):
            evaluaciones = []
            for ind in poblacion:
                fit, hard, soft = self.calcular_fitness(ind)
                evaluaciones.append({'genes': ind, 'fitness': fit, 'hard': hard, 'soft': soft})
            
            evaluaciones.sort(key=lambda x: x['fitness'], reverse=True)
            mejor_actual = evaluaciones[0]
            
            if mejor_actual['fitness'] > mejor_fitness:
                mejor_fitness = mejor_actual['fitness']
                mejor_global = copy.deepcopy(mejor_actual) # Deepcopy para guardar el mejor snapshot
            
            history.append(mejor_fitness)
            
            if progress_callback:
                progress_callback(gen_idx, generaciones, mejor_actual)

            # Elitismo + Torneo
            nueva_poblacion = [mejor_actual['genes']] 
            while len(nueva_poblacion) < pop_size:
                parents = random.sample(evaluaciones, min(4, len(evaluaciones)))
                parents.sort(key=lambda x: x['fitness'], reverse=True)
                hijo = self.cruce(parents[0]['genes'], parents[1]['genes'])
                self.mutacion(hijo, mutacion_rate)
                nueva_poblacion.append(hijo)
            
            poblacion = nueva_poblacion
            
        return mejor_global, history

# ==============================================================================
# 4. INTERFAZ DE USUARIO (STREAMLIT)
# ==============================================================================

def main():
    st.markdown("""
        <style>
        .stAlert { padding: 0.5rem; margin-bottom: 0.5rem; }
        .metric-card { background-color: #f0f2f6; border-radius: 8px; padding: 15px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("⚙️ Panel de Control")
    st.sidebar.markdown("---")
    
    uploaded_file = st.sidebar.file_uploader("📂 Cargar Datos (Excel)", type=['xlsx'])
    
    with st.sidebar.expander("🛠️ Parámetros del Algoritmo", expanded=False):
        pop_size = st.slider("Población", 20, 300, 80)
        generations = st.slider("Generaciones", 10, 1000, 150)
        mutation = st.slider("Tasa de Mutación", 0.01, 0.5, 0.15)

    st.title("⚡ UPRM Auto-Scheduler V2.1 (Fix)")
    st.markdown("Sistema de optimización robusto para generación de horarios.")

    if not uploaded_file:
        st.info("👋 Por favor carga el archivo Excel con las hojas: 'Cursos', 'Profesores', 'Salones'.")
        return

    try:
        xls = pd.ExcelFile(uploaded_file)
        df_cursos = pd.read_excel(xls, 'Cursos')
        df_profes = pd.read_excel(xls, 'Profesores')
        df_salones = pd.read_excel(xls, 'Salones')
    except Exception as e:
        st.error(f"Error leyendo el Excel: {e}")
        return

    # Limpieza de Nombres de Columnas
    df_cursos.columns = [str(c).strip().upper() for c in df_cursos.columns]
    df_profes.columns = [str(c).strip().title() for c in df_profes.columns]
    df_salones.columns = [str(c).strip().upper() for c in df_salones.columns]

    secciones_obj = []
    sec_id_counter = 1
    
    with st.spinner("Procesando datos..."):
        try:
            # 1. Profesores
            profes_obj = []
            for _, row in df_profes.iterrows():
                # Forzamos nombre en MAYUSCULA
                profes_obj.append(Profesor(str(row['Nombre']).upper(), row['Carga_Min'], row['Carga_Max']))
                
            # 2. Salones
            salones_obj = []
            for _, row in df_salones.iterrows():
                salones_obj.append(Salon(row['CODIGO'], row['CAPACIDAD'], row['TIPO']))

            # 3. Cursos (Expansión)
            for _, row in df_cursos.iterrows():
                cantidad = int(row.get('CANTIDAD_SECCIONES', 1))
                for i in range(cantidad):
                    s = Seccion(
                        uid=f"{row['CODIGO']}-{i+1:03d}",
                        codigo=row['CODIGO'],
                        nombre=row.get('NOMBRE', 'N/A'),
                        creditos=row['CREDITOS'],
                        cupo=row['CUPO'],
                        candidatos=row.get('CANDIDATOS', ''), # Esto ahora se normaliza en la clase
                        tipo_salon_req=row.get('TIPO_SALON', 'GENERAL')
                    )
                    secciones_obj.append(s)
                    sec_id_counter += 1
            
            st.success(f"✅ Datos Cargados: {len(secciones_obj)} Secciones | {len(profes_obj)} Profesores | {len(salones_obj)} Salones")
            
        except Exception as e:
            st.error(f"Error procesando datos: {e}")
            return

    if st.button("🚀 INICIAR OPTIMIZACIÓN", type="primary"):
        engine = SchedulerEngine(secciones_obj, profes_obj, salones_obj)
        
        prog_bar = st.progress(0)
        status_text = st.empty()
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        start_time = time.time()
        
        def update_ui(gen, total_gen, best_ind):
            prog = (gen + 1) / total_gen
            prog_bar.progress(prog)
            status_text.text(f"Generación {gen+1}/{total_gen}")
            
            if gen % 5 == 0:
                metric_col1.metric("Fitness", int(best_ind['fitness']))
                metric_col2.metric("Conflictos Hard", len(best_ind['hard']), delta_color="inverse")
                metric_col3.metric("Conflictos Soft", len(best_ind['soft']), delta_color="inverse")

        best_solution, history = engine.evolucionar(pop_size, generations, mutation, update_ui)
        
        elapsed = time.time() - start_time
        st.balloons()
        
        # --- RESULTADOS ---
        st.divider()
        st.subheader("📊 Resultados Finales")

        # Tablas
        rows_data = []
        for g in best_solution['genes']:
            bloque_info = BLOQUES_TIEMPO[g.bloque_id]
            rows_data.append({
                'Código': g.seccion.codigo,
                'Sección': g.seccion.uid.split('-')[1],
                'Profesor': g.profesor_nombre,
                'Días': "".join(bloque_info['dias']),
                'Horario': f"{mins_to_str(bloque_info['inicio'])} - {mins_to_str(bloque_info['inicio'] + bloque_info['duracion'])}",
                'Salón': g.salon_obj.codigo,
                'Cupo': g.seccion.cupo
            })
        
        df_res = pd.DataFrame(rows_data).sort_values(by=['Código', 'Sección'])
        
        tab1, tab2, tab3 = st.tabs(["📅 Tabla", "⚠️ Conflictos", "💾 Exportar"])
        
        with tab1:
            st.dataframe(df_res, use_container_width=True)
            
        with tab2:
            if best_solution['hard']:
                st.error(f"Conflictos Críticos: {len(best_solution['hard'])}")
                for h in best_solution['hard']: st.write(f"- {h}")
            else:
                st.success("¡Horario Factible (0 Conflictos Críticos)!")
                
            with st.expander("Ver Preferencias / Cargas (Soft)"):
                for s in best_solution['soft']: st.write(f"- {s}")
                
        with tab3:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_res.to_excel(writer, sheet_name='Horario', index=False)
            
            st.download_button("Descargar Excel", buffer.getvalue(), "horario_uprm_final.xlsx")

if __name__ == "__main__":
    main()
