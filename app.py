import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
# Esto elimina la aleatoriedad caótica y asegura horarios institucionales válidos.

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
    
    # --- 4 CREDITOS (LMWJ o Bloques largos) - Simplificado para robustez ---
    # Asignaremos bloques especiales que cubren más días/tiempo
    'LMWJ_0730': {'id': 'LMWJ_0730', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 450, 'duracion': 50, 'label': 'LMWJ 7:30 - 8:20 (4 Cr)'},
    'LMWJ_0830': {'id': 'LMWJ_0830', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 510, 'duracion': 50, 'label': 'LMWJ 8:30 - 9:20 (4 Cr)'},
    'LMWJ_1230': {'id': 'LMWJ_1230', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 750, 'duracion': 50, 'label': 'LMWJ 12:30 - 1:20 (4 Cr)'},
    'LMWJ_1330': {'id': 'LMWJ_1330', 'dias': ['Lu', 'Ma', 'Mi', 'Ju'], 'inicio': 810, 'duracion': 50, 'label': 'LMWJ 1:30 - 2:20 (4 Cr)'},
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
        self.codigo = codigo
        self.nombre = nombre
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_salon_req).strip().upper()
        # Parseo robusto de candidatos
        if pd.isna(candidatos) or str(candidatos).strip() == '':
            self.candidatos = []
        else:
            self.candidatos = [c.strip() for c in str(candidatos).split(',') if c.strip()]
    
    def __repr__(self):
        return f"{self.codigo} (ID:{self.uid})"

class Profesor:
    def __init__(self, nombre, carga_min, carga_max):
        self.nombre = nombre
        self.carga_min = float(carga_min)
        self.carga_max = float(carga_max)
        self.carga_actual = 0

class Salon:
    def __init__(self, codigo, capacidad, tipo):
        self.codigo = codigo
        self.capacidad = int(capacidad)
        self.tipo = str(tipo).strip().upper()

class HorarioGen:
    """
    Representa un GEN del cromosoma:
    Una asignación concreta de (Sección -> Profesor, Bloque, Salón)
    """
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
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        
        # Pre-cálculo de dominios factibles (Optimización Masiva)
        # En lugar de que el GA pruebe salones aleatorios, solo le permitimos elegir
        # entre salones que YA cumplen con capacidad y tipo.
        self.dominios_salones = {}
        for sec in secciones:
            validos = []
            for s in salones:
                # 1. Chequeo capacidad
                if s.capacidad >= sec.cupo:
                    # 2. Chequeo tipo (Si curso pide 'COMPUTOS', salón debe ser 'COMPUTOS')
                    if sec.tipo_salon_req == 'GENERAL' or sec.tipo_salon_req == s.tipo:
                        validos.append(s)
            
            # Fallback: si no hay salones validos, usar todos (se penalizará después)
            self.dominios_salones[sec.uid] = validos if validos else salones

        # Filtro de bloques por créditos
        self.bloques_3cr = [k for k, v in BLOQUES_TIEMPO.items() if 'LMWJ' not in k]
        self.bloques_4cr = [k for k, v in BLOQUES_TIEMPO.items() if 'LMWJ' in k]

    def generar_individuo(self):
        genes = []
        for sec in self.secciones:
            # Seleccionar Profesor
            if sec.candidatos:
                prof = random.choice(sec.candidatos)
            else:
                prof = "TBA" # To Be Announced
            
            # Seleccionar Bloque (según créditos)
            if sec.creditos == 4:
                b_id = random.choice(self.bloques_4cr) if self.bloques_4cr else random.choice(list(BLOQUES_TIEMPO.keys()))
            else:
                b_id = random.choice(self.bloques_3cr)
                
            # Seleccionar Salón (del dominio válido pre-calculado)
            salon = random.choice(self.dominios_salones[sec.uid])
            
            genes.append(HorarioGen(sec, prof, b_id, salon))
        return genes

    def calcular_fitness(self, genes):
        """
        Calcula qué tan bueno es el horario.
        Fitness comienza en 0. Se restan puntos por violaciones.
        0 es perfecto (utópico).
        """
        score = 0
        hard_conflicts = []
        soft_conflicts = []
        
        # Estructuras de rastreo rápido (Hash Maps)
        # Clave: (Dia, Minuto) -> Valor: Lista de ocupantes
        ocupacion_profesores = {} # {NombreProf: set((dia, minuto))}
        ocupacion_salones = {}    # {CodigoSalon: set((dia, minuto))}
        carga_profesores = {p: 0 for p in self.profesores_dict}

        PENALTY_HARD_COLLISION = 10000
        PENALTY_HARD_CAPACITY = 5000
        PENALTY_SOFT_PREF = 50
        PENALTY_SOFT_LOAD = 100

        for gen in genes:
            bloque = BLOQUES_TIEMPO[gen.bloque_id]
            duracion = bloque['duracion']
            inicio = bloque['inicio']
            
            # --- 1. VALIDACIÓN SALÓN (HARD) ---
            # (Capacidad y Tipo ya fueron optimizados en la generación, pero verificamos redundancia)
            if gen.salon_obj.capacidad < gen.seccion.cupo:
                score -= PENALTY_HARD_CAPACITY
                hard_conflicts.append(f"[CAPACIDAD] {gen.seccion.codigo} ({gen.seccion.cupo}) en {gen.salon_obj.codigo} ({gen.salon_obj.capacidad})")

            # --- 2. COLISIONES DE TIEMPO (HARD) ---
            # Iteramos por cada minuto del bloque (simplificado a checking de intervalos)
            rango_tiempo = range(inicio, inicio + duracion)
            
            for dia in bloque['dias']:
                # 2.1 Colisión Salón
                key_salon = (gen.salon_obj.codigo, dia)
                if key_salon not in ocupacion_salones: ocupacion_salones[key_salon] = []
                
                # Verificar traslape simple
                colision_salon = False
                for (t_ini, t_fin, curso_existente) in ocupacion_salones[key_salon]:
                    if max(inicio, t_ini) < min(inicio + duracion, t_fin):
                        colision_salon = True
                        other_course = curso_existente
                        break
                
                if colision_salon:
                    score -= PENALTY_HARD_COLLISION
                    hard_conflicts.append(f"[CHOQUE SALÓN] {gen.salon_obj.codigo} en {dia} a las {mins_to_str(inicio)} ({gen.seccion.codigo} vs {other_course})")
                else:
                    ocupacion_salones[key_salon].append((inicio, inicio + duracion, gen.seccion.codigo))

                # 2.2 Colisión Profesor
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
                        hard_conflicts.append(f"[CHOQUE PROF] {gen.profesor_nombre} en {dia} a las {mins_to_str(inicio)} ({gen.seccion.codigo} vs {other_course})")
                    else:
                        ocupacion_profesores[key_prof].append((inicio, inicio + duracion, gen.seccion.codigo))

            # --- 3. RESTRICCIONES SUAVES ---
            # Carga Académica
            if gen.profesor_nombre != "TBA":
                carga_profesores[gen.profesor_nombre] += gen.seccion.creditos
                
                # Preferencia (Si el profesor asignado no estaba en la lista original, pequeña penalización)
                # Esto ayuda al algoritmo a preferir los candidatos listados si es posible
                if gen.seccion.candidatos and gen.profesor_nombre not in gen.seccion.candidatos:
                    score -= PENALTY_SOFT_PREF

        # Validar Cargas Totales
        for prof_nombre, carga in carga_profesores.items():
            prof_obj = self.profesores_dict.get(prof_nombre)
            if prof_obj:
                if carga > prof_obj.carga_max:
                    score -= PENALTY_SOFT_LOAD * (carga - prof_obj.carga_max)
                    soft_conflicts.append(f"[SOBRECARGA] {prof_nombre}: {carga} crds (Max {prof_obj.carga_max})")
                elif carga < prof_obj.carga_min and carga > 0: # Ignorar si es 0 (quizas no se asignó nada)
                    score -= (PENALTY_SOFT_LOAD / 2)
                    soft_conflicts.append(f"[SUBCARGA] {prof_nombre}: {carga} crds (Min {prof_obj.carga_min})")

        return score, hard_conflicts, soft_conflicts

    def cruce(self, padre1, padre2):
        """Uniform Crossover"""
        genes_hijo = []
        for g1, g2 in zip(padre1, padre2):
            genes_hijo.append(copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2))
        return genes_hijo

    def mutacion(self, genes, rate=0.1):
        """Mutación inteligente: Intenta resolver conflictos cambiando recursos"""
        for gen in genes:
            if random.random() < rate:
                tipo = random.choice(['bloque', 'salon', 'prof'])
                
                if tipo == 'bloque':
                    valid_bloques = self.bloques_4cr if gen.seccion.creditos == 4 else self.bloques_3cr
                    if valid_bloques:
                        gen.bloque_id = random.choice(valid_bloques)
                
                elif tipo == 'salon':
                    # Elegir otro salón de su dominio válido
                    gen.salon_obj = random.choice(self.dominios_salones[gen.seccion.uid])
                
                elif tipo == 'prof':
                    if gen.seccion.candidatos:
                        gen.profesor_nombre = random.choice(gen.seccion.candidatos)

    def evolucionar(self, pop_size=50, generaciones=100, mutacion_rate=0.1, progress_callback=None):
        # 1. Población Inicial
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        mejor_global = None
        mejor_fitness = -float('inf')
        
        historial_fitness = []

        for gen_idx in range(generaciones):
            # Evaluar
            evaluaciones = []
            for ind in poblacion:
                fit, hard, soft = self.calcular_fitness(ind)
                evaluaciones.append({'genes': ind, 'fitness': fit, 'hard': hard, 'soft': soft})
            
            # Ordenar por fitness (mayor es mejor, aunque sean negativos)
            evaluaciones.sort(key=lambda x: x['fitness'], reverse=True)
            mejor_actual = evaluaciones[0]
            
            if mejor_actual['fitness'] > mejor_fitness:
                mejor_fitness = mejor_actual['fitness']
                mejor_global = mejor_actual
            
            historial_fitness.append(mejor_fitness)
            
            # Callback UI
            if progress_callback:
                progress_callback(gen_idx, generaciones, mejor_actual)

            # Selección (Torneo) y Elitismo
            nueva_poblacion = [mejor_actual['genes']] # Elitismo: pasa el mejor
            
            while len(nueva_poblacion) < pop_size:
                # Torneo simple
                parents = random.sample(evaluaciones, 4)
                parents.sort(key=lambda x: x['fitness'], reverse=True)
                p1 = parents[0]['genes']
                p2 = parents[1]['genes']
                
                hijo = self.cruce(p1, p2)
                self.mutacion(hijo, mutacion_rate)
                nueva_poblacion.append(hijo)
            
            poblacion = nueva_poblacion
            
        return mejor_global, historial_fitness

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
        pop_size = st.slider("Población", 20, 300, 100, help="Más población = Mejor exploración, más lento.")
        generations = st.slider("Generaciones", 10, 1000, 200, help="Ciclos de evolución.")
        mutation = st.slider("Tasa de Mutación", 0.01, 0.5, 0.15, help="Probabilidad de cambio aleatorio.")

    st.title("⚡ UPRM Auto-Scheduler V2.0 (Enterprise)")
    st.markdown("Sistema de optimización combinatoria para generación de horarios académicos.")

    if not uploaded_file:
        st.info("👋 Por favor carga el archivo Excel con las hojas: 'Cursos', 'Profesores', 'Salones'.")
        # Generate template link logic could go here
        return

    # --- CARGA DE DATOS ---
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_cursos = pd.read_excel(xls, 'Cursos')
        df_profes = pd.read_excel(xls, 'Profesores')
        df_salones = pd.read_excel(xls, 'Salones')
    except Exception as e:
        st.error(f"Error leyendo el Excel. Asegúrate de que tenga las hojas correctas.\nDetalle: {e}")
        return

    # Limpieza de Nombres de Columnas
    df_cursos.columns = [str(c).strip().upper() for c in df_cursos.columns]
    df_profes.columns = [str(c).strip().title() for c in df_profes.columns]
    df_salones.columns = [str(c).strip().upper() for c in df_salones.columns]

    # Procesamiento y Expansión de Secciones
    secciones_obj = []
    sec_id_counter = 1
    
    with st.spinner("Procesando datos y expandiendo secciones..."):
        try:
            # 1. Profesores
            profes_obj = []
            for _, row in df_profes.iterrows():
                profes_obj.append(Profesor(row['Nombre'], row['Carga_Min'], row['Carga_Max']))
                
            # 2. Salones
            salones_obj = []
            for _, row in df_salones.iterrows():
                salones_obj.append(Salon(row['CODIGO'], row['CAPACIDAD'], row['TIPO']))

            # 3. Cursos (Expansión)
            for _, row in df_cursos.iterrows():
                cantidad = int(row.get('CANTIDAD_SECCIONES', 1))
                for i in range(cantidad):
                    s = Seccion(
                        uid=f"{row['CODIGO']}-{i+1:03d}", # E.g. MATE3031-001
                        codigo=row['CODIGO'],
                        nombre=row.get('NOMBRE', 'N/A'),
                        creditos=row['CREDITOS'],
                        cupo=row['CUPO'],
                        candidatos=row.get('CANDIDATOS', ''),
                        tipo_salon_req=row.get('TIPO_SALON', 'GENERAL')
                    )
                    secciones_obj.append(s)
                    sec_id_counter += 1
            
            st.success(f"✅ Datos Cargados: {len(secciones_obj)} Secciones | {len(profes_obj)} Profesores | {len(salones_obj)} Salones")
            
        except KeyError as e:
            st.error(f"Falta una columna requerida en el Excel: {e}")
            return

    # --- BOTÓN DE EJECUCIÓN ---
    if st.button("🚀 INICIAR OPTIMIZACIÓN", type="primary"):
        engine = SchedulerEngine(secciones_obj, profes_obj, salones_obj)
        
        # UI Elements for Progress
        prog_bar = st.progress(0)
        status_text = st.empty()
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        start_time = time.time()
        
        def update_ui(gen, total_gen, best_ind):
            prog = (gen + 1) / total_gen
            prog_bar.progress(prog)
            status_text.text(f"Generación {gen+1}/{total_gen} | Conflictos Fuertes: {len(best_ind['hard'])}")
            
            # Solo actualizar métricas visuales cada 5 gens para rendimiento
            if gen % 5 == 0:
                metric_col1.metric("Fitness", int(best_ind['fitness']))
                metric_col2.metric("Violaciones Hard", len(best_ind['hard']), delta_color="inverse")
                metric_col3.metric("Violaciones Soft", len(best_ind['soft']), delta_color="inverse")

        # EJECUTAR ALGORITMO
        best_solution, history = engine.evolucionar(pop_size, generations, mutation, update_ui)
        
        elapsed = time.time() - start_time
        st.balloons()
        
        # --- VISUALIZACIÓN DE RESULTADOS ---
        st.divider()
        st.subheader("📊 Resultados de la Optimización")
        st.write(f"Tiempo de cómputo: {elapsed:.2f} segundos")

        # 1. Gráfica de Convergencia
        fig_hist = px.line(x=range(len(history)), y=history, labels={'x':'Generación', 'y':'Fitness'}, title="Convergencia del Algoritmo")
        st.plotly_chart(fig_hist, use_container_width=True)

        # 2. Análisis de Conflictos
        c1, c2 = st.columns(2)
        with c1:
            if best_solution['hard']:
                st.error(f"❌ {len(best_solution['hard'])} Restricciones Fuertes Violadas")
                with st.expander("Ver Detalles Críticos"):
                    for h in best_solution['hard']: st.write(f"- {h}")
            else:
                st.success("✅ 0 Restricciones Fuertes Violadas (Horario Factible)")
        
        with c2:
            if best_solution['soft']:
                st.warning(f"⚠️ {len(best_solution['soft'])} Avisos de Preferencias")
                with st.expander("Ver Detalles Suaves"):
                    for s in best_solution['soft']: st.write(f"- {s}")
            else:
                st.success("✨ Horario Perfecto (Ideal)")

        # 3. Construir Tabla Final
        rows_data = []
        for g in best_solution['genes']:
            bloque_info = BLOQUES_TIEMPO[g.bloque_id]
            rows_data.append({
                'Código': g.seccion.codigo,
                'Sección ID': g.seccion.uid.split('-')[1], # Extraer el numero 001
                'Curso': g.seccion.nombre,
                'Profesor': g.profesor_nombre,
                'Días': "".join(bloque_info['dias']),
                'Hora Inicio': mins_to_str(bloque_info['inicio']),
                'Hora Fin': mins_to_str(bloque_info['inicio'] + bloque_info['duracion']),
                'Salón': g.salon_obj.codigo,
                'Cap. Salón': g.salon_obj.capacidad,
                'Cupo': g.seccion.cupo,
                'Bloque Original': bloque_info['id']
            })
        
        df_res = pd.DataFrame(rows_data)
        df_res = df_res.sort_values(by=['Código', 'Sección ID'])

        # Tabs de Visualización
        tab_table, tab_grid, tab_export = st.tabs(["📅 Tabla Detallada", "🧩 Mapa de Salones", "💾 Exportar"])
        
        with tab_table:
            st.dataframe(df_res, use_container_width=True)
        
        with tab_grid:
            st.write("Mapa de calor de ocupación de salones:")
            pivot = df_res.groupby('Salón')['Código'].count().reset_index()
            fig_bar = px.bar(pivot, x='Salón', y='Código', title="Densidad de Uso por Salón")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with tab_export:
            # Excel Buffer
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_res.to_excel(writer, sheet_name='Horario_Oficial', index=False)
                
                # Hoja de conflictos
                if best_solution['hard'] or best_solution['soft']:
                    df_conf = pd.DataFrame({'Tipo': ['Hard']*len(best_solution['hard']) + ['Soft']*len(best_solution['soft']),
                                            'Detalle': best_solution['hard'] + best_solution['soft']})
                    df_conf.to_excel(writer, sheet_name='Reporte_Conflictos', index=False)
                    
            st.download_button(
                label="📥 Descargar Excel Final (.xlsx)",
                data=buffer.getvalue(),
                file_name="horario_generado_uprm.xlsx",
                mime="application/vnd.ms-excel"
            )

if __name__ == "__main__":
    main()
