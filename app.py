import streamlit as st
import pandas as pd
import random
import copy
import time
import math
import plotly.express as px
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

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    h1, h2, h3 { color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

# ========================================================
# 2. LÓGICA DEL NEGOCIO
# ========================================================

MATEMATICAS_SALONES_FIJOS = ["M 102", "M 104", "M 203", "M 205", "M 316", "M 317", "M 402", "M 404"]

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
    def __init__(self, curso_data, bloque, hora_inicio, salon, seccion_num):
        self.curso_data = curso_data
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.salon = salon
        self.seccion_num = seccion_num 
        
        # Selección inicial de profesor
        candidatos = curso_data['candidatos']
        self.prof_asignado = random.choice(candidatos) if candidatos else "Staff"

class IndividuoHorario:
    def __init__(self, genes=None):
        self.genes = genes if genes else []
        self.fitness = 0.0
        self.hard_conflicts = 0
        self.prof_stats = {}
        self.conflict_details = []

    def calcular_fitness(self, profesores_db, preferencias_manuales):
        # PENALIZACIONES
        PENALTY_HARD = 10000     # Choques físicos (salón, profesor, hora prohibida)
        PENALTY_PREF = 10000     # AHORA ES HARD: Violar preferencia de profesor
        PENALTY_LOAD = 5000      # Carga académica inválida
        
        SCORE = 0
        CONFLICTS = 0
        self.conflict_details = []
        
        carga_actual = {k: 0 for k in profesores_db.keys()}
        ocupacion_profesor = {}
        ocupacion_salon = {}
        
        for gen in self.genes:
            prof_nom = gen.prof_asignado
            prof_info_static = profesores_db.get(prof_nom, {})
            # Preferencias dinámicas (Desde la UI)
            prof_prefs = preferencias_manuales.get(prof_nom, {
                'dias_deseados': ['Lu','Ma','Mi','Ju','Vi'], 
                'hora_entrada': '07:00', 
                'hora_salida': '20:00'
            })
            
            # 1. Carga
            creditos_pago = calcular_creditos_pagables(gen.curso_data['creditos'], gen.curso_data['cupo'])
            if prof_nom in carga_actual: carga_actual[prof_nom] += creditos_pago
            
            # 2. Restricción C1: Secciones Grandes
            if gen.curso_data['cupo'] >= 85 and prof_info_static.get('acepta_grandes', 0) == 0:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
                self.conflict_details.append(f"{prof_nom} no acepta grupos grandes ({gen.curso_data['codigo']})")
            
            # 3. PREFERENCIAS OBLIGATORIAS (AHORA SON HARD)
            h_min = a_minutos(gen.hora_inicio)
            h_fin = h_min + int(max(gen.bloque['horas']) * 60)
            p_ini = a_minutos(prof_prefs.get('hora_entrada', '07:00'))
            p_fin = a_minutos(prof_prefs.get('hora_salida', '20:00'))
            
            # Horario Entrada/Salida
            if h_min < p_ini or h_fin > p_fin: 
                SCORE -= PENALTY_PREF
                CONFLICTS += 1 # Cuenta como conflicto
                self.conflict_details.append(f"{prof_nom} fuera de horario preferido ({gen.hora_inicio})")

            # Días Deseados
            dias_des = prof_prefs.get('dias_deseados', [])
            # Si ALGÚN día del bloque NO está en los deseados -> Conflicto
            dias_invalidos = [d for d in gen.bloque['dias'] if d not in dias_des]
            if dias_invalidos:
                SCORE -= PENALTY_PREF
                CONFLICTS += 1
                self.conflict_details.append(f"{prof_nom} no quiere enseñar en {dias_invalidos}")

            # 4. Prioridad 1 Candidato (Esto sigue siendo un bonus soft)
            if gen.curso_data['candidatos'] and prof_nom == gen.curso_data['candidatos'][0]:
                SCORE += 100

            # 5. Conflictos Duros (Solapamientos)
            for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                ini = a_minutos(gen.hora_inicio)
                fin = ini + int(duracion * 60)
                
                # Profe Doble Reserva
                k_p = (prof_nom, dia)
                if k_p not in ocupacion_profesor: ocupacion_profesor[k_p] = []
                for (oi, of) in ocupacion_profesor[k_p]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1
                        self.conflict_details.append(f"Choque horario Profesor {prof_nom} en {dia}")
                        break
                ocupacion_profesor[k_p].append((ini, fin))

                # Salon Doble Reserva
                k_s = (gen.salon, dia)
                if k_s not in ocupacion_salon: ocupacion_salon[k_s] = []
                for (oi, of) in ocupacion_salon[k_s]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1
                        self.conflict_details.append(f"Choque Salón {gen.salon} en {dia} ({gen.curso_data['codigo']})")
                        break
                ocupacion_salon[k_s].append((ini, fin))

        # 6. Evaluar Cargas Globales
        for prof_nom, carga in carga_actual.items():
            info = profesores_db.get(prof_nom, {})
            if carga > info.get('carga_max', 12):
                SCORE -= PENALTY_LOAD * (carga - info.get('carga_max', 12))
                CONFLICTS += 1
                self.conflict_details.append(f"Sobrecarga {prof_nom}: {carga}/{info.get('carga_max', 12)}")
            elif carga < info.get('carga_min', 0):
                SCORE -= 2000 * (info.get('carga_min', 0) - carga)
        
        self.fitness = SCORE
        self.hard_conflicts = CONFLICTS
        self.prof_stats = carga_actual
        return self.fitness

class AlgoritmoGenetico:
    def __init__(self, cursos_expandidos, profesores_db, pref_manuales, zona_config, salones, pop_size, mutation_rate):
        self.cursos_demanda = cursos_expandidos
        self.profesores_db = profesores_db
        self.pref_manuales = pref_manuales
        self.zona_config = zona_config
        self.salones = salones
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.bloques_ref = generar_bloques_horarios()

    def _buscar_slot_valido(self, curso_dict):
        """Intenta exhaustivamente encontrar un slot sin conflictos basicos de zona"""
        curso = curso_dict['data']
        seccion = curso_dict['seccion']
        
        bloques_validos = [b for b in self.bloques_ref if b['creditos'] == curso['creditos']]
        if not bloques_validos: bloques_validos = self.bloques_ref[:1]
        
        # Mezclar opciones para aleatoriedad
        random.shuffle(bloques_validos)
        horarios = list(self.zona_config['horarios_inicio'])
        random.shuffle(horarios)
        salones = list(self.salones)
        random.shuffle(salones)
        
        # Búsqueda Greedy aleatorizada (Intenta hasta encontrar uno que no viole zona)
        for bloque in bloques_validos:
            for hora in horarios:
                # Validar zona primero
                valido_zona = True
                for d, h in zip(bloque['dias'], bloque['horas']):
                    if not es_horario_valido_en_zona(d, hora, h, self.zona_config):
                        valido_zona = False; break
                
                if valido_zona:
                    # Slot candidato encontrado, asignamos un salón al azar
                    return ClaseGene(curso, bloque, hora, salones[0], seccion)
        
        # Fallback si todo falla
        return ClaseGene(curso, bloques_validos[0], horarios[0], salones[0], seccion)

    def inicializar(self):
        self.population = []
        for _ in range(self.pop_size):
            # Usar búsqueda inteligente en lugar de puro random
            genes = [self._buscar_slot_valido(c) for c in self.cursos_demanda]
            ind = IndividuoHorario(genes)
            ind.calcular_fitness(self.profesores_db, self.pref_manuales)
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
                
                # Mutación más agresiva para salir de conflictos
                for i in range(len(hijo.genes)):
                    if random.random() < self.mutation_rate:
                        gen = hijo.genes[i]
                        # Estrategia: Re-generar slot completamente
                        if random.random() < 0.6: # 60% prob de cambiar tiempo/lugar
                            bloques_validos = [b for b in self.bloques_ref if b['creditos'] == gen.curso_data['creditos']]
                            if bloques_validos:
                                gen.bloque = random.choice(bloques_validos)
                                gen.hora_inicio = random.choice(self.zona_config['horarios_inicio'])
                                gen.salon = random.choice(self.salones)
                        else: # 40% prob de cambiar profe
                            if gen.curso_data['candidatos']:
                                gen.prof_asignado = random.choice(gen.curso_data['candidatos'])
                
                hijo.calcular_fitness(self.profesores_db, self.pref_manuales)
                nueva_pop.append(hijo)
            
            self.population = nueva_pop
            progress_bar.progress((g+1)/generaciones)
            if g % 5 == 0: 
                status_text.text(f"Gen {g+1} | Conflictos Actuales: {mejor_historico.hard_conflicts}")
            
        return mejor_historico

def procesar_excel_agrupado(file):
    try:
        xls = pd.ExcelFile(file)
        # 1. Cursos
        df_cursos = pd.read_excel(xls, 'Cursos')
        cursos_expandidos = []
        
        cols_map = {'CODIGO': 'codigo', 'NOMBRE': 'nombre', 'CREDITOS': 'creditos', 'TOTAL_MATRICULA': 'total_estudiantes', 'CUPO_SECCION': 'cupo', 'CANDIDATOS': 'candidatos'}
        
        for _, row in df_cursos.iterrows():
            data_row = {}
            for k, v in cols_map.items():
                for c in df_cursos.columns:
                    if k in str(c).upper(): data_row[v] = row[c]; break
            
            cands = str(data_row.get('candidatos', 'Staff')).split(',')
            cands = [c.strip() for c in cands if c.strip()]
            
            total_est = int(data_row.get('total_estudiantes', 0))
            cupo_max = int(data_row.get('cupo', 30))
            if cupo_max <= 0: cupo_max = 30
            
            num_secciones = math.ceil(total_est / cupo_max)
            if num_secciones == 0 and total_est > 0: num_secciones = 1
            if num_secciones == 0: continue 

            obj_curso = {
                'codigo': str(data_row.get('codigo', 'UNK')),
                'nombre': str(data_row.get('nombre', 'Curso')),
                'creditos': int(data_row.get('creditos', 3)),
                'cupo': cupo_max,
                'candidatos': cands
            }
            
            for i in range(num_secciones):
                cursos_expandidos.append({'data': obj_curso, 'seccion': f"{i+1:03d}"})

        # 2. Profesores
        df_profes = pd.read_excel(xls, 'Profesores')
        profes_db = {}
        for _, row in df_profes.iterrows():
            nombre = str(row.get('Nombre', 'Unknown')).strip()
            profes_db[nombre] = {
                'carga_min': float(row.get('Carga_Min', 0)),
                'carga_max': float(row.get('Carga_Max', 12)),
                'acepta_grandes': int(row.get('Acepta_Grandes', 0))
            }
        return cursos_expandidos, profes_db
    except Exception as e: return None, str(e)

# ========================================================
# 4. INTERFAZ GRÁFICA PRINCIPAL
# ========================================================

def main():
    if 'pref_manuales' not in st.session_state: st.session_state.pref_manuales = {}
    if 'data_cursos' not in st.session_state: st.session_state.data_cursos = None
    if 'data_profes' not in st.session_state: st.session_state.data_profes = None
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    # Sidebar
    with st.sidebar:
        st.title("🎛️ Panel de Control")
        st.markdown("---")
        
        st.subheader("1. Carga de Datos")
        file = st.file_uploader("Archivo Excel (.xlsx)", type=['xlsx'])
        
        st.subheader("2. Configuración")
        zona = st.selectbox("Zona del Campus", ["Central", "Periférica"])
        
        with st.expander("⚙️ Parámetros Avanzados"):
            pop = st.slider("Población", 50, 500, 100)
            gen = st.slider("Generaciones", 50, 1000, 150)
            mut = st.slider("Mutación", 0.0, 0.5, 0.2)
        
        st.markdown("---")
        
        if st.session_state.data_profes:
            st.subheader("🕒 Preferencias (Obligatorias)")
            prof_list = list(st.session_state.data_profes.keys())
            prof_sel = st.selectbox("Editar Profesor:", prof_list)
            
            curr_pref = st.session_state.pref_manuales.get(prof_sel, {})
            
            dias = st.multiselect("Días Permitidos", ["Lu","Ma","Mi","Ju","Vi"], 
                                default=curr_pref.get('dias_deseados', ["Lu","Ma","Mi","Ju","Vi"]))
            
            c1, c2 = st.columns(2)
            h_ini = c1.time_input("Hora Entrada", 
                                value=datetime.strptime(curr_pref.get('hora_entrada', "07:00"), "%H:%M").time())
            h_fin = c2.time_input("Hora Salida", 
                                value=datetime.strptime(curr_pref.get('hora_salida', "20:00"), "%H:%M").time())
            
            st.session_state.pref_manuales[prof_sel] = {
                'dias_deseados': dias,
                'hora_entrada': h_ini.strftime("%H:%M"),
                'hora_salida': h_fin.strftime("%H:%M")
            }
            st.info(f"Configurado: {prof_sel}")

    # Main Area
    st.title("🎓 Sistema de Programación Académica")
    st.markdown("Generación automática de secciones y optimización de horarios.")
    st.markdown("---")

    if file:
        if st.button("Procesar Archivo Excel", key="load_btn"):
            cursos, profes = procesar_excel_agrupado(file)
            if cursos:
                st.session_state.data_cursos = cursos
                st.session_state.data_profes = profes
                # Init defaults
                for p in profes:
                    if p not in st.session_state.pref_manuales:
                        st.session_state.pref_manuales[p] = {
                            'dias_deseados': ["Lu","Ma","Mi","Ju","Vi"],
                            'hora_entrada': "07:00", 'hora_salida': "20:00"
                        }
                st.rerun()
            else:
                st.error(f"Error: {profes}")

    if st.session_state.data_cursos is None:
        st.info("👈 Sube el archivo Excel para comenzar.")
        return

    # Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Secciones a Crear", len(st.session_state.data_cursos))
    col2.metric("Profesores Activos", len(st.session_state.data_profes))
    col3.metric("Zona", zona)
    col4.metric("Estado", "Listo" if not st.session_state.resultado else "Completado")

    if st.button("🚀 Iniciar Optimización", type="primary"):
        with st.status("Optimizando Horarios (Modo Estricto)...", expanded=True) as status:
            prog = st.progress(0)
            text = st.empty()
            
            ga = AlgoritmoGenetico(
                st.session_state.data_cursos,
                st.session_state.data_profes,
                st.session_state.pref_manuales,
                ZonaConfig.CENTRAL if zona == "Central" else ZonaConfig.PERIFERICA,
                MATEMATICAS_SALONES_FIJOS,
                pop, mut
            )
            
            start = time.time()
            mejor = ga.evolucionar(gen, prog, text)
            st.session_state.resultado = mejor
            status.update(label="✅ Finalizado", state="complete", expanded=False)
        st.balloons()

    if st.session_state.resultado:
        res = st.session_state.resultado
        st.divider()
        
        k1, k2 = st.columns(2)
        k1.metric("Score Calidad", int(res.fitness))
        k2.metric("Conflictos Totales", res.hard_conflicts, delta="-0 es ideal", delta_color="inverse")
        
        if res.hard_conflicts > 0:
            st.error(f"⚠️ Se encontraron {res.hard_conflicts} conflictos. Revisa la pestaña 'Reporte Conflictos'.")
        else:
            st.success("✅ ¡Horario Perfecto! Cero conflictos detectados.")
        
        rows = []
        for g in res.genes:
            cred_pago = calcular_creditos_pagables(g.curso_data['creditos'], g.curso_data['cupo'])
            rows.append({
                "Curso": g.curso_data['codigo'],
                "Sección": g.seccion_num,
                "Nombre": g.curso_data['nombre'],
                "Profesor": g.prof_asignado,
                "Cupo": g.curso_data['cupo'],
                "Créditos Pago": cred_pago,
                "Días": "".join(g.bloque['dias']),
                "Horario": f"{g.hora_inicio} - {a_minutos(g.hora_inicio)+int(max(g.bloque['horas'])*60)//60}:{int(max(g.bloque['horas'])*60)%60:02d}",
                "Salón": g.salon
            })
        df_res = pd.DataFrame(rows)
        
        t1, t2, t3, t4 = st.tabs(["📅 Horario", "⚖️ Cargas", "🚨 Reporte Conflictos", "📥 Exportar"])
        
        with t1:
            st.dataframe(df_res, use_container_width=True)
            
        with t2:
            load_data = []
            for p, d in st.session_state.data_profes.items():
                real = res.prof_stats.get(p, 0)
                estado = "OK"
                if real < d['carga_min']: estado = "Subcarga"
                if real > d['carga_max']: estado = "Sobrecarga"
                load_data.append({"Profesor": p, "Carga Real": real, "Min": d['carga_min'], "Max": d['carga_max'], "Estado": estado})
            
            df_l = pd.DataFrame(load_data)
            fig = px.bar(df_l, x="Profesor", y="Carga Real", color="Estado", 
                         color_discrete_map={"OK":"#2ecc71", "Subcarga":"#f1c40f", "Sobrecarga":"#e74c3c"})
            st.plotly_chart(fig, use_container_width=True)
        
        with t3:
            if res.conflict_details:
                st.write("Detalle de problemas encontrados:")
                for c in res.conflict_details:
                    st.warning(c)
            else:
                st.info("No hay conflictos que reportar.")
            
        with t4:
            st.download_button("Descargar CSV", df_res.to_csv(index=False).encode('utf-8'), "horario.csv")

if __name__ == "__main__":
    main()
