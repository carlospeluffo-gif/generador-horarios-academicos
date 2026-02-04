import streamlit as st
import pandas as pd
import random
import copy
import io
import plotly.express as px

# ==============================================================================
# 1. CONFIGURACIÓN Y ESTÉTICA PLATINUM PRO
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum Final", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3); }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #333; background: #111; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MODELOS DE DATOS AVANZADOS
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, creditos, cupo, candidatos, tipo_salon):
        self.uid = uid
        self.cod_base = str(cod_base).strip().upper()
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon = str(tipo_salon).strip().upper()
        cands = str(candidatos).strip().upper()
        self.cands_list = [c.strip() for c in cands.split(',') if c.strip()]
        self.es_graduado_req = "GRADUADOS" in self.cands_list
        self.es_lab = "LAB" in self.uid

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, recibe=None):
        self.nombre = str(nombre).strip().upper()
        self.c_min, self.c_max = float(c_min), float(c_max)
        self.es_graduado = es_graduado
        self.recibe = recibe if recibe else []

# ==============================================================================
# 3. MOTOR PLATINUM CON LÓGICA DE LABORATORIOS
# ==============================================================================
class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profes_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.bloques = self._gen_bloques(zona)

    def _gen_bloques(self, zona):
        b = {}
        h_ini = [h*60 + 30 for h in range(7, 20)] if zona == "CENTRAL" else [h*60 for h in range(7, 20)]
        for h in h_ini:
            b[f"LMV_{h}"] = {'dias': ['Lu','Mi','Vi'], 'ini': h, 'fin': h+50}
            b[f"MJ_{h}"] = {'dias': ['Ma','Ju'], 'ini': h, 'fin': h+80}
        return b

    def ejecutar(self):
        res, oc_p, oc_s, cargas = [], {}, {}, {p: 0 for p in self.profes_dict}
        mapa_teoria = {} # Para guardar donde quedaron las teorías y poner los labs después
        tba_report = []

        # Ordenar: Teorías primero, luego Labs
        sec_ord = sorted(self.secciones, key=lambda x: (x.es_lab, not x.es_graduado_req))

        for sec in sec_ord:
            # 1. Selección de Profesor
            cands = [p.nombre for p in self.profes_dict.values() if p.es_graduado] if sec.es_graduado_req else [c for c in sec.cands_list if c in self.profes_dict]
            prof = "TBA"
            if cands:
                validos = [c for c in cands if cargas[c] + sec.creditos <= self.profes_dict[c].c_max]
                if validos:
                    validos.sort(key=lambda c: (cargas[c] >= self.profes_dict[c].c_min, cargas[c]))
                    prof = validos[0]
                else: tba_report.append(f"Carga excedida para {sec.uid}")

            # 2. Búsqueda de Espacio (Con restricción de Lab)
            pool_b = list(self.bloques.keys())
            if sec.es_lab:
                # Si es lab, intentamos que sea más tarde que la teoría del mismo código
                cod_teoria = sec.cod_base.replace(" LAB", "").strip()
                if cod_teoria in mapa_teoria:
                    h_teoria = mapa_teoria[cod_teoria]['ini']
                    pool_b = [k for k in pool_b if self.bloques[k]['ini'] > h_teoria] or pool_b

            asignado = False
            for bk in pool_b:
                b = self.bloques[bk]
                # Filtrar salón por tipo
                s_validos = [s for s in self.salones if s.capacidad >= sec.cupo and (s.tipo == sec.tipo_salon or sec.tipo_salon == 'GENERAL')]
                for s in s_validos:
                    # Validar choques
                    choque = False
                    for d in b['dias']:
                        if (s.codigo, d) in oc_s or (prof != "TBA" and (prof, d) in oc_p):
                            # (Simplicidad de choque por bloque)
                            choque = True; break
                    
                    if not choque:
                        cargas[prof] += sec.creditos
                        for d in b['dias']:
                            oc_s[(s.codigo, d)] = True
                            if prof != "TBA": oc_p[(prof, d)] = True
                        
                        data = {'Sección': sec.uid, 'Profesor': prof, 'Días': "".join(b['dias']), 'Hora': f"{int(b['ini']//60)}:{int(b['ini']%60):02d}", 'Salón': s.codigo}
                        res.append(data)
                        if not sec.es_lab: mapa_teoria[sec.cod_base] = b
                        asignado = True; break
                if asignado: break
            
            if not asignado: res.append({'Sección': sec.uid, 'Profesor': "TBA", 'Días': "ERROR", 'Hora': "N/A", 'Salón': "N/A"})

        return pd.DataFrame(res), tba_report, cargas

# ==============================================================================
# 4. INTERFAZ FINAL
# ==============================================================================
def main():
    st.title("🏛️ Sistema de Planificación Platinum Pro")
    
    with st.sidebar:
        st.header("Entrada de Datos")
        zona = st.selectbox("Zona Académica", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("Subir Archivo Excel", type=['xlsx'])
        
    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')
        df_gra = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else pd.DataFrame()

        # Procesar Profesores y Graduados
        profesores = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max']) for _, r in df_pro.iterrows()]
        if not df_gra.empty:
            for _, r in df_gra.iterrows():
                recibe = [c.strip().upper() for c in str(r.get('CLASES A RECIBIR','')).split(',') if c.strip()]
                profesores.append(Profesor(r['NOMBRE'], 0, r['CREDITOS'], True, recibe))

        # Generar Secciones automáticas
        secciones = []
        for _, r in df_cur.iterrows():
            total_cupo = int(r['CUPO'])
            n_sec = int(r.get('CANTIDAD_SECCIONES', total_cupo // 30))
            for i in range(1, n_sec + 1):
                secciones.append(Seccion(f"{r['CODIGO']}-{i:02d}", r['CODIGO'], r['CREDITOS'], total_cupo//n_sec, r['CANDIDATOS'], r.get('TIPO_SALON','GENERAL')))

        salones = [type('S',(),{'codigo':str(r['CODIGO']), 'capacidad':int(r['CAPACIDAD']), 'tipo':str(r['TIPO']).upper()}) for _,r in df_sal.iterrows()]

        if st.button("🚀 GENERAR HORARIO MAESTRO"):
            engine = PlatinumEngine(secciones, profesores, salones, zona)
            df_res, tbas, cargas_finales = engine.ejecutar()

            tab1, tab2, tab3 = st.tabs(["📅 Horario Maestro", "📊 Análisis de Carga", "🧪 Reporte de Tesis"])

            with tab1:
                st.dataframe(df_res, use_container_width=True)
                csv = df_res.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar Resultados (CSV)", csv, "horario_uprm.csv", "text/csv")

            with tab2:
                c_df = pd.DataFrame([{'Nombre': k, 'Créditos': v} for k, v in cargas_finales.items()])
                st.plotly_chart(px.bar(c_df, x='Nombre', y='Créditos', title="Distribución de Créditos por Profesor"))

            with tab3:
                st.subheader("Validación Académica")
                col1, col2 = st.columns(2)
                col1.metric("Secciones Totales", len(secciones))
                col1.metric("Conflictos/TBA", len(tbas))
                with col2:
                    st.write("### Hallazgos del Motor")
                    for t in tbas[:5]: st.warning(t)
                    if not tbas: st.success("¡Optimización completada sin violaciones de carga!")

if __name__ == "__main__":
    main()
