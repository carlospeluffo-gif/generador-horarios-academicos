import streamlit as st
import pandas as pd
import numpy as np
import random
import copy

# ==============================================================================
# 1. MODELOS DE DATOS MEJORADOS
# ==============================================================================

class Seccion:
    def __init__(self, uid, codigo_base, nombre, creditos, cupo, candidatos, tipo_salon, matriculados=None):
        self.uid = uid
        self.codigo_base = str(codigo_base).strip().upper()
        self.nombre = str(nombre).strip().upper()
        self.creditos = float(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_salon).strip().upper() if not pd.isna(tipo_salon) else "GENERAL"
        self.prefijo = "".join([c for c in self.codigo_base if c.isalpha()]) # Ej: MATE
        
        if pd.isna(candidatos) or str(candidatos).strip() == "":
            self.candidatos = ["TBA"]
        else:
            self.candidatos = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()]
        
        self.matriculados = [] if pd.isna(matriculados) else [m.strip().upper() for m in str(matriculados).split(',') if m.strip()]

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, estudiante_id=None):
        self.nombre = str(nombre).strip().upper()
        self.carga_min = float(c_min)
        self.carga_max = float(c_max)
        self.es_graduado = str(es_graduado).upper() in ["SÍ", "SI", "TRUE", "1"]
        self.estudiante_id = str(estudiante_id).strip().upper() if not pd.isna(estudiante_id) else None
        # Preferencias (se llenan desde la UI)
        self.pref_dias = []
        self.pref_horas = (7*60, 21*60)
        self.pref_cursos = []

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
# 2. CONFIGURACIÓN DE TIEMPOS
# ==============================================================================

def generar_bloques(zona):
    bloques = {}
    offset = 30 if zona == "CENTRAL" else 0
    # LMWV
    for h in range(7, 20):
        inicio = h * 60 + offset
        bloques[f"LMWV_{inicio}"] = {'dias': ['Lu', 'Mi', 'Vi'], 'inicio': inicio, 'dur': 50}
    # MJ
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
# 3. ENGINE (MOTOR DE TESIS)
# ==============================================================================

class EngineThesis:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.bloques = generar_bloques(zona)
        self.u_ini, self.u_fin = (630, 750) if zona == "CENTRAL" else (600, 720)

    def analizar_conflictos(self, genes):
        errores = []
        oc_salon = {} # (codigo, dia, bloque_key) -> lista de uids
        oc_prof = {}
        cargas = {p: 0 for p in self.profesores_dict}

        for g in genes:
            b = self.bloques[g.bloque_key]
            ini, fin = b['inicio'], b['inicio'] + b['dur']
            
            # 1. Conflictos de Salón (con lógica de Laboratorios en salones grandes FA, FB, FC)
            es_lab_grande = "LAB" in g.seccion.codigo_base and g.salon_obj.codigo in ["F A", "F B", "F C"]
            
            for d in b['dias']:
                ks = (g.salon_obj.codigo, d)
                if ks not in oc_salon: oc_salon[ks] = []
                
                for (t1, t2, id_c, cod_base_c) in oc_salon[ks]:
                    if max(ini, t1) < min(fin, t2):
                        # Si no es un laboratorio compartiendo un salón grande, hay conflicto
                        if not (es_lab_grande and "LAB" in cod_base_c):
                            errores.append(f"SALÓN: {g.salon_obj.codigo} choca {g.seccion.uid} con {id_c}")
                
                oc_salon[ks].append((ini, fin, g.seccion.uid, g.seccion.codigo_base))

            # 2. Conflictos de Profesor y Preferencias
            if g.profesor_nombre in self.profesores_dict:
                p = self.profesores_dict[g.profesor_nombre]
                cargas[g.profesor_nombre] += g.seccion.creditos
                
                # Restricciones de Preferencia (Hard)
                if p.pref_dias and not any(d in p.pref_dias for d in b['dias']):
                    errores.append(f"PREF_DIA: {p.nombre} no puede dar clase los {b['dias']}")
                
                if ini < p.pref_horas[0] or (ini + b['dur']) > p.pref_horas[1]:
                    errores.append(f"PREF_HORA: {p.nombre} fuera de su rango horario")

                for d in b['dias']:
                    kp = (g.profesor_nombre, d)
                    if kp in oc_prof:
                        for (t1, t2, id_c) in oc_prof[kp]:
                            if max(ini, t1) < min(fin, t2):
                                errores.append(f"PROFESOR: {p.nombre} choca en {g.seccion.uid}")
                    if kp not in oc_prof: oc_prof[kp] = []
                    oc_prof[kp].append((ini, fin, g.seccion.uid))

            # 3. Hora Universal
            if any(d in ['Ma', 'Ju'] for d in b['dias']):
                if max(ini, self.u_ini) < min(fin, self.u_fin):
                    errores.append(f"HORA_UNI: {g.seccion.uid} invade Asamblea")

        # 4. Cargas
        for p_nom, c in cargas.items():
            prof = self.profesores_dict[p_nom]
            if c > prof.carga_max: errores.append(f"CARGA: {p_nom} excede máx")
            
        return errores

    def calcular_fitness(self, genes):
        return -len(self.analizar_conflictos(genes))

    def mutar_dirigido(self, genes):
        # Seleccionamos un gen que esté involucrado en un conflicto (simplificado)
        idx = random.randint(0, len(genes)-1)
        sec = genes[idx].seccion
        genes[idx].bloque_key = random.choice(list(self.bloques.keys()))
        posibles = [s for s in self.salones if s.capacidad >= sec.cupo and s.tipo == sec.tipo_salon_req]
        if posibles: genes[idx].salon_obj = random.choice(posibles)
        return genes

    def evolucionar(self, pop_size, gens, callback):
        poblacion = [[HorarioGen(s, random.choice(s.candidatos), random.choice(list(self.bloques.keys())), random.choice(self.salones)) for s in self.secciones] for _ in range(pop_size)]
        
        mejor_global = None
        fit_max = -99999

        for g in range(gens):
            poblacion.sort(key=lambda x: self.calcular_fitness(x), reverse=True)
            actual_fit = self.calcular_fitness(poblacion[0])
            
            if actual_fit > fit_max:
                fit_max = actual_fit
                mejor_global = copy.deepcopy(poblacion[0])
            
            callback(g, gens, abs(actual_fit), poblacion[0])
            if actual_fit == 0: break

            nueva_gen = poblacion[:5] # Elitismo aumentado
            while len(nueva_gen) < pop_size:
                hijo = copy.deepcopy(random.choice(poblacion[:10]))
                nueva_gen.append(self.mutar_dirigido(hijo))
            poblacion = nueva_gen
            
        return mejor_global, abs(fit_max)

# ==============================================================================
# 4. INTERFAZ Y LÓGICA DE USUARIO
# ==============================================================================

def main():
    st.set_page_config(page_title="UPRM Schedule Thesis", layout="wide")
    st.title("🎓 Optimizador de Horarios Académicos UPRM")

    if 'profesores_obj' not in st.session_state: st.session_state.profesores_obj = []

    with st.sidebar:
        st.header("1. Carga de Datos")
        file = st.file_uploader("Archivo Excel", type=['xlsx'])
        zona = st.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
        pop_size = st.number_input("Población", 10, 500, 100)
        max_gens = st.number_input("Generaciones", 10, 5000, 200)

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        # Procesar Profesores y Preferencias
        profesores = []
        for _, r in df_pro.iterrows():
            p = Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max'], r.get('ES_GRADUADO'), r.get('ESTUDIANTE_ID'))
            profesores.append(p)
        
        st.sidebar.header("2. Preferencias de Profesores")
        p_sel_nom = st.sidebar.selectbox("Seleccionar Profesor", [p.nombre for p in profesores])
        p_sel = next(p for p in profesores if p.nombre == p_sel_nom)
        p_sel.pref_dias = st.sidebar.multiselect(f"Días para {p_sel_nom}", ["Lu", "Ma", "Mi", "Ju", "Vi"], default=["Lu", "Ma", "Mi", "Ju", "Vi"])
        p_sel.pref_horas = st.sidebar.slider(f"Rango Horario", 420, 1260, (420, 1260), format="") # 7am a 9pm en mins
        
        if st.button("🚀 GENERAR HORARIO OPTIMIZADO"):
            from funciones_aux import explotar_secciones # Asumiendo tu funcion de parseo
            secciones = explotar_secciones(df_cur)
            salones = [Salon(r['CODIGO'], r['CAPACIDAD'], r['TIPO']) for _, r in df_sal.iterrows()]
            
            engine = EngineThesis(secciones, profesores, salones, zona)
            prog = st.progress(0)
            status = st.empty()
            
            def update(g, t, f, ind):
                prog.progress((g+1)/t)
                status.info(f"Generación {g}/{t} | Conflictos: {f}")

            mejor, final_f = engine.evolucionar(pop_size, max_gens, update)

            if final_f > 0:
                st.error(f"Se encontraron {final_f} conflictos residuales:")
                st.write(engine.analizar_conflictos(mejor))
            else:
                st.balloons()
                st.success("¡Horario perfecto generado!")

            # RESULTADOS Y FILTROS
            res_df = pd.DataFrame([{
                "Sección": g.seccion.uid, "Curso": g.seccion.nombre, "Prefijo": g.seccion.prefijo,
                "Profesor": g.profesor_nombre, "Días": "".join(b['dias']), 
                "Inicio": mins_to_str(engine.bloques[g.bloque_key]['inicio']), "Salón": g.salon_obj.codigo
            } for g in mejor for b in [engine.bloques[g.bloque_key]]])

            st.divider()
            st.subheader("🔍 Visualización y Filtros")
            col1, col2 = st.columns(2)
            with col1:
                f_texto = st.text_input("Filtrar por nombre/profesor/salón")
            with col2:
                f_dep = st.multiselect("Filtrar por Departamento", res_df['Prefijo'].unique())

            filtered_df = res_df.copy()
            if f_texto:
                filtered_df = filtered_df[filtered_df.apply(lambda row: f_texto.upper() in row.astype(str).str.upper().values, axis=1)]
            if f_dep:
                filtered_df = filtered_df[filtered_df['Prefijo'].isin(f_dep)]

            st.dataframe(filtered_df, use_container_width=True)

# La funcion explotar_secciones debe estar definida igual que en tu codigo original
def explotar_secciones(df_cursos):
    secciones = []
    for _, row in df_cursos.iterrows():
        try:
            codigo = str(row['CODIGO']).strip()
            demanda = int(row['DEMANDA_TOTAL'])
            reglas_str = str(row['REGLAS']).lower()
            atendido, idx = 0, 1
            partes_regla = [p.strip() for p in reglas_str.split(',')]
            for p in partes_regla:
                if 'x' in p:
                    cant, cap = map(int, p.split('x'))
                    for _ in range(cant):
                        if atendido < demanda:
                            secciones.append(Seccion(f"{codigo}-{idx:03d}", codigo, row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                            atendido += cap; idx += 1
                elif 'todas' in p or 'resto' in p:
                    cap = int(''.join(filter(str.isdigit, p)))
                    while atendido < demanda:
                        secciones.append(Seccion(f"{codigo}-{idx:03d}", codigo, row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                        atendido += cap; idx += 1
        except: continue
    return secciones

if __name__ == "__main__":
    main()
