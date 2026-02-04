import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. ESTÉTICA Y CONFIGURACIÓN
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4); }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000 !important; font-weight: 800; border-radius: 6px; }
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

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # HOJA CURSOS SIMPLIFICADA
        pd.DataFrame(columns=[
            'CODIGO', 'CREDITOS', 'CUPO_TOTAL_REQUERIDO', 'TAMANO_SECCION_ESTANDAR', 
            'SECCIONES_ESPECIALES', 'CANDIDATOS', 'TIPO_SALON'
        ]).to_excel(writer, sheet_name='Cursos', index=False)
        
        # HOJA PROFESORES
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max']).to_excel(writer, sheet_name='Profesores', index=False)
        
        # HOJA SALONES
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        
        # HOJA GRADUADOS
        pd.DataFrame(columns=['NOMBRE', 'CREDITOS', 'CLASES_A_RECIBIR']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR LOGICO CON AUTO-DISTRIBUCIÓN
# ==============================================================================
class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profes_dict = {p['Nombre']: p for p in profesores}
        self.salones = sorted(salones, key=lambda x: x['CAPACIDAD'])
        self.zona = zona
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)
        
    def ejecutar(self):
        res = []
        conflictos = []
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profes_dict}
        
        h_ini = [h*60 + (30 if self.zona == "CENTRAL" else 0) for h in range(7, 20)]
        
        for sec in self.secciones:
            # Lógica de candidatos
            pool_p = [p for p, info in self.profes_dict.items() if (info['es_graduado'] if sec['es_graduado'] else p in sec['cands'])]
            prof = "TBA"
            if pool_p:
                validos = [p for p in pool_p if cargas[p] + sec['creditos'] <= self.profes_dict[p]['Carga_Max']]
                if validos:
                    validos.sort(key=lambda p: (cargas[p] >= self.profes_dict[p]['Carga_Min'], cargas[p]))
                    prof = validos[0]
            
            asignado = False
            random.shuffle(h_ini)
            for h in h_ini:
                dias = ['Lu', 'Mi', 'Vi'] if sec['creditos'] != 4 else ['Ma', 'Ju']
                dur = 50 if len(dias)==3 else 80
                
                # Validar Hora Universal
                if max(h, self.h_univ[0]) < min(h+dur, self.h_univ[1]) and any(d in ['Ma','Ju'] for d in dias):
                    continue

                for s in self.salones:
                    if s['CAPACIDAD'] >= sec['cupo']:
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
                                'Cupo': sec['cupo'], 'Es_Grad': sec['es_graduado']
                            })
                            asignado = True; break
                if asignado: break
            if not asignado: 
                conflictos.append(f"❌ Sin espacio: {sec['uid']} (Cupo: {sec['cupo']})")
                
        return pd.DataFrame(res), conflictos, cargas

# ==============================================================================
# 4. INTERFAZ PRINCIPAL
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum")
    
    # 1. DESCARGA DE GUIA
    st.markdown("### 1. Preparación")
    excel_guia = crear_excel_guia()
    st.download_button("📥 Descargar Nueva Plantilla Guía", excel_guia, "plantilla_uprm_v2.xlsx")
    
    # Explicación de las nuevas columnas
    with st.expander("ℹ️ Cómo llenar la nueva columna de Cursos"):
        st.write("""
        - **CUPO_TOTAL_REQUERIDO**: Cuántos estudiantes totales deben tomar la materia.
        - **TAMANO_SECCION_ESTANDAR**: El tamaño normal de una clase (ej. 30).
        - **SECCIONES_ESPECIALES**: Si quieres clases de tamaño distinto, escríbelo así: `4x45, 1x90`. 
          El programa restará esos cupos del total y creará el resto con el tamaño estándar.
        """)

    with st.sidebar:
        st.header("Configuración")
        zona = st.selectbox("📍 Zona de Horarios", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("📂 Cargar Excel", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')
        df_gra = pd.read_excel(xls, 'Graduados')

        if st.button("🚀 GENERAR HORARIO MAESTRO"):
            # LÓGICA DE AUTO-GENERACIÓN DE SECCIONES
            secciones_list = []
            for _, r in df_cur.iterrows():
                codigo = str(r['CODIGO'])
                cupo_objetivo = int(r['CUPO_TOTAL_REQUERIDO'])
                std_size = int(r['TAMANO_SECCION_ESTANDAR'])
                cands = str(r['CANDIDATOS']).split(',') if not pd.isna(r['CANDIDATOS']) else []
                
                cupo_cubierto = 0
                sec_id = 1
                
                # 1. Procesar Especiales (ej. 4x45, 1x90)
                if not pd.isna(r['SECCIONES_ESPECIALES']):
                    especiales = str(r['SECCIONES_ESPECIALES']).split(',')
                    for esp in especiales:
                        try:
                            cant, tam = esp.lower().split('x')
                            for _ in range(int(cant)):
                                secciones_list.append({
                                    'uid': f"{codigo}-{sec_id:02d}", 'creditos': r['CREDITOS'],
                                    'cupo': int(tam), 'cands': cands, 'es_graduado': False
                                })
                                cupo_cubierto += int(tam)
                                sec_id += 1
                        except: continue
                
                # 2. Rellenar con Estándar hasta cubrir el total
                while cupo_cubierto < cupo_objetivo:
                    secciones_list.append({
                        'uid': f"{codigo}-{sec_id:02d}", 'creditos': r['CREDITOS'],
                        'cupo': std_size, 'cands': cands, 'es_graduado': False
                    })
                    cupo_cubierto += std_size
                    sec_id += 1

            # Procesar Profesores y Graduados
            profes_final = []
            for _, r in df_pro.iterrows():
                profes_final.append({'Nombre': str(r['Nombre']).upper(), 'Carga_Min': r['Carga_Min'], 'Carga_Max': r['Carga_Max'], 'es_graduado': False})
            for _, r in df_gra.iterrows():
                # Agregar curso de graduado a la lista de secciones
                secciones_list.append({
                    'uid': f"GRAD-{r['NOMBRE'][:5]}", 'creditos': r['CREDITOS'], 'cupo': 15, 'cands': [r['NOMBRE']], 'es_graduado': True
                })
                profes_final.append({'Nombre': str(r['NOMBRE']).upper(), 'Carga_Min': 0, 'Carga_Max': r['CREDITOS'], 'es_graduado': True})

            engine = PlatinumEngine(secciones_list, profes_final, df_sal.to_dict('records'), zona)
            df_res, confs, cargas_f = engine.ejecutar()
            
            st.session_state.horario = df_res
            st.session_state.confs = confs
            st.session_state.cargas = cargas_f
            st.session_state.profes_objs = profes_final

        if 'horario' in st.session_state:
            if st.session_state.confs:
                with st.expander("⚠️ REPORTE DE CONFLICTOS", expanded=True):
                    for c in st.session_state.confs: st.error(c)
            
            tab1, tab2 = st.tabs(["📅 HORARIO GENERAL", "👨‍🏫 DASHBOARD"])
            
            with tab1:
                df_disp = st.session_state.horario.copy()
                df_disp['Hora'] = df_disp['Inicio'].apply(mins_to_str) + " - " + df_disp['Fin'].apply(mins_to_str)
                st.dataframe(df_disp[['Curso', 'Profesor', 'Días', 'Hora', 'Salón', 'Cupo']], use_container_width=True)

            with tab2:
                p_sel = st.selectbox("Profesor:", st.session_state.horario['Profesor'].unique())
                carga = st.session_state.cargas[p_sel]
                st.metric("Carga Total Asignada", f"{carga} Créditos")
                st.table(st.session_state.horario[st.session_state.horario['Profesor'] == p_sel][['Curso', 'Días', 'Salón', 'Cupo']])

if __name__ == "__main__":
    main()
