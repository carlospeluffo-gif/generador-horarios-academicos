import streamlit as st
import pandas as pd
import random
import re
import copy
import time
import numpy as np

# ========================================================
# 1. CONFIGURACIÓN Y CONSTANTES (Contexto UPRM)
# ========================================================

MATEMATICAS_SALONES_FIJOS = [
    "M 102", "M 104", "M 203", "M 205", "M 316", "M 317", "M 402", "M 404"
]

class ZonaConfig:
    """Configuración de zonas Central y Periférica"""
    CENTRAL = {
        "nombre": "Zona Central",
        "horarios_inicio": ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30"],
        "restricciones": {"Ma": [("10:30", "12:30")], "Ju": [("10:30", "12:30")]}, # Hora universal
    }
    PERIFERICA = {
        "nombre": "Zona Periférica",
        "horarios_inicio": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"],
        "restricciones": {d: [("10:00", "12:00")] for d in ["Lu", "Ma", "Mi", "Ju", "Vi"]},
    }

# ========================================================
# 2. LÓGICA DE NEGOCIO Y UTILIDADES
# ========================================================

def a_minutos(hhmm):
    try:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    except:
        return 0

def generar_bloques_horarios():
    """Genera bloques de tiempo estándar (Genes posibles)"""
    bloques = []
    # 3 créditos (LuMiVi 1 hora)
    bloques.append({"dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3})
    # 3 créditos (MaJu 1.5 horas)
    bloques.append({"dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3})
    # 4 créditos (L-M-M-J)
    bloques.append({"dias": ["Lu","Ma","Mi","Ju"], "horas": [1,1,1,1], "creditos": 4})
    # 4 créditos (2 días x 2 horas)
    bloques.append({"dias": ["Lu","Mi"], "horas": [2,2], "creditos": 4})
    bloques.append({"dias": ["Ma","Ju"], "horas": [2,2], "creditos": 4})
    return bloques

def es_horario_valido_en_zona(dia, hora_inicio_str, duracion, zona_config):
    """Verifica si un bloque choca con la hora universal o restricciones de zona"""
    ini = a_minutos(hora_inicio_str)
    fin = ini + int(duracion * 60)
    
    restricciones = zona_config['restricciones']
    if dia in restricciones:
        for r_ini, r_fin in restricciones[dia]:
            r_ini_m = a_minutos(r_ini)
            r_fin_m = a_minutos(r_fin)
            # Si hay solapamiento con la restricción
            if not (fin <= r_ini_m or ini >= r_fin_m):
                return False
    return True

# ========================================================
# 3. ALGORITMO GENÉTICO (CORE DE LA TESIS)
# ========================================================

class ClaseGene:
    """Representa un GEN: Una asignación específica de un curso"""
    def __init__(self, curso_id, prof_id, bloque, hora_inicio, salon, curso_obj, prof_obj):
        self.curso_id = curso_id
        self.prof_id = prof_id
        self.bloque = bloque      # Estructura {dias, horas, creditos}
        self.hora_inicio = hora_inicio
        self.salon = salon
        self.curso_obj = curso_obj # Metadatos
        self.prof_obj = prof_obj   # Metadatos

class IndividuoHorario:
    """Representa un CROMOSOMA: Un horario completo"""
    def __init__(self, genes=None):
        self.genes = genes if genes else []
        self.fitness = 0.0
        self.hard_conflicts = 0
        self.soft_score = 0

    def calcular_fitness(self):
        """
        Función de Aptitud (Fitness Function).
        Objetivo: Maximizar Score.
        Formula: (Puntos Preferencias) - (Penalización Choques * 10000)
        """
        conflicto_penalty = 10000
        preference_reward = 10
        
        conflicts = 0
        soft_points = 0
        
        # Mapa de ocupación: (Dia, Minuto) -> [Recursos ocupados]
        # Recurso = ProfesorID o SalonID
        # Optimizamos comparando todos contra todos (O(N^2)) o usando buckets.
        # Para ~100 cursos, N^2 es aceptable en Python moderno.
        
        n = len(self.genes)
        for i in range(n):
            gene_a = self.genes[i]
            
            # 1. Evaluar Preferencias (Soft Constraints)
            # Días preferidos
            dias_pref = gene_a.prof_obj.get('dias_preferidos', [])
            for dia in gene_a.bloque['dias']:
                if dia in dias_pref:
                    soft_points += preference_reward
            
            # Turno preferido
            turno = gene_a.prof_obj.get('turno_preferido', 'Sin preferencia')
            hora_m = a_minutos(gene_a.hora_inicio)
            if turno == 'Mañana' and hora_m < a_minutos("12:30"): soft_points += 5
            elif turno == 'Tarde' and hora_m >= a_minutos("12:30"): soft_points += 5
            
            # 2. Evaluar Conflictos (Hard Constraints)
            for j in range(i + 1, n):
                gene_b = self.genes[j]
                
                # Chequear solapamiento temporal
                hay_solape = False
                for da, dura in zip(gene_a.bloque['dias'], gene_a.bloque['horas']):
                    for db, durb in zip(gene_b.bloque['dias'], gene_b.bloque['horas']):
                        if da == db:
                            ia = a_minutos(gene_a.hora_inicio)
                            fa = ia + int(dura * 60)
                            ib = a_minutos(gene_b.hora_inicio)
                            fb = ib + int(durb * 60)
                            
                            if not (fa <= ib or ia >= fb):
                                hay_solape = True
                                break
                    if hay_solape: break
                
                if hay_solape:
                    # Choque de Profesor (El mismo prof no puede estar en 2 sitios)
                    if gene_a.prof_id == gene_b.prof_id:
                        conflicts += 1
                    
                    # Choque de Salón (El mismo salón no puede tener 2 clases)
                    if gene_a.salon == gene_b.salon:
                        conflicts += 1

        self.hard_conflicts = conflicts
        self.soft_score = soft_points
        # El Fitness es negativo si hay conflictos, positivo si es válido
        self.fitness = soft_points - (conflicts * conflicto_penalty)
        return self.fitness

class AlgoritmoGenetico:
    def __init__(self, cursos_data, profes_data, zona_config, salones, population_size=50, mutation_rate=0.1):
        self.cursos_data = cursos_data # Lista aplanada de cursos
        self.profes_data = profes_data
        self.zona_config = zona_config
        self.salones = salones
        self.pop_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.bloques_ref = generar_bloques_horarios()

    def _crear_gen_aleatorio(self, curso_tuple):
        """Crea un gen válido aleatorio para un curso"""
        prof_nombre, curso, prof_data = curso_tuple
        
        # Filtrar bloques por créditos
        bloques_validos = [b for b in self.bloques_ref if b['creditos'] == curso['creditos']]
        if not bloques_validos: bloques_validos = self.bloques_ref[:1] # Fallback
        
        # Intentar encontrar slot válido en zona (max 50 intentos)
        for _ in range(50):
            bloque = random.choice(bloques_validos)
            hora = random.choice(self.zona_config['horarios_inicio'])
            salon = random.choice(self.salones)
            
            valido = True
            for d, dur in zip(bloque['dias'], bloque['horas']):
                if not es_horario_valido_en_zona(d, hora, dur, self.zona_config):
                    valido = False
                    break
            
            if valido:
                return ClaseGene(curso['codigo'], prof_nombre, bloque, hora, salon, curso, prof_data)
        
        # Si falla, devuelve uno cualquiera (el fitness lo penalizará)
        return ClaseGene(curso['codigo'], prof_nombre, bloques_validos[0], 
                         self.zona_config['horarios_inicio'][0], self.salones[0], curso, prof_data)

    def inicializar_poblacion(self):
        self.population = []
        # Preparamos la lista de cursos a programar
        cursos_flat = []
        for prof, data in self.profes_data.items():
            for curso in data['cursos']:
                cursos_flat.append((prof, curso, data))
        
        for _ in range(self.pop_size):
            genes = [self._crear_gen_aleatorio(c) for c in cursos_flat]
            ind = IndividuoHorario(genes)
            ind.calcular_fitness()
            self.population.append(ind)

    def seleccion_torneo(self, k=3):
        seleccionados = random.sample(self.population, k)
        return max(seleccionados, key=lambda x: x.fitness)

    def crossover(self, padre1, padre2):
        """Cruce uniforme: cada gen se toma de padre1 o padre2 al azar"""
        genes_hijo = []
        for g1, g2 in zip(padre1.genes, padre2.genes):
            if random.random() > 0.5:
                genes_hijo.append(copy.deepcopy(g1))
            else:
                genes_hijo.append(copy.deepcopy(g2))
        return IndividuoHorario(genes_hijo)

    def mutacion(self, individuo):
        """Mutación: Cambia la hora/salón de un gen al azar"""
        for i in range(len(individuo.genes)):
            if random.random() < self.mutation_rate:
                # Regenerar este gen
                gen_actual = individuo.genes[i]
                # Reconstruir tupla data
                data_tuple = (gen_actual.prof_id, gen_actual.curso_obj, gen_actual.prof_obj)
                individuo.genes[i] = self._crear_gen_aleatorio(data_tuple)
        individuo.calcular_fitness()

    def ejecutar(self, generaciones, progress_bar=None):
        self.inicializar_poblacion()
        mejor_historico = max(self.population, key=lambda x: x.fitness)
        
        for g in range(generaciones):
            nueva_poblacion = []
            
            # Elitismo: Pasar el mejor directamente
            mejor_gen = max(self.population, key=lambda x: x.fitness)
            if mejor_gen.fitness > mejor_historico.fitness:
                mejor_historico = copy.deepcopy(mejor_gen)
            nueva_poblacion.append(mejor_historico)
            
            while len(nueva_poblacion) < self.pop_size:
                p1 = self.seleccion_torneo()
                p2 = self.seleccion_torneo()
                hijo = self.crossover(p1, p2)
                self.mutacion(hijo)
                nueva_poblacion.append(hijo)
            
            self.population = nueva_poblacion
            
            if progress_bar:
                progress_bar.progress((g + 1) / generaciones)
        
        return mejor_historico

# ========================================================
# 4. PROCESADOR DE DATOS (EXCEL)
# ========================================================

class ProcesadorExcel:
    def __init__(self, file):
        self.file = file
        self.profesores_data = {}

    def procesar(self):
        try:
            df = pd.read_excel(self.file)
            # Normalización de columnas básica
            cols_map = {
                'SERIES': 'codigo', 'NAME SPA': 'nombre', 'CREDITS': 'creditos',
                'PROFESSORS': 'profesor', 'CAPACITY': 'cupo', 'PROFESSORS EMAIL': 'email'
            }
            # Intentar encontrar columnas que contengan las palabras clave
            found_cols = {}
            for key, val in cols_map.items():
                for col_excel in df.columns:
                    if key in str(col_excel).upper():
                        found_cols[key] = col_excel
                        break
            
            if len(found_cols) < 3: return False # Fallo crítico

            for _, row in df.iterrows():
                prof_raw = str(row.get(found_cols.get('PROFESSORS'), 'Sin Profesor'))
                # Limpiar nombre prof "Nombre (100%)" -> "Nombre"
                prof_match = re.search(r'(.+?)\s*\(', prof_raw)
                prof_nombre = prof_match.group(1) if prof_match else prof_raw
                
                if prof_nombre not in self.profesores_data:
                    self.profesores_data[prof_nombre] = {
                        'email': str(row.get(found_cols.get('PROFESSORS EMAIL'), '')),
                        'cursos': [],
                        'creditos_totales': 0,
                        'dias_preferidos': [],
                        'turno_preferido': 'Sin preferencia'
                    }
                
                curso = {
                    'codigo': str(row.get(found_cols.get('SERIES'), 'unk')),
                    'nombre': str(row.get(found_cols.get('NAME SPA'), 'unk')),
                    'creditos': int(row.get(found_cols.get('CREDITS'), 3)),
                    'estudiantes': int(row.get(found_cols.get('CAPACITY'), 30))
                }
                
                self.profesores_data[prof_nombre]['cursos'].append(curso)
                self.profesores_data[prof_nombre]['creditos_totales'] += curso['creditos']
            
            return True
        except Exception as e:
            st.error(f"Error procesando Excel: {e}")
            return False

# ========================================================
# 5. INTERFAZ DE USUARIO (STREAMLIT)
# ========================================================

def main():
    st.set_page_config(page_title="GA Scheduler UPRM", page_icon="🧬", layout="wide")
    
    st.title("🧬 Generador de Horarios con Algoritmos Genéticos")
    st.markdown("**Basado en la Tesis: Programación de Cursos Universitarios en la UPRM**")

    # --- SIDEBAR: Configuración ---
    st.sidebar.header("1. Configuración")
    zona_sel = st.sidebar.radio("Zona del Campus", ["Central", "Periférica"])
    zona_obj = ZonaConfig.CENTRAL if zona_sel == "Central" else ZonaConfig.PERIFERICA
    
    uploaded_file = st.sidebar.file_uploader("Cargar Excel (Formulario)", type=["xlsx"])
    
    # Session State Init
    if 'data_procesada' not in st.session_state: st.session_state.data_procesada = None
    if 'horario_final' not in st.session_state: st.session_state.horario_final = None
    
    # Procesar Archivo
    if uploaded_file:
        if st.sidebar.button("Procesar Datos", type="primary"):
            proc = ProcesadorExcel(uploaded_file)
            if proc.procesar():
                st.session_state.data_procesada = proc.profesores_data
                st.success("✅ Datos cargados correctamente")
                st.rerun()

    # --- CUERPO PRINCIPAL ---
    tab1, tab2, tab3 = st.tabs(["⚙️ Preferencias", "🧬 Algoritmo Genético", "📊 Resultados"])

    # TAB 1: Preferencias
    with tab1:
        if st.session_state.data_procesada:
            st.subheader("Preferencias de Profesores (Restricciones Suaves)")
            prof_sel = st.selectbox("Seleccionar Profesor", list(st.session_state.data_procesada.keys()))
            
            data_prof = st.session_state.data_procesada[prof_sel]
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"Cursos: {len(data_prof['cursos'])} | Créditos: {data_prof['creditos_totales']}")
                turno = st.radio("Turno Preferido", ["Mañana", "Tarde", "Sin preferencia"], key="t_pref")
                data_prof['turno_preferido'] = turno
                
            with col2:
                dias = st.multiselect("Días Preferidos", ["Lu", "Ma", "Mi", "Ju", "Vi"], 
                                    default=data_prof['dias_preferidos'], key="d_pref")
                data_prof['dias_preferidos'] = dias
            
            if st.button("Guardar Preferencias"):
                st.toast(f"Preferencias guardadas para {prof_sel}")
        else:
            st.info("👈 Carga un archivo Excel primero.")

    # TAB 2: Ejecución del GA
    with tab2:
        st.subheader("Configuración del Algoritmo Genético")
        
        col1, col2, col3 = st.columns(3)
        pop_size = col1.number_input("Tamaño Población", 10, 200, 50, step=10, help="Más población = Mejor exploración pero más lento")
        generaciones = col2.number_input("Generaciones", 10, 500, 50, step=10, help="Iteraciones del algoritmo")
        mutacion = col3.slider("Tasa de Mutación", 0.0, 1.0, 0.1, help="Probabilidad de cambio aleatorio")

        st.markdown("---")
        
        if st.button("🚀 Ejecutar Algoritmo Genético", type="primary", disabled=not st.session_state.data_procesada):
            
            with st.status("Evolucionando horarios...", expanded=True) as status:
                st.write("Inicializando población aleatoria...")
                progress = st.progress(0)
                
                # Instanciar GA
                ga = AlgoritmoGenetico(
                    cursos_data=None, # No se usa directamente, se extrae de profes_data
                    profes_data=st.session_state.data_procesada,
                    zona_config=zona_obj,
                    salones=MATEMATICAS_SALONES_FIJOS,
                    population_size=pop_size,
                    mutation_rate=mutacion
                )
                
                st.write("Compitiendo y mutando...")
                start_time = time.time()
                mejor_individuo = ga.ejecutar(generaciones, progress)
                end_time = time.time()
                
                status.update(label="¡Optimización Completada!", state="complete", expanded=False)
            
            # Guardar resultado
            st.session_state.horario_final = mejor_individuo
            
            # Mostrar métricas inmediatas
            c1, c2, c3 = st.columns(3)
            c1.metric("Fitness Score", f"{mejor_individuo.fitness:.0f}")
            c2.metric("Conflictos (Hard)", mejor_individuo.hard_conflicts, delta_color="inverse")
            c3.metric("Tiempo Ejecución", f"{end_time - start_time:.2f}s")
            
            if mejor_individuo.hard_conflicts > 0:
                st.error(f"⚠️ El mejor horario encontrado tiene {mejor_individuo.hard_conflicts} conflictos. Intenta aumentar las generaciones o la población.")
            else:
                st.balloons()
                st.success("✅ ¡Solución válida encontrada sin conflictos!")

    # TAB 3: Visualización
    with tab3:
        if st.session_state.horario_final:
            ind = st.session_state.horario_final
            
            # Convertir Individuo a DataFrame
            rows = []
            for g in ind.genes:
                for dia, dura in zip(g.bloque['dias'], g.bloque['horas']):
                    fin_min = a_minutos(g.hora_inicio) + int(dura * 60)
                    h_fin = f"{fin_min//60:02d}:{fin_min%60:02d}"
                    rows.append({
                        "Profesor": g.prof_id,
                        "Curso": g.curso_id,
                        "Nombre": g.curso_obj['nombre'],
                        "Día": dia,
                        "Inicio": g.hora_inicio,
                        "Fin": h_fin,
                        "Salón": g.salon
                    })
            
            df = pd.DataFrame(rows)
            
            st.subheader("Vista Tabla Detallada")
            st.dataframe(df, use_container_width=True)
            
            # Pivot Table Visual
            st.subheader("Matriz de Horario")
            try:
                pivot = df.pivot_table(index="Inicio", columns="Día", values="Curso", aggfunc=lambda x: ' | '.join(x))
                st.dataframe(pivot)
            except:
                st.warning("No se pudo generar la matriz visual (posibles datos vacíos)")
                
            # Descarga
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Horario (CSV)", csv, "horario_genetico.csv", "text/csv")
            
        else:
            st.info("Ejecuta el algoritmo para ver resultados aquí.")

if __name__ == "__main__":
    main()
