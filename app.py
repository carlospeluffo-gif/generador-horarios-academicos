import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px
import base64

# ==============================================================================
# 1. ESTÉTICA PREMIUM (BLACK & GOLD - UPRM STYLE)
# ==============================================================================

st.set_page_config(page_title="UPRM Scheduler Gold", page_icon="🏛️", layout="wide")

# CSS Profesional con Fondo Geométrico y Tema Dorado/Negro
st.markdown("""
<style>
    /* FONDO Y TEMA PRINCIPAL */
    .stApp {
        background-color: #0e0e0e;
        background-image: radial-gradient(#1c1c1c 1px, transparent 1px), radial-gradient(#1c1c1c 1px, transparent 1px);
        background-size: 40px 40px;
        background-position: 0 0, 20px 20px;
        color: #e0e0e0;
    }
    
    /* TÍTULOS */
    h1, h2, h3 {
        color: #FFD700 !important; /* DORADO */
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #333;
    }
    
    /* BOTONES PRIMARIOS (DORADOS) */
    .stButton>button {
        background: linear-gradient(145deg, #FFD700, #DAA520);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
        color: #000;
    }

    /* TARJETAS MÉTRICAS */
    div[data-testid="stMetricValue"] {
        color: #FFD700;
        font-size: 2rem !important;
    }
    div[data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* TABLAS */
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
        border-radius: 10px;
    }
    
    /* ALERTA DE ÉXITO */
    .stSuccess {
        background-color: rgba(0, 255, 127, 0.1);
        border-left: 5px solid #00FF7F;
        color: #00FF7F;
    }
    
    /* ALERTA DE ERROR */
    .stError {
        background-color: rgba(255, 69, 0, 0.1);
        border-left: 5px solid #FF4500;
        color: #FF4500;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DINÁMICA DE TIEMPO (ZONAS)
# ==============================================================================

def generar_bloques_por_zona(zona):
    """
    Genera el diccionario BLOQUES_TIEMPO dinámicamente según la zona.
    Zona Central: Inicio XX:30. Universal 10:30-12:30.
    Zona Periférica: Inicio XX:00. Universal 10:00-12:00.
    """
    bloques = {}
    
    # Configuración base
    if zona == "CENTRAL":
        offset_min = 30 # Empiezan y media
        # Horas inicio posibles (7:30, 8:30... hasta 19:30)
        # 7*60+30 = 450
        horas_inicio = [h*60 + 30 for h in range(7, 20)] 
    else: # PERIFERICA
        offset_min = 0  # Empiezan en punto
        # Horas inicio posibles (7:00, 8:00... hasta 19:00)
        horas_inicio = [h*60 for h in range(7, 20)]

    def add_b(id_base, dias, dur, lbl):
        for h in horas_inicio:
            # Filtro fin del día (Max 10 PM)
            if h + dur > 1320: continue
            
            key = f"{id_base}_{h}"
            h_str = mins_to_str(h)
            bloques[key] = {
                'id_base': id_base, # 1-7 (3cr), 8-16 (4cr), 17+ (5cr)
                'dias': dias,
                'inicio': h,
                'duracion': dur,
                'label': f"{lbl} ({h_str})"
            }

    # --- DEFINICIÓN DE PATRONES ---
    # 3 CRÉDITOS
    add_b(1, ['Lu', 'Mi', 'Vi'], 50, "LMV")
    add_b(2, ['Ma', 'Ju'], 80, "MJ") # 1h 20m
    
    # 4 CRÉDITOS
    add_b(8, ['Lu','Ma','Mi','Ju'], 50, "LMWJ")
    add_b(9, ['Lu','Ma','Mi','Vi'], 50, "LMWV")
    add_b(10,['Lu','Ma','Ju','Vi'], 50, "LMJV")
    add_b(11,['Lu','Mi','Ju','Vi'], 50, "LWJV")
    add_b(12,['Ma','Mi','Ju','Vi'], 50, "MJWV")
    add_b(13, ['Lu', 'Mi'], 110, "LW (Largo)") # Casi 2h
    add_b(15, ['Ma', 'Ju'], 110, "MJ (Largo)")

    # 5 CRÉDITOS
    add_b(17, ['Lu','Ma','Mi','Ju','Vi'], 50, "Diario")

    return bloques

def get_hora_universal(zona):
    """Retorna intervalo prohibido (inicio, fin) en minutos"""
    if zona == "CENTRAL":
        return (630, 750) # 10:30 - 12:30
    else:
        return (600, 720) # 10:00 - 12:00

def mins_to_str(minutes):
    h, m = minutes // 60, minutes % 60
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

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
# 4. MOTOR INTELIGENTE V5 (CON ZONAS Y PREFERENCIAS)
# ==============================================================================

class GoldenSchedulerEngine:
    def __init__(self, secciones, profesores, salones, zona, preferencias_profe):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.preferencias = preferencias_profe # Dict {Prof: [DiasProhibidos]}
        
        # 1. GENERAR BLOQUES SEGÚN ZONA
        self.bloques_tiempo = generar_bloques_por_zona(zona)
        self.hora_univ_range = get_hora_universal(zona)
        
        # Clasificar keys
        self.keys_3cr = [k for k, v in self.bloques_tiempo.items() if v['id_base'] <= 7]
        self.keys_4cr = [k for k, v in self.bloques_tiempo.items() if 8 <= v['id_base'] <= 16]
        self.keys_5cr = [k for k, v in self.bloques_tiempo.items() if v['id_base'] >= 17]
        
        # Dominios Salones
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
        
        # 1. HORA UNIVERSAL (Solo Martes y Jueves)
        if 'Ma' in bloque['dias'] or 'Ju' in bloque['dias']:
            u_ini, u_fin = self.hora_univ_range
            # Si el bloque se superpone aunque sea un minuto con la hora universal
            if max(inicio, u_ini) < min(fin, u_fin):
                return False

        # 2. PREFERENCIAS DEL PROFESOR (Restricción añadida)
        if profesor != "TBA" and profesor in self.preferencias:
            dias_prohibidos = self.preferencias[profesor]
            # Si el bloque tiene ALGÚN día prohibido, no es compatible
            for dia_bloque in bloque['dias']:
                if dia_bloque in dias_prohibidos:
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
        
        # Ordenar: Grandes primero para asegurar salón
        secciones_ordenadas = sorted(self.secciones, key=lambda x: (not x.es_grande, random.random()))
        
        for sec in secciones_ordenadas:
            # Seleccionar Profesor
            prof = random.choice(sec.candidatos) if sec.candidatos else "TBA"
            
            # Pool de Bloques
            if sec.creditos == 3: pool_b = self.keys_3cr
            elif sec.creditos == 4: pool_b = self.keys_4cr
            else: pool_b = self.keys_5cr
            if not pool_b: pool_b = list(self.bloques_tiempo.keys())
            
            # Pool Salones
            pool_s = self.dominios_salones[sec.uid]
            
            random.shuffle(pool_b)
            random.shuffle(pool_s)
            
            asignado = False
            # Greedy
            for s in pool_s:
                for b in pool_b:
                    if self.es_compatible(b, prof, s, oc_prof, oc_salon):
                        # Asignar
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
        
        for idx, gen in enumerate(genes):
            bloque = self.bloques_tiempo[gen.bloque_key]
            ini, end = bloque['inicio'], bloque['inicio'] + bloque['duracion']
            
            # Check Hora Universal
            if 'Ma' in bloque['dias'] or 'Ju' in bloque['dias']:
                u_ini, u_fin = self.hora_univ_range
                if max(ini, u_ini) < min(end, u_fin):
                    conflictos.append(idx)

            # Check Preferencias
            if gen.profesor_nombre != "TBA" and gen.profesor_nombre in self.preferencias:
                bad_days = self.preferencias[gen.profesor_nombre]
                for d in bloque['dias']:
                    if d in bad_days:
                        conflictos.append(idx) # Penalizar
                        break

            for dia in bloque['dias']:
                # Salón
                ks = (gen.salon_obj.codigo, dia)
                if ks not in oc_salon: oc_salon[ks] = []
                for (t1, t2, o_idx) in oc_salon[ks]:
                    if max(ini, t1) < min(end, t2):
                        conflictos.append(idx)
                        conflictos.append(o_idx)
                oc_salon[ks].append((ini, end, idx))
                
                # Profesor
                if gen.profesor_nombre != "TBA":
                    kp = (gen.profesor_nombre, dia)
                    if kp not in oc_prof: oc_prof[kp] = []
                    for (t1, t2, o_idx) in oc_prof[kp]:
                        if max(ini, t1) < min(end, t2):
                            conflictos.append(idx)
                            conflictos.append(o_idx)
                    oc_prof[kp].append((ini, end, idx))
        return list(set(conflictos))

    def reparar(self, genes):
        rotos = self.detectar_conflictos(genes)
        if not rotos: return genes
        
        # Mapa Sanos
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
# 5. INTERFAZ GRÁFICA (GUI PREMIUM)
# ==============================================================================

def main():
    # HEADER
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown("# 🏛️")
    with c2:
        st.title("UPRM ACADEMIC SCHEDULER")
        st.markdown("**GOLD EDITION V5.0** | Powered by Genetic Algorithms")

    st.markdown("---")

    # SIDEBAR
    with st.sidebar:
        st.header("⚙️ Configuración Global")
        
        # SELECTOR DE ZONA CRÍTICO
        zona = st.selectbox("📍 Selección de Zona", ["CENTRAL", "PERIFERICA"], 
                            help="Define hora de inicio (7:30 vs 7:00) y Hora Universal.")
        
        if zona == "CENTRAL":
            st.info("ℹ️ **Central:** Inicia :30. Univ: 10:30-12:30.")
        else:
            st.info("ℹ️ **Periférica:** Inicia :00. Univ: 10:00-12:00.")
            
        st.markdown("---")
        
        uploaded_file = st.file_uploader("📂 Cargar Datos (Excel)", type=['xlsx'])
        
        st.markdown("### 🧬 Parámetros IA")
        pop_size = st.slider("Población", 20, 200, 50)
        gen_count = st.slider("Generaciones", 10, 500, 80)

    # ESTADO DE LA SESIÓN (Para guardar preferencias)
    if 'prefs' not in st.session_state:
        st.session_state.prefs = {} # {NombreProf: [Dias]}

    # LOGICA PRINCIPAL
    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            df_pro = pd.read_excel(xls, 'Profesores')
            df_cur = pd.read_excel(xls, 'Cursos')
            df_sal = pd.read_excel(xls, 'Salones')
            
            # PREPARAR LISTA PROFESORES
            lista_profes = sorted([str(n).strip().upper() for n in df_pro['Nombre'].unique()])
            
            # --- PANEL DE PREFERENCIAS DOCENTES ---
            with st.expander("👨‍🏫 Gestión de Preferencias Docentes (Opcional)", expanded=True):
                col_p1, col_p2 = st.columns([1, 2])
                with col_p1:
                    prof_sel = st.selectbox("Seleccionar Profesor", lista_profes)
                with col_p2:
                    # Mostrar días prohibidos actuales
                    current_blocks = st.session_state.prefs.get(prof_sel, [])
                    days = st.multiselect(f"Días NO Disponibles para {prof_sel}", 
                                          ["Lu", "Ma", "Mi", "Ju", "Vi"], 
                                          default=current_blocks)
                    
                    if st.button("💾 Guardar Preferencia"):
                        st.session_state.prefs[prof_sel] = days
                        st.success(f"Preferencias guardadas para {prof_sel}: {days}")
            
            # Mostrar resumen de preferencias guardadas
            if st.session_state.prefs:
                st.caption(f"Profesores con restricciones manuales: {len(st.session_state.prefs)}")

            # --- BOTÓN DE ACCIÓN ---
            st.markdown("###")
            col_act1, col_act2, col_act3 = st.columns([1, 2, 1])
            with col_act2:
                run_btn = st.button("🚀 GENERAR HORARIO PROFESIONAL", use_container_width=True)

            if run_btn:
                # PROCESAR DATOS
                secciones = []
                for _, row in df_cur.iterrows():
                    qty = int(row.get('CANTIDAD_SECCIONES', 1))
                    for i in range(qty):
                        secciones.append(Seccion(f"{row['CODIGO']}-{i+1}", row['CODIGO'], row.get('NOMBRE',''), row['CREDITOS'], row['CUPO'], row.get('CANDIDATOS'), row.get('TIPO_SALON','GENERAL')))
                
                profesores = [Profesor(row['Nombre'], row['Carga_Min'], row['Carga_Max']) for _, row in df_pro.iterrows()]
                salones = [Salon(row['CODIGO'], row['CAPACIDAD'], row['TIPO']) for _, row in df_sal.iterrows()]

                # INICIAR ENGINE
                engine = GoldenSchedulerEngine(secciones, profesores, salones, zona, st.session_state.prefs)
                
                # BARRA PROGRESO PERSONALIZADA
                progress_text = "Optimizando red neuronal de horarios..."
                my_bar = st.progress(0, text=progress_text)
                
                col_m1, col_m2, col_m3 = st.columns(3)
                m1 = col_m1.empty()
                
                def ui_callback(g, tot, fit):
                    pct = (g+1)/tot
                    my_bar.progress(pct, text=f"Evolucionando Generación {g+1}/{tot}")
                    m1.metric("Conflictos Actuales", fit, delta_color="inverse")

                start_t = time.time()
                best_ind, conflicts = engine.evolucionar(pop_size, gen_count, ui_callback)
                duration = time.time() - start_t
                
                my_bar.empty()
                
                # --- RESULTADOS ---
                st.markdown("---")
                if conflicts == 0:
                    st.balloons()
                    st.markdown("""
                    <div style="background-color: #006400; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #00FF00;">
                        <h2 style="color: white !important; margin:0;">✨ HORARIO PERFECTO GENERADO ✨</h2>
                        <p style="color: #ddd; margin:0;">Se han cumplido todas las restricciones de zona, hora universal y preferencias.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ Se encontraron {conflicts} conflictos menores. Intenta aumentar las generaciones.")

                # DATA FRAME
                rows = []
                for g in best_ind:
                    bd = engine.bloques_tiempo[g.bloque_key]
                    rows.append({
                        'Curso': g.seccion.codigo,
                        'Sección': g.seccion.uid.split('-')[1],
                        'Profesor': g.profesor_nombre,
                        'Días': "".join(bd['dias']),
                        'Horario': bd['label'],
                        'Salón': g.salon_obj.codigo,
                        'Cupo': g.seccion.cupo
                    })
                
                df_res = pd.DataFrame(rows).sort_values('Curso')
                
                t1, t2 = st.tabs(["📅 VISTA TABULAR", "📊 ESTADÍSTICAS"])
                
                with t1:
                    st.dataframe(df_res, use_container_width=True)
                
                with t2:
                    c_chart1, c_chart2 = st.columns(2)
                    with c_chart1:
                        st.markdown("**Ocupación de Salones**")
                        pivot = df_res.groupby('Salón')['Curso'].count().reset_index()
                        fig = px.bar(pivot, x='Salón', y='Curso', color_discrete_sequence=['#FFD700'])
                        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                
                # DESCARGA
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer) as writer:
                    df_res.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DESCARGAR EXCEL OFICIAL",
                    data=buffer.getvalue(),
                    file_name=f"Horario_UPRM_{zona}.xlsx",
                    mime="application/vnd.ms-excel"
                )

        except Exception as e:
            st.error(f"Error Crítico: {e}")
    else:
        # PANTALLA DE BIENVENIDA
        st.markdown("""
        <div style="text-align: center; padding: 50px; opacity: 0.7;">
            <h3>Esperando archivo de datos...</h3>
            <p>Por favor carga el archivo Excel en el menú lateral para comenzar.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
