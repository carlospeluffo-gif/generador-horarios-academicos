import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
from datetime import datetime

# ==============================================================================
# 1. ARQUITECTURA VISUAL: PLATINUM HYPER-ENGINE
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v3", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    .stApp { background: radial-gradient(circle at top, #1a1a1a 0%, #000000 100%); color: #e0e0e0; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #D4AF37 !important; text-align: center; text-shadow: 2px 2px 10px rgba(212, 175, 55, 0.3); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 25px; border: 1px solid rgba(212, 175, 55, 0.2); backdrop-filter: blur(10px); margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; color: white !important; font-weight: bold !important; border-radius: 2px !important; width: 100%; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
    .math-text { font-family: 'Source Code Pro', monospace; color: #B8860B; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)
# ==============================================================================
# 2. CORE ENGINE: OPTIMIZACIÓN DE ALTO VOLUMEN
# ==============================================================================

class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False, grad_owner=None):
        self.cod = cod
        self.creditos = creditos
        self.cupo = cupo
        self.cands = cands
        self.tipo_salon = tipo_salon
        self.es_ayudantia = es_ayudantia
        self.grad_owner = grad_owner

class UPRMEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona):
        self.zona = zona
        self.salones = df_salones.to_dict('records')
        self.profesores = {str(r['Nombre']).upper().strip(): r for _, r in df_profes.iterrows()}
        
        # Mapa de Graduados (Matemáticas)
        self.graduados_config = {}
        for _, r in df_grad.iterrows():
            nombre = str(r['NOMBRE_GRADUADO']).upper().strip()
            self.graduados_config[nombre] = {
                'recibe': [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()],
                'creditos_dar': r['CREDITOS_A_DICTAR']
            }
            
        self.oferta = self._build_oferta(df_cursos)
        
        # Parámetros de Tiempo (Standard UPRM)
        if zona == "CENTRAL":
            self.start, self.end, self.h_univ = 450, 1140, (630, 750) # 7:30am - 7:00pm | Block: 10:30-12:30
        else:
            self.start, self.end, self.h_univ = 420, 1080, (600, 720) # 7:00am - 6:00pm | Block: 10:00-12:00

    def _build_oferta(self, df_c):
        items = []
        # Cursos regulares
        for _, r in df_c.iterrows():
            cands = [c.strip().upper() for c in str(r['CANDIDATOS']).split(',') if c.strip()]
            for i in range(int(r['CANT_SECCIONES'])):
                items.append(SeccionData(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], r['CUPO'], cands, r['TIPO_SALON']))
        
        # Ayudantías Graduados
        for nombre, config in self.graduados_config.items():
            items.append(SeccionData(f"GRAD-{nombre[:4]}", config['creditos_dar'], 1, [nombre], "OFICINA", True, nombre))
        return items

    def check_grad_conflict(self, prof_name, dias, ini, fin, current_schedule_map):
        """Verifica si un graduado está tomando una clase en el horario que pretende dictar."""
        if prof_name not in self.graduados_config:
            return False # No es graduado, no hay conflicto de este tipo
        
        clases_que_toma = self.graduados_config[prof_name]['recibe']
        dias_set = set(["Lu", "Mi", "Vi"] if dias == "LuMiVi" else ["Ma", "Ju"])
        
        for cod_curso in clases_que_toma:
            if cod_curso in current_schedule_map:
                clase_info = current_schedule_map[cod_curso]
                dias_clase = set(["Lu", "Mi", "Vi"] if clase_info['dias'] == "LuMiVi" else ["Ma", "Ju"])
                
                # Si coinciden los días, ver solapamiento
                if dias_set.intersection(dias_clase):
                    if max(ini, clase_info['ini']) < min(fin, clase_info['fin']):
                        return True # ¡CONFLICTO! Está en clase mientras debería dar clase
        return False

    def solve(self, pop_size=50, generations=100):
        # Inicialización de población
        population = [self._create_random_ind() for _ in range(pop_size)]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for gen in range(generations):
            # Scoring
            scored = []
            for ind in population:
                score, schedule_map = self._fitness(ind)
                scored.append((score, ind, schedule_map))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            
            # Elitismo
            new_gen = [x[1] for x in scored[:5]]
            
            while len(new_gen) < pop_size:
                p1, p2 = random.sample(scored[:15], 2)
                child = self._crossover(p1[1], p2[1])
                if random.random() < 0.2: self._mutate(child)
                new_gen.append(child)
                
            population = new_gen
            progress_bar.progress((gen + 1) / generations)
            status_text.markdown(f"**Generación {gen+1}/{generations}** | Mejor Fitness: `{scored[0][0]:.6f}`")
            
        return scored[0][1] # Retornar el mejor

    def _create_random_ind(self):
        ind = []
        for s in self.oferta:
            dias = "MaJu" if s.creditos >= 4 or random.random() > 0.5 else "LuMiVi"
            dur = 80 if dias == "MaJu" else 50
            h_ini = random.randrange(self.start, self.end - dur, 30)
            prof = random.choice(s.cands) if s.cands else "TBA"
            salon = random.choice(self.salones)['CODIGO'] if self.salones else "TBA"
            ind.append({'sec': s, 'prof': prof, 'salon': salon, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur})
        return ind

    def _fitness(self, ind):
        penalty = 0
        schedule_map = {item['sec'].cod.split('-')[0]: item for item in ind}
        occ_prof = {}
        occ_salon = {}
        
        for g in ind:
            # 1. Bloqueo Universitario (INVIOLABLE)
            if g['dias'] == "MaJu":
                if max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                    penalty += 10**8
            
            # 2. Conflicto Graduado (INVIOLABLE para Matemáticas)
            if self.check_grad_conflict(g['prof'], g['dias'], g['ini'], g['fin'], schedule_map):
                penalty += 10**9
            
            # 3. Preferencias del Profesor
            if g['prof'] in self.profesores:
                pref = self.profesores[g['prof']]
                if str(pref['Pref_Dias']) != "Cualquiera" and pref['Pref_Dias'] != g['dias']: penalty += 500
                if pref['Pref_Horario'] == "AM" and g['ini'] > 720: penalty += 500
                if pref['Pref_Horario'] == "PM" and g['ini'] <= 720: penalty += 500
            
            # 4. Colisiones Físicas
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    p_key, s_key = (g['prof'], d, t), (g['salon'], d, t)
                    if p_key in occ_prof and g['prof'] != "TBA": penalty += 10**6
                    if s_key in occ_salon and g['salon'] != "TBA": penalty += 10**6
                    occ_prof[p_key] = True
                    occ_salon[s_key] = True
                    
        return 1 / (1 + penalty), schedule_map

    def _crossover(self, p1, p2):
        point = random.randint(0, len(p1)-1)
        return p1[:point] + p2[point:]

    def _mutate(self, ind):
        i = random.randint(0, len(ind)-1)
        dur = 80 if ind[i]['dias'] == "MaJu" else 50
        ind[i]['ini'] = random.randrange(self.start, self.end - dur, 30)
        ind[i]['fin'] = ind[i]['ini'] + dur

# ==============================================================================
# 3. INTERFAZ Y UTILIDADES DE EXPORTACIÓN
# ==============================================================================

def format_time(m):
    h, mins = divmod(int(m), 60)
    return f"{h if h<=12 else h-12:02d}:{mins:02d} {'AM' if h<12 else 'PM'}"

def get_excel_template():
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as w:
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CANT_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(w, 'Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'Pref_Dias', 'Pref_Horario']).to_excel(w, 'Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(w, 'Salones', index=False)
        pd.DataFrame(columns=['NOMBRE_GRADUADO', 'CREDITOS_A_DICTAR', 'CODIGOS_RECIBE']).to_excel(w, 'Graduados', index=False)
    return out.getvalue()

def main():
    st.markdown("<h1 class='main-header'>UPRM PLATINUM HYPER-ENGINE</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### `SYSTEM_CONFIG`")
        zona = st.selectbox("Campus Zone", ["CENTRAL", "PERIFERICA"])
        pop = st.select_slider("Heuristic Population", options=[20, 50, 100, 200], value=50)
        gens = st.select_slider("Iterations", options=[50, 100, 300, 500], value=100)
        file = st.file_uploader("Upload Excel Protocol", type=['xlsx'])
    
    if not file:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            <div class='glass-panel'>
                <h2>Protocolo de Carga</h2>
                <p>Bienvenido al motor de nivel corporativo para la UPRM. Este sistema está diseñado para:</p>
                <ul>
                    <li>Bloquear automáticamente la <b>Hora Universal</b> según zona.</li>
                    <li>Sincronizar las clases que <b>toman</b> los graduados de Matemáticas con las que <b>dictan</b>.</li>
                    <li>Respetar preferencias de facultad y capacidades de salón.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("### Template")
            st.download_button("📥 DOWNLOAD V3.4 MASTER", get_excel_template(), "UPRM_Master_Template.xlsx")
    else:
        xls = pd.ExcelFile(file)
        if st.button("🚀 INICIAR OPTIMIZACIÓN MASIVA"):
            engine = UPRMEnterpriseEngine(
                pd.read_excel(xls, 'Cursos'),
                pd.read_excel(xls, 'Profesores'),
                pd.read_excel(xls, 'Salones'),
                pd.read_excel(xls, 'Graduados'),
                zona
            )
            
            with st.spinner("Analizando billones de combinaciones..."):
                mejor_ind = engine.solve(pop, gens)
                
                st.session_state.result = pd.DataFrame([{
                    'ID': i['sec'].cod,
                    'Persona': i['prof'],
                    'Días': i['dias'],
                    'Horario': f"{format_time(i['ini'])} - {format_time(i['fin'])}",
                    'Salón': i['salon'],
                    'Tipo': "AYUDANTÍA" if i['sec'].es_ayudantia else "REGULAR"
                } for i in mejor_ind])

    if 'result' in st.session_state:
        st.markdown("---")
        t1, t2, t3 = st.tabs(["📊 HORARIO MAESTRO", "👤 VISTA DOCENTE", "📑 EXPORTACIÓN"])
        
        with t1:
            st.data_editor(st.session_state.result, use_container_width=True, num_rows="dynamic")
            
        with t2:
            user = st.selectbox("Filtrar por Profesor/Graduado", st.session_state.result['Persona'].unique())
            st.table(st.session_state.result[st.session_state.result['Persona'] == user])
            
        with t3:
            st.markdown("### Finalizar Proceso")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.result.to_excel(writer, sheet_name='MAESTRO_UPRM', index=False)
                # Hojas por persona
                for p in st.session_state.result['Persona'].unique():
                    if p != "TBA":
                        st.session_state.result[st.session_state.result['Persona'] == p].to_excel(writer, sheet_name=str(p)[:31], index=False)
            
            st.download_button("💾 DESCARGAR REPORTE FINAL", output.getvalue(), "Horario_UPRM_Final.xlsx")

if __name__ == "__main__":
    main()
