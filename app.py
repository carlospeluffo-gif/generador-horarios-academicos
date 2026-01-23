import streamlit as st
import pandas as pd
import random
import copy
import time
import math
import plotly.express as px
from datetime import datetime

# ========================================================
# 1. CONFIGURACIÓN
# ========================================================

st.set_page_config(page_title="UPRM Master Scheduler", page_icon="📅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #fff; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }
    h1, h2 { color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# ========================================================
# 2. LÓGICA DE NEGOCIO Y BLOQUES
# ========================================================

def a_minutos(hhmm):
    try:
        if isinstance(hhmm, str):
            # Normalizar formato (ej. 7:30 am -> 07:30)
            hhmm = hhmm.lower().replace(' am', '').replace(' pm', '').strip()
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

def generar_bloques_horarios():
    bloques = []
    # --- 3 CREDITOS ---
    # Estándar LWV (50 min)
    bloques.append({"dias": ["Lu","Mi","Vi"], "horas": [0.83, 0.83, 0.83], "creditos": 3, "desc": "LWV 50min"}) 
    # Estándar MJ (1 hora 15 min = 1.25 hr)
    bloques.append({"dias": ["Ma","Ju"], "horas": [1.25, 1.25], "creditos": 3, "desc": "MJ 1h 15m"})
    # Graduados / Nocturnos (1 día x 3 horas)
    for d in ["Lu", "Ma", "Mi", "Ju", "Vi"]:
        bloques.append({"dias": [d], "horas": [2.9], "creditos": 3, "desc": f"{d} 3hr (Grad)"})

    # --- 4 CREDITOS ---
    # LMWJ (50 min)
    bloques.append({"dias": ["Lu","Ma","Mi","Ju"], "horas": [0.83]*4, "creditos": 4, "desc": "LMWJ 50min"})
    # LW 2 horas (ej. 1:30 - 3:20)
    bloques.append({"dias": ["Lu","Mi"], "horas": [1.83, 1.83], "creditos": 4, "desc": "LW 1h 50m"})
    # MJ 2 horas
    bloques.append({"dias": ["Ma","Ju"], "horas": [1.83, 1.83], "creditos": 4, "desc": "MJ 1h 50m"})
    
    # --- 5 CREDITOS (Pre-Calc) ---
    bloques.append({"dias": ["Lu","Ma","Mi","Ju","Vi"], "horas": [0.83]*5, "creditos": 5, "desc": "Diaria 50min"})
    
    return bloques

def calcular_creditos_pagables(creditos, cupo):
    if cupo >= 85: return creditos + 3
    elif cupo >= 60: return creditos + 1.5
    return creditos

def es_horario_valido_en_zona(dia, hora_inicio_str, duracion, zona_config):
    ini = a_minutos(hora_inicio_str)
    fin = ini + int(duracion * 60)
    hlu = zona_config['bloqueo_hlu']
    
    # Validar HLU
    if dia in hlu['dias']:
        # Si choca con HLU
        if not (fin <= hlu['inicio'] or ini >= hlu['fin']): return False
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
        self.prof_asignado = random.choice(candidatos) if candidatos else "Staff"

class IndividuoHorario:
    def __init__(self, genes=None):
        self.genes = genes if genes else []
        self.fitness = 0.0
        self.hard_conflicts = 0
        self.prof_stats = {}
        self.conflict_details = []

    def calcular_fitness(self, profesores_db, preferencias_manuales):
        SCORE = 0; CONFLICTS = 0; self.conflict_details = []
        PENALTY_HARD = 10000; PENALTY_PREF = 5000; PENALTY_LOAD = 2000
        
        carga_actual = {k: 0 for k in profesores_db.keys()}
        ocupacion_profesor = {}; ocupacion_salon = {}
        
        for gen in self.genes:
            prof_nom = gen.prof_asignado
            
            # --- 1. RESTRICCIONES FIJAS (HARD) ---
            # Hora Fija
            if gen.curso_data.get('bloque_fijo'):
                if gen.hora_inicio != gen.curso_data['bloque_fijo']:
                    SCORE -= PENALTY_HARD; CONFLICTS += 1
                    self.conflict_details.append(f"Error Hora Fija: {gen.curso_data['codigo']} requiere {gen.curso_data['bloque_fijo']}")
            
            # Días Fijos (Nuevo V8)
            if gen.curso_data.get('dias_fijos'):
                dias_req = gen.curso_data['dias_fijos'] # Ej: "MJ"
                dias_gen = "".join(gen.bloque['dias']) # Ej: "MaJu" -> convertir a formato corto si necesario
                # Simplificación: Comprobar si los dias generados coinciden con lo pedido
                # Mapeo rápido: L=Lu, M=Ma, W=Mi, J=Ju, V=Vi
                mapa = {'L':'Lu', 'M':'Ma', 'W':'Mi', 'J':'Ju', 'V':'Vi'}
                dias_gen_code = "".join([k for k,v in mapa.items() if v in gen.bloque['dias']])
                
                # Check flexible (si contiene los dias)
                if dias_req != dias_gen_code:
                     SCORE -= PENALTY_HARD; CONFLICTS += 1
                     self.conflict_details.append(f"Error Días Fijos: {gen.curso_data['codigo']} requiere {dias_req}, tiene {dias_gen_code}")

            # --- 2. SALONES ---
            if gen.curso_data['cupo'] > gen.salon_obj['capacidad']:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
                self.conflict_details.append(f"Cupo: {gen.curso_data['codigo']} ({gen.curso_data['cupo']}) > {gen.salon_obj['capacidad']}")
            
            if gen.curso_data.get('tipo_salon', 'General') != gen.salon_obj['tipo']:
                SCORE -= PENALTY_HARD; CONFLICTS += 1
            
            # --- 3. CARGA Y CHOQUES ---
            creditos_pago = calcular_creditos_pagables(gen.curso_data['creditos'], gen.curso_data['cupo'])
            if prof_nom != "Staff":
                if prof_nom in carga_actual: carga_actual[prof_nom] += creditos_pago
                
                # Choques Temporales
                for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                    ini = a_minutos(gen.hora_inicio); fin = ini + int(duracion * 60)
                    k_p = (prof_nom, dia)
                    if k_p not in ocupacion_profesor: ocupacion_profesor[k_p] = []
                    for (oi, of) in ocupacion_profesor[k_p]:
                        if not (fin <= oi or ini >= of):
                            SCORE -= PENALTY_HARD; CONFLICTS += 1
                            self.conflict_details.append(f"Choque Prof. {prof_nom} en {dia} ({gen.hora_inicio})")
                            break
                    ocupacion_profesor[k_p].append((ini, fin))

            # Choque Salón
            for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                ini = a_minutos(gen.hora_inicio); fin = ini + int(duracion * 60)
                k_s = (gen.salon_obj['codigo'], dia)
                if k_s not in ocupacion_salon: ocupacion_salon[k_s] = []
                for (oi, of) in ocupacion_salon[k_s]:
                    if not (fin <= oi or ini >= of):
                        SCORE -= PENALTY_HARD; CONFLICTS += 1
                        self.conflict_details.append(f"Choque Salón {gen.salon_obj['codigo']} en {dia}")
                        break
                ocupacion_salon[k_s].append((ini, fin))

        # Cargas Globales
        for prof_nom, carga in carga_actual.items():
            if prof_nom == "Staff": continue
            info = profesores_db.get(prof_nom, {})
            if carga > info.get('carga_max', 12):
                SCORE -= PENALTY_LOAD * (carga - info.get('carga_max', 12))
                CONFLICTS += 1
                self.conflict_details.append(f"Sobrecarga {prof_nom}: {carga}")

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

    def _crear_gen_inteligente(self, curso_data):
        hora_fija = curso_data.get('bloque_fijo')
        dias_fijos = curso_data.get('dias_fijos') # String "MJ", "LWV"
        
        # Filtrar bloques compatibles por créditos
        bloques_validos = [b for b in self.bloques_ref if b['creditos'] == curso_data['creditos']]
        
        # Filtrar bloques compatibles por DÍAS FIJOS (Si existen)
        if dias_fijos:
            mapa = {'L':'Lu', 'M':'Ma', 'W':'Mi', 'J':'Ju', 'V':'Vi'}
            bloques_filtrados = []
            for b in bloques_validos:
                codigo_bloque = "".join([k for k,v in mapa.items() if v in b['dias']])
                if codigo_bloque == dias_fijos:
                    bloques_filtrados.append(b)
            if bloques_filtrados:
                bloques_validos = bloques_filtrados
        
        if not bloques_validos: bloques_validos = self.bloques_ref[:1]
        
        salones_validos = self._get_salones_validos(curso_data)
        
        for _ in range(50):
            bloque = random.choice(bloques_validos)
            hora = hora_fija if hora_fija else random.choice(self.zona_config['horarios_inicio'])
            salon = random.choice(salones_validos)
            
            # Si tiene hora/dias fijos, asumimos que es válido por decreto (ignora HLU si es fijo)
            if hora_fija or dias_fijos:
                return ClaseGene(curso_data, bloque, hora, salon)

            # Validar Zona/HLU para el resto
            valido = True
            for d, h in zip(bloque['dias'], bloque['horas']):
                if not es_horario_valido_en_zona(d, hora, h, self.zona_config):
                    valido = False; break
            
            if valido: return ClaseGene(curso_data, bloque, hora, salon)
            
        return ClaseGene(curso_data, bloques_validos[0], hora_fija if hora_fija else "07:30", salones_validos[0])

    def inicializar(self):
        self.population = []
        for _ in range(self.pop_size):
            genes = [self._crear_gen_inteligente(c) for c in self.lista_secciones]
            ind = IndividuoHorario(genes)
            ind.calcular_fitness(self.profesores_db, self.pref_manuales)
            self.population.append(ind)

    def evolucionar(self, generaciones, progress_bar, status_text):
        self.inicializar()
        mejor = max(self.population, key=lambda x: x.fitness)
        
        for g in range(generaciones):
            nueva_pop = []
            mejor_actual = max(self.population, key=lambda x: x.fitness)
            if mejor_actual.fitness > mejor.fitness: mejor = copy.deepcopy(mejor_actual)
            nueva_pop.append(mejor)
            
            while len(nueva_pop) < self.pop_size:
                padres = random.sample(self.population, 3)
                p1 = max(padres, key=lambda x: x.fitness)
                p2 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                genes_hijo = []
                for g1, g2 in zip(p1.genes, p2.genes):
                    genes_hijo.append(copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2))
                hijo = IndividuoHorario(genes_hijo)
                
                for i in range(len(hijo.genes)):
                    if random.random() < self.mutation_rate:
                        gen = hijo.genes[i]
                        # Respetar restricciones fijas al mutar
                        if not gen.curso_data.get('bloque_fijo') and not gen.curso_data.get('dias_fijos'):
                            if random.random() < 0.5:
                                gen.hora_inicio = random.choice(self.zona_config['horarios_inicio'])
                        
                        if random.random() < 0.5 and gen.curso_data['candidatos']:
                            gen.prof_asignado = random.choice(gen.curso_data['candidatos'])
                            
                hijo.calcular_fitness(self.profesores_db, self.pref_manuales)
                nueva_pop.append(hijo)
            
            self.population = nueva_pop
            progress_bar.progress((g+1)/generaciones)
            if g % 5 == 0: status_text.text(f"Gen {g} | Conflictos: {mejor.hard_conflicts}")
            
        return mejor

def procesar_excel_planificado(file):
    try:
        xls = pd.ExcelFile(file)
        df_cursos = pd.read_excel(xls, 'Cursos')
        lista_secciones = []
        cols_map = {'CODIGO':'codigo', 'SECCION':'seccion', 'NOMBRE':'nombre', 'CREDITOS':'creditos', 'CUPO':'cupo', 'CANDIDATOS':'candidatos', 'TIPO_SALON':'tipo_salon', 'BLOQUE_FIJO':'bloque_fijo', 'DIAS_FIJOS':'dias_fijos'}
        
        for _, row in df_cursos.iterrows():
            data = {}
            for k, v in cols_map.items():
                for c in df_cursos.columns:
                    if k in str(c).upper(): data[v] = row[c]; break
            
            cands = str(data.get('candidatos', 'Staff')).split(',')
            cands = [c.strip() for c in cands if c.strip()]
            hora_fija = str(data.get('bloque_fijo', '')).strip()
            if hora_fija.lower() in ['nan', 'none', '']: hora_fija = None
            dias_fijos = str(data.get('dias_fijos', '')).strip()
            if dias_fijos.lower() in ['nan', 'none', '']: dias_fijos = None
            
            lista_secciones.append({
                'codigo': str(data.get('codigo', 'UNK')),
                'seccion': str(data.get('seccion', '001')),
                'nombre': str(data.get('nombre', 'Curso')),
                'creditos': int(data.get('creditos', 3)),
                'cupo': int(data.get('cupo', 30)),
                'candidatos': cands,
                'tipo_salon': str(data.get('tipo_salon', 'General')).strip(),
                'bloque_fijo': hora_fija,
                'dias_fijos': dias_fijos
            })

        df_prof = pd.read_excel(xls, 'Profesores')
        profes_db = {}
        for _, row in df_prof.iterrows():
            profes_db[str(row.get('Nombre', 'Unknown')).strip()] = {'carga_min': float(row.get('Carga_Min', 0)), 'carga_max': float(row.get('Carga_Max', 12)), 'acepta_grandes': int(row.get('Acepta_Grandes', 0))}

        df_salones = pd.read_excel(xls, 'Salones')
        salones_db = []
        for _, row in df_salones.iterrows():
            salones_db.append({'codigo': str(row.get('CODIGO', 'G01')), 'capacidad': int(row.get('CAPACIDAD', 30)), 'tipo': str(row.get('TIPO', 'General')).strip()})
            
        return lista_secciones, profes_db, salones_db
    except Exception as e: return None, None, None, str(e)

# ========================================================
# 4. INTERFAZ
# ========================================================

def main():
    if 'pref_manuales' not in st.session_state: st.session_state.pref_manuales = {}
    if 'data_secciones' not in st.session_state: st.session_state.data_secciones = None
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    with st.sidebar:
        st.header("🎛️ Panel de Control")
        file = st.file_uploader("Excel Planificado (3 Hojas)", type=['xlsx'])
        zona = st.selectbox("Zona", ["Central", "Periférica"])
        
        with st.expander("Avanzado"):
            pop = st.slider("Población", 50, 500, 150)
            gen = st.slider("Generaciones", 50, 1000, 200)
            mut = st.slider("Mutación", 0.0, 0.5, 0.2)
        
        if st.session_state.get('data_profes'):
            st.markdown("---")
            st.subheader("🕒 Preferencias Docentes")
            p_sel = st.selectbox("Profesor:", list(st.session_state.data_profes.keys()))
            curr = st.session_state.pref_manuales.get(p_sel, {})
            dias = st.multiselect("Días", ["Lu","Ma","Mi","Ju","Vi"], default=curr.get('dias_deseados', ["Lu","Ma","Mi","Ju","Vi"]))
            c1, c2 = st.columns(2)
            h_in = c1.time_input("Entrada", value=datetime.strptime(curr.get('hora_entrada', "07:00"), "%H:%M").time())
            h_out = c2.time_input("Salida", value=datetime.strptime(curr.get('hora_salida', "20:00"), "%H:%M").time())
            st.session_state.pref_manuales[p_sel] = {'dias_deseados': dias, 'hora_entrada': h_in.strftime("%H:%M"), 'hora_salida': h_out.strftime("%H:%M")}

    st.title("📅 UPRM Master Scheduler V8")
    
    if file:
        if st.button("Cargar Planificación"):
            res = procesar_excel_planificado(file)
            if res[0]: 
                st.session_state.data_secciones, st.session_state.data_profes, st.session_state.data_salones = res
                # Init prefs
                for p in st.session_state.data_profes:
                    if p not in st.session_state.pref_manuales:
                        st.session_state.pref_manuales[p] = {'dias_deseados': ["Lu","Ma","Mi","Ju","Vi"], 'hora_entrada': "07:00", 'hora_salida': "20:00"}
                st.success(f"Cargadas {len(st.session_state.data_secciones)} secciones planificadas.")
            else: st.error(res[3])

    if st.session_state.data_secciones:
        c1, c2, c3 = st.columns(3)
        c1.metric("Oferta Total", len(st.session_state.data_secciones))
        c2.metric("Profesores", len(st.session_state.data_profes))
        c3.metric("Salones", len(st.session_state.data_salones))

        if st.button("🚀 Generar Horario Oficial", type="primary"):
            with st.status("Asignando recursos...", expanded=True) as status:
                prog = st.progress(0); txt = st.empty()
                ga = AlgoritmoGenetico(
                    st.session_state.data_secciones, st.session_state.data_profes, st.session_state.data_salones,
                    st.session_state.pref_manuales, ZonaConfig.CENTRAL if zona == "Central" else ZonaConfig.PERIFERICA,
                    pop, mut
                )
                start = time.time()
                mejor = ga.evolucionar(gen, prog, txt)
                st.session_state.resultado = mejor
                status.update(label="✅ Horario Generado", state="complete", expanded=False)
    
    if st.session_state.resultado:
        res = st.session_state.resultado
        st.divider()
        k1, k2 = st.columns(2)
        k1.metric("Calidad (Fitness)", int(res.fitness))
        k2.metric("Conflictos", res.hard_conflicts, delta_color="inverse")
        
        rows = []
        for g in res.genes:
            cred = calcular_creditos_pagables(g.curso_data['creditos'], g.curso_data['cupo'])
            rows.append({
                "Código": g.curso_data['codigo'],
                "Sección": g.curso_data['seccion'],
                "Curso": g.curso_data['nombre'],
                "Profesor": g.prof_asignado,
                "Días": "".join(g.bloque['dias']),
                "Horario": f"{g.hora_inicio} - {a_minutos(g.hora_inicio)+int(max(g.bloque['horas'])*60)//60}:{int(max(g.bloque['horas'])*60)%60:02d}",
                "Salón": g.salon_obj['codigo'],
                "Créditos Pago": cred
            })
        df = pd.DataFrame(rows)
        
        t1, t2, t3 = st.tabs(["Horario Oficial", "Conflictos", "Descargar"])
        t1.dataframe(df, use_container_width=True)
        with t2:
            if res.conflict_details:
                for c in res.conflict_details: st.error(c)
            else: st.success("Sin conflictos.")
        with t3:
            st.download_button("Descargar Excel", df.to_csv(index=False).encode('utf-8'), "horario_oficial.csv")

if __name__ == "__main__":
    main()
