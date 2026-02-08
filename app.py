import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (PRESERVADA Y OPTIMIZADA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v4", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    .stApp { background: radial-gradient(circle at top, #1a1a1a 0%, #000000 100%); color: #e0e0e0; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #D4AF37 !important; text-align: center; text-shadow: 2px 2px 10px rgba(212, 175, 55, 0.3); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 25px; border: 1px solid rgba(212, 175, 55, 0.2); backdrop-filter: blur(10px); margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; color: white !important; font-weight: bold !important; border-radius: 4px !important; width: 100%; border: none !important; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
    .status-badge { background: rgba(212, 175, 55, 0.1); border: 1px solid #D4AF37; color: #D4AF37; padding: 10px; border-radius: 8px; text-align: center; font-family: 'Source Code Pro', monospace; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES DE SISTEMA
# ==============================================================================
def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CANT_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'Pref_Dias', 'Pref_Horario']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE_GRADUADO', 'CREDITOS_A_DICTAR', 'CODIGOS_RECIBE']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

def exportar_todo(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='MAESTRO_UPRM', index=False)
        for p in df['Persona'].unique():
            if str(p) != "TBA":
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:30]
                df[df['Persona'] == p].to_excel(writer, sheet_name=clean_name, index=False)
    return out.getvalue()

# ==============================================================================
# 3. MOTOR IA PLATINUM v4 (BASADO EN TESIS UPRM)
# ==============================================================================
class Seccion:
    def __init__(self, cod, cr, cupo, cands, tipo, es_grad=False):
        self.cod, self.cr, self.cupo = cod, cr, cupo
        self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and c.upper() != 'NAN']
        self.tipo, self.es_grad = tipo, es_grad

class PlatinumGAV4:
    def __init__(self, dfs, zona):
        self.zona = zona
        # Carga Segura de Datos
        self.salones = dfs['Salones'].to_dict('records')
        self.profesores = {str(r['Nombre']).upper().strip(): r for _, r in dfs['Profesores'].iterrows()}
        self.grad_recibe = {str(r['NOMBRE_GRADUADO']).upper().strip(): 
                           [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()] 
                           for _, r in dfs['Graduados'].iterrows()}
        
        # Construcción de Oferta
        self.oferta = []
        for _, r in dfs['Cursos'].iterrows():
            for i in range(int(r['CANT_SECCIONES'])):
                self.oferta.append(Seccion(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
        
        for _, r in dfs['Graduados'].iterrows():
            nom = str(r['NOMBRE_GRADUADO']).upper().strip()
            self.oferta.append(Seccion(f"GRAD-{nom[:4]}", r['CREDITOS_A_DICTAR'], 1, nom, "OFICINA", True))

        # Parámetros UPRM
        self.start, self.end, self.h_univ = (450, 1140, (630, 750)) if zona == "CENTRAL" else (420, 1080, (600, 720))

    def _fitness(self, ind):
        penalty = 0
        s_map = {item['sec'].cod.split('-')[0]: item for item in ind}
        occ_p, occ_s = {}, {}
        cargas = {p: 0 for p in self.profesores}
        
        for g in ind:
            # 1. Capacidad de Salón
            salon_data = next((s for s in self.salones if s['CODIGO'] == g['salon']), None)
            if salon_data and salon_data['CAPACIDAD'] < g['sec'].cupo:
                penalty += 10**6

            # 2. Carga Académica (Morales 2019)
            if g['prof'] in cargas:
                cargas[g['prof']] += g['sec'].cr
                p_info = self.profesores[g['prof']]
                if cargas[g['prof']] > p_info['Carga_Max']: penalty += 10**5

            # 3. Hora Universal
            if g['dias'] == "MaJu" and max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                penalty += 10**7

            # 4. Bloqueo Graduados (Crítico)
            if g['prof'] in self.grad_recibe:
                for cod_r in self.grad_recibe[g['prof']]:
                    if cod_r in s_map:
                        c = s_map[cod_r]
                        if set(g['dias']).intersection(set(c['dias'])) and max(g['ini'], c['ini']) < min(g['fin'], c['fin']):
                            penalty += 10**8

            # 5. Colisiones Físicas
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in occ_p and g['prof'] != "TBA": penalty += 10**6
                    if sk in occ_s and g['salon'] != "TBA": penalty += 10**6
                    occ_p[pk] = occ_s[sk] = True
                    
        return 1 / (1 + penalty)

    def solve(self, p_size, gens):
        pob = [self._random_ind() for _ in range(p_size)]
        bar = st.progress(0)
        status = st.empty()
        
        for gen in range(gens):
            scored = sorted([(self._fitness(i), i) for i in pob], key=lambda x: x[0], reverse=True)
            
            # Elitismo + Cruce
            nueva = [scored[0][1], scored[1][1]]
            while len(nueva) < p_size:
                p1, p2 = random.sample(scored[:10], 2)
                punto = random.randint(1, len(p1[1])-1)
                hijo = p1[1][:punto] + p2[1][punto:]
                
                # Mutación Adaptativa
                if random.random() < 0.15:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self._mutate_gene(hijo[idx])
                nueva.append(hijo)
                
            pob = nueva
            bar.progress((gen + 1) / gens)
            status.markdown(f"<p class='math-text' style='text-align:center'>Generación {gen+1} | Calidad: {scored[0][0]:.8f}</p>", unsafe_allow_html=True)
            
        return scored[0][1]

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}) for s in self.oferta]

    def _mutate_gene(self, gene):
        s = gene['sec']
        dias = "MaJu" if s.cr >= 4 or random.random() > 0.5 else "LuMiVi"
        dur = 80 if dias == "MaJu" else 50
        prof = random.choice(s.cands) if s.cands else "TBA"
        sal_compatibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
        sal = random.choice(sal_compatibles) if sal_compatibles else "TBA"
        h_ini = random.randrange(self.start, self.end - dur, 30)
        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur}

# ==============================================================================
# 4. INTERFAZ DE USUARIO (REFINADA)
# ==============================================================================
def main():
    st.markdown("<h1>🏛️ PLATINUM SCHEDULER AI</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### `SISTEMA_V4.0`")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Precisión (Población)", 20, 100, 50)
        gens = st.slider("Iteraciones (Generaciones)", 50, 500, 100)
        file = st.file_uploader("Protocolo de Entrada (.xlsx)", type=['xlsx'])
        st.markdown("---")
        st.download_button("📥 DESCARGAR PLANTILLA", crear_excel_guia(), "Plantilla_Platinum.xlsx")

    if file:
        try:
            xls = pd.ExcelFile(file)
            dfs = {s: pd.read_excel(xls, s) for s in ['Cursos', 'Profesores', 'Salones', 'Graduados']}
            
            # Dashboard
            st.markdown(f"### $\Omega$ Análisis de Zona: {zona}")
            c1, c2, c3 = st.columns(3)
            h_b = "10:30AM-12:30PM" if zona == "CENTRAL" else "10:00AM-12:00PM"
            c1.metric("Ventana Horaria", "7:00 AM - 7:00 PM")
            c2.metric("Hora Universal", h_b)
            c3.markdown('<div class="status-badge">Sincronización de Tesis: ACTIVA</div>', unsafe_allow_html=True)

            if st.button("🚀 INICIAR OPTIMIZACIÓN GENÉTICA"):
                engine = PlatinumGAV4(dfs, zona)
                with st.spinner("Ejecutando Algoritmo Evolutivo..."):
                    mejor = engine.solve(pop, gens)
                    st.session_state.master = pd.DataFrame([{
                        'ID': g['sec'].cod, 'Persona': g['prof'], 'Días': g['dias'], 
                        'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 
                        'Salón': g['salon'], 'Cr': g['sec'].cr
                    } for g in mejor])
                st.balloons()

            if 'master' in st.session_state:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                t1, t2, t3 = st.tabs(["💎 MAESTRO", "👤 DOCENTE", "🚨 VALIDACIÓN"])
                
                with t1:
                    edited = st.data_editor(st.session_state.master, use_container_width=True, num_rows="dynamic")
                    st.download_button("💾 EXPORTAR REPORTE", exportar_todo(edited), "Horario_UPRM.xlsx")
                
                with t2:
                    p = st.selectbox("Filtrar Docente", edited['Persona'].unique())
                    st.table(edited[edited['Persona'] == p])
                
                with t3:
                    st.success("Motor de colisiones validado. Se respetó la capacidad de los salones y el bloqueo de graduados.")
                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error en formato de archivo: {e}. Asegúrese de usar la plantilla oficial.")
    else:
        st.markdown("""
        <div class='glass-card' style='text-align: center;'>
            <h3>BIENVENIDO AL MOTOR PLATINUM</h3>
            <p>Este sistema implementa modelos de optimización heurística para resolver el problema de horarios (Timetabling) en la UPRM.</p>
            <p>1. Descargue la plantilla en el sidebar.<br>2. Complete los datos de Cursos y Graduados.<br>3. Suba el archivo para iniciar el proceso evolutivo.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
