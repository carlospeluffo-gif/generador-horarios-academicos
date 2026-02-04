import streamlit as st
import pandas as pd
import random
import copy
import io
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN Y ESTÉTICA PLATINUM
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum Pro", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3); }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000 !important; font-weight: bold; border-radius: 8px; }
    .report-card { background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .conflict-card { border-left: 5px solid #ff4b4b; background-color: #260c0c; padding: 10px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MODELOS DE DATOS
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, creditos, cupo, candidatos, tipo_salon):
        self.uid = uid
        self.cod_base = str(cod_base).strip().upper()
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon = str(tipo_salon).strip().upper()
        self.cands_list = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()]
        self.solo_graduados = "GRADUADOS" in self.cands_list

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, clases_recibe=None):
        self.nombre = str(nombre).strip().upper()
        self.c_min = float(c_min)
        self.c_max = float(c_max)
        self.es_graduado = es_graduado
        self.clases_recibe = [c.strip().upper() for c in clases_recibe] if clases_recibe else []

# ==============================================================================
# 3. MOTOR DE TIEMPO Y LOGICA GA
# ==============================================================================
def get_bloques(zona):
    bloques = {}
    h_inicio = [h*60 + 30 for h in range(7, 20)] if zona == "CENTRAL" else [h*60 for h in range(7, 20)]
    def add_b(id_b, dias, dur):
        for h in h_inicio:
            if h + dur <= 1320: bloques[f"{id_b}_{h}"] = {'dias': dias, 'inicio': h, 'fin': h+dur}
    add_b(1, ['Lu', 'Mi', 'Vi'], 50)
    add_b(2, ['Ma', 'Ju'], 80)
    add_b(3, ['Lu', 'Mi'], 110)
    return bloques

def mins_to_str(m):
    return f"{int(m//60):02d}:{int(m%60):02d}"

class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profes_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.bloques = get_bloques(zona)
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)

    def es_compatible(self, b_key, prof_nom, s_obj, oc_p, oc_s, mapa_horarios):
        b = self.bloques[b_key]
        # Hora Universal
        if any(d in ['Ma', 'Ju'] for d in b['dias']):
            if max(b['inicio'], self.h_univ[0]) < min(b['fin'], self.h_univ[1]): return False, "Hora Universal"
        
        # Restricción de Graduado Estudiante
        p_obj = self.profes_dict.get(prof_nom)
        if p_obj and p_obj.clases_recibe:
            for curso in p_obj.clases_recibe:
                if curso in mapa_horarios:
                    for (h_ini, h_fin, h_dias) in mapa_horarios[curso]:
                        if any(d in b['dias'] for d in h_dias):
                            if max(b['inicio'], h_ini) < min(b['fin'], h_fin):
                                return False, f"Choque con clase que recibe: {curso}"
        
        # Choques físicos
        for d in b['dias']:
            if (s_obj.codigo, d) in oc_s:
                for (t1, t2) in oc_s[(s_obj.codigo, d)]:
                    if max(b['inicio'], t1) < min(b['fin'], t2): return False, "Salón Ocupado"
            if prof_nom != "TBA" and (prof_nom, d) in oc_p:
                for (t1, t2) in oc_p[(prof_nom, d)]:
                    if max(b['inicio'], t1) < min(b['fin'], t2): return False, "Profesor Ocupado"
        
        return True, ""

    def ejecutar(self):
        genes, oc_p, oc_s, cargas = [], {}, {}, {p: 0 for p in self.profes_dict}
        mapa_horarios = {} # Codigo_Base -> [(ini, fin, dias)]
        reporte_tba = []
        detalles_conflictos = []

        # Ordenar: Laboratorios primero para cumplir la regla de "después de teoría" si fuera necesario
        # (Aquí priorizamos graduados por su rigidez de horario)
        sec_ord = sorted(self.secciones, key=lambda x: (not x.solo_graduados, x.uid))

        for sec in sec_ord:
            pool_p = [p.nombre for p in self.profes_dict.values() if p.es_graduado] if sec.solo_graduados else [c for c in sec.cands_list if c in self.profes_dict]
            
            prof = "TBA"
            if pool_p:
                validos = [p for p in pool_p if cargas[p] + sec.creditos <= self.profes_dict[p].c_max]
                if validos:
                    validos.sort(key=lambda p: (cargas[p] >= self.profes_dict[p].c_min, cargas[p]))
                    prof = validos[0]
                else:
                    reporte_tba.append(f"Sección {sec.uid}: Candidatos exceden carga máxima.")

            asignado = False
            pool_b = list(self.bloques.keys()); random.shuffle(pool_b)
            pool_s = [s for s in self.salones if s.capacidad >= sec.cupo and (sec.tipo_salon == 'GENERAL' or s.tipo == sec.tipo_salon)]
            random.shuffle(pool_s)

            for s in pool_s:
                for bk in pool_b:
                    comp, msg = self.es_compatible(bk, prof, s, oc_p, oc_s, mapa_horarios)
                    if comp:
                        b = self.bloques[bk]
                        cargas[prof] = cargas.get(prof, 0) + sec.creditos
                        for d in b['dias']:
                            oc_s.setdefault((s.codigo, d), []).append((b['inicio'], b['fin']))
                            if prof != "TBA": oc_p.setdefault((prof, d), []).append((b['inicio'], b['fin']))
                        
                        genes.append({'Seccion': sec.uid, 'Cod': sec.cod_base, 'Profesor': prof, 'Dias': "".join(b['dias']), 'Inicio': mins_to_str(b['inicio']), 'Fin': mins_to_str(b['fin']), 'Salon': s.codigo, 'IniMins': b['inicio']})
                        mapa_horarios.setdefault(sec.cod_base, []).append((b['inicio'], b['fin'], b['dias']))
                        asignado = True; break
                if asignado: break
            
            if not asignado:
                genes.append({'Seccion': sec.uid, 'Cod': sec.cod_base, 'Profesor': "TBA", 'Dias': "N/A", 'Inicio': "00:00", 'Fin': "00:00", 'Salon': "SIN ASIGNAR", 'IniMins': 0})
                detalles_conflictos.append(f"Error Crítico: No se encontró espacio para {sec.uid}")

        return pd.DataFrame(genes), reporte_tba, detalles_conflictos, cargas

# ==============================================================================
# 4. INTERFAZ STREAMLINED (TABS Y FILTROS)
# ==============================================================================
def main():
    st.header("🏛️ UPRM Scheduler Pro: Platinum Edition")
    
    with st.sidebar:
        st.subheader("Configuración Académica")
        zona = st.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
        archivo = st.file_uploader("Excel Maestro", type=['xlsx'])
        
        # Recomendación 4: Plantilla
        if st.checkbox("Ver guía de Excel"):
            st.info("Hojas: Cursos, Profesores, Salones, Graduados. En 'Graduados' usa nombres exactos.")

    if archivo:
        xls = pd.ExcelFile(archivo)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')
        df_gra = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else pd.DataFrame()

        # Validación Inicial (Recomendación 1)
        codigos_existentes = set(df_cur['CODIGO'].unique())
        if not df_gra.empty:
            for _, r in df_gra.iterrows():
                recibe = [c.strip().upper() for c in str(r.get('CLASES A RECIBIR','')).split(',') if c.strip()]
                for c in recibe:
                    if c not in codigos_existentes:
                        st.warning(f"⚠️ El graduado {r['NOMBRE']} toma {c}, pero ese curso no existe en la pestaña Cursos.")

        # Generar Objetos
        profesores = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max']) for _, r in df_pro.iterrows()]
        if not df_gra.empty:
            for _, r in df_gra.iterrows():
                clases = [c.strip().upper() for c in str(r.get('CLASES A RECIBIR','')).split(',') if c.strip()]
                profesores.append(Profesor(r['NOMBRE'], 0, r['CREDITOS'], True, clases))

        secciones = []
        for _, r in df_cur.iterrows():
            cupo_t = int(r['CUPO'])
            # Recomendación 2: Expansión de secciones
            cant = int(r.get('CANTIDAD_SECCIONES', cupo_t // 30))
            for i in range(1, cant + 1):
                secciones.append(Seccion(f"{r['CODIGO']}-{i:02d}", r['CODIGO'], r['CREDITOS'], cupo_t//cant, r['CANDIDATOS'], r.get('TIPO_SALON','GENERAL')))

        salones = [type('S',(),{'codigo':str(r['CODIGO']), 'capacidad':int(r['CAPACIDAD']), 'tipo':str(r['TIPO']).upper()}) for _,r in df_sal.iterrows()]

        if st.button("🚀 GENERAR PLANIFICACIÓN ACADÉMICA"):
            engine = PlatinumEngine(secciones, profesores, salones, zona)
            df_final, tba_list, conflictos, cargas_f = engine.ejecutar()

            # Recomendación 3: Pestañas
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Horario Maestro", "👨‍🏫 Carga Docente", "🏫 Uso de Salones", "⚠️ Reporte de Tesis"])

            with tab1:
                st.subheader("Horario Completo")
                # Filtros
                f_prof = st.multiselect("Filtrar por Profesor", options=df_final['Profesor'].unique())
                df_disp = df_final[df_final['Profesor'].isin(f_prof)] if f_prof else df_final
                st.dataframe(df_disp, use_container_width=True, hide_index=True)
                
                # Botón de Descarga (Recomendación 3)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Horario')
                st.download_button("📥 Descargar Excel", output.getvalue(), "Horario_UPRM.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            with tab2:
                st.subheader("Carga Asignada por Profesor")
                cargas_df = pd.DataFrame([{'Nombre': k, 'Creditos': v} for k, v in cargas_f.items()])
                st.bar_chart(cargas_df.set_index('Nombre'))
                st.table(cargas_df)

            with tab3:
                st.subheader("Ocupación de Salones")
                salon_occ = df_final.groupby('Salon').size().reset_index(name='Secciones')
                st.plotly_chart(px.pie(salon_occ, values='Secciones', names='Salon', hole=0.3))

            with tab4:
                st.subheader("Análisis para Jurado/Asesor")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### ❌ Conflictos y TBAs")
                    for t in tba_list: st.error(t)
                    for c in conflictos: st.warning(c)
                with col2:
                    st.write("### 🎓 Restricciones de Graduados")
                    for p in [p for p in profesores if p.es_graduado]:
                        st.info(f"Graduado: {p.nombre} | Bloqueado por tomar: {', '.join(p.clases_recibe)}")

if __name__ == "__main__":
    main()
