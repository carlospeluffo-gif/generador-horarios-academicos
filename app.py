import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import io
import plotly.express as px
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN Y ESTÉTICA
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Thesis Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    h1, h2, h3 { color: #FFD700 !important; }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MODELOS DE DATOS
# ==============================================================================

class Seccion:
    def __init__(self, uid, codigo_base, nombre, creditos, cupo, candidatos, tipo_salon, matriculados=None):
        self.uid = uid
        self.codigo_base = codigo_base
        self.nombre = nombre
        self.creditos = creditos
        self.cupo = cupo
        self.tipo_salon_req = str(tipo_salon).upper()
        self.candidatos = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()]
        # IDs de graduados que TOMAN esta sección
        self.matriculados = [m.strip().upper() for m in str(matriculados).split(',') if m.strip()] if matriculados else []

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, estudiante_id=None):
        self.nombre = str(nombre).strip().upper()
        self.carga_min = float(c_min)
        self.carga_max = float(c_max)
        self.es_graduado = str(es_graduado).upper() == "SI"
        self.estudiante_id = str(estudiante_id).strip().upper() if estudiante_id else None

class Salon:
    def __init__(self, codigo, capacidad, tipo):
        self.codigo = str(codigo).upper()
        self.capacidad = int(capacidad)
        self.tipo = str(tipo).upper()

class HorarioGen:
    def __init__(self, seccion, profesor_nombre, bloque_key, salon_obj):
        self.seccion = seccion
        self.profesor_nombre = profesor_nombre
        self.bloque_key = bloque_key
        self.salon_obj = salon_obj

# ==============================================================================
# 3. LÓGICA DE TIEMPO UPRM
# ==============================================================================

def generar_bloques(zona):
    bloques = {}
    offset = 30 if zona == "CENTRAL" else 0
    # LMV (50 min) y MJ (80 min)
    for h in range(7, 20):
        inicio = h * 60 + offset
        # LMV
        bloques[f"LMV_{inicio}"] = {'dias': ['Lu', 'Mi', 'Vi'], 'inicio': inicio, 'dur': 50, 'label': 'LMV'}
        # MJ
        bloques[f"MJ_{inicio}"] = {'dias': ['Ma', 'Ju'], 'inicio': inicio, 'dur': 80, 'label': 'MJ'}
    return bloques

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    ampm = "AM" if h < 12 else "PM"
    h = h if h <= 12 else h - 12
    if h == 0: h = 12
    return f"{h:02d}:{mins:02d} {ampm}"

# ==============================================================================
# 4. MOTOR DE OPTIMIZACIÓN (ALGORITMO GENÉTICO)
# ==============================================================================

class EngineThesis:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.grad_to_prof = {p.estudiante_id: p.nombre for p in profesores if p.es_graduado}
        self.salones = salones
        self.bloques = generar_bloques(zona)
        self.u_ini, self.u_fin = (630, 750) if zona == "CENTRAL" else (600, 720)

    def hay_traslape(self, b1_key, b2_key):
        b1, b2 = self.bloques[b1_key], self.bloques[b2_key]
        if not set(b1['dias']).intersection(b2['dias']): return False
        return max(b1['inicio'], b2['inicio']) < min(b1['inicio']+b1['dur'], b2['inicio']+b2['dur'])

    def calcular_fitness(self, genes):
        conflictos = 0
        oc_salon = {} # (salon, dia): [(ini, fin)]
        oc_prof = {}  # (prof, dia): [(ini, fin)]
        horario_estudiante = {} # (est_id, dia): [(ini, fin)]
        cargas = {p: 0 for p in self.profesores_dict}

        # Primera pasada: Registrar donde los graduados RECIBEN clase
        for g in genes:
            bloque = self.bloques[g.bloque_key]
            for est_id in g.seccion.matriculados:
                for d in bloque['dias']:
                    key = (est_id, d)
                    if key not in horario_estudiante: horario_estudiante[key] = []
                    horario_estudiante[key].append((bloque['inicio'], bloque['inicio']+bloque['dur']))

        # Segunda pasada: Validar choques
        for g in genes:
            b = self.bloques[g.bloque_key]
            ini, fin = b['inicio'], b['inicio'] + b['dur']
            
            # 1. Choque de Salon
            for d in b['dias']:
                ks = (g.salon_obj.codigo, d)
                if ks in oc_salon:
                    for (t1, t2) in oc_salon[ks]:
                        if max(ini, t1) < min(fin, t2): conflictos += 1
                if ks not in oc_salon: oc_salon[ks] = []
                oc_salon[ks].append((ini, fin))

            # 2. Choque de Profesor Y Doble Rol
            if g.profesor_nombre != "TBA":
                p_obj = self.profesores_dict[g.profesor_nombre]
                cargas[g.profesor_nombre] += g.seccion.creditos
                
                for d in b['dias']:
                    kp = (g.profesor_nombre, d)
                    # Choque docente
                    if kp in oc_prof:
                        for (t1, t2) in oc_prof[kp]:
                            if max(ini, t1) < min(fin, t2): conflictos += 1
                    if kp not in oc_prof: oc_prof[kp] = []
                    oc_prof[kp].append((ini, fin))
                    
                    # Choque Doble Rol (Graduado dando y recibiendo a la vez)
                    if p_obj.es_graduado:
                        ke = (p_obj.estudiante_id, d)
                        if ke in horario_estudiante:
                            for (t1, t2) in horario_estudiante[ke]:
                                if max(ini, t1) < min(fin, t2): conflictos += 10 # Penalidad alta

            # 3. Hora Universal
            if any(d in ['Ma', 'Ju'] for d in b['dias']):
                if max(ini, self.u_ini) < min(fin, self.u_fin): conflictos += 1

        # 4. Carga Académica
        for p_nombre, carga in cargas.items():
            p = self.profesores_dict[p_nombre]
            if carga < p.carga_min or carga > p.carga_max: conflictos += 1

        return -conflictos

    def generar_individuo(self):
        genes = []
        for sec in self.secciones:
            prof = random.choice(sec.candidatos) if sec.candidatos else "TBA"
            bloque = random.choice(list(self.bloques.keys()))
            salon = random.choice([s for s in self.salones if s.capacidad >= sec.cupo] or self.salones)
            genes.append(HorarioGen(sec, prof, bloque, salon))
        return genes

    def evolucionar(self, pop_size, gens, callback):
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        
        for g in range(gens):
            scores = [(self.calcular_fitness(ind), ind) for ind in poblacion]
            scores.sort(key=lambda x: x[0], reverse=True)
            
            callback(g, gens, abs(scores[0][0]))
            if scores[0][0] == 0: break

            # Elitismo + Cruce + Mutación simple
            nueva_gen = [scores[0][1], scores[1][1]]
            while len(nueva_gen) < pop_size:
                padre = random.choice(scores[:pop_size//2])[1]
                hijo = copy.deepcopy(padre)
                # Mutación: cambiar un curso al azar
                idx = random.randint(0, len(hijo)-1)
                hijo[idx].bloque_key = random.choice(list(self.bloques.keys()))
                nueva_gen.append(hijo)
            poblacion = nueva_gen
            
        return scores[0][1], abs(scores[0][0])

# ==============================================================================
# 5. EXPLOSIÓN DE DEMANDA (CORRECCIÓN ASESOR)
# ==============================================================================

def explotar_secciones(df_cursos):
    secciones = []
    for _, row in df_cursos.iterrows():
        demanda = int(row['DEMANDA_TOTAL'])
        reglas = str(row['REGLAS']).split(',')
        atendido = 0
        idx = 1
        for r in reglas:
            r = r.strip().upper()
            if 'X' in r:
                cant, cap = map(int, r.split('X'))
                for _ in range(cant):
                    if atendido < demanda:
                        secciones.append(Seccion(f"{row['CODIGO']}-{idx:03d}", row['CODIGO'], row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                        atendido += cap; idx += 1
            elif r.startswith('R'):
                cap = int(r[1:])
                while atendido < demanda:
                    secciones.append(Seccion(f"{row['CODIGO']}-{idx:03d}", row['CODIGO'], row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                    atendido += cap; idx += 1
    return secciones

# ==============================================================================
# 6. INTERFAZ PRINCIPAL
# ==============================================================================

def main():
    st.title("🏛️ UPRM Academic Planner - Tesis Edition")
    st.sidebar.header("Configuración")
    
    zona = st.sidebar.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
    file = st.sidebar.file_uploader("Cargar Excel", type=['xlsx'])
    pop = st.sidebar.slider("Población", 20, 100, 50)
    gens = st.sidebar.slider("Generaciones", 10, 500, 100)

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            secciones = explotar_secciones(df_cur)
            profesores = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max'], r.get('ES_GRADUADO'), r.get('ESTUDIANTE_ID')) for _, r in df_pro.iterrows()]
            salones = [Salon(r['CODIGO'], r['CAPACIDAD'], r['TIPO']) for _, r in df_sal.iterrows()]

            engine = EngineThesis(secciones, profesores, salones, zona)
            bar = st.progress(0)
            status = st.empty()

            def update(g, t, f):
                bar.progress((g+1)/t)
                status.write(f"🧬 Generación {g}/{t} | ⚠️ Conflictos: {f}")

            mejor_ind, conflictos = engine.evolucionar(pop, gens, update)

            # Resultados
            st.success(f"Proceso completado con {conflictos} conflictos.")
            data = []
            for g in mejor_ind:
                b = engine.bloques[g.bloque_key]
                data.append({
                    "Sección": g.seccion.uid, "Curso": g.seccion.nombre,
                    "Profesor": g.profesor_nombre, "Días": "".join(b['dias']),
                    "Horario": f"{mins_to_str(b['inicio'])} - {mins_to_str(b['inicio']+b['dur'])}",
                    "Salón": g.salon_obj.codigo
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)

if __name__ == "__main__":
    main()
