import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# 1. ESTÉTICA PLATINUM (INTERFAZ ORIGINAL INTACTA)
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
# 2. FUNCIONES DE APOYO
# ==============================================================================
def mins_to_str(minutes):
    h, m = divmod(int(minutes), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

def mins_to_datetime(minutes):
    # Auxiliar para el gráfico de Gantt
    base = datetime(2024, 1, 1, 0, 0)
    return base + timedelta(minutes=int(minutes))

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CUPO_TOTAL_REQUERIDO', 'TAMANO_SECCION_ESTANDAR', 
                             'SECCIONES_ESPECIALES', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'Dias_Preferencia', 'Horas_Preferencia']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE', 'CREDITOS', 'CLASES A RECIBIR']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR PLATINUM (CON PREFERENCIAS Y OPTIMIZACIÓN)
# ==============================================================================
class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profes_dict = {p['Nombre']: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)
        
    def ejecutar(self):
        res = []
        conflictos = []
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profes_dict}
        
        # MEJORA: Ordenar secciones por cupo (de mayor a menor) para evitar el "punto ciego"
        secciones_ordenadas = sorted(self.secciones, key=lambda x: x['cupo'], reverse=True)
        
        h_posibles = [h*60 + (30 if self.zona == "CENTRAL" else 0) for h in range(7, 20)]
        
        for sec in secciones_ordenadas:
            # Selección de Profesor (Considerando Carga y Candidatos)
            pool_p = [p for p, info in self.profes_dict.items() if (info['es_graduado'] if sec['es_graduado'] else p in sec['cands'])]
            prof = "TBA"
            if pool_p:
                validos = [p for p in pool_p if cargas[p] + sec['creditos'] <= self.profes_dict[p]['Carga_Max']]
                if validos:
                    validos.sort(key=lambda p: (cargas[p] >= self.profes_dict[p].get('Carga_Min', 0), cargas[p]))
                    prof = validos[0]
            
            asignado = False
            # MEJORA: Priorizar horarios según PREFERENCIAS del profesor si existen
            h_actuales = h_posibles.copy()
            random.shuffle(h_actuales)
            
            if prof != "TBA":
                pref_h = self.profes_dict[prof].get('Horas_Preferencia')
                if pref_h: # Si el profesor tiene horas preferidas, ponerlas al frente del pool
                    h_actuales = sorted(h_actuales, key=lambda x: x in pref_h, reverse=True)

            for h in h_actuales:
                dias_opciones = [['Lu', 'Mi', 'Vi']] if sec['creditos'] != 4 else [['Ma', 'Ju']]
                dur = 50 if sec['creditos'] != 4 else 80
                
                # MEJORA: Filtrar días según PREFERENCIAS obligatorias
                if prof != "TBA":
                    pref_d = self.profes_dict[prof].get('Dias_Preferencia')
                    if pref_d:
                        dias_opciones = [opt for opt in dias_opciones if any(d in pref_d for d in opt)]

                for dias in dias_opciones:
                    # Regla Hora Universal
                    if max(h, self.h_univ[0]) < min(h+dur, self.h_univ[1]) and any(d in ['Ma','Ju'] for d in dias):
                        continue

                    # MEJORA: Buscar el salón más eficiente (Smallest Fit)
                    salones_aptos = sorted([s for s in self.salones if s['CAPACIDAD'] >= sec['cupo']], key=lambda x: x['CAPACIDAD'])
                    
                    for s in salones_aptos:
                        choque = False
                        for d in dias:
                            if (s['CODIGO'], d, h) in oc_s or (prof != "TBA" and (prof, d, h) in oc_p):
                                choque = True; break
                        
                        if not choque:
                            for d in dias:
                                oc_s[(s['CODIGO'], d, h)] = True
                                if prof != "TBA": oc_p[(prof, d, h)] = True
                            if prof != "TBA": cargas[prof] += sec['creditos']
                            res.append({
                                'Curso': sec['uid'], 'Profesor': prof, 'Días': "".join(dias), 
                                'Inicio': h, 'Fin': h+dur, 'Salón': s['CODIGO'], 
                                'Cupo': sec['cupo'], 'Es_Grad': sec['es_graduado'],
                                'Inicio_DT': mins_to_datetime(h), 'Fin_DT': mins_to_datetime(h+dur)
                            })
                            asignado = True; break
                    if asignado: break
                if asignado: break
            if not asignado: conflictos.append(f"Conflicto: {sec['uid']} (Cupo: {sec['cupo']}). Verifique salones o preferencias de {prof}.")
                
        return pd.DataFrame(res), conflictos, cargas

# ==============================================================================
# 4. INTERFAZ PRINCIPAL
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum")
    
    excel_guia = crear_excel_guia()
    st.download_button("📥 Descargar Excel Guía (Plantilla v2)", excel_guia, "plantilla_uprm.xlsx")
    
    with st.sidebar:
        st.header("Configuración")
        zona = st.selectbox("📍 Zona de Horarios", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("📂 Cargar Excel de Datos", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')
        df_gra = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else pd.DataFrame()

        if st.button("🚀 GENERAR HORARIO MAESTRO"):
            secciones_generadas = []
            for _, r in df_cur.iterrows():
                codigo = str(r['CODIGO'])
                cupo_total, std_size = int(r['CUPO_TOTAL_REQUERIDO']), int(r['TAMANO_SECCION_ESTANDAR'])
                cands = [c.strip().upper() for c in str(r['CANDIDATOS']).split(',') if c.strip()] if not pd.isna(r['CANDIDATOS']) else []
                cupo_acumulado, idx = 0, 1
                
                if not pd.isna(r['SECCIONES_ESPECIALES']):
                    for esp in str(r['SECCIONES_ESPECIALES']).split(','):
                        try:
                            cant, tam = esp.lower().split('x')
                            for _ in range(int(cant)):
                                secciones_generadas.append({'uid': f"{codigo}-{idx:02d}", 'creditos': r['CREDITOS'], 'cupo': int(tam), 'cands': cands, 'es_graduado': False})
                                cupo_acumulado += int(tam); idx += 1
                        except: continue
                while cupo_acumulado < cupo_total:
                    secciones_generadas.append({'uid': f"{codigo}-{idx:02d}", 'creditos': r['CREDITOS'], 'cupo': std_size, 'cands': cands, 'es_graduado': False})
                    cupo_acumulado += std_size; idx += 1

            profes = []
            for _, r in df_pro.iterrows():
                # Procesar preferencias si vienen en el Excel
                d_pref = str(r['Dias_Preferencia']).split(',') if not pd.isna(r['Dias_Preferencia']) else None
                h_pref = [int(x) for x in str(r['Horas_Preferencia']).split(',')] if not pd.isna(r['Horas_Preferencia']) else None
                profes.append({'Nombre': str(r['Nombre']).upper(), 'Carga_Min': r['Carga_Min'], 'Carga_Max': r['Carga_Max'], 
                               'es_graduado': False, 'Dias_Preferencia': d_pref, 'Horas_Preferencia': h_pref})
            
            for _, r in df_gra.iterrows():
                secciones_generadas.append({'uid': f"GRAD-{r['NOMBRE'][:5]}", 'creditos': r['CREDITOS'], 'cupo': 15, 'cands': [str(r['NOMBRE']).upper()], 'es_graduado': True})
                profes.append({'Nombre': str(r['NOMBRE']).upper(), 'Carga_Min': 0, 'Carga_Max': r['CREDITOS'], 'es_graduado': True})
            
            engine = PlatinumEngine(secciones_generadas, profes, df_sal.to_dict('records'), zona)
            df_res, confs, cargas_f = engine.ejecutar()
            
            st.session_state.horario = df_res
            st.session_state.confs = confs
            st.session_state.cargas = cargas_f
            st.session_state.profes_objs = profes

        if 'horario' in st.session_state:
            if st.session_state.confs:
                with st.expander("⚠️ CONFLICTOS DETECTADOS", expanded=True):
                    for c in st.session_state.confs: st.error(c)
            
            tab1, tab2 = st.tabs(["📅 HORARIO GENERAL", "👨‍🏫 DASHBOARD PROFESOR"])
            
            with tab1:
                df_disp = st.session_state.horario.copy()
                df_disp['Hora'] = df_disp['Inicio'].apply(mins_to_str) + " - " + df_disp['Fin'].apply(mins_to_str)
                st.dataframe(df_disp[['Curso', 'Profesor', 'Días', 'Hora', 'Salón', 'Cupo']], use_container_width=True)
                
                # EXPORTACIÓN
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_disp.to_excel(writer, index=False, sheet_name='Horario')
                st.download_button("📊 Descargar Horario Maestro (.xlsx)", buffer, "Horario_UPRM.xlsx")

            with tab2:
                p_sel = st.selectbox("Seleccione Profesor:", st.session_state.horario['Profesor'].unique())
                df_p = st.session_state.horario[st.session_state.horario['Profesor'] == p_sel]
                
                # GAUGE
                info_p = next((p for p in st.session_state.profes_objs if p['Nombre'] == p_sel), {'Carga_Min':0, 'Carga_Max':15})
                carga_actual = st.session_state.cargas.get(p_sel, 0)
                fig_g = go.Figure(go.Indicator(mode = "gauge+number", value = carga_actual, title = {'text': f"Carga Académica: {p_sel}"},
                    gauge = {'axis': {'range': [0, 21]}, 'bar': {'color': "#FFD700"},
                             'steps': [{'range': [0, info_p['Carga_Min']], 'color': "red"}, {'range': [info_p['Carga_Min'], info_p['Carga_Max']], 'color': "green"}]}))
                fig_g.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig_g, use_container_width=True)
                
                # GANTT (AGENDA VISUAL)
                if not df_p.empty:
                    st.subheader("📅 Agenda Semanal Visual")
                    fig_gantt = px.timeline(df_p, x_start="Inicio_DT", x_end="Fin_DT", y="Días", color="Curso",
                                           hover_data=['Salón'], template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_gantt.update_layout(xaxis_title="Horario", yaxis_title="Días de Clase", showlegend=True)
                    st.plotly_chart(fig_gantt, use_container_width=True)

                st.table(df_p[['Curso', 'Días', 'Salón', 'Cupo']])

if __name__ == "__main__":
    main()
