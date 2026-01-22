import streamlit as st
import pandas as pd
import random
import copy
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ========================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ========================================================

st.set_page_config(
    page_title="UPRM Scheduler Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para "look" profesional
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ========================================================
# 2. CONSTANTES Y LÓGICA DEL NEGOCIO (V3 FINAL)
# ========================================================

MATEMATICAS_SALONES_FIJOS = [
    "M 102", "M 104", "M 203", "M 205", "M 316", "M 317", "M 402", "M 404"
]

class ZonaConfig:
    CENTRAL = {
        "nombre": "Zona Central",
        "horarios_inicio": ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30"],
        "restricciones": {"Ma": [("10:30", "12:30")], "Ju": [("10:30", "12:30")]},
    }
    PERIFERICA = {
        "nombre": "Zona Periférica",
        "horarios_inicio": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"],
        "restricciones": {d: [("10:00", "12:00")] for d in ["Lu", "Ma", "Mi", "Ju", "Vi"]},
    }

def a_minutos(hhmm):
    try:
        if isinstance(hhmm, str):
            h, m = map(int, hhmm.strip().split(":"))
            return h * 60 + m
        return 0
    except: return 0

def generar_bloques_horarios():
    bloques = []
    bloques.append({"dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3})
    bloques.append({"dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3})
    bloques.append({"dias": ["Lu","Ma","Mi","Ju"], "horas": [1,1,1,1], "creditos": 4})
    bloques.append({"dias": ["Lu","Mi"], "horas": [2,2], "creditos": 4})
    bloques.append({"dias": ["Ma","Ju"], "horas": [2,2], "creditos": 4})
    return bloques

def calcular_creditos_pagables(creditos_base, n_estudiantes):
    if n_estudiantes >= 85: return creditos_base + 3
    elif n_estudiantes >= 60: return creditos_base + 1.5
    else: return creditos_base

def es_horario_valido_en_zona(dia, hora_inicio_str, duracion, zona_config):
    ini = a_minutos(hora_inicio_str)
    fin = ini + int(duracion * 60)
    restricciones = zona_config['restricciones']
    if dia in restricciones:
        for r_ini, r_fin in restricciones[dia]:
            r_ini_m = a_minutos(r_ini)
            r_fin_m = a_minutos(r_fin)
            if not (fin <= r_ini_m or ini >= r_fin_m): return False
    return True

# ========================================================
# 3. ALGORITMO GENÉTICO
# ========================================================

class ClaseGene:
    def __init__(self, curso_data, bloque, hora_inicio, salon):
        self.curso_data = curso_data
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.salon = salon
        candidatos = curso_data['candidatos']
        self.prof_asignado = random.choice(candidatos) if candidatos else "Staff"

class IndividuoHorario:
    def __init__(self, genes=None):
        self.genes = genes if genes else []
        self.fitness = 0.0
        self.hard_conflicts = 0
        self.prof_stats = {}

    def calcular_fitness(self, profesores_db):
        PENALTY_HARD = 10000
        PENALTY_LOAD = 5000
        SCORE = 0
        CONFLICTS = 0
        carga_actual = {k: 0 for k in profesores_db.keys()}
        ocupacion_profesor = {}
        ocupacion_salon = {}
        
        for gen in self.genes:
            prof_nom = gen.prof_asignado
            prof_info = profesores_db.get(prof_nom, {})
            
            # Carga
            creditos_pago = calcular_creditos_pagables(gen.curso_data['creditos'], gen.curso_data['cupo'])
            if prof_nom in carga_actual: carga_actual[prof_nom] += creditos_pago
            
            # Restricciones
            if gen.curso_data['cupo'] >= 85 and prof_info.get('acepta_grandes', 0) == 0:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
            
            # Preferencia horaria (Suave)
            h_min = a_minutos(gen.hora_inicio)
            h_fin = h_min + int(max(gen.bloque['horas']) * 60)
            p_ini = a_minutos(prof_info.get('hora_entrada', '07:00'))
            p_fin = a_minutos(prof_info.get('hora_salida', '20:00'))
            if h_min < p_ini or h_fin > p_fin: SCORE -= 500

            # Días Deseados (Suave)
            dias_des = prof_info.get('dias_deseados', [])
            coincidencias = sum(1 for d in gen.bloque['dias'] if d in dias_des)
            SCORE += (coincidencias * 20)

            # Prioridad 1
            if gen.curso_data['candidatos'] and prof_nom == gen.curso_data['candidatos'][0]:
                SCORE += 100

            # Conflictos Duros
            for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                ini = a_minutos(gen.hora_inicio)
                fin = ini + int(duracion * 60)
                
                # Profe
                k_p = (prof_nom, dia)
                if k_p not in ocupacion_profesor: ocupacion_profesor[k_p] = []
                for (oi, of) in ocupacion_profesor[k_p]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1; break
                ocupacion_profesor[k_p].append((ini, fin))

                # Salon
                k_s = (gen.salon, dia)
                if k_s not in ocupacion_salon: ocupacion_salon[k_s] = []
                for (oi, of) in ocupacion_salon[k_s]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1; break
                ocupacion_salon[k_s].append((ini, fin))

        # Evaluar Cargas Globales
        for prof_nom, carga in carga_actual.items():
            info = profesores_db.get(prof_nom, {})
            if carga > info.get('carga_max', 12):
                SCORE -= PENALTY_LOAD * (carga - info.get('carga_max', 12))
                CONFLICTS += 1
            elif carga < info.get('carga_min', 0):
                SCORE -= 2000 * (info.get('carga_min', 0) - carga)
        
        self.fitness = SCORE
        self.hard_conflicts = CONFLICTS
        self.prof_stats = carga_actual
        return self.fitness

class AlgoritmoGenetico:
    def __init__(self, cursos_demanda, profesores_db, zona_config, salones, pop_size, mutation_rate):
        self.cursos_demanda = cursos_demanda
        self.profesores_db = profesores_db
        self.zona_config = zona_config
        self.salones = salones
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.bloques_ref = generar_bloques_horarios()

    def _crear_gen_aleatorio(self, curso):
        bloques_validos = [b for b in self.bloques_ref if b['creditos'] == curso['creditos']]
        if not bloques_validos: bloques_validos = self.bloques_ref[:1]
        
        for _ in range(20):
            bloque = random.choice(bloques_validos)
            hora = random.choice(self.zona_config['horarios_inicio'])
            salon = random.choice(self.salones)
            valido = True
            for d, h in zip(bloque['dias'], bloque['horas']):
                if not es_horario_valido_en_zona(d, hora, h, self.zona_config):
                    valido = False; break
            if valido: return ClaseGene(curso, bloque, hora, salon)
        return ClaseGene(curso, bloques_validos[0], self.zona_config['horarios_inicio'][0], self.salones[0])

    def inicializar(self):
        self.population = []
        for _ in range(self.pop_size):
            genes = [self._crear_gen_aleatorio(c) for c in self.cursos_demanda]
            ind = IndividuoHorario(genes)
            ind.calcular_fitness(self.profesores_db)
            self.population.append(ind)

    def evolucionar(self, generaciones, progress_bar, status_text):
        self.inicializar()
        mejor_historico = max(self.population, key=lambda x: x.fitness)
        
        for g in range(generaciones):
            nueva_pop = []
            mejor_actual = max(self.population, key=lambda x: x.fitness)
            if mejor_actual.fitness > mejor_historico.fitness:
                mejor_historico = copy.deepcopy(mejor_actual)
            nueva_pop.append(mejor_historico)
            
            while len(nueva_pop) < self.pop_size:
                p1 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                p2 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                genes_hijo = []
                for g1, g2 in zip(p1.genes, p2.genes):
                    genes_hijo.append(copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2))
                hijo = IndividuoHorario(genes_hijo)
                
                for gen in hijo.genes:
                    if random.random() < self.mutation_rate:
                        if random.random() < 0.5 and gen.curso_data['candidatos']:
                            gen.prof_asignado = random.choice(gen.curso_data['candidatos'])
                        else:
                            bloques_validos = [b for b in self.bloques_ref if b['creditos'] == gen.curso_data['creditos']]
                            if bloques_validos:
                                gen.bloque = random.choice(bloques_validos)
                                gen.hora_inicio = random.choice(self.zona_config['horarios_inicio'])
                                gen.salon = random.choice(self.salones)
                
                hijo.calcular_fitness(self.profesores_db)
                nueva_pop.append(hijo)
            self.population = nueva_pop
            progress_bar.progress((g+1)/generaciones)
            if g % 10 == 0: status_text.text(f"Generación {g+1}/{generaciones} | Fitness: {mejor_historico.fitness:.0f} | Conflictos: {mejor_historico.hard_conflicts}")
            
        return mejor_historico

def procesar_excel_completo(file):
    try:
        xls = pd.ExcelFile(file)
        df_cursos = pd.read_excel(xls, 'Cursos')
        cursos_lista = []
        for _, row in df_cursos.iterrows():
            cands = str(row.get('Candidatos', 'Staff')).split(',')
            cands = [c.strip() for c in cands if c.strip()]
            cursos_lista.append({
                'codigo': str(row.get('Codigo', 'UNK')),
                'nombre': str(row.get('Nombre', 'Curso')),
                'creditos': int(row.get('Creditos', 3)),
                'cupo': int(row.get('Cupo', 30)),
                'candidatos': cands
            })
            
        df_profes = pd.read_excel(xls, 'Profesores')
        profes_db = {}
        for _, row in df_profes.iterrows():
            nombre = str(row.get('Nombre', 'Unknown')).strip()
            dias_raw = str(row.get('Dias_Deseados', '')).replace(';',',')
            dias_list = [d.strip() for d in dias_raw.split(',') if d.strip()]
            profes_db[nombre] = {
                'carga_min': float(row.get('Carga_Min', 0)),
                'carga_max': float(row.get('Carga_Max', 12)),
                'acepta_grandes': int(row.get('Acepta_Grandes', 0)),
                'hora_entrada': str(row.get('Hora_Entrada', '07:00')),
                'hora_salida': str(row.get('Hora_Salida', '20:00')),
                'dias_deseados': dias_list
            }
        return cursos_lista, profes_db
    except Exception as e: return None, str(e)

# ========================================================
# 4. INTERFAZ GRÁFICA PRINCIPAL
# ========================================================

def main():
    # Sidebar: Panel de Control
    with st.sidebar:
        st.title("🎛️ Panel de Control")
        st.markdown("---")
        
        st.subheader("1. Carga de Datos")
        file = st.file_uploader("Archivo Excel (.xlsx)", type=['xlsx'])
        if st.button("Descargar Plantilla Ejemplo"):
            st.info("Función placeholder para descargar excel ejemplo.")
        
        st.subheader("2. Configuración")
        zona = st.selectbox("Zona del Campus", ["Central", "Periférica"])
        
        with st.expander("⚙️ Parámetros Avanzados AG"):
            pop = st.slider("Población", 50, 500, 100)
            gen = st.slider("Generaciones", 50, 1000, 150)
            mut = st.slider("Tasa Mutación", 0.0, 0.5, 0.15)
        
        st.markdown("---")
        st.caption("UPRM Timetabling System v3.0")

    # Área Principal
    st.title("🎓 Sistema de Programación Académica UPRM")
    st.markdown("Optimización inteligente de horarios basada en **Carga Docente** y **Preferencias**.")
    st.markdown("---")

    # Inicializar Session State
    if 'data_cursos' not in st.session_state: st.session_state.data_cursos = None
    if 'data_profes' not in st.session_state: st.session_state.data_profes = None
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    # Lógica de Carga
    if file:
        if st.session_state.data_cursos is None:
            cursos, profes = procesar_excel_completo(file)
            if cursos:
                st.session_state.data_cursos = cursos
                st.session_state.data_profes = profes
                st.toast("✅ Archivo cargado y procesado correctamente", icon="📂")
            else:
                st.error(f"Error en archivo: {profes}")

    # Si no hay datos, mostrar bienvenida
    if st.session_state.data_cursos is None:
        st.info("👈 Por favor, sube el archivo Excel de planificación en el menú lateral para comenzar.")
        st.markdown("""
            #### ¿Cómo funciona?
            1. Sube tu Excel con pestañas `Cursos` y `Profesores`.
            2. Ajusta la Zona (Central/Periférica).
            3. Ejecuta el Algoritmo Genético.
            4. Visualiza horarios y análisis de carga docente en tiempo real.
        """)
        return

    # Si hay datos, mostrar Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cursos a Programar", len(st.session_state.data_cursos))
    col2.metric("Profesores Disponibles", len(st.session_state.data_profes))
    col3.metric("Zona Seleccionada", zona)
    col4.metric("Estado", "Listo para Ejecutar" if not st.session_state.resultado else "Completado", 
                delta="Esperando..." if not st.session_state.resultado else "Finalizado", delta_color="normal")

    # Botón de Ejecución
    if st.button("🚀 Iniciar Optimización de Horarios", type="primary"):
        with st.status("Ejecutando Algoritmo Genético...", expanded=True) as status:
            st.write("🧬 Inicializando población...")
            prog_bar = st.progress(0)
            status_text = st.empty()
            
            ga = AlgoritmoGenetico(
                st.session_state.data_cursos,
                st.session_state.data_profes,
                ZonaConfig.CENTRAL if zona == "Central" else ZonaConfig.PERIFERICA,
                MATEMATICAS_SALONES_FIJOS,
                pop, mut
            )
            
            start_t = time.time()
            mejor = ga.evolucionar(gen, prog_bar, status_text)
            st.session_state.resultado = mejor
            
            status.update(label="✅ Optimización Finalizada", state="complete", expanded=False)
        st.balloons()
        st.rerun()

    # Visualización de Resultados
    if st.session_state.resultado:
        res = st.session_state.resultado
        st.divider()
        
        # Métricas de Resultado
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Fitness Score", f"{res.fitness:.0f}")
        kpi2.metric("Conflictos Duros", res.hard_conflicts, delta="-0 es ideal", delta_color="inverse")
        
        # Crear DataFrame de Resultados
        rows = []
        for g in res.genes:
            cred_reales = calcular_creditos_pagables(g.curso_data['creditos'], g.curso_data['cupo'])
            rows.append({
                "Curso": g.curso_data['codigo'],
                "Nombre": g.curso_data['nombre'],
                "Profesor": g.prof_asignado,
                "Cupo": g.curso_data['cupo'],
                "Créditos Pago": cred_reales,
                "Días": "".join(g.bloque['dias']),
                "Horario": f"{g.hora_inicio} - {a_minutos(g.hora_inicio) + int(max(g.bloque['horas'])*60)//60}:{int(max(g.bloque['horas'])*60)%60:02d}",
                "Salón": g.salon
            })
        df_res = pd.DataFrame(rows)

        # Tabs de visualización profesional
        tab_h, tab_c, tab_m, tab_d = st.tabs(["📅 Horario Detallado", "⚖️ Carga Docente", "🧩 Matriz Visual", "📥 Exportar"])

        with tab_h:
            st.subheader("Horario General")
            filtro_prof = st.multiselect("Filtrar por Profesor", options=df_res["Profesor"].unique())
            df_show = df_res if not filtro_prof else df_res[df_res["Profesor"].isin(filtro_prof)]
            st.dataframe(df_show, use_container_width=True, hide_index=True)

        with tab_c:
            st.subheader("Análisis de Carga Académica")
            load_data = []
            for prof, data in st.session_state.data_profes.items():
                carga_real = res.prof_stats.get(prof, 0)
                status = "Optimo"
                if carga_real < data['carga_min']: status = "Subcarga"
                if carga_real > data['carga_max']: status = "Sobrecarga"
                
                load_data.append({
                    "Profesor": prof,
                    "Carga Real": carga_real,
                    "Mínimo": data['carga_min'],
                    "Máximo": data['carga_max'],
                    "Estado": status
                })
            df_load = pd.DataFrame(load_data)
            
            # Gráfico de Barras con Plotly
            fig = px.bar(df_load, x="Profesor", y="Carga Real", color="Estado",
                         color_discrete_map={"Optimo": "#2ecc71", "Subcarga": "#f1c40f", "Sobrecarga": "#e74c3c"},
                         title="Carga Real vs Límites")
            
            # Añadir líneas de referencia visual (ejemplo con promedio, o markers)
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Ver tabla de datos de carga"):
                st.dataframe(df_load, use_container_width=True)

        with tab_m:
            st.subheader("Matriz de Ocupación")
            try:
                pivot = df_res.pivot_table(index="Horario", columns="Días", values="Curso", aggfunc=lambda x: ' '.join(x))
                st.dataframe(pivot, use_container_width=True)
            except:
                st.warning("Datos insuficientes para generar matriz.")

        with tab_d:
            st.subheader("Descargar Resultados")
            col_d1, col_d2 = st.columns(2)
            csv = df_res.to_csv(index=False).encode('utf-8')
            col_d1.download_button("📄 Descargar Horario (CSV)", csv, "horario_final.csv", "text/csv", type="primary")
            
            csv_load = df_load.to_csv(index=False).encode('utf-8')
            col_d2.download_button("📊 Descargar Reporte de Cargas (CSV)", csv_load, "reporte_cargas.csv", "text/csv")

if __name__ == "__main__":
    main()
