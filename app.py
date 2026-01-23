import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# 1. ESTÉTICA PLATINUM (SIN CAMBIOS VISUALES)
# ==============================================================================

st.set_page_config(page_title="UPRM Scheduler Platinum", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    /* FONDO GENERAL */
    .stApp {
        background-color: #000000;
        background-image: 
            linear-gradient(rgba(15, 15, 15, 0.50), rgba(15, 15, 15, 0.50)),
            url("https://www.transparenttextures.com/patterns/cubes.png");
        color: #ffffff;
    }
    
    /* TEXTOS GLOBALES */
    p, label, .stMarkdown, .stDataFrame, div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* TITULOS DORADOS */
    h1, h2, h3, h4 {
        color: #FFD700 !important;
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #080808;
        border-right: 1px solid #333;
    }
    
    /* BOTONES */
    .stButton>button {
        background: linear-gradient(90deg, #B8860B, #FFD700);
        color: #000 !important;
        font-weight: 800;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }
    
    /* INPUTS */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #444;
    }
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #222 !important;
    }
    
    /* TABLAS */
    [data-testid="stDataFrame"] {
        background-color: #111;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DE TIEMPO Y ZONAS
# ==============================================================================

def generar_bloques_por_zona(zona):
    bloques = {}
    if zona == "CENTRAL":
        horas_inicio = [h*60 + 30 for h in range(7, 20)] 
    else: # PERIFERICA
        horas_inicio = [h*60 for h in range(7, 20)]

    def add_b(id_base, dias, dur, lbl):
        for h in horas_inicio:
            if h + dur > 1320: continue 
            key = f"{id_base}_{h}"
            bloques[key] = {
                'id_base': id_base,
                'dias': dias,
                'inicio': h,
                'duracion': dur,
                'label': lbl 
            }

    # 3 CRÉDITOS
    add_b(1, ['Lu', 'Mi', 'Vi'], 50, "LMV")
    add_b(2, ['Ma', 'Ju'], 80, "MJ")
    # 4 CRÉDITOS
    add_b(8, ['Lu','Ma','Mi','Ju'], 50, "LMWJ")
    add_b(9, ['Lu','Ma','Mi','Vi'], 50, "LMWV")
    add_b(10,['Lu','Ma','Ju','Vi'], 50, "LMJV")
    add_b(11,['Lu','Mi','Ju','Vi'], 50, "LWJV")
    add_b(12,['Ma','Mi','Ju','Vi'], 50, "MJWV")
    add_b(13, ['Lu', 'Mi'], 110, "LW (Largo)")
    add_b(15, ['Ma', 'Ju'], 110, "MJ (Largo)")
    # 5 CRÉDITOS
    add_b(17, ['Lu','Ma','Mi','Ju','Vi'], 50, "Diario")

    return bloques

def get_hora_universal(zona):
    if zona == "CENTRAL": return (630, 750) # 10:30 - 12:30
    else: return (600, 720) # 10:00 - 12:00

def mins_to_str(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

def time_input_to_mins(t_obj):
    return t_obj.hour * 60 + t_obj.minute

# ==============================================================================
# 3. ESTRUCTURAS DE DATOS
# ==============================================================================

class Seccion:
    def __init__(self, uid, codigo, nombre, creditos, cupo, candidatos, tipo_salon_req):
        self.uid = uid
        self.codigo = str(codigo).strip().upper()
        self.nombre = str(nombre).strip()
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_salon_req).strip().upper()
        if pd.isna(candidatos) or str(candidatos).strip() == '':
            self.candidatos = []
        else:
            self.candidatos = [str(c).strip().upper() for c in str(candidatos).split(',') if str(c).strip()]
        self.es_grande = (self.cupo >= 85)

class Profesor:
    def __init__(self, nombre, carga_min, carga_max):
        self.nombre = str(nombre).strip().upper()
        self.carga_min = float(carga_min)
        self.carga_max = float(carga_max)

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
# 4. MOTOR INTELIGENTE (CON BALANCEO DE CARGA OBLIGATORIO)
# ==============================================================================

class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona, preferencias_profe):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.preferencias = preferencias_profe 
        
        self.bloques_tiempo = generar_bloques_por_zona(zona)
        self.hora_univ_range = get_hora_universal(zona)
        
        self.keys_3cr = [k for k, v in self.bloques_tiempo.items() if v['id_base'] <= 7]
        self.keys_4cr = [k for k, v in self.bloques_tiempo.items() if 8 <= v['id_base'] <= 16]
        self.keys_5cr = [k for k, v in self.bloques_tiempo.items() if v['id_base'] >= 17]
        
        self.dominios_salones = {}
        for sec in secciones:
            validos = [s for s in salones if s.capacidad >= sec.cupo]
            if sec.tipo_salon_req != 'GENERAL':
                validos = [s for s in validos if s.tipo == sec.tipo_salon_req]
            self.dominios_salones[sec.uid] = validos if validos else salones

    def es_compatible(self, bloque_key, profesor, salon_obj, ocupacion_profesores, ocupacion_salones):
        bloque = self.bloques_tiempo[bloque_key]
        inicio = bloque['inicio']
        fin = inicio + bloque['duracion']
        
        # 1. HORA UNIVERSAL
        if 'Ma' in bloque['dias'] or 'Ju' in bloque['dias']:
            u_ini, u_fin = self.hora_univ_range
            if max(inicio, u_ini) < min(fin, u_fin):
                return False

        # 2. PREFERENCIAS
        if profesor != "TBA" and profesor in self.preferencias:
            restricciones = self.preferencias[profesor]
            for r in restricciones:
                if r['dia'] in bloque['dias']:
                    if max(inicio, r['ini']) < min(fin, r['fin']):
                        return False 

        # 3. CHOQUE SALÓN
        for dia in bloque['dias']:
            key_s = (salon_obj.codigo, dia)
            if key_s in ocupacion_salones:
                for (t1, t2) in ocupacion_salones[key_s]:
                    if max(inicio, t1) < min(fin, t2): return False
        
        # 4. CHOQUE PROFESOR
        if profesor != "TBA":
            for dia in bloque['dias']:
                key_p = (profesor, dia)
                if key_p in ocupacion_profesores:
                    for (t1, t2) in ocupacion_profesores[key_p]:
                        if max(inicio, t1) < min(fin, t2): return False
                        
        return True

    def generar_individuo(self):
        genes = []
        oc_prof = {}
        oc_salon = {}
        
        # RASTREO DE CARGA EN TIEMPO REAL
        cargas_actuales = {p: 0 for p in self.profesores_dict}

        # Ordenar: Grandes primero
        secciones_ordenadas = sorted(self.secciones, key=lambda x: (not x.es_grande, random.random()))
        
        for sec in secciones_ordenadas:
            # SELECCIÓN DE PROFESOR CON PRIORIDAD DE CARGA MINIMA
            prof = "TBA"
            if sec.candidatos:
                # Filtrar candidatos que no excedan su máximo (considerando los créditos de este curso)
                validos = []
                for cand in sec.candidatos:
                    if cand in self.profesores_dict:
                        info = self.profesores_dict[cand]
                        if cargas_actuales[cand] + sec.creditos <= info.carga_max:
                            validos.append(cand)
                
                if validos:
                    # ORDENAR CANDIDATOS: 
                    # 1. Prioridad: Quienes NO han cumplido el mínimo.
                    # 2. Prioridad: Quienes tienen menos carga en general.
                    validos.sort(key=lambda c: (cargas_actuales[c] >= self.profesores_dict[c].carga_min, cargas_actuales[c]))
                    
                    # Escoger el más necesitado
                    prof = validos[0]
                    cargas_actuales[prof] += sec.creditos
                else:
                    # Si todos están llenos, asignar TBA (esto generará conflicto soft luego) o random
                    prof = "TBA"
            
            # SELECCIÓN DE HORARIO
            if sec.creditos == 3: pool_b = self.keys_3cr
            elif sec.creditos == 4: pool_b = self.keys_4cr
            else: pool_b = self.keys_5cr
            if not pool_b: pool_b = list(self.bloques_tiempo.keys())
            
            pool_s = self.dominios_salones[sec.uid]
            
            random.shuffle(pool_b)
            random.shuffle(pool_s)
            
            asignado = False
            for s in pool_s:
                for b in pool_b:
                    if self.es_compatible(b, prof, s, oc_prof, oc_salon):
                        bd = self.bloques_tiempo[b]
                        i, f = bd['inicio'], bd['inicio']+bd['duracion']
                        for d in bd['dias']:
                            ks = (s.codigo, d)
                            if ks not in oc_salon: oc_salon[ks] = []
                            oc_salon[ks].append((i, f))
                            if prof != "TBA":
                                kp = (prof, d)
                                if kp not in oc_prof: oc_prof[kp] = []
                                oc_prof[kp].append((i, f))
                        genes.append(HorarioGen(sec, prof, b, s))
                        asignado = True
                        break
                if asignado: break
            
            if not asignado:
                genes.append(HorarioGen(sec, prof, random.choice(pool_b), random.choice(pool_s)))
                
        return genes

    def detectar_conflictos(self, genes):
        conflictos = []
        oc_prof = {}
        oc_salon = {}
        
        # Calcular cargas finales para validación
        cargas_finales = {p: 0 for p in self.profesores_dict}

        for idx, gen in enumerate(genes):
            # Sumar carga
            if gen.profesor_nombre != "TBA" and gen.profesor_nombre in cargas_finales:
                cargas_finales[gen.profesor_nombre] += gen.seccion.creditos

            bloque = self.bloques_tiempo[gen.bloque_key]
            ini, end = bloque['inicio'], bloque['inicio'] + bloque['duracion']
            
            # Universal
            if 'Ma' in bloque['dias'] or 'Ju' in bloque['dias']:
                u_ini, u_fin = self.hora_univ_range
                if max(ini, u_ini) < min(end, u_fin):
                    conflictos.append(f"UNIV_IDX_{idx}")

            # Preferencias
            if gen.profesor_nombre != "TBA" and gen.profesor_nombre in self.preferencias:
                restricciones = self.preferencias[gen.profesor_nombre]
                for r in restricciones:
                    if r['dia'] in bloque['dias']:
                        if max(ini, r['ini']) < min(end, r['fin']):
                            conflictos.append(f"PREF_IDX_{idx}")
                            break

            for dia in bloque['dias']:
                # Salon
                ks = (gen.salon_obj.codigo, dia)
                if ks not in oc_salon: oc_salon[ks] = []
                for (t1, t2, o_idx) in oc_salon[ks]:
                    if max(ini, t1) < min(end, t2):
                        conflictos.append(f"SALON_{idx}_{o_idx}")
                oc_salon[ks].append((ini, end, idx))
                
                # Profesor
                if gen.profesor_nombre != "TBA":
                    kp = (gen.profesor_nombre, dia)
                    if kp not in oc_prof: oc_prof[kp] = []
                    for (t1, t2, o_idx) in oc_prof[kp]:
                        if max(ini, t1) < min(end, t2):
                            conflictos.append(f"PROF_{idx}_{o_idx}")
                    oc_prof[kp].append((ini, end, idx))
        
        # VALIDACIÓN DE CARGA MÍNIMA (NUEVO)
        # Si un profesor queda por debajo del mínimo, es un conflicto grave.
        for p_nombre, p_obj in self.profesores_dict.items():
            load = cargas_finales[p_nombre]
            if load < p_obj.carga_min and load > 0: 
                # Solo penalizamos si tiene algo asignado pero no llega al minimo. 
                # Si tiene 0 puede ser que no era candidato para nada (aunque raro).
                # Para forzar asignacion, penalizamos si load < min.
                conflictos.append(f"MINLOAD_{p_nombre}")

        return list(set(conflictos))

    def reparar(self, genes):
        rotos_ids = self.detectar_conflictos(genes)
        # Extraer indices numéricos de los strings de error
        rotos = []
        for r in rotos_ids:
            parts = r.split('_')
            # Intentar extraer números
            for p in parts:
                if p.isdigit(): rotos.append(int(p))
        
        rotos = list(set(rotos))
        if not rotos: return genes
        
        oc_prof = {}
        oc_salon = {}
        for i, gen in enumerate(genes):
            if i in rotos: continue
            bd = self.bloques_tiempo[gen.bloque_key]
            ini, end = bd['inicio'], bd['inicio']+bd['duracion']
            for d in bd['dias']:
                if gen.profesor_nombre!="TBA":
                    kp = (gen.profesor_nombre, d)
                    if kp not in oc_prof: oc_prof[kp]=[]
                    oc_prof[kp].append((ini,end))
                ks = (gen.salon_obj.codigo, d)
                if ks not in oc_salon: oc_salon[ks]=[]
                oc_salon[ks].append((ini,end))
        
        random.shuffle(rotos)
        for i in rotos:
            gen = genes[i]
            if gen.seccion.creditos==3: pool_b = self.keys_3cr
            elif gen.seccion.creditos==4: pool_b = self.keys_4cr
            else: pool_b = self.keys_5cr
            if not pool_b: pool_b = list(self.bloques_tiempo.keys())
            
            pool_s = self.dominios_salones[gen.seccion.uid]
            random.shuffle(pool_b)
            random.shuffle(pool_s)
            
            reparado = False
            for s in pool_s:
                for b in pool_b:
                    if self.es_compatible(b, gen.profesor_nombre, s, oc_prof, oc_salon):
                        gen.bloque_key = b
                        gen.salon_obj = s
                        # Update
                        bd = self.bloques_tiempo[b]
                        ini, end = bd['inicio'], bd['inicio']+bd['duracion']
                        for d in bd['dias']:
                            ks=(s.codigo,d)
                            if ks not in oc_salon: oc_salon[ks]=[]
                            oc_salon[ks].append((ini,end))
                            if gen.profesor_nombre!="TBA":
                                kp=(gen.profesor_nombre,d)
                                if kp not in oc_prof: oc_prof[kp]=[]
                                oc_prof[kp].append((ini,end))
                        reparado=True
                        break
                if reparado: break
        return genes

    def evolucionar(self, pop, gens, callback):
        poblacion = [self.generar_individuo() for _ in range(pop)]
        best_ind = None
        best_fit = -float('inf')
        
        for g in range(gens):
            scores = []
            for ind in poblacion:
                c = self.detectar_conflictos(ind)
                fit = -len(c)
                scores.append((fit, ind))
                if fit > best_fit:
                    best_fit = fit
                    best_ind = copy.deepcopy(ind)
            
            if best_fit == 0:
                callback(g, gens, 0)
                return best_ind, 0
            
            callback(g, gens, abs(best_fit))
            
            scores.sort(key=lambda x: x[0], reverse=True)
            nueva = [scores[0][1], scores[1][1]]
            while len(nueva) < pop:
                padre = random.choice(scores[:pop//2])[1]
                hijo = copy.deepcopy(padre)
                hijo = self.reparar(hijo)
                nueva.append(hijo)
            poblacion = nueva
            
        return best_ind, abs(best_fit)

# ==============================================================================
# 5. INTERFAZ GRÁFICA PLATINUM (PERSISTENTE)
# ==============================================================================

def main():
    # HEADER
    c1, c2 = st.columns([1, 6])
    with c1:
        st.write("") 
        st.markdown("<div style='font-size: 3rem;'>🏛️</div>", unsafe_allow_html=True)
    with c2:
        st.title("UPRM ACADEMIC SCHEDULER")
        st.caption("PLATINUM EDITION | BALANCED LOAD")

    st.markdown("---")

    # SIDEBAR
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        zona = st.selectbox("📍 Zona de Horarios", ["CENTRAL", "PERIFERICA"])
        if zona == "CENTRAL":
            st.info("Inicio: XX:30. Univ: 10:30-12:30.")
        else:
            st.info("Inicio: XX:00. Univ: 10:00-12:00.")
            
        st.markdown("---")
        uploaded_file = st.file_uploader("📂 Excel de Entrada", type=['xlsx'])
        
        st.markdown("### 🧬 IA Control")
        pop_size = st.slider("Población", 20, 200, 50)
        gen_count = st.slider("Generaciones", 10, 500, 80)

    # --- ESTADO DE SESIÓN (PERSISTENCIA) ---
    if 'prefs' not in st.session_state: st.session_state.prefs = {} 
    if 'horario_final' not in st.session_state: st.session_state.horario_final = None 
    if 'engine_data' not in st.session_state: st.session_state.engine_data = None 

    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            df_pro = pd.read_excel(xls, 'Profesores')
            df_cur = pd.read_excel(xls, 'Cursos')
            df_sal = pd.read_excel(xls, 'Salones')
            
            lista_profes = sorted([str(n).strip().upper() for n in df_pro['Nombre'].unique()])
            profesores_objs = [Profesor(row['Nombre'], row['Carga_Min'], row['Carga_Max']) for _, row in df_pro.iterrows()]
            
            # --- PREFERENCIAS ---
            with st.expander("🚫 Restricciones Horarias Docentes", expanded=True):
                c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns([2, 1, 1, 1, 1])
                with c_p1: prof_sel = st.selectbox("Profesor", lista_profes)
                with c_p2: dia_sel = st.selectbox("Día", ["Lu", "Ma", "Mi", "Ju", "Vi"])
                with c_p3: h_ini = st.time_input("Desde", value=datetime.strptime("07:30", "%H:%M"))
                with c_p4: h_fin = st.time_input("Hasta", value=datetime.strptime("12:00", "%H:%M"))
                with c_p5: 
                    st.write("")
                    add_btn = st.button("➕ Añadir")
                
                if add_btn:
                    if prof_sel not in st.session_state.prefs: st.session_state.prefs[prof_sel] = []
                    mini, mfin = time_input_to_mins(h_ini), time_input_to_mins(h_fin)
                    if mini >= mfin:
                        st.error("Error: Hora fin > inicio.")
                    else:
                        st.session_state.prefs[prof_sel].append({'dia': dia_sel, 'ini': mini, 'fin': mfin})
                        st.success(f"Bloqueado: {prof_sel} | {dia_sel}")

                if prof_sel in st.session_state.prefs:
                    st.caption(f"Restricciones para {prof_sel}:")
                    for r in st.session_state.prefs[prof_sel]:
                        st.code(f"{r['dia']}: {mins_to_str(r['ini'])} - {mins_to_str(r['fin'])}")

            # --- BOTON GENERAR ---
            st.markdown("###")
            if st.button("🚀 GENERAR HORARIO MAESTRO", type="primary", use_container_width=True):
                secciones = []
                for _, row in df_cur.iterrows():
                    qty = int(row.get('CANTIDAD_SECCIONES', 1))
                    for i in range(qty):
                        full_code = f"{row['CODIGO']}-{i+1:03d}"
                        secciones.append(Seccion(full_code, full_code, row.get('NOMBRE',''), row['CREDITOS'], row['CUPO'], row.get('CANDIDATOS'), row.get('TIPO_SALON','GENERAL')))
                
                salones = [Salon(row['CODIGO'], row['CAPACIDAD'], row['TIPO']) for _, row in df_sal.iterrows()]

                engine = PlatinumEngine(secciones, profesores_objs, salones, zona, st.session_state.prefs)
                
                bar = st.progress(0, text="Iniciando motor genético...")
                metric_ph = st.empty()
                
                def cb(g, tot, fit):
                    bar.progress((g+1)/tot, text=f"Evolución: {g+1}/{tot}")
                    metric_ph.metric("Conflictos Detectados", fit)
                
                best_ind, conflicts = engine.evolucionar(pop_size, gen_count, cb)
                bar.empty()
                metric_ph.empty()
                
                if conflicts == 0:
                    st.success("✨ ¡HORARIO PERFECTO GENERADO! (0 Conflictos)")
                    st.balloons()
                else:
                    st.warning(f"⚠️ El horario tiene {conflicts} conflictos (incluyendo carga baja).")

                rows = []
                for g in best_ind:
                    bd = engine.bloques_tiempo[g.bloque_key]
                    rows.append({
                        'Curso': g.seccion.codigo,
                        'Asignatura': g.seccion.nombre,
                        'Profesor': g.profesor_nombre,
                        'Días': "".join(bd['dias']),
                        'Hora Inicio': mins_to_str(bd['inicio']),
                        'Hora Fin': mins_to_str(bd['inicio'] + bd['duracion']),
                        'Salón': g.salon_obj.codigo,
                        'Cupo': g.seccion.cupo
                    })
                
                st.session_state.horario_final = pd.DataFrame(rows).sort_values('Curso')
                st.session_state.engine_data = {'profesores': profesores_objs}

            # --- MOSTRAR RESULTADOS ---
            if st.session_state.horario_final is not None:
                df_res = st.session_state.horario_final
                
                tab_table, tab_prof = st.tabs(["📅 HORARIO GENERAL", "👨‍🏫 DASHBOARD PROFESOR"])
                
                with tab_table:
                    st.dataframe(df_res, use_container_width=True, hide_index=True)
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer) as writer: df_res.to_excel(writer, index=False)
                    st.download_button("📥 Descargar Excel", buffer.getvalue(), f"Horario_{zona}.xlsx")
                
                with tab_prof:
                    col_sel, col_stats = st.columns([1, 3])
                    with col_sel:
                        p_view = st.selectbox("Ver Profesor:", lista_profes)
                        
                        df_p = df_res[df_res['Profesor'] == p_view]
                        
                        prof_objs = st.session_state.engine_data['profesores']
                        prof_obj = next((p for p in prof_objs if p.nombre == p_view), None)
                        if prof_obj:
                            st.caption("Límites de Carga:")
                            st.markdown(f"**Min:** {prof_obj.carga_min} | **Max:** {prof_obj.carga_max}")
                    
                    with col_stats:
                        if df_p.empty:
                            st.info("Este profesor no tiene cursos asignados.")
                        else:
                            st.markdown(f"**Horario Semanal: {p_view}**")
                            
                            plot_data = []
                            dia_map = {'Lu': '2023-01-02', 'Ma': '2023-01-03', 'Mi': '2023-01-04', 'Ju': '2023-01-05', 'Vi': '2023-01-06'}
                            
                            for _, row in df_p.iterrows():
                                dias_str = row['Días']
                                dias_list = [dias_str[i:i+2] for i in range(0, len(dias_str), 2)]
                                h_i = datetime.strptime(row['Hora Inicio'], "%I:%M %p")
                                h_f = datetime.strptime(row['Hora Fin'], "%I:%M %p")
                                
                                for d in dias_list:
                                    if d in dia_map:
                                        base_date = dia_map[d]
                                        start_dt = f"{base_date} {h_i.strftime('%H:%M:%S')}"
                                        end_dt = f"{base_date} {h_f.strftime('%H:%M:%S')}"
                                        plot_data.append({
                                            'Curso': row['Curso'],
                                            'Salón': row['Salón'],
                                            'Start': start_dt,
                                            'Finish': end_dt,
                                            'Día': d
                                        })
                            
                            df_plot = pd.DataFrame(plot_data)
                            if not df_plot.empty:
                                fig = px.timeline(df_plot, x_start="Start", x_end="Finish", y="Día", color="Curso", 
                                                  hover_data=['Salón'], title="", height=350)
                                fig.update_yaxes(categoryorder="array", categoryarray=['Vi', 'Ju', 'Mi', 'Ma', 'Lu'])
                                fig.update_layout(xaxis=dict(tickformat="%I:%M %p"), plot_bgcolor='#111', paper_bgcolor='#111', font_color='white')
                                st.plotly_chart(fig, use_container_width=True)
                            
                            carga_est = len(df_p) * 3 
                            fig_bar = go.Figure(go.Indicator(
                                mode = "gauge+number", value = carga_est,
                                title = {'text': "Carga Est. (Créditos)"},
                                gauge = {
                                    'axis': {'range': [0, 21]},
                                    'bar': {'color': "#FFD700"},
                                    'steps': [
                                        {'range': [0, prof_obj.carga_min], 'color': "#8B0000"},
                                        {'range': [prof_obj.carga_min, prof_obj.carga_max], 'color': "#006400"},
                                        {'range': [prof_obj.carga_max, 21], 'color': "#8B0000"}
                                    ]
                                }
                            ))
                            fig_bar.update_layout(height=200, margin=dict(l=20,r=20,t=30,b=20), paper_bgcolor='#000', font_color='white')
                            st.plotly_chart(fig_bar, use_container_width=True)

        except Exception as e:
            st.error(f"Error cargando datos: {e}")

if __name__ == "__main__":
    main()
