import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (DISEÑO MATEMÁTICO AVANZADO)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v5", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    /* Fondo con Cuadrícula 3D Hiper-Realista */
    .stApp { 
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(212, 175, 55, 0.1) 2px, transparent 2px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.1) 2px, transparent 2px),
            radial-gradient(circle at 50% 20%, #1a1a1a 0%, #000000 100%);
        background-size: 80px 80px, 80px 80px, 100% 100%;
        background-attachment: fixed;
        color: #e0e0e0; 
    }

    /* Encabezado Abstracto Matemático */
    .math-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 30px 60px;
        background: rgba(0, 0, 0, 0.85);
        border-bottom: 3px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 50px rgba(212, 175, 55, 0.15);
        position: relative;
        overflow: hidden;
    }

    .math-header::before {
        content: '∑';
        position: absolute;
        left: 5%;
        font-size: 8rem;
        color: rgba(212, 175, 55, 0.05);
        font-family: serif;
    }
    .math-header::after {
        content: '∫';
        position: absolute;
        right: 5%;
        font-size: 8rem;
        color: rgba(212, 175, 55, 0.05);
        font-family: serif;
    }

    .title-box { text-align: center; z-index: 2; }

    .abstract-icon {
        font-size: 3rem;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        padding: 10px 20px;
        border-radius: 50% 0% 50% 0%;
        background: rgba(212, 175, 55, 0.05);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }

    h1 { 
        font-family: 'Playfair Display', serif !important; 
        color: #D4AF37 !important; 
        font-size: 3.2rem !important;
        margin: 10px 0 !important;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        letter-spacing: 2px;
    }

    .glass-card { 
        background: rgba(15, 15, 15, 0.9); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.25); 
        backdrop-filter: blur(15px); 
        margin-bottom: 20px; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.8);
    }

    /* Botones Generales */
    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; font-weight: bold !important; border-radius: 4px !important; 
        width: 100%; border: none !important; height: 55px; font-size: 1.1rem;
        transition: 0.4s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(212, 175, 55, 0.4); }

    /* Estilo Dorado para "Descargar Plantilla" */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 50%, #B8860B 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: 1px solid #D4AF37 !important;
    }

    /* Sidebar y Título Σ Configuración */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
    
    [data-testid="stSidebar"] h3 {
        color: #D4AF37 !important;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
        font-family: 'Playfair Display', serif;
    }

    .status-badge { 
        background: rgba(212, 175, 55, 0.1); 
        border: 1px solid #D4AF37; 
        color: #D4AF37; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center;
        font-family: 'Source Code Pro', monospace;
        font-weight: 500;
    }
</style>

<div class="math-header">
    <div class="abstract-icon">Δx</div>
    <div class="title-box">
        <h1>UPRM TIMETABLE SYSTEM</h1>
        <p style="color: #888; font-family: 'Source Code Pro'; letter-spacing: 4px; font-size: 0.9rem;">
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v5.0 (FINAL RELEASE)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"\blacksquare \quad \text{SISTEMA DE PLANIFICACIÓN ACADÉMICA OPTIMIZADA - TESIS MASTER} \quad \blacksquare")

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
        pd.DataFrame(columns=['Nombre', 'Carga_Max', 'Pref_Horario']).to_excel(writer, sheet_name='Profesores', index=False)
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
# 3. MOTOR IA (PLATINUM ENGINE V5.0)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod, self.creditos, self.cupo = cod, creditos, cupo
        # Limpieza de candidatos para evitar errores 'nan'
        self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and str(c).upper() != 'NAN']
        self.tipo_salon, self.es_ayudantia = tipo_salon, es_ayudantia

class PlatinumEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona):
        self.zona = zona
        self.salones = df_salones.to_dict('records')
        
        # Mapa de Profesores y Preferencias
        self.profesores = {}
        for _, r in df_profes.iterrows():
            nombre = str(r['Nombre']).upper().strip()
            self.profesores[nombre] = {
                'Carga_Max': r['Carga_Max'],
                'Pref_Bloque': str(r.get('Pref_Horario', 'AM')).upper() # Preferencia Suave
            }
            
        # Mapa de Graduados
        self.graduados_cfg = {str(r['NOMBRE_GRADUADO']).upper().strip(): {
            'recibe': [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()],
            'dar': r['CREDITOS_A_DICTAR']
        } for _, r in df_grad.iterrows()}
        
        # Generación de la Oferta Académica (Genes Base)
        self.oferta = []
        for _, r in df_cursos.iterrows():
            for i in range(int(r['CANT_SECCIONES'])):
                self.oferta.append(SeccionData(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
        
        # Añadir 'clases' ficticias para los Graduados (Ayudantías)
        for nom, cfg in self.graduados_cfg.items():
            self.oferta.append(SeccionData(f"AYUD-{nom[:4]}", cfg['dar'], 1, [nom], "OFICINA", True))

        # --- BLOQUES DE TIEMPO OFICIALES UPRM ---
        # Convertimos horas a minutos (e.g., 7:30 = 450 min)
        # Bloques LMV (1 hora estándar)
        self.bloques_lmv = [450, 510, 570, 630, 690, 750, 810, 870, 930, 990] 
        # Bloques MaJu (1.5 horas estándar, saltando Hora Universal)
        self.bloques_mj = [450, 540, 750, 840, 930, 1020]
        
        # Hora Universal (Bloqueo Duro)
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720) 

    def solve(self, pop_size, generations):
        pob = [self._random_ind() for _ in range(pop_size)]
        bar = st.progress(0)
        status_text = st.empty()
        
        for gen in range(generations):
            # Evaluar toda la población
            scored = sorted([(self._fitness(ind), ind) for ind in pob], key=lambda x: x[0], reverse=True)
            
            # Elitismo: Conservar el TOP 10% intacto
            nueva_gen = [x[1] for x in scored[:int(pop_size*0.1)]]
            
            status_text.markdown(f"**Generando Solución {gen+1}/{generations}** | Fitness Actual: `{scored[0][0]:.6f}`")
            
            # Operadores Genéticos: Torneo y Cruce
            while len(nueva_gen) < pop_size:
                padres = random.sample(scored[:int(pop_size*0.5)], 2) 
                p1, p2 = padres[0][1], padres[1][1]
                
                punto = random.randint(1, len(p1)-1)
                hijo = p1[:punto] + p2[punto:]
                
                # Mutación Dinámica (más alta al principio, baja al final)
                prob_mut = 0.2 if gen < generations * 0.3 else 0.05
                if random.random() < prob_mut:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self._mutate_gene(hijo[idx])
                
                nueva_gen.append(hijo)
            
            pob = nueva_gen
            bar.progress((gen + 1) / generations)
            
        return scored[0][1]

    def _mutate_gene(self, gene):
        s = gene['sec']
        
        # Lógica de días: Clases de 4+ créditos o aleatorio suelen ser MJ
        es_mj = (s.creditos >= 4) or (random.random() > 0.6)
        dias = "MaJu" if es_mj else "LuMiVi"
        dur = 80 if es_mj else 50 # Duración en minutos
        
        # Selección de hora restringida a BLOQUES VÁLIDOS
        posibles_inicios = self.bloques_mj if es_mj else self.bloques_lmv
        h_ini = random.choice(posibles_inicios)
        
        # Selección de Profesor
        prof = random.choice(s.cands) if s.cands else "TBA"
        
        # Selección de Salón (Solo si cumple capacidad y tipo)
        sal_compatibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and sl['TIPO'] == s.tipo_salon]
        sal = random.choice(sal_compatibles) if sal_compatibles else "TBA"
        
        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur}

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}) for s in self.oferta]

    def _fitness(self, ind):
        penalty = 0
        soft_penalty = 0 
        
        s_map = {item['sec'].cod.split('-')[0]: item for item in ind}
        occ_p, occ_s = {}, {}
        cargas = {p: 0 for p in self.profesores}
        horarios_por_curso = {} # Para controlar distribución (Anti-Aglomeración)
        
        for g in ind:
            # =========================================
            # RESTRICCIONES DURAS (Hard Constraints)
            # =========================================
            
            # 1. PENALIZACIÓN "TBA" (Crucial para obligar asignación)
            if g['salon'] == "TBA": penalty += 5000
            if g['prof'] == "TBA": penalty += 5000

            # 2. HORA UNIVERSAL
            if g['dias'] == "MaJu":
                if max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                    penalty += 10000

            # 3. CHOQUE DE GRADUADOS (Profesor vs Estudiante)
            if g['prof'] in self.graduados_cfg:
                for cod in self.graduados_cfg[g['prof']]['recibe']:
                    if cod in s_map:
                        clase = s_map[cod]
                        # Intersección simple de días
                        dias_g = ["Ma", "Ju"] if g['dias'] == "MaJu" else ["Lu", "Mi", "Vi"]
                        dias_c = ["Ma", "Ju"] if clase['dias'] == "MaJu" else ["Lu", "Mi", "Vi"]
                        
                        share_days = set(dias_g).intersection(set(dias_c))
                        if share_days and max(g['ini'], clase['ini']) < min(g['fin'], clase['fin']):
                            penalty += 20000

            # 4. CARGA ACADÉMICA
            if g['prof'] in cargas:
                cargas[g['prof']] += g['sec'].creditos
                if cargas[g['prof']] > self.profesores[g['prof']]['Carga_Max']: penalty += 5000

            # 5. CHOQUES DE TIEMPO/ESPACIO (Salones y Profesores)
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                pk, sk = (g['prof'], d), (g['salon'], d)
                rango = (g['ini'], g['fin'])
                
                if g['prof'] != "TBA":
                    if pk in occ_p:
                        for r in occ_p[pk]:
                            if max(rango[0], r[0]) < min(rango[1], r[1]): penalty += 10000
                        occ_p[pk].append(rango)
                    else: occ_p[pk] = [rango]
                
                if g['salon'] != "TBA":
                    if sk in occ_s:
                        for r in occ_s[sk]:
                            if max(rango[0], r[0]) < min(rango[1], r[1]): penalty += 10000
                        occ_s[sk].append(rango)
                    else: occ_s[sk] = [rango]
            
            # =========================================
            # RESTRICCIONES SUAVES (Soft Constraints)
            # =========================================
            
            # A. Preferencias AM/PM del profesor
            if g['prof'] in self.profesores:
                pref = self.profesores[g['prof']]['Pref_Bloque']
                es_am = g['ini'] < 720
                if (pref == 'AM' and not es_am) or (pref == 'PM' and es_am):
                    soft_penalty += 100

            # B. DISTRIBUCIÓN DE SECCIONES (NUEVO: Hace el horario "Perfecto")
            # Evita que todas las secciones de un curso (ej. MATE3005) sean a la misma hora
            curso_base = g['sec'].cod.split('-')[0]
            if curso_base not in horarios_por_curso:
                horarios_por_curso[curso_base] = []
            
            # Si este curso ya tiene una sección a esta hora, penalizar la aglomeración
            if g['ini'] in horarios_por_curso[curso_base]:
                soft_penalty += 500 
            
            horarios_por_curso[curso_base].append(g['ini'])

        # Cálculo final del Fitness
        return 1 / (1 + penalty + (soft_penalty * 0.001))

# ==============================================================================
# 4. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 20, 200, 50)
        gens = st.slider("Generaciones", 50, 500, 100)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    st.markdown(f"### $\Omega$ Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    
    h_bloqueo = "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM"
    limites = "07:30 AM - 06:30 PM"
    
    with c1: st.metric("Ventana Operativa", limites)
    with c2: st.metric("Hora Universal", h_bloqueo)
    with c3:
        st.markdown(f"""<div class="status-badge">ALGORITMO GENÉTICO V5: Distribución Optimizada</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Cargue el protocolo de secciones para iniciar el procesamiento de optimización multivariable.</p>
            </div>
        """, unsafe_allow_html=True)
        st.download_button("DESCARGAR PLANTILLA MAESTRA V5.0", crear_excel_guia(), "Plantilla_UPRM_Enterprise.xlsx", use_container_width=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            xls = pd.ExcelFile(file)
            engine = PlatinumEnterpriseEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona)
            
            start_time = time.time()
            mejor = engine.solve(pop, gens)
            elapsed = time.time() - start_time
            
            st.success(f"Optimización completada en {elapsed:.2f} segundos.")
            
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].cod, 
                'Asignatura': g['sec'].cod.split('-')[0],
                'Creditos': g['sec'].creditos,
                'Persona': g['prof'], 
                'Días': g['dias'], 
                'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 
                'Salón': g['salon'],
                'Tipo': 'AYUDANTÍA' if g['sec'].es_ayudantia else 'REGULAR'
            } for g in mejor])

    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTA POR USUARIO", "🚨 AUDITORÍA INTELIGENTE"])
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=500)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
        with t2:
            lista_personas = sorted(st.session_state.master['Persona'].unique())
            p = st.selectbox("Seleccionar Facultad/Graduado", lista_personas)
            subset = st.session_state.master[st.session_state.master['Persona'] == p]
            st.table(subset[['ID', 'Días', 'Horario', 'Salón']])
        with t3:
            # Auditoría rápida de TBAs
            tbas = st.session_state.master[
                (st.session_state.master['Salón'] == 'TBA') | 
                (st.session_state.master['Persona'] == 'TBA')
            ]
            if not tbas.empty:
                st.warning(f"Se detectaron {len(tbas)} cursos con asignaciones pendientes (TBA). Revise la capacidad de los salones.")
                st.dataframe(tbas)
            else:
                st.success("Validación Perfecta: 0 Conflictos y 100% Asignación.")
                
            # Auditoría de Aglomeración
            df = st.session_state.master
            counts = df.groupby(['Asignatura', 'Horario']).size().reset_index(name='count')
            aglomerados = counts[counts['count'] > 2] # Si hay más de 2 secciones del mismo curso a la misma hora
            if not aglomerados.empty:
                st.info("Nota: Algunos cursos tienen múltiples secciones en el mismo horario. Verifique si es deseado.")
                st.dataframe(aglomerados)
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
