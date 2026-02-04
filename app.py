import streamlit as st
import pandas as pd
import numpy as np
import random
import copy

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
        self.prefijo = "".join([c for c in self.codigo_base if c.isalpha()]) 
        
        if pd.isna(candidatos) or str(candidatos).strip() == "" or str(candidatos).upper() == "TBA":
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
        self.pref_dias = ["LU", "MA", "MI", "JU", "VI"]
        self.pref_horas = (420, 1260) 

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
# 2. FUNCIONES DE APOYO Y TIEMPOS
# ==============================================================================

def generar_bloques(zona):
    bloques = {}
    offset = 30 if zona == "CENTRAL" else 0
    dias_semana = {'LMWV': ['LU', 'MI', 'VI'], 'MJ': ['MA', 'JU']}
    for h in range(7, 21):
        inicio = h * 60 + offset
        bloques[f"LMWV_{inicio}"] = {'dias': dias_semana['LMWV'], 'inicio': inicio, 'dur': 50}
        if h < 20:
            bloques[f"MJ_{inicio}"] = {'dias': dias_semana['MJ'], 'inicio': inicio, 'dur': 80}
    return bloques

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    ampm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {ampm}"

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

# ==============================================================================
# 3. MOTOR GENÉTICO
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
        oc_salon = {} 
        oc_prof = {}
        horario_estudiante = {}
        cargas = {p: 0 for p in self.profesores_dict}

        # 1. Mapa de Estudiantes (Doble Rol)
        for g in genes:
            bloque = self.bloques[g.bloque_key]
            for est_id in g.seccion.matriculados:
                for d in bloque['dias']:
                    key = (est_id, d)
                    if key not in horario_estudiante: horario_estudiante[key] = []
                    horario_estudiante[key].append((bloque['inicio'], bloque['inicio']+bloque['dur'], g.seccion.uid))

        for g in genes:
            b = self.bloques[g.bloque_key]
            ini, fin = b['inicio'], b['inicio'] + b['dur']
            
            # 2. Salones (Lógica Especial FA, FB, FC para LABs)
            es_lab_grande = "LAB" in g.seccion.codigo_base and g.salon_obj.codigo in ["F A", "F B", "F C"]
            for d in b['dias']:
                ks = (g.salon_obj.codigo, d)
                if ks not in oc_salon: oc_salon[ks] = []
                for (t1, t2, id_c, cod_base_c) in oc_salon[ks]:
                    if max(ini, t1) < min(fin, t2):
                        if not (es_lab_grande and "LAB" in cod_base_c):
                            errores.append(f"SALÓN: {g.salon_obj.codigo} choca {g.seccion.uid} con {id_c}")
                oc_salon[ks].append((ini, fin, g.seccion.uid, g.seccion.codigo_base))

            # 3. Profesores y Preferencias
            if g.profesor_nombre in self.profesores_dict:
                p = self.profesores_dict[g.profesor_nombre]
                cargas[g.profesor_nombre] += g.seccion.creditos
                if not all(d in p.pref_dias for d in b['dias']):
                    errores.append(f"PREF_DIA: {p.nombre} no puede los {b['dias']}")
                if ini < p.pref_horas[0] or (ini + b['dur']) > p.pref_horas[1]:
                    errores.append(f"PREF_HORA: {p.nombre} fuera de rango")

                for d in b['dias']:
                    kp = (g.profesor_nombre, d)
                    if kp in oc_prof:
                        for (t1, t2, id_c) in oc_prof[kp]:
                            if max(ini, t1) < min(fin, t2):
                                errores.append(f"PROFESOR: {p.nombre} choca en {g.seccion.uid}")
                    if kp not in oc_prof: oc_prof[kp] = []
                    oc_prof[kp].append((ini, fin, g.seccion.uid))
                    
                    # DOBLE ROL
                    if p.es_graduado:
                        ke = (p.estudiante_id, d)
                        if ke in horario_estudiante:
                            for (t1, t2, id_t) in horario_estudiante[ke]:
                                if max(ini, t1) < min(fin, t2):
                                    errores.append(f"DOBLE ROL: {p.nombre} dicta {g.seccion.uid} y toma {id_t}")

            # 4. Hora Universal
            if any(d in ['MA', 'JU'] for d in b['dias']):
                if max(ini, self.u_ini) < min(fin, self.u_fin):
                    errores.append(f"HORA UNIVERSAL: {g.seccion.uid} en asamblea")

        for p_nom, c in cargas.items():
            prof = self.profesores_dict[p_nom]
            if c > prof.carga_max: errores.append(f"CARGA: {p_nom} excede máximo")
            
        return errores

    def calcular_fitness(self, genes):
        return -len(self.analizar_conflictos(genes))

    def generar_individuo(self):
        genes = []
        for sec in self.secciones:
            prof = random.choice(sec.candidatos)
            bloque = random.choice(list(self.bloques.keys()))
            posibles = [s for s in self.salones if s.capacidad >= sec.cupo and s.tipo == sec.tipo_salon_req]
            salon = random.choice(posibles if posibles else self.salones)
            genes.append(HorarioGen(sec, prof, bloque, salon))
        return genes

    def evolucionar(self, pop_size, gens, callback):
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        mejor_historico = poblacion[0]
        mejor_fit = -999999

        for g in range(gens):
            poblacion.sort(key=lambda x: self.calcular_fitness(x), reverse=True)
            current_fit = self.calcular_fitness(poblacion[0])
            
            if current_fit > mejor_fit:
                mejor_fit = current_fit
                mejor_historico = copy.deepcopy(poblacion[0])
            
            callback(g, gens, abs(current_fit), poblacion[0])
            if current_fit == 0: break

            nueva_gen = poblacion[:10]
            while len(nueva_gen) < pop_size:
                hijo = copy.deepcopy(random.choice(poblacion[:20]))
                idx = random.randint(0, len(hijo)-1)
                hijo[idx].bloque_key = random.choice(list(self.bloques.keys()))
                nueva_gen.append(hijo)
            poblacion = nueva_gen
        return mejor_historico, abs(mejor_fit)

# ==============================================================================
# 4. INTERFAZ
# ==============================================================================

def main():
    st.set_page_config(page_title="UPRM Thesis Optimizer", layout="wide")
    st.title("🎓 Sistema de Planificación Académica (Tesis)")

    if 'prefs' not in st.session_state: st.session_state.prefs = {}

    with st.sidebar:
        st.header("⚙️ Configuración")
        file = st.file_uploader("Subir Excel", type=['xlsx'])
        zona = st.selectbox("Zona Horaria", ["CENTRAL", "PERIFERICA"])
        pop_size = st.slider("Población", 50, 300, 100)
        max_gens = st.slider("Generaciones", 50, 1000, 200)

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        st.sidebar.divider()
        st.sidebar.header("👨‍🏫 Preferencias de Profesores")
        p_sel = st.sidebar.selectbox("Profesor", sorted(df_pro['Nombre'].unique()))
        
        if p_sel not in st.session_state.prefs:
            st.session_state.prefs[p_sel] = {"dias": ["LU", "MA", "MI", "JU", "VI"], "horas": (420, 1260)}
        
        st.session_state.prefs[p_sel]["dias"] = st.sidebar.multiselect(f"Días para {p_sel}", ["LU", "MA", "MI", "JU", "VI"], default=st.session_state.prefs[p_sel]["dias"])
        st.session_state.prefs[p_sel]["horas"] = st.sidebar.slider(f"Rango Minutos (420=7am)", 420, 1260, st.session_state.prefs[p_sel]["horas"])

        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            secciones = explotar_secciones(df_cur)
            profesores = []
            for _, r in df_pro.iterrows():
                p = Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max'], r.get('ES_GRADUADO'), r.get('ESTUDIANTE_ID'))
                if p.nombre in st.session_state.prefs:
                    p.pref_dias = st.session_state.prefs[p.nombre]["dias"]
                    p.pref_horas = st.session_state.prefs[p.nombre]["horas"]
                profesores.append(p)

            salones = [Salon(r['CODIGO'], r['CAPACIDAD'], r['TIPO']) for _, r in df_sal.iterrows()]
            engine = EngineThesis(secciones, profesores, salones, zona)
            
            prog_bar = st.progress(0)
            status_txt = st.empty()
            
            def update_ui(g, t, f, ind):
                prog_bar.progress((g+1)/t)
                status_txt.info(f"🧬 Generación {g} | Conflictos: {f}")

            mejor_ind, final_f = engine.evolucionar(pop_size, max_gens, update_ui)

            if final_f == 0:
                st.balloons()
                st.success("✅ ¡Horario Perfecto!")
            else:
                st.warning(f"⚠️ Terminado con {final_f} conflictos.")
                with st.expander("Detalle de Conflictos Finales"):
                    for err in engine.analizar_conflictos(mejor_ind):
                        st.write(f"❌ {err}")

            st.divider()
            res_df = pd.DataFrame([{
                "Sección": g.seccion.uid, "Curso": g.seccion.nombre, "Prefijo": g.seccion.prefijo,
                "Profesor": g.profesor_nombre, "Días": "".join(engine.bloques[g.bloque_key]['dias']),
                "Inicio": mins_to_str(engine.bloques[g.bloque_key]['inicio']), "Salón": g.salon_obj.codigo
            } for g in mejor_ind])

            st.subheader("🔍 Filtros de Resultados")
            c1, c2, c3 = st.columns(3)
            f_p = c1.multiselect("Profesor", sorted(res_df['Profesor'].unique()))
            f_s = c2.multiselect("Salón", sorted(res_df['Salón'].unique()))
            f_d = c3.multiselect("Departamento", sorted(res_df['Prefijo'].unique()))

            if f_p: res_df = res_df[res_df['Profesor'].isin(f_p)]
            if f_s: res_df = res_df[res_df['Salón'].isin(f_s)]
            if f_d: res_df = res_df[res_df['Prefijo'].isin(f_d)]

            st.dataframe(res_df, use_container_width=True)

if __name__ == "__main__":
    main()
