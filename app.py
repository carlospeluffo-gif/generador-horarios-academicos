import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import io

# ==============================================================================
# 1. MODELOS DE DATOS
# ==============================================================================

class Seccion:
    def __init__(self, uid, codigo_base, nombre, creditos, cupo, candidatos, tipo_salon, matriculados=None):
        self.uid = uid
        self.codigo_base = str(codigo_base).strip().upper()
        self.nombre = str(nombre).strip().upper()
        self.creditos = float(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_salon).strip().upper() if not pd.isna(tipo_salon) else "GENERAL"
        
        # Candidatos: Profesores asignables
        if pd.isna(candidatos) or str(candidatos).strip() == "":
            self.candidatos = ["TBA"]
        else:
            self.candidatos = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()]
        
        # Matriculados: IDs de estudiantes graduados que TOMAN esta clase
        if pd.isna(matriculados) or str(matriculados).strip() == "":
            self.matriculados = []
        else:
            self.matriculados = [m.strip().upper() for m in str(matriculados).split(',') if m.strip()]

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, estudiante_id=None):
        self.nombre = str(nombre).strip().upper()
        self.carga_min = float(c_min)
        self.carga_max = float(c_max)
        # Soporta 'SÍ', 'SI', 'TRUE' del nuevo excel
        self.es_graduado = str(es_graduado).upper() in ["SÍ", "SI", "TRUE", "1"]
        self.estudiante_id = str(estudiante_id).strip().upper() if not pd.isna(estudiante_id) else None

class Salon:
    def __init__(self, codigo, capacidad, tipo):
        self.codigo = str(codigo).strip().upper()
        self.capacidad = int(capacidad)
        self.tipo = str(tipo).strip().upper()

class HorarioGen:
    def __init__(self, seccion, profesor_nombre, bloque_key, salon_obj):
        self.seccion = seccion
        self.profesor_nombre = profesor_nombre
        self.bloque_key = bloque_key
        self.salon_obj = salon_obj

# ==============================================================================
# 2. CONFIGURACIÓN DE TIEMPOS Y BLOQUES
# ==============================================================================

def generar_bloques(zona):
    bloques = {}
    offset = 30 if zona == "CENTRAL" else 0
    # LMWV (Lunes, Miércoles, Viernes) - 50 min
    for h in range(7, 20):
        inicio = h * 60 + offset
        bloques[f"LMWV_{inicio}"] = {'dias': ['Lu', 'Mi', 'Vi'], 'inicio': inicio, 'dur': 50}
    # MJ (Martes, Jueves) - 80 min
    for h in range(7, 20):
        inicio = h * 60 + offset
        bloques[f"MJ_{inicio}"] = {'dias': ['Ma', 'Ju'], 'inicio': inicio, 'dur': 80}
    return bloques

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    ampm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {ampm}"

# ==============================================================================
# 3. MOTOR DE OPTIMIZACIÓN (ENGINE)
# ==============================================================================

class EngineThesis:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.bloques = generar_bloques(zona)
        # Hora Universal (Asamblea)
        self.u_ini, self.u_fin = (630, 750) if zona == "CENTRAL" else (600, 720)

    def analizar_conflictos(self, genes):
        errores = []
        oc_salon = {}
        oc_prof = {}
        horario_estudiante = {}
        cargas = {p: 0 for p in self.profesores_dict}

        # 1. Mapa de Estudiantes (quién toma qué y cuándo)
        for g in genes:
            bloque = self.bloques[g.bloque_key]
            for est_id in g.seccion.matriculados:
                for d in bloque['dias']:
                    key = (est_id, d)
                    if key not in horario_estudiante: horario_estudiante[key] = []
                    horario_estudiante[key].append((bloque['inicio'], bloque['inicio']+bloque['dur'], g.seccion.uid))

        # 2. Mapa de Profesores y Salones (quién dicta qué)
        for g in genes:
            b = self.bloques[g.bloque_key]
            ini, fin = b['inicio'], b['inicio'] + b['dur']
            
            # Conflictos de Salón
            for d in b['dias']:
                ks = (g.salon_obj.codigo, d)
                if ks in oc_salon:
                    for (t1, t2, id_c) in oc_salon[ks]:
                        if max(ini, t1) < min(fin, t2):
                            errores.append(f"SALÓN: {g.salon_obj.codigo} ocupado por {g.seccion.uid} y {id_c} el {d}")
                if ks not in oc_salon: oc_salon[ks] = []
                oc_salon[ks].append((ini, fin, g.seccion.uid))

            # Conflictos de Profesor y Doble Rol
            if g.profesor_nombre != "TBA":
                p_obj = self.profesores_dict.get(g.profesor_nombre)
                if p_obj:
                    cargas[g.profesor_nombre] += g.seccion.creditos
                    for d in b['dias']:
                        kp = (g.profesor_nombre, d)
                        if kp in oc_prof:
                            for (t1, t2, id_c) in oc_prof[kp]:
                                if max(ini, t1) < min(fin, t2):
                                    errores.append(f"PROFESOR: {g.profesor_nombre} choca {g.seccion.uid} con {id_c} el {d}")
                        if kp not in oc_prof: oc_prof[kp] = []
                        oc_prof[kp].append((ini, fin, g.seccion.uid))
                        
                        # DOBLE ROL: Si el profesor es graduado y está tomando clase a esa misma hora
                        if p_obj.es_graduado:
                            ke = (p_obj.estudiante_id, d)
                            if ke in horario_estudiante:
                                for (t1, t2, id_toma) in horario_estudiante[ke]:
                                    if max(ini, t1) < min(fin, t2):
                                        errores.append(f"DOBLE ROL: {p_obj.nombre} dicta {g.seccion.uid} pero toma {id_toma} el {d}")

            # Hora Universal (MJ)
            if any(d in ['Ma', 'Ju'] for d in b['dias']):
                if max(ini, self.u_ini) < min(fin, self.u_fin):
                    errores.append(f"HORA UNIVERSAL: {g.seccion.uid} invade bloque de asamblea")

        # 3. Cargas Académicas
        for p_nombre, carga in cargas.items():
            p = self.profesores_dict[p_nombre]
            if carga > p.carga_max:
                errores.append(f"CARGA: {p_nombre} tiene {carga} cr (Máx: {p.carga_max})")
            elif carga < p.carga_min:
                errores.append(f"CARGA: {p_nombre} tiene {carga} cr (Mín: {p.carga_min})")

        return errores

    def calcular_fitness(self, genes):
        return -len(self.analizar_conflictos(genes))

    def generar_individuo(self):
        genes = []
        for sec in self.secciones:
            prof = random.choice(sec.candidatos)
            bloque = random.choice(list(self.bloques.keys()))
            # Filtrar salones por capacidad y tipo
            posibles_salones = [s for s in self.salones if s.capacidad >= sec.cupo and s.tipo == sec.tipo_salon_req]
            if not posibles_salones: posibles_salones = self.salones
            salon = random.choice(posibles_salones)
            genes.append(HorarioGen(sec, prof, bloque, salon))
        return genes

    def evolucionar(self, pop_size, gens, callback):
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        for g in range(gens):
            scores = [(self.calcular_fitness(ind), ind) for ind in poblacion]
            scores.sort(key=lambda x: x[0], reverse=True)
            callback(g, gens, abs(scores[0][0]), scores[0][1])
            if scores[0][0] == 0: break
            
            nueva_gen = [scores[0][1], scores[1][1]] # Elitismo
            while len(nueva_gen) < pop_size:
                padre = copy.deepcopy(random.choice(scores[:10])[1])
                # Mutación dirigida
                idx = random.randint(0, len(padre)-1)
                padre[idx].bloque_key = random.choice(list(self.bloques.keys()))
                nueva_gen.append(padre)
            poblacion = nueva_gen
        return scores[0][1], abs(scores[0][0])

# ==============================================================================
# 4. PROCESADOR DE ENTRADAS (REGLAS NUEVAS)
# ==============================================================================

def explotar_secciones(df_cursos):
    secciones = []
    df_cursos = df_cursos.dropna(subset=['CODIGO', 'REGLAS'])
    
    for _, row in df_cursos.iterrows():
        try:
            codigo = str(row['CODIGO']).strip()
            demanda = int(row['DEMANDA_TOTAL'])
            reglas_str = str(row['REGLAS']).lower()
            atendido, idx = 0, 1
            
            # Separar por comas (ej: "4x30, resto15")
            partes_regla = [p.strip() for p in reglas_str.split(',')]
            
            for p in partes_regla:
                # Caso: 4x30
                if 'x' in p:
                    cant, cap = map(int, p.split('x'))
                    for _ in range(cant):
                        if atendido < demanda:
                            secciones.append(Seccion(f"{codigo}-{idx:03d}", codigo, row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                            atendido += cap; idx += 1
                # Caso: todas30, resto15
                elif 'todas' in p or 'resto' in p:
                    cap = int(''.join(filter(str.isdigit, p)))
                    while atendido < demanda:
                        secciones.append(Seccion(f"{codigo}-{idx:03d}", codigo, row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                        atendido += cap; idx += 1
        except:
            continue
    return secciones

# ==============================================================================
# 5. INTERFAZ STREAMLIT
# ==============================================================================

def main():
    st.set_page_config(page_title="UPRM Optimizer", layout="wide")
    st.title("🏛️ Sistema de Planificación Académica (Tesis)")
    
    with st.sidebar:
        st.header("⚙️ Parámetros")
        zona = st.selectbox("Zona Horaria", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("Subir Excel (Cursos, Profesores, Salones)", type=['xlsx'])
        pop_size = st.slider("Población", 50, 500, 100)
        max_gens = st.slider("Generaciones Máximas", 100, 2000, 500)

    if file:
        xls = pd.ExcelFile(file)
        if all(s in xls.sheet_names for s in ['Cursos', 'Profesores', 'Salones']):
            df_cur = pd.read_excel(xls, 'Cursos')
            df_pro = pd.read_excel(xls, 'Profesores')
            df_sal = pd.read_excel(xls, 'Salones')

            if st.button("🚀 INICIAR OPTIMIZACIÓN GENÉTICA"):
                secciones = explotar_secciones(df_cur)
                profesores = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max'], r.get('ES_GRADUADO'), r.get('ESTUDIANTE_ID')) for _, r in df_pro.iterrows()]
                salones = [Salon(r['CODIGO'], r['CAPACIDAD'], r['TIPO']) for _, r in df_sal.iterrows()]

                engine = EngineThesis(secciones, profesores, salones, zona)
                
                prog_bar = st.progress(0)
                status_txt = st.empty()
                log_expander = st.expander("🔍 Monitor de Conflictos Activos", expanded=True)

                def update_ui(g, t, f, mejor):
                    prog_bar.progress((g+1)/t)
                    status_txt.info(f"🧬 Generación {g} | Conflictos actuales: {f}")
                    if f > 0:
                        with log_expander:
                            st.write(engine.analizar_conflictos(mejor)[:10])

                mejor_ind, final_f = engine.evolucionar(pop_size, max_gens, update_ui)

                if final_f == 0:
                    st.balloons()
                    st.success("✅ ¡Horario Perfecto Encontrado sin Conflictos!")
                else:
                    st.warning(f"⚠️ Se alcanzó el límite con {final_f} conflictos.")

                # Resultados en DataFrame
                res_list = []
                for g in mejor_ind:
                    b = engine.bloques[g.bloque_key]
                    res_list.append({
                        "Sección": g.seccion.uid, "Curso": g.seccion.nombre, "Profesor": g.profesor_nombre,
                        "Días": "".join(b['dias']), "Inicio": mins_to_str(b['inicio']), "Salón": g.salon_obj.codigo
                    })
                st.subheader("🗓️ Horario Propuesto")
                st.dataframe(pd.DataFrame(res_list), use_container_width=True)
        else:
            st.error("Error: El archivo debe contener las pestañas 'Cursos', 'Profesores' y 'Salones'.")

if __name__ == "__main__":
    main()
