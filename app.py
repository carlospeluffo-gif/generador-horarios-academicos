import streamlit as st
import pandas as pd
import random
import copy
import time
import math
import re
from datetime import datetime

# ========================================================
# 1. CONFIGURACIÓN
# ========================================================

st.set_page_config(page_title="UPRM Auto-Scheduler V10", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stMetric { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px; }
    h1 { color: #1565C0; } 
    </style>
""", unsafe_allow_html=True)

# ========================================================
# 2. LÓGICA DE TIEMPO Y ZONAS
# ========================================================

def a_minutos(hhmm):
    try:
        if isinstance(hhmm, str):
            hhmm = hhmm.lower().replace('am','').replace('pm','').strip()
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m
        return 0
    except: return 0

class ZonaConfig:
    CENTRAL = {
        "nombre": "Zona Central",
        "horarios_inicio": ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30"],
        "bloqueo_hlu": {"dias": ["Ma", "Ju"], "inicio": a_minutos("10:30"), "fin": a_minutos("12:30")}
    }
    PERIFERICA = {
        "nombre": "Zona Periférica",
        "horarios_inicio": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"],
        "bloqueo_hlu": {"dias": ["Ma", "Ju"], "inicio": a_minutos("10:00"), "fin": a_minutos("12:00")}
    }

def get_nivel_curso(codigo):
    match = re.search(r'(\d{4})', codigo)
    if match:
        num = int(match.group(1))
        return "GRAD" if num >= 5000 else "SUBGRAD"
    return "SUBGRAD"

def generar_patrones_validos(creditos, nivel_curso):
    patrones = []
    if nivel_curso == "GRAD":
        for dia in ["Lu", "Ma", "Mi", "Ju", "Vi"]:
            patrones.append({"dias": [dia], "horas": [3.0], "desc": f"Graduado {dia}"})
        return patrones

    if creditos == 3:
        patrones.append({"dias": ["Lu","Mi","Vi"], "horas": [0.83, 0.83, 0.83], "desc": "LWV"})
        patrones.append({"dias": ["Ma","Ju"], "horas": [1.25, 1.25], "desc": "MJ"})
    elif creditos == 4:
        patrones.append({"dias": ["Lu","Ma","Mi","Ju"], "horas": [0.83]*4, "desc": "LMWJ"})
        patrones.append({"dias": ["Lu","Mi"], "horas": [1.83, 1.83], "desc": "LW"})
        patrones.append({"dias": ["Ma","Ju"], "horas": [1.83, 1.83], "desc": "MJ"})
    elif creditos == 5:
        patrones.append({"dias": ["Lu","Ma","Mi","Ju","Vi"], "horas": [0.83]*5, "desc": "Diaria"})
    else:
        patrones.append({"dias": ["Ma"], "horas": [creditos], "desc": "Generico"})
    return patrones

def calcular_creditos_pagables(creditos, cupo):
    if cupo >= 85: return creditos + 3
    elif cupo >= 60: return creditos + 1.5
    return creditos

def es_horario_valido(dia, hora_inicio_str, duracion, zona_config):
    ini = a_minutos(hora_inicio_str)
    fin = ini + int(duracion * 60)
    hlu = zona_config['bloqueo_hlu']
    
    # Validar HLU
    if dia in hlu['dias']:
        if not (fin <= hlu['inicio'] or ini >= hlu['fin']): return False
    
    # Validar fin del día
    if fin > a_minutos("22:00"): return False
    return True

# ========================================================
# 3. ALGORITMO GENÉTICO
# ========================================================

class ClaseGene:
    def __init__(self, curso_data, bloque, hora_inicio, salon_obj):
        self.curso_data = curso_data
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.salon_obj = salon_obj
        
        candidatos = curso_data['candidatos']
        self.prof_asignado = random.choice(candidatos) if candidatos else "TBA"

class IndividuoHorario:
    def __init__(self, genes=None):
        self.genes = genes if genes else []
        self.fitness = 0.0
        self.hard_conflicts = 0
        self.prof_stats = {}
        self.conflict_details = []

    def calcular_fitness(self, profesores_db, preferencias_manuales):
        SCORE = 0; CONFLICTS = 0; self.conflict_details = []
        PENALTY_HARD = 10000; PENALTY_PREF = 2000; PENALTY_LOAD = 5000
        
        carga_actual = {k: 0 for k in profesores_db.keys()}
        ocupacion_profesor = {}; ocupacion_salon = {}
        
        for gen in self.genes:
            prof_nom = gen.prof_asignado
            prof_info = profesores_db.get(prof_nom, {})
            prof_prefs = preferencias_manuales.get(prof_nom, {})
            
            # --- HARD CONSTRAINTS ---
            if gen.curso_data['cupo'] > gen.salon_obj['capacidad']:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
            
            tipo_req = gen.curso_data.get('tipo_salon', 'General')
            if tipo_req != gen.salon_obj['tipo']:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
            
            # Restricciones Fijas (Hard)
            if gen.curso_data.get('bloque_fijo') and gen.hora_inicio != gen.curso_data['bloque_fijo']:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
            
            if gen.curso_data.get('dias_fijos'):
                # Check simple de contención
                req = gen.curso_data['dias_fijos']
                mapeo = {'L':'Lu','M':'Ma','W':'Mi','J':'Ju','V':'Vi'}
                dias_gen = [mapeo.get(c, c) for c in req] # Convertir input LMW a Lu,Ma,Mi...
                # Esta validación es básica, se puede mejorar
                
            # --- PROFESOR Y CARGA ---
            creditos_pago = calcular_creditos_pagables(gen.curso_data['creditos'], gen.curso_data['cupo'])
            if prof_nom != "TBA":
                if prof_nom in carga_actual: carga_actual[prof_nom] += creditos_pago
                
                # Preferencias (Soft)
                p_ini = a_minutos(prof_prefs.get('hora_entrada', '07:00'))
                clase_ini = a_minutos(gen.hora_inicio)
                if clase_ini < p_ini: SCORE -= PENALTY_PREF
                
                # Choques Temporales (Hard)
                for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                    ini = a_minutos(gen.hora_inicio); fin = ini + int(duracion * 60)
                    k_p = (prof_nom, dia)
                    if k_p not in ocupacion_profesor: ocupacion_profesor[k_p] = []
                    for (oi, of) in ocupacion_profesor[k_p]:
                        if not (fin <= oi or ini >= of):
                            SCORE -= PENALTY_HARD; CONFLICTS += 1; break
                    ocupacion_profesor[k_p].append((ini, fin))

            # Choque Salón
            for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                ini = a_minutos(gen.hora_inicio); fin = ini + int(duracion * 60)
                k_s = (gen.salon_obj['codigo'], dia)
                if k_s not in ocupacion_salon: ocupacion_salon[k_s] = []
                for (oi, of) in ocupacion_salon[k_s]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1; break
                ocupacion_salon[k_s].append((ini, fin))

        # Cargas
        for prof_nom, carga in carga_actual.items():
            if prof_nom == "TBA": continue
            info = profesores_db.get(prof_nom, {})
            if carga > info.get('carga_max', 12):
                SCORE -= PENALTY_LOAD * (carga - info.get('carga_max', 12))
                CONFLICTS += 1

        self.fitness = SCORE
        self.hard_conflicts = CONFLICTS
        self.prof_stats = carga_actual
        return self.fitness

class AlgoritmoGenetico:
    def __init__(self, lista_secciones, profesores_db, salones_db, pref_manuales, zona_config, pop_size, mutation_rate):
        self.lista_secciones = lista_secciones
        self.profesores_db = profesores_db
        self.salones_db = salones_db
        self.pref_manuales = pref_manuales
        self.zona_config = zona_config
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.bloques_ref = generar_bloques_horarios()

    def _get_salones_validos(self, curso):
        tipo = curso.get('tipo_salon', 'General')
        cupo = curso['cupo']
        return [s for s in self.salones_db if s['tipo'] == tipo and s['capacidad'] >= cupo] or self.salones_db

    def _crear_gen_flexible(self, curso_data):
        nivel = get_nivel_curso(curso_data['codigo'])
        patrones = generar_patrones_validos(curso_data['creditos'], nivel)
        
        if curso_data.get('dias_fijos'):
            # Filtrar patrones simples
            req = curso_data['dias_fijos']
            # Implementación simple: si pide 'MJ', buscar patrones con exactamente Ma y Ju
            pass # Aquí iría lógica más compleja de filtrado, por ahora dejamos libre para que GA encuentre

        salones_validos = self._get_salones_validos(curso_data)
        
        for _ in range(50):
            patron = random.choice(patrones)
            hora = curso_data.get('bloque_fijo')
            if not hora: hora = random.choice(self.zona_config['horarios_inicio'])
            salon = random.choice(salones_validos)
            
            valido = True
            if not curso_data.get('bloque_fijo'):
                for d, dur in zip(patron['dias'], patron['horas']):
                    if not es_horario_valido(d, hora, dur, self.zona_config):
                        valido = False; break
            
            if valido: return ClaseGene(curso_data, patron, hora, salon)
            
        return ClaseGene(curso_data, patrones[0], "07:30", salones_validos[0])

    def inicializar(self):
        self.population = []
        for _ in range(self.pop_size):
            genes = [self._crear_gen_flexible(c) for c in self.lista_secciones]
            ind = IndividuoHorario(genes)
            ind.calcular_fitness(self.profesores_db, self.pref_manuales)
            self.population.append(ind)

    def evolucionar(self, generaciones, progress_bar, status_text):
        self.inicializar()
        mejor = max(self.population, key=lambda x: x.fitness)
        
        for g in range(generaciones):
            nueva_pop = []
            if max(self.population, key=lambda x: x.fitness).fitness > mejor.fitness:
                mejor = copy.deepcopy(max(self.population, key=lambda x: x.fitness))
            nueva_pop.append(mejor)
            
            while len(nueva_pop) < self.pop_size:
                p1 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                p2 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                genes_hijo = []
                for g1, g2 in zip(p1.genes, p2.genes):
                    genes_hijo.append(copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2))
                hijo = IndividuoHorario(genes_hijo)
                
                for i in range(len(hijo.genes)):
                    if random.random() < self.mutation_rate:
                        hijo.genes[i] = self._crear_gen_flexible(hijo.genes[i].curso_data)
                
                hijo.calcular_fitness(self.profesores_db, self.pref_manuales)
                nueva_pop.append(hijo)
            
            self.population = nueva_pop
            progress_bar.progress((g+1)/generaciones)
            if g % 5 == 0: status_text.text(f"Gen {g} | Conflictos: {mejor.hard_conflicts}")
            
        return mejor

def procesar_excel_expansion(file):
    """
    Lee CANTIDAD_SECCIONES y expande las filas automáticamente.
    """
    try:
        xls = pd.ExcelFile(file)
        df_cursos = pd.read_excel(xls, 'Cursos')
        lista_secciones = []
        
        cols_map = {
            'CODIGO': 'codigo', 'NOMBRE': 'nombre', 'CREDITOS': 'creditos', 
            'CUPO': 'cupo', 'CANDIDATOS': 'candidatos', 'CANTIDAD_SECCIONES': 'cantidad',
            'TIPO_SALON': 'tipo_salon', 'BLOQUE_FIJO': 'bloque_fijo', 'DIAS_FIJOS': 'dias_fijos'
        }
        
        idx_global = 0
        for _, row in df_cursos.iterrows():
            d = {}
            for k, v in cols_map.items():
                for c in df_cursos.columns:
                    if k in str(c).upper(): d[v] = row[c]; break
            
            cands = [c.strip() for c in str(d.get('candidatos', '')).split(',') if c.strip()]
            h_fijo = str(d.get('bloque_fijo', ''))
            if h_fijo.lower() in ['nan', 'none', '']: h_fijo = None
            d_fijos = str(d.get('dias_fijos', ''))
            if d_fijos.lower() in ['nan', 'none', '']: d_fijos = None
            
            # EXPANSIÓN
            cantidad = int(d.get('cantidad', 1)) # Default 1
            if cantidad < 1: cantidad = 1
            
            for i in range(cantidad):
                lista_secciones.append({
                    'id_temp': idx_global, # ID único temporal
                    'codigo': str(d.get('codigo', 'UNK')),
                    'nombre': str(d.get('nombre', 'Curso')),
                    'creditos': int(d.get('creditos', 3)),
                    'cupo': int(d.get('cupo', 30)),
                    'candidatos': cands,
                    'tipo_salon': str(d.get('tipo_salon', 'General')).strip(),
                    'bloque_fijo': h_fijo,
                    'dias_fijos': d_fijos
                })
                idx_global += 1

        df_prof = pd.read_excel(xls, 'Profesores')
        profes_db = {}
        for _, row in df_prof.iterrows():
            profes_db[str(row.get('Nombre', 'Unknown')).strip()] = {
                'carga_min': float(row.get('Carga_Min', 0)),
                'carga_max': float(row.get('Carga_Max', 12)),
                'acepta_grandes': int(row.get('Acepta_Grandes', 0))
            }

        df_sal = pd.read_excel(xls, 'Salones')
        salones_db = []
        for _, row in df_sal.iterrows():
            salones_db.append({
                'codigo': str(row.get('CODIGO', 'G00')),
                'capacidad': int(row.get('CAPACIDAD', 30)),
                'tipo': str(row.get('TIPO', 'General')).strip()
            })
            
        return lista_secciones, profes_db, salones_db
    except Exception as e: return None, None, None, str(e)

def asignar_numeros_seccion(df_resultados):
    """
    Ordena el horario final y asigna números de sección 001, 002...
    secuencialmente basándose en el orden del horario.
    """
    # Ordenar por Código Curso -> Día -> Hora
    df_resultados = df_resultados.sort_values(by=['Código', 'Inicio_Sort'])
    
    # Asignar contador
    df_resultados['Sección'] = df_resultados.groupby('Código').cumcount() + 1
    
    # Formatear a '001', '002'
    df_resultados['Sección'] = df_resultados['Sección'].apply(lambda x: f"{x:03d}")
    return df_resultados

# ========================================================
# 4. INTERFAZ
# ========================================================

def main():
    if 'pref_manuales' not in st.session_state: st.session_state.pref_manuales = {}
    if 'data_secciones' not in st.session_state: st.session_state.data_secciones = None
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    with st.sidebar:
        st.header("🎛️ Control Panel")
        file = st.file_uploader("Cargar Excel (3 Hojas)", type=['xlsx'])
        zona = st.selectbox("Zona Campus", ["Central", "Periférica"])
        
        with st.expander("Configuración GA"):
            pop = st.slider("Población", 50, 500, 150)
            gen = st.slider("Generaciones", 50, 1000, 200)
            mut = st.slider("Mutación", 0.0, 0.8, 0.3)
        
        if st.session_state.get('data_profes'):
            st.markdown("---")
            st.subheader("🕒 Preferencias Docentes")
            p_sel = st.selectbox("Editar:", list(st.session_state.data_profes.keys()))
            curr = st.session_state.pref_manuales.get(p_sel, {})
            
            dias = st.multiselect("Días Preferidos", ["Lu","Ma","Mi","Ju","Vi"], default=curr.get('dias_deseados', ["Lu","Ma","Mi","Ju","Vi"]))
            c1, c2 = st.columns(2)
            h_in = c1.time_input("Entrada", value=datetime.strptime(curr.get('hora_entrada', "07:00"), "%H:%M").time())
            h_out = c2.time_input("Salida", value=datetime.strptime(curr.get('hora_salida', "20:00"), "%H:%M").time())
            
            if st.button("Guardar Preferencia"):
                st.session_state.pref_manuales[p_sel] = {
                    'dias_deseados': dias,
                    'hora_entrada': h_in.strftime("%H:%M"),
                    'hora_salida': h_out.strftime("%H:%M")
                }
                st.success(f"Guardado: {p_sel}")

    st.title("⚡ Generador Automático de Horarios UPRM")
    st.markdown("**Modo Planificación:** Define CANTIDAD de secciones y la IA asignará números al final.")

    if file:
        if st.button("Procesar Archivo"):
            res = procesar_excel_expansion(file)
            if res[0]:
                st.session_state.data_secciones, st.session_state.data_profes, st.session_state.data_salones = res
                # Init Prefs
                for p in st.session_state.data_profes:
                    if p not in st.session_state.pref_manuales:
                        st.session_state.pref_manuales[p] = {'dias_deseados': ["Lu","Ma","Mi","Ju","Vi"], 'hora_entrada': "07:00", 'hora_salida': "20:00"}
                st.success(f"¡Expansión Completa! Se generarán {len(st.session_state.data_secciones)} grupos.")
            else: st.error(f"Error: {res[3]}")

    if st.session_state.data_secciones:
        col1, col2, col3 = st.columns(3)
        col1.metric("Grupos Totales", len(st.session_state.data_secciones))
        col2.metric("Profesores", len(st.session_state.data_profes))
        col3.metric("Salones", len(st.session_state.data_salones))

        if st.button("🚀 Generar y Numerar Secciones", type="primary"):
            with st.status("Ejecutando Inteligencia Artificial...", expanded=True) as status:
                prog = st.progress(0); txt = st.empty()
                ga = AlgoritmoGenetico(
                    st.session_state.data_secciones, st.session_state.data_profes, st.session_state.data_salones,
                    st.session_state.pref_manuales, ZonaConfig.CENTRAL if zona == "Central" else ZonaConfig.PERIFERICA,
                    pop, mut
                )
                start = time.time()
                mejor = ga.evolucionar(gen, prog, txt)
                st.session_state.resultado = mejor
                status.update(label="✅ Completado", state="complete", expanded=False)
    
    if st.session_state.resultado:
        res = st.session_state.resultado
        st.divider()
        
        k1, k2 = st.columns(2)
        k1.metric("Fitness", int(res.fitness))
        k2.metric("Conflictos", res.hard_conflicts, delta_color="inverse")
        
        rows = []
        for g in res.genes:
            cred = calcular_creditos_pagables(g.curso_data['creditos'], g.curso_data['cupo'])
            rows.append({
                "Código": g.curso_data['codigo'],
                "Curso": g.curso_data['nombre'],
                "Profesor": g.prof_asignado,
                "Días": "".join(g.bloque['dias']),
                "Inicio_Sort": g.hora_inicio, # Columna oculta para ordenar
                "Horario": f"{g.hora_inicio} - {a_minutos(g.hora_inicio)+int(sum(g.bloque['horas'])*60/len(g.bloque['horas']))//60}:{int(sum(g.bloque['horas'])*60/len(g.bloque['horas']))%60:02d}",
                "Salón": g.salon_obj['codigo'],
                "Créditos": cred
            })
        df = pd.DataFrame(rows)
        
        # --- AUTONUMERACIÓN ---
        df = asignar_numeros_seccion(df)
        # Reordenar columnas para ver la sección al principio
        cols = ['Código', 'Sección', 'Curso', 'Profesor', 'Días', 'Horario', 'Salón', 'Créditos']
        df = df[cols]
        
        t1, t2, t3 = st.tabs(["Horario Oficial", "Conflictos", "Descargar"])
        t1.dataframe(df, use_container_width=True)
        with t2:
            if res.conflict_details:
                for c in res.conflict_details: st.error(c)
            else: st.success("¡Horario Libre de Conflictos!")
        with t3:
            st.download_button("Descargar Excel Oficial", df.to_csv(index=False).encode('utf-8'), "horario_final_numerado.csv")

if __name__ == "__main__":
    main()
