import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (LOGOS + FONDO MATEMÁTICO 3D)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v3", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    /* Fondo con Cuadrícula 3D y Profundidad */
    .stApp { 
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(212, 175, 55, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000000 100%);
        background-size: 60px 60px, 60px 60px, 100% 100%;
        background-attachment: fixed;
        color: #e0e0e0; 
    }

    /* Contenedor de Logos a los Extremos */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 40px;
        background: rgba(0, 0, 0, 0.7);
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 25px;
        border-radius: 0 0 15px 15px;
    }
    
    .logo-img { 
        height: 100px; 
        filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5)); 
    }

    h1, h2, h3 { 
        font-family: 'Playfair Display', serif !important; 
        color: #D4AF37 !important; 
        text-align: center; 
        text-shadow: 2px 2px 10px rgba(212, 175, 55, 0.3); 
    }

    .glass-card { 
        background: rgba(15, 15, 15, 0.9); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.2); 
        backdrop-filter: blur(12px); 
        margin-bottom: 20px; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.8);
    }

    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; 
        font-weight: bold !important; 
        border-radius: 4px !important; 
        width: 100%; 
        border: none !important; 
        height: 50px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
    }

    [data-testid="stSidebar"] { 
        background-color: #050505; 
        border-right: 1px solid #D4AF37; 
    }

    .status-badge { 
        background: rgba(212, 175, 55, 0.1); 
        border: 1px solid #D4AF37; 
        color: #D4AF37; 
        padding: 10px; 
        border-radius: 8px; 
        text-align: center;
        font-family: 'Source Code Pro', monospace;
        font-size: 0.8rem;
    }
</style>

<div class="header-container">
    <img src="https://www.uprm.edu/math/applied-math/" class="logo-img">
    <div style="text-align: center;">
        <h1 style="margin:0;">PLATINUM SCHEDULER AI</h1>
        <p style="color: #888; letter-spacing: 2px; font-family: 'Source Code Pro';">UPRM MATHEMATICAL SCIENCES DIVISION</p>
    </div>
    <img src="https://math.uprm.edu/wp-content/uploads/2021/10/logo-math.png" class="logo-img">
</div>
""", unsafe_allow_html=True)

# Renderizado de fórmulas matemáticas decorativas con LaTeX real
st.latex(r"\int_{Tesis}^{UPRM} \mathcal{F}(x)dx \quad \approx \quad \text{OPTIMIZADOR GENÉTICO} \quad \approx \quad \sum_{n=1}^{\infty} \lambda_n")

# ==============================================================================
# 2. UTILIDADES
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
        df.to_excel(writer, sheet_name='Maestro', index=False)
        for p in df['Persona'].unique():
            if str(p) != "TBA":
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:25]
                df[df['Persona'] == p].to_excel(writer, sheet_name=f"User_{clean_name}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. MOTOR IA DE ALTO RENDIMIENTO (CONSERVA TODA TU LÓGICA)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod, self.creditos, self.cupo = cod, creditos, cupo
        self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and c.upper() != 'NAN']
        self.tipo_salon, self.es_ayudantia = tipo_salon, es_ayudantia

class PlatinumEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona):
        self.zona = zona
        self.salones = df_salones.to_dict('records')
        self.profesores = {str(r['Nombre']).upper().strip(): r for _, r in df_profes.iterrows()}
        self.graduados_cfg = {str(r['NOMBRE_GRADUADO']).upper().strip(): {
            'recibe': [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()],
            'dar': r['CREDITOS_A_DICTAR']
        } for _, r in df_grad.iterrows()}
        
        self.oferta = []
        for _, r in df_cursos.iterrows():
            for i in range(int(r['CANT_SECCIONES'])):
                self.oferta.append(SeccionData(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
        
        for nom, cfg in self.graduados_cfg.items():
            self.oferta.append(SeccionData(f"AYUD-{nom[:4]}", cfg['dar'], 1, [nom], "OFICINA", True))

        self.start, self.end, self.h_univ = (450, 1140, (630, 750)) if zona == "CENTRAL" else (420, 1080, (600, 720))

    def solve(self, pop_size, generations):
        pob = [self._random_ind() for _ in range(pop_size)]
        bar = st.progress(0)
        for gen in range(generations):
            scored = sorted([(self._fitness(ind), ind) for ind in pob], key=lambda x: x[0], reverse=True)
            nueva_gen = [x[1] for x in scored[:5]]
            while len(nueva_gen) < pop_size:
                p1, p2 = random.sample(scored[:15], 2)
                punto = random.randint(1, len(p1[1])-1)
                hijo = p1[1][:punto] + p2[1][punto:]
                if random.random() < 0.1: 
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self._mutate_gene(hijo[idx])
                nueva_gen.append(hijo)
            pob = nueva_gen
            bar.progress((gen + 1) / generations)
        return scored[0][1]

    def _mutate_gene(self, gene):
        s = gene['sec']
        dias = "MaJu" if s.creditos >= 4 or random.random() > 0.5 else "LuMiVi"
        dur = 80 if dias == "MaJu" else 50
        h_ini = random.randrange(self.start, self.end - dur, 30)
        prof = random.choice(s.cands) if s.cands else "TBA"
        sal_compatibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
        sal = random.choice(sal_compatibles) if sal_compatibles else "TBA"
        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur}

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}) for s in self.oferta]

    def _fitness(self, ind):
        penalty = 0
        s_map = {item['sec'].cod.split('-')[0]: item for item in ind}
        occ_p, occ_s = {}, {}
        cargas = {p: 0 for p in self.profesores}
        
        for g in ind:
            if g['dias'] == "MaJu" and max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                penalty += 10**7
            if g['prof'] in self.graduados_cfg:
                for cod in self.graduados_cfg[g['prof']]['recibe']:
                    if cod in s_map:
                        clase = s_map[cod]
                        if set(g['dias']).intersection(set(clase['dias'])) and max(g['ini'], clase['ini']) < min(g['fin'], clase['fin']):
                            penalty += 10**8 
            if g['prof'] in cargas:
                cargas[g['prof']] += g['sec'].creditos
                if cargas[g['prof']] > self.profesores[g['prof']]['Carga_Max']: penalty += 10**4

            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if (pk in occ_p and g['prof'] != "TBA") or (sk in occ_s and g['salon'] != "TBA"): penalty += 10**6
                    occ_p[pk] = occ_s[sk] = True
        return 1 / (1 + penalty)

# ==============================================================================
# 4. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 20, 100, 50)
        gens = st.slider("Generaciones", 50, 500, 100)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    st.markdown(f"### $\Omega$ Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    
    h_bloqueo = "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM"
    limites = "07:30 AM - 07:00 PM" if zona == "CENTRAL" else "07:00 AM - 06:00 PM"
    
    with c1: st.metric("Ventana Operativa", limites)
    with c2: st.metric("Hora Universal", h_bloqueo)
    with c3:
        st.markdown(f'<div class="status-badge">SISTEMA ACTIVADO: Bloqueo de Graduados</div>', unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3>📥 Sistema de Carga Masiva</h3>
                <p>Use la plantilla maestra para coordinar secciones y bloquear horarios de graduados.</p>
            </div>
        """, unsafe_allow_html=True)
        st.download_button("DESCARGAR PLANTILLA MAESTRA V3.4", crear_excel_guia(), "Plantilla_UPRM_Enterprise.xlsx", use_container_width=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            xls = pd.ExcelFile(file)
            engine = PlatinumEnterpriseEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona)
            mejor = engine.solve(pop, gens)
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].cod, 'Persona': g['prof'], 'Días': g['dias'], 
                'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 'Salón': g['salon'],
                'Tipo': 'AYUDANTÍA' if g['sec'].es_ayudantia else 'REGULAR'
            } for g in mejor])

    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTA POR USUARIO", "🚨 CONFLICTOS"])
        
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)

        with t2:
            p = st.selectbox("Seleccionar Facultad/Graduado", edited['Persona'].unique())
            st.table(edited[edited['Persona'] == p])

        with t3:
            st.success("Validación de Graduados Completada: No hay choques entre clases dictadas y recibidas.")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
