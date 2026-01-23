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

def a_minutos(hhmm):
    try:
        if isinstance(hhmm, str):
            h, m = map(int, hhmm.strip().split(":"))
            return h * 60 + m
        return 0
    except: return 0

class ZonaConfig:
    # Definición estricta de HLU
    CENTRAL = {
        "nombre": "Zona Central",
        "horarios_inicio": ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30"],
        "bloqueo_hlu": {
            "dias": ["Ma", "Ju"],
            "inicio": a_minutos("10:30"),
            "fin": a_minutos("12:30")
        }
    }
    PERIFERICA = {
        "nombre": "Zona Periférica",
        "horarios_inicio": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"],
        "bloqueo_hlu": {
            "dias": ["Ma", "Ju"], # Según requerimiento usuario: periferica tambien Ma/Ju 10-12
            "inicio": a_minutos("10:00"),
            "fin": a_minutos("12:00")
        }
    }

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
    
    # Verificación HLU (Hora Libre Universal)
    hlu = zona_config['bloqueo_hlu']
    if dia in hlu['dias']:
        # Si la clase termina después de que empieza la HLU Y empieza antes de que termine la HLU
        # (Intersección de intervalos)
        if not (fin <= hlu['inicio'] or ini >= hlu['fin']):
            return False
            
    return True

# ========================================================
# 3. ALGORITMO GENÉTICO
# ========================================================

class ClaseGene:
    def __init__(self, curso_data, bloque, hora_inicio, salon_obj, seccion_num):
        self.curso_data = curso_data
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.salon_obj = salon_obj # Objeto completo del salón (codigo, cap, tipo)
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
        PENALTY_HARD = 10000     
        PENALTY_PREF = 10000     
        PENALTY_LOAD = 5000      
        
        SCORE = 0
        CONFLICTS = 0
        self.conflict_details = []
        
        carga_actual = {k: 0 for k in profesores_db.keys()}
        ocupacion_profesor = {}
        ocupacion_salon = {}
        
        for gen in self.genes:
            prof_nom = gen.prof_asignado
            prof_info_static = profesores_db.get(prof_nom, {})
            prof_prefs = preferencias_manuales.get(prof_nom, {
                'dias_deseados': ['Lu','Ma','Mi','Ju','Vi'], 
                'hora_entrada': '07:00', 'hora_salida': '20:00'
            })
            
            # --- VALIDACIONES DE SALÓN (NUEVO) ---
            # 1. Tipo de Salón Incorrecto
            if gen.curso_data.get('tipo_salon', 'General') != gen.salon_obj['tipo']:
                SCORE -= PENALTY_HARD
                CONFLICTS += 1
                self.conflict_details.append(f"Error Tipo Salón: {gen.curso_data['codigo']} requiere {gen.curso_data.get('tipo_salon')} pero se asignó {gen.salon_obj['tipo']}")

            # 2. Capacidad Insuficiente
            if gen.curso_data['cupo'] > gen.salon_obj['capacidad']:
                SCORE -= PENALTY_HARD
                CONFLICTS += 1
                self.conflict_details.append(f"Error Capacidad: {gen.curso_data['codigo']} ({gen.curso_data['cupo']}) no cabe en {gen.salon_obj['codigo']} ({gen.salon_obj['capacidad']})")

            # --- VALIDACIONES ANTERIORES ---
            # Carga
            creditos_pago = calcular_creditos_pagables(gen.curso_data['creditos'], gen.curso_data['cupo'])
            if prof_nom in carga_actual: carga_actual[prof_nom] += creditos_pago
            
            # Secciones Grandes
            if gen.curso_data['cupo'] >= 85 and prof_info_static.get('acepta_grandes', 0) == 0:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
            
            # Preferencias
            h_min = a_minutos(gen.hora_inicio)
            h_fin = h_min + int(max(gen.bloque['horas']) * 60)
            p_ini = a_minutos(prof_prefs.get('hora_entrada', '07:00'))
            p_fin = a_minutos(prof_prefs.get('hora_salida', '20:00'))
            
            if h_min < p_ini or h_fin > p_fin: 
                SCORE -= PENALTY_PREF; CONFLICTS += 1
            
            dias_des = prof_prefs.get('dias_deseados', [])
            if any(d not in dias_des for d in gen.bloque['dias']):
                SCORE -= PENALTY_PREF; CONFLICTS += 1

            if gen.curso_data['candidatos'] and prof_nom == gen.curso_data['candidatos'][0]:
                SCORE += 100

            # Conflictos Duros (Solapamientos)
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

                # Salon (Usando el ID del salón cargado del Excel)
                k_s = (gen.salon_obj['codigo'], dia)
                if k_s not in ocupacion_salon: ocupacion_salon[k_s] = []
                for (oi, of) in ocupacion_salon[k_s]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1; 
                        self.conflict_details.append(f"Choque Salón {gen.salon_obj['codigo']} en {dia}")
                        break
                ocupacion_salon[k_s].append((ini, fin))

        # Cargas Globales
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
    def __init__(self, cursos_expandidos, profesores_db, salones_db, pref_manuales, zona_config, pop_size, mutation_rate):
        self.cursos_demanda = cursos_expandidos
        self.profesores_db = profesores_db
        self.salones_db = salones_db # Lista de dicts: [{'codigo': 'M101', 'capacidad': 30, 'tipo': 'General'}]
        self.pref_manuales = pref_manuales
        self.zona_config = zona_config
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.bloques_ref = generar_bloques_horarios()

    def _get_salones_validos(self, curso):
        """Filtra salones por TIPO y CAPACIDAD antes de elegir"""
        tipo_req = curso.get('tipo_salon', 'General')
        cupo_req = curso['cupo']
        
        # Filtrar
        validos = [s for s in self.salones_db if s['tipo'] == tipo_req and s['capacidad'] >= cupo_req]
        
        # Si no hay ninguno, devolver todos (generará conflicto pero no crashea)
        if not validos:
            return self.salones_db
        return validos

    def _buscar_slot_inteligente(self, curso_dict):
        curso = curso_dict['data']
        seccion = curso_dict['seccion']
        
        bloques_validos = [b for b in self.bloques_ref if b['creditos'] == curso['creditos']]
        if not bloques_validos: bloques_validos = self.bloques_ref[:1]
        
        # Obtener salones compatibles
        salones_compatibles = self._get_salones_validos(curso)
        
        # Intentar encontrar configuración válida
        for _ in range(30): # 30 intentos
            bloque = random.choice(bloques_validos)
            hora = random.choice(self.zona_config['horarios_inicio'])
            salon = random.choice(salones_compatibles)
            
            # Validar HLU
            valido_zona = True
            for d, h in zip(bloque['dias'], bloque['horas']):
                if not es_horario_valido_en_zona(d, hora, h, self.zona_config):
                    valido_zona = False; break
            
            if valido_zona:
                return ClaseGene(curso, bloque, hora, salon, seccion)
        
        # Fallback
        return ClaseGene(curso, bloques_validos[0], self.zona_config['horarios_inicio'][0], salones_compatibles[0], seccion)

    def inicializar(self):
        self.population = []
        for _ in range(self.pop_size):
            genes = [self._buscar_slot_inteligente(c) for c in self.cursos_demanda]
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
                
                # Mutación
                for i in range(len(hijo.genes)):
                    if random.random() < self.mutation_rate:
                        gen = hijo.genes[i]
                        r = random.random()
                        
                        if r < 0.33: # Cambiar Slot (Tiempo)
                            bloques_validos = [b for b in self.bloques_ref if b['creditos'] == gen.curso_data['creditos']]
                            if bloques_validos:
                                gen.bloque = random.choice(bloques_validos)
                                gen.hora_inicio = random.choice(self.zona_config['horarios_inicio'])
                        
                        elif r < 0.66: # Cambiar Salón
                            salones_validos = self._get_salones_validos(gen.curso_data)
                            gen.salon_obj = random.choice(salones_validos)
                            
                        else: # Cambiar Profe
                            if gen.curso_data['candidatos']:
                                gen.prof_asignado = random.choice(gen.curso_data['candidatos'])
                
                hijo.calcular_fitness(self.profesores_db, self.pref_manuales)
                nueva_pop.append(hijo)
            
            self.population = nueva_pop
            progress_bar.progress((g+1)/generaciones)
            if g % 5 == 0: 
                status_text.text(f"Gen {g+1} | Conflictos: {mejor_historico.hard_conflicts}")
            
        return mejor_historico

def procesar_excel_agrupado(file):
    try:
        xls = pd.ExcelFile(file)
        
        # 1. Cursos
        df_cursos = pd.read_excel(xls, 'Cursos')
        cursos_expandidos = []
        cols_map = {'CODIGO': 'codigo', 'NOMBRE': 'nombre', 'CREDITOS': 'creditos', 'TOTAL_MATRICULA': 'total_estudiantes', 'CUPO_SECCION': 'cupo', 'CANDIDATOS': 'candidatos', 'TIPO_SALON': 'tipo_salon'}
        
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
                'candidatos': cands,
                'tipo_salon': str(data_row.get('tipo_salon', 'General')).strip() # Nuevo campo
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
            
        # 3. Salones (NUEVO)
        df_salones = pd.read_excel(xls, 'Salones')
        salones_db = []
        for _, row in df_salones.iterrows():
            salones_db.append({
                'codigo': str(row.get('CODIGO', 'GEN00')),
                'capacidad': int(row.get('CAPACIDAD', 30)),
                'tipo': str(row.get('TIPO', 'General')).strip()
            })
            
        return cursos_expandidos, profes_db, salones_db
    except Exception as e: return None, None, str(e)

# ========================================================
# 4. INTERFAZ GRÁFICA PRINCIPAL
# ========================================================

def main():
    if 'pref_manuales' not in st.session_state: st.session_state.pref_manuales = {}
    if 'data_cursos' not in st.session_state: st.session_state.data_cursos = None
    if 'data_profes' not in st.session_state: st.session_state.data_profes = None
    if 'data_salones' not in st.session_state: st.session_state.data_salones = None
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    # Sidebar
    with st.sidebar:
        st.title("🎛️ Panel de Control")
        st.markdown("---")
        
        st.subheader("1. Carga de Datos")
        file = st.file_uploader("Excel 3 Hojas (Cursos, Profesores, Salones)", type=['xlsx'])
        
        st.subheader("2. Configuración")
        zona = st.selectbox("Zona del Campus", ["Central", "Periférica"])
        
        with st.expander("⚙️ Parámetros Avanzados"):
            pop = st.slider("Población", 50, 500, 150)
            gen = st.slider("Generaciones", 50, 1000, 200)
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
    
    # Info de HLU
    if zona == "Central":
        st.warning("⚠️ **HLU Activa:** No habrá clases Martes/Jueves 10:30-12:30")
    else:
        st.warning("⚠️ **HLU Activa:** No habrá clases Martes/Jueves 10:00-12:00")

    if file:
        if st.button("Procesar Archivo Excel", key="load_btn"):
            cursos, profes, salones = procesar_excel_agrupado(file)
            if cursos and salones:
                st.session_state.data_cursos = cursos
                st.session_state.data_profes = profes
                st.session_state.data_salones = salones
                # Init defaults
                for p in profes:
                    if p not in st.session_state.pref_manuales:
                        st.session_state.pref_manuales[p] = {
                            'dias_deseados': ["Lu","Ma","Mi","Ju","Vi"],
                            'hora_entrada': "07:00", 'hora_salida': "20:00"
                        }
                st.rerun()
            else:
                st.error(f"Error procesando archivo: {salones}")

    if st.session_state.data_cursos is None:
        st.info("👈 Sube el archivo Excel para comenzar (Asegúrate de tener la hoja 'Salones').")
        return

    # Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Secciones a Crear", len(st.session_state.data_cursos))
    col2.metric("Profesores Activos", len(st.session_state.data_profes))
    col3.metric("Salones Disponibles", len(st.session_state.data_salones))
    col4.metric("Estado", "Listo" if not st.session_state.resultado else "Completado")

    if st.button("🚀 Iniciar Optimización", type="primary"):
        with st.status("Optimizando Horarios (Modo Estricto)...", expanded=True) as status:
            prog = st.progress(0)
            text = st.empty()
            
            ga = AlgoritmoGenetico(
                st.session_state.data_cursos,
                st.session_state.data_profes,
                st.session_state.data_salones,
                st.session_state.pref_manuales,
                ZonaConfig.CENTRAL if zona == "Central" else ZonaConfig.PERIFERICA,
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
                "Salón": g.salon_obj['codigo'],
                "Tipo Salón": g.salon_obj['tipo']
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
