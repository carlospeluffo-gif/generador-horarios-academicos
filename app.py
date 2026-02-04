import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM (TU INTERFAZ ORIGINAL)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; background-image: linear-gradient(rgba(15, 15, 15, 0.50), rgba(15, 15, 15, 0.50)), url("https://www.transparenttextures.com/patterns/cubes.png"); color: #ffffff; }
    p, label, .stMarkdown, .stDataFrame, div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3, h4 { color: #FFD700 !important; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4); }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #333; }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000 !important; font-weight: 800; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; transition: transform 0.2s; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FUNCIONES DE APOYO Y TIEMPO
# ==============================================================================
def mins_to_str(minutes):
    h, m = divmod(int(minutes), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

def time_input_to_mins(t_obj):
    return t_obj.hour * 60 + t_obj.minute

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'NOMBRE', 'CREDITOS', 'CANTIDAD_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE', 'CREDITOS', 'CLASES A RECIBIR']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR CON REPORTE DE CONFLICTOS
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, nombre, creditos, cupo, candidatos, tipo_salon):
        self.uid = uid
        self.cod_base = str(cod_base).upper()
        self.nombre = nombre
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon = str(tipo_salon).upper()
        self.cands = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()] if not pd.isna(candidatos) else []
        self.es_graduado = "GRADUADOS" in self.cands

class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona, prefs):
        self.secciones = secciones
        self.profes_dict = {p['Nombre']: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.prefs = prefs
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)
        
    def ejecutar(self):
        res = []
        conflictos = []
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profes_dict}
        
        # Bloques simplificados LMV y MJ
        h_ini = [h*60 + (30 if self.zona == "CENTRAL" else 0) for h in range(7, 20)]
        
        for sec in self.secciones:
            pool_p = [p for p, info in self.profes_dict.items() if (info['es_graduado'] if sec.es_graduado else p in sec.cands)]
            prof = "TBA"
            if pool_p:
                validos = [p for p in pool_p if cargas[p] + sec.creditos <= self.profes_dict[p]['Carga_Max']]
                if validos:
                    validos.sort(key=lambda p: (cargas[p] >= self.profes_dict[p]['Carga_Min'], cargas[p]))
                    prof = validos[0]
            
            asignado = False
            random.shuffle(h_ini)
            for h in h_ini:
                dias = ['Lu', 'Mi', 'Vi'] if sec.creditos != 4 else ['Ma', 'Ju']
                dur = 50 if len(dias)==3 else 80
                
                # Validar Hora Universal
                if max(h, self.h_univ[0]) < min(h+dur, self.h_univ[1]) and any(d in ['Ma','Ju'] for d in dias):
                    continue

                for s in self.salones:
                    if s['CAPACIDAD'] >= sec.cupo:
                        # Validar Choques
                        choque = False
                        for d in dias:
                            if (s['CODIGO'], d) in oc_s or (prof != "TBA" and (prof, d) in oc_p):
                                choque = True; break
                        
                        if not choque:
                            for d in dias:
                                oc_s[(s['CODIGO'], d)] = (h, h+dur)
                                if prof != "TBA": oc_p[(prof, d)] = (h, h+dur)
                            cargas[prof] += sec.creditos
                            res.append({'Curso': sec.uid, 'Nombre': sec.nombre, 'Profesor': prof, 'Días': "".join(dias), 'Inicio': h, 'Fin': h+dur, 'Salón': s['CODIGO'], 'Es_Grad': sec.es_graduado})
                            asignado = True; break
                if asignado: break
            if not asignado: conflictos.append(f"No se encontró espacio para {sec.uid}")

        # Validar Carga Mínima
        for p, c in cargas.items():
            if 0 < c < self.profes_dict[p]['Carga_Min']:
                conflictos.append(f"Profesor {p} no alcanzó carga mínima ({c}/{self.profes_dict[p]['Carga_Min']})")
                
        return pd.DataFrame(res), conflictos, cargas

# ==============================================================================
# 4. INTERFAZ PRINCIPAL
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum")
    
    # --- BOTÓN DESCARGA GUIA ---
    excel_guia = crear_excel_guia()
    st.download_button("📥 Descargar Excel Guía (Plantilla)", excel_guia, "plantilla_uprm.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with st.sidebar:
        st.header("Configuración")
        zona = st.selectbox("📍 Zona de Horarios", ["CENTRAL", "PERIFERICA"])
        if zona == "CENTRAL":
            st.caption("Inicio: XX:30. Hora Universal: 10:30 a 12:30 (No programable).")
        else:
            st.caption("Inicio: XX:00. Hora Universal: 10:00 a 12:00 (No programable).")
            
        file = st.file_uploader("📂 Cargar Excel Lleno", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')
        df_gra = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else pd.DataFrame()

        if st.button("🚀 GENERAR HORARIO MAESTRO"):
            # Procesar datos
            profes = []
            for _, r in df_pro.iterrows():
                profes.append({'Nombre': str(r['Nombre']).upper(), 'Carga_Min': r['Carga_Min'], 'Carga_Max': r['Carga_Max'], 'es_graduado': False})
            for _, r in df_gra.iterrows():
                profes.append({'Nombre': str(r['NOMBRE']).upper(), 'Carga_Min': 0, 'Carga_Max': r['CREDITOS'], 'es_graduado': True, 'recibe': r['CLASES A RECIBIR']})
            
            secciones = []
            for _, r in df_cur.iterrows():
                for i in range(int(r.get('CANTIDAD_SECCIONES', 1))):
                    secciones.append(Seccion(f"{r['CODIGO']}-{i+1:02d}", r['CODIGO'], r['NOMBRE'], r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
            
            salones = df_sal.to_dict('records')
            engine = PlatinumEngine(secciones, profes, salones, zona, {})
            df_res, confs, cargas_f = engine.ejecutar()
            
            st.session_state.horario = df_res
            st.session_state.confs = confs
            st.session_state.cargas = cargas_f
            st.session_state.profes_objs = profes

        if 'horario' in st.session_state:
            # MOSTRAR CONFLICTOS
            if st.session_state.confs:
                with st.expander("⚠️ CONFLICTOS DETECTADOS", expanded=True):
                    for c in st.session_state.confs: st.error(c)
            else:
                st.success("✅ Horario generado sin conflictos.")

            tab1, tab2 = st.tabs(["📅 HORARIO GENERAL", "👨‍🏫 DASHBOARD PROFESOR"])
            
            with tab1:
                st.subheader("Clasificación y Filtros")
                c1, c2, c3 = st.columns(3)
                f_prof = c1.multiselect("Filtrar por Profesor", st.session_state.horario['Profesor'].unique())
                f_sal = c2.multiselect("Filtrar por Salón", st.session_state.horario['Salón'].unique())
                f_grad = c3.checkbox("Mostrar solo Graduados")
                
                df_disp = st.session_state.horario.copy()
                if f_prof: df_disp = df_disp[df_disp['Profesor'].isin(f_prof)]
                if f_sal: df_disp = df_disp[df_disp['Salón'].isin(f_sal)]
                if f_grad: df_disp = df_disp[df_disp['Es_Grad'] == True]
                
                # Formatear horas para vista
                df_disp['Hora'] = df_disp['Inicio'].apply(mins_to_str) + " - " + df_disp['Fin'].apply(mins_to_str)
                st.dataframe(df_disp[['Curso', 'Nombre', 'Profesor', 'Días', 'Hora', 'Salón']], use_container_width=True, hide_index=True)

            with tab2:
                p_sel = st.selectbox("Seleccione Profesor para Dashboard:", st.session_state.horario['Profesor'].unique())
                df_p = st.session_state.horario[st.session_state.horario['Profesor'] == p_sel]
                
                # --- GRÁFICO GANTT ---
                plot_data = []
                dia_map = {'Lu': '2024-01-01', 'Ma': '2024-01-02', 'Mi': '2024-01-03', 'Ju': '2024-01-04', 'Vi': '2024-01-05'}
                for _, row in df_p.iterrows():
                    for i in range(0, len(row['Días']), 2):
                        d = row['Días'][i:i+2]
                        plot_data.append({
                            'Curso': row['Curso'], 'Día': d, 
                            'Start': f"{dia_map[d]} {int(row['Inicio']//60):02d}:{int(row['Inicio']%60):02d}:00",
                            'Finish': f"{dia_map[d]} {int(row['Fin']//60):02d}:{int(row['Fin']%60):02d}:00"
                        })
                
                if plot_data:
                    fig = px.timeline(pd.DataFrame(plot_data), x_start="Start", x_end="Finish", y="Día", color="Curso", template="plotly_dark")
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                
                # --- GAUGE DE CARGA ---
                info_p = next(p for p in st.session_state.profes_objs if p['Nombre'] == p_sel)
                carga_actual = st.session_state.cargas[p_sel]
                
                fig_g = go.Figure(go.Indicator(
                    mode = "gauge+number", value = carga_actual,
                    title = {'text': f"Carga de {p_sel} (Créditos)"},
                    gauge = {'axis': {'range': [0, 20]}, 'bar': {'color': "#FFD700"},
                             'steps': [{'range': [0, info_p['Carga_Min']], 'color': "red"},
                                       {'range': [info_p['Carga_Min'], info_p['Carga_Max']], 'color': "green"}]}))
                fig_g.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig_g, use_container_width=True)

if __name__ == "__main__":
    main()
