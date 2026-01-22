import streamlit as st
import pandas as pd
import random
import copy
import time
import numpy as np

# ========================================================
# 1. CONFIGURACIÓN Y CONSTANTES
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
    """Convierte HH:MM a minutos del día"""
    try:
        if isinstance(hhmm, str):
            h, m = map(int, hhmm.strip().split(":"))
            return h * 60 + m
        return 0 # Si viene vacío o nulo
    except:
        return 0

def generar_bloques_horarios():
    """Genera los bloques de tiempo estándar"""
    bloques = []
    bloques.append({"dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3})
    bloques.append({"dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3})
    bloques.append({"dias": ["Lu","Ma","Mi","Ju"], "horas": [1,1,1,1], "creditos": 4})
    bloques.append({"dias": ["Lu","Mi"], "horas": [2,2], "creditos": 4})
    bloques.append({"dias": ["Ma","Ju"], "horas": [2,2], "creditos": 4})
    return bloques

def calcular_creditos_pagables(creditos_base, n_estudiantes):
    """
    Implementación de la Lógica de Tabla 4.12
    Calcula cuántos créditos de carga recibe el profesor según el tamaño del grupo.
    """
    # Lógica estándar UPR (Aproximada según descripción de la tesis)
    # Secciones estándar (< 60): Carga = Créditos
    # Secciones medianas (60-84): Carga = Créditos + Bono (ej. 1.5)
    # Secciones grandes (>= 85): Carga = Créditos * 2 (o Créditos + 3)
    
    if n_estudiantes >= 85:
        return creditos_base + 3 # Bono significativo por sección grande
    elif n_estudiantes >= 60:
        return creditos_base + 1.5 # Bono medio
    else:
        return creditos_base # Carga normal

def es_horario_valido_en_zona(dia, hora_inicio_str, duracion, zona_config):
    ini = a_minutos(hora_inicio_str)
    fin = ini + int(duracion * 60)
    restricciones = zona_config['restricciones']
    if dia in restricciones:
        for r_ini, r_fin in restricciones[dia]:
            r_ini_m = a_minutos(r_ini)
            r_fin_m = a_minutos(r_fin)
            if not (fin <= r_ini_m or ini >= r_fin_m):
                return False
    return True

# ========================================================
# 2. CLASES DEL ALGORITMO GENÉTICO
# ========================================================

class ClaseGene:
    """Un gen representa la asignación completa de UNA sección"""
    def __init__(self, curso_data, bloque, hora_inicio, salon):
        self.curso_data = curso_data # Diccionario con toda la info del curso
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.salon = salon
        
        # Selección inicial de profesor
        candidatos = curso_data['candidatos']
        self.prof_asignado = random.choice(candidatos) if candidatos else "Staff"

class IndividuoHorario:
    def __init__(self, genes=None):
        self.genes = genes if genes else []
        self.fitness = 0.0
        self.hard_conflicts = 0
        self.prof_stats = {} # Para guardar cargas finales

    def calcular_fitness(self, profesores_db):
        """
        Función de Aptitud Maestra.
        Evalúa Restricciones Duras (Penalización -10,000) y Suaves (Puntos +).
        """
        PENALTY_HARD = 10000
        PENALTY_LOAD = 5000 # Violar Min/Max carga
        SCORE = 0
        CONFLICTS = 0
        
        # Estructuras auxiliares
        carga_actual = {k: 0 for k in profesores_db.keys()}
        ocupacion_profesor = {} # (Prof, Dia, Minuto) -> Bool
        ocupacion_salon = {}    # (Salon, Dia, Minuto) -> Bool
        
        # --- 1. EVALUACIÓN GEN A GEN ---
        for gen in self.genes:
            prof_nom = gen.prof_asignado
            prof_info = profesores_db.get(prof_nom, {})
            
            # A. Cálculo de Carga (Tabla 4.12)
            creditos_pago = calcular_creditos_pagables(gen.curso_data['creditos'], gen.curso_data['cupo'])
            if prof_nom in carga_actual:
                carga_actual[prof_nom] += creditos_pago
            
            # B. Restricción C1: Secciones Grandes
            es_grande = gen.curso_data['cupo'] >= 85
            acepta_grandes = prof_info.get('acepta_grandes', 0) # 1=Sí, 0=No
            if es_grande and acepta_grandes == 0:
                SCORE -= PENALTY_HARD # El profe no acepta grupos grandes
                CONFLICTS += 1

            # C. Restricción C3 y C4: Horario Entrada/Salida
            hora_gen_min = a_minutos(gen.hora_inicio)
            duracion_max = max(gen.bloque['horas']) * 60
            hora_gen_fin = hora_gen_min + int(duracion_max)
            
            pref_inicio = a_minutos(prof_info.get('hora_entrada', '07:00'))
            pref_fin = a_minutos(prof_info.get('hora_salida', '20:00'))
            
            # Verificar si se sale de sus horas preferidas (Penalización Suave/Media)
            if hora_gen_min < pref_inicio or hora_gen_fin > pref_fin:
                SCORE -= 500 # Penalización media por salir de su horario deseado

            # D. Días Deseados (C2) - Bonificación
            dias_deseados = prof_info.get('dias_deseados', []) # Lista ej ['Lu', 'Ma']
            coincidencias = sum(1 for d in gen.bloque['dias'] if d in dias_deseados)
            SCORE += (coincidencias * 20) # 20 puntos por cada día que coincide
            
            # E. Prioridad de Candidato
            if gen.curso_data['candidatos'] and prof_nom == gen.curso_data['candidatos'][0]:
                SCORE += 100 # Bonificación por usar al candidato #1
            
            # F. Chequeo de Choques (Hard)
            # Iteramos sobre los días/horas de este gen para llenar la matriz de ocupación
            for dia, duracion in zip(gen.bloque['dias'], gen.bloque['horas']):
                ini = a_minutos(gen.hora_inicio)
                fin = ini + int(duracion * 60)
                
                # Chequeo Profesor
                key_prof = (prof_nom, dia)
                if key_prof not in ocupacion_profesor: ocupacion_profesor[key_prof] = []
                for (o_ini, o_fin) in ocupacion_profesor[key_prof]:
                    if not (fin <= o_ini or ini >= o_fin): # Solapamiento
                        SCORE -= PENALTY_HARD
                        CONFLICTS += 1
                        break
                ocupacion_profesor[key_prof].append((ini, fin))
                
                # Chequeo Salón
                key_salon = (gen.salon, dia)
                if key_salon not in ocupacion_salon: ocupacion_salon[key_salon] = []
                for (o_ini, o_fin) in ocupacion_salon[key_salon]:
                    if not (fin <= o_ini or ini >= o_fin): # Solapamiento
                        SCORE -= PENALTY_HARD
                        CONFLICTS += 1
                        break
                ocupacion_salon[key_salon].append((ini, fin))

        # --- 2. EVALUACIÓN GLOBAL (CARGAS) ---
        for prof_nom, carga in carga_actual.items():
            prof_info = profesores_db.get(prof_nom, {})
            min_carga = prof_info.get('carga_min', 0)
            max_carga = prof_info.get('carga_max', 12) # Default 12 si no especifica
            
            if carga > max_carga:
                SCORE -= PENALTY_LOAD * (carga - max_carga) # Penalización proporcional al exceso
                CONFLICTS += 1 # Consideramos sobrecarga como conflicto duro
            elif carga < min_carga:
                SCORE -= 2000 * (min_carga - carga) # Penalización por subcarga (menos grave que sobrecarga)
        
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
        # Seleccionar bloque compatible con créditos
        bloques_validos = [b for b in self.bloques_ref if b['creditos'] == curso['creditos']]
        if not bloques_validos: bloques_validos = self.bloques_ref[:1]
        
        # Intentar 20 veces encontrar slot válido en zona
        for _ in range(20):
            bloque = random.choice(bloques_validos)
            hora = random.choice(self.zona_config['horarios_inicio'])
            salon = random.choice(self.salones)
            valido = True
            for d, h in zip(bloque['dias'], bloque['horas']):
                if not es_horario_valido_en_zona(d, hora, h, self.zona_config):
                    valido = False; break
            if valido:
                return ClaseGene(curso, bloque, hora, salon)
        
        # Fallback
        return ClaseGene(curso, bloques_validos[0], self.zona_config['horarios_inicio'][0], self.salones[0])

    def inicializar(self):
        self.population = []
        for _ in range(self.pop_size):
            genes = [self._crear_gen_aleatorio(c) for c in self.cursos_demanda]
            ind = IndividuoHorario(genes)
            ind.calcular_fitness(self.profesores_db)
            self.population.append(ind)

    def evolucionar(self, generaciones, progress_bar):
        self.inicializar()
        mejor_historico = max(self.population, key=lambda x: x.fitness)
        
        for g in range(generaciones):
            nueva_pop = []
            # Elitismo
            mejor_actual = max(self.population, key=lambda x: x.fitness)
            if mejor_actual.fitness > mejor_historico.fitness:
                mejor_historico = copy.deepcopy(mejor_actual)
            nueva_pop.append(mejor_historico)
            
            while len(nueva_pop) < self.pop_size:
                # Torneo
                p1 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                p2 = max(random.sample(self.population, 3), key=lambda x: x.fitness)
                
                # Cruce Uniforme
                genes_hijo = []
                for g1, g2 in zip(p1.genes, p2.genes):
                    genes_hijo.append(copy.deepcopy(g1) if random.random() > 0.5 else copy.deepcopy(g2))
                
                hijo = IndividuoHorario(genes_hijo)
                
                # Mutación
                for gen in hijo.genes:
                    if random.random() < self.mutation_rate:
                        if random.random() < 0.5 and gen.curso_data['candidatos']:
                            # Mutar Profesor
                            gen.prof_asignado = random.choice(gen.curso_data['candidatos'])
                        else:
                            # Mutar Tiempo/Lugar
                            bloques_validos = [b for b in self.bloques_ref if b['creditos'] == gen.curso_data['creditos']]
                            if bloques_validos:
                                gen.bloque = random.choice(bloques_validos)
                                gen.hora_inicio = random.choice(self.zona_config['horarios_inicio'])
                                gen.salon = random.choice(self.salones)
                
                hijo.calcular_fitness(self.profesores_db)
                nueva_pop.append(hijo)
            
            self.population = nueva_pop
            progress_bar.progress((g+1)/generaciones)
            
        return mejor_historico

# ========================================================
# 3. PROCESAMIENTO DE EXCEL (MULTI-HOJA)
# ========================================================

def procesar_excel_completo(file):
    try:
        xls = pd.ExcelFile(file)
        
        # 1. Hoja Cursos
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
            
        # 2. Hoja Profesores (Restricciones y Preferencias)
        df_profes = pd.read_excel(xls, 'Profesores')
        profes_db = {}
        for _, row in df_profes.iterrows():
            nombre = str(row.get('Nombre', 'Unknown')).strip()
            
            # Parsear días deseados "Lu,Ma" -> list
            dias_raw = str(row.get('Dias_Deseados', '')).replace(';',',')
            dias_list = [d.strip() for d in dias_raw.split(',') if d.strip()]
            
            profes_db[nombre] = {
                'carga_min': float(row.get('Carga_Min', 0)),
                'carga_max': float(row.get('Carga_Max', 12)),
                'acepta_grandes': int(row.get('Acepta_Grandes', 0)), # 1 o 0
                'hora_entrada': str(row.get('Hora_Entrada', '07:00')),
                'hora_salida': str(row.get('Hora_Salida', '20:00')),
                'dias_deseados': dias_list
            }
            
        return cursos_lista, profes_db
        
    except Exception as e:
        return None, f"Error leyendo Excel: {str(e)}"

# ========================================================
# 4. INTERFAZ GRÁFICA
# ========================================================

def main():
    st.set_page_config(page_title="Sistema UPRM Timetabling", layout="wide")
    
    st.title("🎓 Sistema de Programación Académica (UPRM Logic)")
    st.markdown("Algoritmo Genético con control de **Carga Docente** y **Tabla 4.12**")
    
    # Sidebar
    st.sidebar.header("Datos de Entrada")
    file = st.sidebar.file_uploader("Subir Excel (.xlsx)", type=['xlsx'])
    
    with st.sidebar.expander("ℹ️ Formato del Excel"):
        st.markdown("""
        El archivo debe tener **2 Hojas**:
        
        **1. Hoja 'Cursos':**
        - `Codigo`, `Nombre`, `Creditos`, `Cupo`, `Candidatos` (separados por coma)
        
        **2. Hoja 'Profesores':**
        - `Nombre`
        - `Carga_Min`, `Carga_Max`
        - `Acepta_Grandes` (1=Sí, 0=No)
        - `Dias_Deseados` (ej: Lu,Ma)
        - `Hora_Entrada`, `Hora_Salida` (Formato HH:MM)
        """)

    zona = st.sidebar.selectbox("Zona Campus", ["Central", "Periférica"])
    zona_cfg = ZonaConfig.CENTRAL if zona == "Central" else ZonaConfig.PERIFERICA
    
    if 'data_cursos' not in st.session_state: st.session_state.data_cursos = None
    if 'data_profes' not in st.session_state: st.session_state.data_profes = None
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    if file:
        if st.sidebar.button("Procesar Archivo"):
            cursos, profes = procesar_excel_completo(file)
            if cursos:
                st.session_state.data_cursos = cursos
                st.session_state.data_profes = profes
                st.success(f"Cargados: {len(cursos)} cursos y {len(profes)} perfiles docentes.")
                st.rerun()
            else:
                st.error(profes) # Mensaje de error

    # Tabs
    t1, t2, t3 = st.tabs(["📋 Datos Cargados", "⚙️ Ejecutar Algoritmo", "📊 Resultados Finales"])
    
    with t1:
        if st.session_state.data_profes:
            st.subheader("Perfiles Docentes Detectados")
            df_p = pd.DataFrame.from_dict(st.session_state.data_profes, orient='index')
            st.dataframe(df_p)
            
            st.subheader("Demanda de Cursos")
            st.dataframe(pd.DataFrame(st.session_state.data_cursos))
        else:
            st.info("Sube el archivo Excel para ver los datos.")

    with t2:
        c1, c2, c3 = st.columns(3)
        pop = c1.number_input("Población", 50, 500, 100)
        gen = c2.number_input("Generaciones", 50, 1000, 150)
        mut = c3.slider("Tasa Mutación", 0.0, 1.0, 0.15)
        
        if st.button("🚀 Iniciar Optimización", type="primary", disabled=not st.session_state.data_profes):
            progress = st.progress(0)
            status = st.empty()
            
            ga = AlgoritmoGenetico(
                st.session_state.data_cursos,
                st.session_state.data_profes,
                zona_cfg,
                MATEMATICAS_SALONES_FIJOS,
                pop, mut
            )
            
            start = time.time()
            mejor = ga.evolucionar(gen, progress)
            st.session_state.resultado = mejor
            
            status.success(f"Terminado en {time.time()-start:.1f}s | Fitness: {mejor.fitness}")
            
            if mejor.hard_conflicts > 0:
                st.warning(f"⚠️ Atención: La solución tiene {mejor.hard_conflicts} conflictos duros (choques o restricciones violadas).")
            else:
                st.balloons()
                st.success("✅ ¡Solución Válida Encontrada!")

    with t3:
        if st.session_state.resultado:
            res = st.session_state.resultado
            
            # --- Tabla Detallada ---
            st.subheader("Horario Generado")
            rows = []
            for g in res.genes:
                prof_data = st.session_state.data_profes.get(g.prof_asignado, {})
                creditos_reales = calcular_creditos_pagables(g.curso_data['creditos'], g.curso_data['cupo'])
                
                rows.append({
                    "Curso": g.curso_data['codigo'],
                    "Sección": "001", # Placeholder
                    "Profesor": g.prof_asignado,
                    "Cupo": g.curso_data['cupo'],
                    "Créditos Pago": creditos_reales,
                    "Días": "".join(g.bloque['dias']),
                    "Inicio": g.hora_inicio,
                    "Salón": g.salon
                })
            df_res = pd.DataFrame(rows)
            st.dataframe(df_res, use_container_width=True)
            
            # --- Análisis de Cargas ---
            st.subheader("Análisis de Carga Docente (Min/Max)")
            
            load_data = []
            for prof, data in st.session_state.data_profes.items():
                carga_real = res.prof_stats.get(prof, 0)
                estado = "✅ OK"
                if carga_real < data['carga_min']: estado = "⚠️ Bajo Carga"
                if carga_real > data['carga_max']: estado = "⛔ Sobrecarga"
                
                load_data.append({
                    "Profesor": prof,
                    "Carga Real": carga_real,
                    "Min": data['carga_min'],
                    "Max": data['carga_max'],
                    "Estado": estado
                })
            
            df_load = pd.DataFrame(load_data)
            st.dataframe(df_load.style.apply(lambda x: ['background-color: #ffcccc' if '⛔' in str(v) else '' for v in x], axis=1))

            # Descarga
            st.download_button("Descargar Excel Resultado", df_res.to_csv(index=False), "horario_final.csv")

if __name__ == "__main__":
    main()
