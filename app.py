import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from datetime import time as dtime
import matplotlib.pyplot as plt
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA "WHITE PLATINUM" (MODIFICADO)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v14", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Playfair+Display:wght@700&display=swap');
    
    .stApp { 
        background-color: #FFFFFF;
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 40px 40px;
        color: #1f2937; 
    }

    .math-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 40px 60px;
        background: #FFFFFF;
        border-bottom: 4px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }

    .title-box h1 { 
        font-family: 'Playfair Display', serif !important; 
        color: #1a1a1a !important; 
        font-size: 3rem !important;
        margin: 0 !important;
        letter-spacing: -1px;
    }
    
    .subtitle {
        color: #D4AF37;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: 2px;
        font-size: 0.8rem;
        margin-top: 5px;
    }

    .glass-card { 
        background: #FFFFFF; 
        border-radius: 12px; 
        padding: 30px; 
        border: 1px solid #e5e7eb; 
        margin-bottom: 25px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
    }

    .stButton>button { 
        background: #1a1a1a !important; 
        color: white !important; 
        font-weight: 600 !important; 
        border-radius: 8px !important; 
        height: 50px;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: #D4AF37 !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2);
    }

    [data-testid="stSidebar"] { 
        background-color: #f9fafb; 
        border-right: 1px solid #e5e7eb; 
    }

    .status-badge { 
        background: #fffbeb; 
        border: 1px solid #D4AF37; 
        color: #b45309; 
        padding: 10px 20px; 
        border-radius: 9999px; 
        font-size: 0.75rem;
        font-weight: 700;
        text-align: center;
    }
</style>

<div class="math-header">
    <div style="font-size: 2.5rem; color: #D4AF37;">∫</div>
    <div class="title-box">
        <h1>UPRM Scheduler <span style="color: #D4AF37;">Platinum</span></h1>
        <div class="subtitle">OPTIMIZACIÓN POR COMPACTACIÓN & DEMANDA INTELIGENTE v14</div>
    </div>
    <div style="font-size: 2.5rem; color: #D4AF37;">∑</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. TABLAS Y LÓGICA DE NEGOCIO (SIN CAMBIOS)
# ==============================================================================
COMPENSACION_TABLE = [
    (1, 1, 44, 0.0), (1, 45, 74, 0.5), (1, 75, 104, 1.0), (1, 105, 134, 1.5), (1, 135, 164, 2.0),
    (2, 1, 37, 0.0), (2, 38, 52, 0.5), (2, 53, 67, 1.0), (2, 68, 82, 1.5), (2, 83, 97, 2.0),
    (2, 98, 112, 2.5), (2, 113, 127, 3.0), (2, 128, 142, 3.5), (2, 143, 147, 4.0),
    (3, 1, 34, 0.0), (3, 35, 44, 0.5), (3, 45, 54, 1.0), (3, 55, 64, 1.5), (3, 65, 74, 2.0),
    (3, 75, 84, 2.5), (3, 85, 94, 3.0), (3, 95, 104, 3.5), (3, 105, 114, 4.0), (3, 115, 124, 4.5),
    (3, 125, 134, 5.0), (3, 135, 144, 5.5), (3, 145, 154, 6.0),
    (4, 1, 33, 0.0), (4, 34, 41, 0.5), (4, 42, 48, 1.0), (4, 49, 56, 1.5), (4, 57, 63, 2.0),
    (4, 64, 71, 2.5), (4, 72, 78, 3.0), (4, 79, 86, 3.5), (4, 87, 93, 4.0), (4, 94, 101, 4.5),
    (4, 102, 108, 5.0), (4, 109, 116, 5.5), (4, 117, 123, 6.0), (4, 124, 131, 6.5), (4, 132, 138, 7.0),
    (4, 139, 146, 7.5), (4, 147, 153, 8.0),
    (5, 1, 32, 0.0), (5, 33, 38, 0.5), (5, 39, 44, 1.0), (5, 45, 50, 1.5), (5, 51, 56, 2.0),
    (5, 57, 62, 2.5), (5, 63, 68, 3.0), (5, 69, 74, 3.5), (5, 75, 80, 4.0), (5, 81, 86, 4.5),
    (5, 87, 92, 5.0), (5, 93, 98, 5.5), (5, 99, 104, 6.0), (5, 105, 110, 6.5), (5, 111, 116, 7.0),
    (5, 117, 122, 7.5), (5, 123, 128, 8.0)
]

def get_creditos_reales(creditos_base, cupo):
    for (cb, min_est, max_est, extra) in COMPENSACION_TABLE:
        if cb == creditos_base and min_est <= cupo <= max_est:
            return float(creditos_base) + extra
    return float(creditos_base)

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def str_to_mins(t_str):
    t_str = str(t_str).strip().upper()
    parts = t_str.split()
    time_part = parts[0]
    ampm = parts[1] if len(parts) > 1 else "AM"
    h, m = map(int, time_part.split(':'))
    if ampm == "PM" and h != 12: h += 12
    if ampm == "AM" and h == 12: h = 0
    return h * 60 + m

PATRONES = {
    3: [
        {"name": "Lu-Mi-Vi", "days": {"Lu": 1, "Mi": 1, "Vi": 1}, "type": "MWF"},
        {"name": "Ma-Ju", "days": {"Ma": 1.5, "Ju": 1.5}, "type": "TTH"},
        {"name": "Lu (Int)", "days": {"Lu": 3}, "type": "INT"},
        {"name": "Ma (Int)", "days": {"Ma": 3}, "type": "INT"},
        {"name": "Mi (Int)", "days": {"Mi": 3}, "type": "INT"},
        {"name": "Ju (Int)", "days": {"Ju": 3}, "type": "INT"},
        {"name": "Vi (Int)", "days": {"Vi": 3}, "type": "INT"},
    ],
    4: [
        {"name": "Lu-Ma-Mi-Ju", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1}, "type": "MIX"},
        {"name": "Lu-Mi", "days": {"Lu": 2, "Mi": 2}, "type": "MWF"},
        {"name": "Ma-Ju", "days": {"Ma": 2, "Ju": 2}, "type": "TTH"},
    ],
    5: [
        {"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}, "type": "MIX"},
        {"name": "Lu-Mi-Vi", "days": {"Lu": 2, "Mi": 2, "Vi": 1}, "type": "MWF"},
    ]
}

def compatible_tipo(curso_tipo, salon_tipo):
    salon_cat = int(float(salon_tipo))
    if curso_tipo == 2: return salon_cat == 2
    if curso_tipo == 3: return salon_cat == 3
    return salon_cat != 2

# ==============================================================================
# 3. CLASES DE DATOS (MODIFICADO)
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.cands = [c.strip().upper() for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']
        self.tipo_salon = int(float(tipo_salon))
        self.prof_preasignado = None
        self.es_grande = self.cupo >= 85
        self.es_fusionable = self.cod.split('-')[0] in ["MATE3171", "MATE3172", "MATE3173"]

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas, bloqueos_info, prefs_cursos, compensacion, acepta_grandes, cursos_intensivos):
        self.nombre = nombre.upper().strip()
        self.carga_min = float(carga_min) if pd.notnull(carga_min) else 0.0
        self.carga_max = float(carga_max) if pd.notnull(carga_max) else 12.0
        self.pref_horas = str(pref_horas).upper().strip() if pd.notnull(pref_horas) else 'ANY'
        self.compensacion = str(compensacion).upper().strip() in ('SI', 'SÍ', 'YES', '1')
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) else 0
        self.cursos_intensivos = int(cursos_intensivos) if pd.notnull(cursos_intensivos) else 0
        self.bloqueos = bloqueos_info # Lista de (dias_set, start, end)
        self.pref_dias_set = set() # Parsear pref_dias...
        self.preferencias = prefs_cursos

# ==============================================================================
# 4. MOTOR DE OPTIMIZACIÓN (MODIFICADO)
# ==============================================================================
class TabuScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        self.salones = []
        for _, r in df_salones.iterrows():
            self.salones.append({
                'CODIGO': str(r['CODIGO']).strip().upper(),
                'CAPACIDAD': int(r['CAPACIDAD']),
                'TIPO': float(r['TIPO'])
            })
        
        self.profesores = {}
        for _, r in df_profes.iterrows():
            bloqueos = []
            if pd.notnull(r.get('BLOQUEO_DIAS')):
                dias = set(str(r['BLOQUEO_DIAS']).upper().replace(' ','').split(','))
                try:
                    ini = str_to_mins(r['BLOQUEO_HORA_INI'])
                    fin = str_to_mins(r['BLOQUEO_HORA_FIN'])
                    bloqueos.append((dias, ini, fin))
                except: pass
            
            p = Profesor(
                nombre=r['NOMBRE'], carga_min=r['CARGA_MIN'], carga_max=r['CARGA_MAX'],
                pref_dias=r['PREF_DIAS'], pref_horas=r['PREF_HORAS'],
                bloqueos_info=bloqueos,
                prefs_cursos=[str(r.get(f'PREF{i}','')).strip().upper() for i in range(1,4)],
                compensacion=r['COMPENSACION'], acepta_grandes=r['ACEPTA_GRANDES'],
                cursos_intensivos=r['CURSOS_INTENSIVOS']
            )
            self.profesores[p.nombre] = p

        # LÓGICA DE SECCIONES MEJORADA (REGLA CUPO/2)
        self.secciones = []
        for _, r in df_cursos.iterrows():
            cod = str(r['CODIGO']).strip().upper()
            demanda = int(r['DEMANDA'])
            cupo = int(r['CUPO'])
            
            num_completas = demanda // cupo
            sobrante = demanda % cupo
            
            total_sec = num_completas
            if sobrante >= (cupo / 2):
                total_sec += 1
            
            for i in range(total_sec):
                # Si es la última sección y hubo sobrante >= cupo/2, su cupo es el sobrante
                # pero si el sobrante es muy pequeño y total_sec aumentó, distribuimos
                est_sec = cupo if (i < num_completas) else sobrante
                self.secciones.append(Seccion(f"{cod}-{i+1:02d}", r['CREDITOS'], est_sec, r['CANDIDATOS'], r['TIPO_SALON']))

        self._preasignar_profesores()
        
        self.limite_operativo = (450, 1110) if zona == "CENTRAL" else (420, 1080)
        self.bloques = list(range(self.limite_operativo[0], self.limite_operativo[1]-50, 30))
        self.solucion = self._construir_inicial()
        self.mejor_solucion = deepcopy(self.solucion)
        self.mejor_costo = 99999999
        self.historial = []

    def _preasignar_profesores(self):
        carga = {p: 0.0 for p in self.profesores}
        for s in self.secciones:
            # Intentar asignar a alguien con carga disponible
            cands = [c for c in s.cands if c in self.profesores]
            random.shuffle(cands)
            asignado = False
            for c in cands:
                cred = get_creditos_reales(s.creditos, s.cupo) if self.profesores[c].compensacion else float(s.creditos)
                if carga[c] + cred <= self.profesores[c].carga_max:
                    s.prof_preasignado = c
                    carga[c] += cred
                    asignado = True
                    break
            if not asignado:
                # REGLA 5: Si no hay profesor disponible, asignar TBA
                s.prof_preasignado = "TBA"

    def _construir_inicial(self):
        sol = []
        for s in self.secciones:
            patron = random.choice(PATRONES.get(s.creditos, PATRONES[3]))
            ini = random.choice(self.bloques)
            salon = random.choice(self.salones)['CODIGO']
            sol.append({'seccion': s, 'profesor': s.prof_preasignado, 'salon': salon, 'patron': patron, 'ini': ini})
        return sol

    def _costo_total(self, sol):
        hard = 0
        soft = 0
        occ_prof = {}
        occ_salon = {}
        prof_day_types = {} # Para compactación

        for a in sol:
            s, p, sl, pat, ini = a['seccion'], a['profesor'], a['salon'], a['patron'], a['ini']
            
            # Compactación (Restricción Fuerte Solicitada)
            if p != "TBA" and p != "GRADUADOS":
                if p not in prof_day_types: prof_day_types[p] = set()
                prof_day_types[p].add(pat['type'])
            
            # Cruces y Horarios
            for dia, dur in pat['days'].items():
                fin = ini + int(dur * 50)
                if fin > self.limite_operativo[1]: hard += 10000
                
                # Cruce Prof
                if p != "TBA":
                    key_p = (p, dia)
                    if key_p in occ_prof:
                        for (e_i, e_f) in occ_prof[key_p]:
                            if max(ini, e_i) < min(fin, e_f): hard += 10000
                    occ_prof.setdefault(key_p, []).append((ini, fin))
                
                # Cruce Salon
                key_s = (sl, dia)
                if key_s in occ_salon:
                    for (e_i, e_f) in occ_salon[key_s]:
                        if max(ini, e_i) < min(fin, e_f): hard += 10000
                occ_salon.setdefault(key_s, []).append((ini, fin))

            # Capacidad y Tipo
            s_info = next(x for x in self.salones if x['CODIGO'] == sl)
            if s_info['CAPACIDAD'] < s.cupo: hard += 5000
            if not compatible_tipo(s.tipo_salon, s_info['TIPO']): hard += 5000

        # Penalización por No Compactación (Regla 1)
        for p, types in prof_day_types.items():
            # Si un profesor tiene más de un tipo de bloque (ej. MWF y TTH), penalización fuerte
            if len(types) > 1:
                hard += 20000 * (len(types) - 1)
        
        return hard + soft, hard, soft

    def optimizar(self, iterations, bar, status):
        curr_sol = deepcopy(self.solucion)
        curr_cost, _, _ = self._costo_total(curr_sol)
        
        for i in range(iterations):
            idx = random.randint(0, len(curr_sol)-1)
            old_val = curr_sol[idx]
            
            # Mutación
            mode = random.random()
            if mode < 0.3: # Cambiar hora
                curr_sol[idx]['ini'] = random.choice(self.bloques)
            elif mode < 0.6: # Cambiar salón
                curr_sol[idx]['salon'] = random.choice(self.salones)['CODIGO']
            else: # Cambiar patrón
                curr_sol[idx]['patron'] = random.choice(PATRONES.get(curr_sol[idx]['seccion'].creditos, PATRONES[3]))
            
            new_cost, h, s = self._costo_total(curr_sol)
            
            if new_cost < curr_cost or random.random() < math.exp((curr_cost - new_cost) / (500 / (i+1))):
                curr_cost = new_cost
                if new_cost < self.mejor_costo:
                    self.mejor_costo = new_cost
                    self.mejor_solucion = deepcopy(curr_sol)
            else:
                curr_sol[idx] = old_val
            
            self.historial.append(self.mejor_costo)
            
            if i % 50 == 0:
                # Calcular % de cumplimiento suave (estimado)
                duros = int(h // 10000)
                # Estimamos cumplimiento suave: si soft=0 es 100%, pero como no hay límite superior, usamos una escala relativa
                cumplimiento_suave = max(0, 100 - (s / 100)) 
                status.markdown(f"""
                <div class="status-badge">
                GEN {i}/{iterations} | CONFLICTOS: {duros} | CUMPLIMIENTO PREF: {cumplimiento_suave:.1f}%
                </div>
                """, unsafe_allow_html=True)
                bar.progress(i / iterations)
        
        return self.mejor_solucion

# ==============================================================================
# 5. VISUALIZACIONES (MODIFICADO)
# ==============================================================================
def generar_heatmap_v14(scheduler, solucion):
    dias = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    # Horas de 7 AM a 7 PM
    horas = list(range(scheduler.limite_operativo[0], scheduler.limite_operativo[1], 30))
    
    # Eje X: Días, Eje Y: Horas (Solicitado por el usuario)
    matriz = np.zeros((len(horas), len(dias)))
    
    for a in solucion:
        if a['salon'] == "TBA": continue
        for dia, dur in a['patron']['days'].items():
            if dia in dias:
                d_idx = dias.index(dia)
                for m in range(a['ini'], a['ini'] + int(dur*50), 30):
                    if m in horas:
                        h_idx = horas.index(m)
                        matriz[h_idx, d_idx] += 1

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matriz, cmap='YlOrBr', aspect='auto')
    
    ax.set_xticks(range(len(dias)))
    ax.set_xticklabels(dias, fontweight='bold')
    
    ax.set_yticks(range(0, len(horas), 2))
    ax.set_yticklabels([mins_to_str(horas[i]) for i in range(0, len(horas), 2)])
    
    plt.colorbar(im, label='Num. Secciones simultáneas')
    ax.set_title('OCUPACIÓN DE PLANTA FÍSICA', pad=20, fontweight='bold')
    
    # Estética blanca
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f9fafb')
    plt.tight_layout()
    return fig

# ==============================================================================
# 6. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### ⚙️ Parámetros")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        iteraciones = st.slider("Intensidad de Búsqueda", 500, 10000, 3000)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])
        
        if st.button("Generar Datos de Prueba"):
            st.info("Suba un archivo con hojas 'Cursos', 'Profesores' y 'Salones'")

    if not file:
        st.info("Esperando archivo de protocolo para iniciar el motor...")
    else:
        if st.button("🚀 EJECUTAR OPTIMIZACIÓN PLATINUM"):
            xls = pd.ExcelFile(file)
            df_c = pd.read_excel(xls, 'Cursos')
            df_p = pd.read_excel(xls, 'Profesores')
            df_s = pd.read_excel(xls, 'Salones')
            
            engine = TabuScheduler(df_c, df_p, df_s, zona)
            
            bar = st.progress(0)
            status = st.empty()
            
            start = time.time()
            mejor_sol = engine.optimizar(iteraciones, bar, status)
            end = time.time()
            
            st.session_state.engine = engine
            st.session_state.mejor_sol = mejor_sol
            st.session_state.runtime = end - start
            
            # Preparar Master
            st.session_state.master = pd.DataFrame([{
                'ID': a['seccion'].cod,
                'Curso': a['seccion'].cod.split('-')[0],
                'Cupo': a['seccion'].cupo,
                'Profesor': a['profesor'],
                'Patrón': a['patron']['name'],
                'Horario': f"{mins_to_str(a['ini'])}",
                'Salón': a['salon']
            } for a in mejor_sol])

    if 'master' in st.session_state:
        st.balloons()
        st.success(f"Procesado en {st.session_state.runtime:.2f}s")
        
        t1, t2, t3 = st.tabs(["📋 HORARIO MAESTRO", "📊 MÉTRICAS & HEATMAP", "👤 VISTA POR PROFESOR"])
        
        with t1:
            st.dataframe(st.session_state.master, use_container_width=True)
            
        with t2:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("### Compactación de Recursos")
                fig = generar_heatmap_v14(st.session_state.engine, st.session_state.mejor_sol)
                st.pyplot(fig)
            with col2:
                st.markdown("### Convergencia")
                fig2, ax2 = plt.subplots()
                ax2.plot(st.session_state.engine.historial, color='#D4AF37')
                ax2.set_yscale('log')
                ax2.set_title("Reducción de Conflictos")
                st.pyplot(fig2)
                
        with t3:
            profes = sorted(st.session_state.master['Profesor'].unique())
            p_sel = st.selectbox("Ver profesor:", profes)
            st.table(st.session_state.master[st.session_state.master['Profesor'] == p_sel])

if __name__ == "__main__":
    main()
