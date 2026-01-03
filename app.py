import streamlit as st
import pandas as pd
import random
import re
from datetime import datetime

# ========================================================
# CONFIGURACIÓN DE ZONAS
# ========================================================

class ZonaConfig:
    """Configuración de zonas Central y Periférica"""
    
    CENTRAL = {
        "nombre": "Zona Central",
        "horarios_inicio": ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30", "17:30", "18:30"],
        "restricciones": {
            "Ma": [("10:30", "12:30")],
            "Ju": [("10:30", "12:30")]
        },
        "descripcion": "⏰ Horarios cada 60 min desde 7:30 AM\n🚫 Hora Universal: No clases Ma-Ju 10:30-12:30"
    }
    
    PERIFERICA = {
        "nombre": "Zona Periférica",
        "horarios_inicio": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
        "restricciones": {
            "Lu": [("10:00", "12:00")],
            "Ma": [("10:00", "12:00")],
            "Mi": [("10:00", "12:00")],
            "Ju": [("10:00", "12:00")],
            "Vi": [("10:00", "12:00")]
        },
        "descripcion": "⏰ Horarios cada 60 min desde 7:00 AM\n🚫 Hora Universal: No clases 10:00-12:00"
    }

# ========================================================
# PROCESADOR DE EXCEL/CSV
# ========================================================

class ProcesadorExcelFormulario:
    """Procesa el Excel/CSV del formulario de Google Forms"""
    
    def __init__(self, archivo):
        self.archivo = archivo
        self.df_original = None
        self.profesores_data = {}
        
    def cargar_archivo(self):
        """Carga el archivo Excel o CSV"""
        try:
            # Intentar cargar como Excel
            try:
                df = pd.read_excel(self.archivo, sheet_name=0)
                st.success(f"✅ Excel cargado: {len(df)} filas")
            except:
                # Intentar como CSV
                self.archivo.seek(0)
                df = pd.read_csv(self.archivo)
                st.success(f"✅ CSV cargado: {len(df)} filas")
            
            # Verificar si las columnas están en la primera fila
            if len(df.columns) == 1 or ',' in str(df.columns[0]):
                st.warning("⚠️ Detectado formato especial, reprocessando...")
                
                # Leer de nuevo sin header
                self.archivo.seek(0)
                try:
                    df_raw = pd.read_excel(self.archivo, sheet_name=0, header=None)
                except:
                    self.archivo.seek(0)
                    df_raw = pd.read_csv(self.archivo, header=None)
                
                # Buscar la fila con los headers
                for idx, row in df_raw.iterrows():
                    row_str = str(row[0])
                    if 'SERIES' in row_str or 'PROFESSORS' in row_str:
                        # Encontramos los headers
                        headers = row_str.split(',')
                        headers = [h.strip().strip('"') for h in headers]
                        
                        # Extraer datos
                        data_rows = []
                        for idx2 in range(idx + 1, len(df_raw)):
                            row_data = str(df_raw.iloc[idx2, 0]).split(',')
                            row_data = [d.strip().strip('"') for d in row_data]
                            if len(row_data) == len(headers):
                                data_rows.append(row_data)
                        
                        df = pd.DataFrame(data_rows, columns=headers)
                        st.success(f"✅ Formato corregido: {len(df)} filas, {len(df.columns)} columnas")
                        break
            
            self.df_original = df
            
            # Mostrar columnas detectadas
            with st.expander("🔍 Columnas detectadas"):
                for i, col in enumerate(df.columns):
                    st.write(f"{i+1}. `{col}`")
            
            # Mostrar muestra de datos
            with st.expander("👀 Primeras filas"):
                st.dataframe(df.head(3))
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al cargar archivo: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    def extraer_profesor_y_porcentaje(self, profesor_str):
        """Extrae nombre del profesor y porcentaje"""
        if pd.isna(profesor_str) or str(profesor_str).strip() == '':
            return None, 100
        
        match = re.search(r'(.+?)\s*\((\d+)%\)', str(profesor_str))
        if match:
            return match.group(1).strip(), int(match.group(2))
        return str(profesor_str).strip(), 100
    
    def procesar_datos(self):
        """Procesa los datos y extrae información de profesores"""
        if self.df_original is None:
            return False
        
        # Mapeo de columnas
        col_map = {}
        for col in self.df_original.columns:
            col_upper = str(col).upper()
            if 'SERIES' in col_upper or 'CODIGO' in col_upper:
                col_map['codigo'] = col
            elif 'NAME SPA' in col_upper or 'NOMBRE' in col_upper:
                col_map['nombre'] = col
            elif 'CREDIT' in col_upper:
                col_map['creditos'] = col
            elif 'PROFESSOR' in col_upper and 'EMAIL' not in col_upper:
                col_map['profesor'] = col
            elif 'EMAIL' in col_upper:
                col_map['email'] = col
            elif 'CAPACITY' in col_upper or 'CAPACIDAD' in col_upper:
                col_map['capacidad'] = col
            elif 'SECTION' in col_upper or 'SECCION' in col_upper:
                col_map['seccion'] = col
        
        st.info("📋 Mapeo de columnas:")
        for key, val in col_map.items():
            st.success(f"✅ {key}: `{val}`")
        
        # Procesar filas
        filas_ok = 0
        filas_error = 0
        
        for idx, fila in self.df_original.iterrows():
            try:
                # Extraer datos
                codigo = fila.get(col_map.get('codigo', ''), f'CURSO_{idx}')
                nombre = fila.get(col_map.get('nombre', ''), 'Sin nombre')
                creditos = fila.get(col_map.get('creditos', ''), 3)
                capacidad = fila.get(col_map.get('capacidad', ''), 30)
                profesor_str = fila.get(col_map.get('profesor', ''), '')
                email = fila.get(col_map.get('email', ''), '')
                seccion = fila.get(col_map.get('seccion', ''), '001')
                
                # Saltar filas vacías
                if pd.isna(codigo) or str(codigo).strip() == '':
                    continue
                
                # Extraer profesor
                profesor_nombre, porcentaje = self.extraer_profesor_y_porcentaje(profesor_str)
                if not profesor_nombre:
                    profesor_nombre = f"Profesor_{idx}"
                
                # Inicializar profesor
                if profesor_nombre not in self.profesores_data:
                    self.profesores_data[profesor_nombre] = {
                        'email': email,
                        'cursos': [],
                        'creditos_totales': 0,
                        'dias_preferidos': [],
                        'turno_preferido': 'Mañana'
                    }
                
                # Convertir valores
                try:
                    creditos_num = int(float(creditos))
                except:
                    creditos_num = 3
                
                try:
                    capacidad_num = int(float(capacidad))
                except:
                    capacidad_num = 30
                
                # Agregar curso
                curso_info = {
                    'codigo': str(codigo),
                    'nombre': str(nombre),
                    'creditos': creditos_num,
                    'estudiantes': capacidad_num,
                    'porcentaje_carga': porcentaje,
                    'seccion': str(seccion)
                }
                
                self.profesores_data[profesor_nombre]['cursos'].append(curso_info)
                self.profesores_data[profesor_nombre]['creditos_totales'] += creditos_num
                
                filas_ok += 1
                
            except Exception as e:
                filas_error += 1
                continue
        
        st.success(f"✅ Procesamiento completado:")
        st.info(f"• {filas_ok} cursos procesados")
        st.info(f"• {len(self.profesores_data)} profesores identificados")
        if filas_error > 0:
            st.warning(f"• {filas_error} filas con errores")
        
        return len(self.profesores_data) > 0
    
    def obtener_profesores_config(self):
        return self.profesores_data

# ========================================================
# GENERACIÓN DE HORARIOS
# ========================================================

SALONES = [
    "M 102", "M 104", "M 105", "M 110", "M 112", "M 203", "M 205", "M 210", 
    "M 213", "M 214", "M 215", "M 220", "M 222", "M 236", "M 238", "M 302", 
    "M 303", "M 304", "M 305", "M 306", "M 311", "M 315", "M 316", "M 317", 
    "M 338", "M 340", "M 341", "M 402", "M 403", "M 404"
]

def generar_bloques_horarios():
    """Genera bloques de horarios según créditos"""
    bloques = []
    id_counter = 1

    # Bloques de 4 créditos
    for dias in [["Lu","Ma","Mi","Ju"], ["Lu","Ma","Mi","Vi"], ["Ma","Mi","Ju","Vi"]]:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4})
        id_counter += 1

    for dias in [["Lu","Mi"], ["Ma","Ju"]]:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2,2], "creditos": 4})
        id_counter += 1

    # Bloques de 3 créditos
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3})
    id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3})
    id_counter += 1

    # Bloques de 5 créditos
    for dias, horas in [(["Lu","Mi","Vi"], [2,2,1]), (["Ma","Ju","Vi"], [1.5,1.5,2])]:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5})
        id_counter += 1

    return bloques

def a_minutos(hhmm):
    """Convierte hora a minutos"""
    try:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    except:
        return 0

def horario_valido_zona(dia, hora_inicio, duracion, zona_config):
    """Verifica si el horario es válido según restricciones de zona"""
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    restricciones = zona_config['restricciones']
    if dia in restricciones:
        for r_ini, r_fin in restricciones[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False
    
    return True

class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_codigo = curso_info["codigo"]
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.seccion = curso_info.get("seccion", "001")
        
    def get_horario_detallado(self):
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            
            horarios.append({
                "Código": self.curso_codigo,
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Sección": self.seccion,
                "Día": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Estudiantes": self.estudiantes,
                "Salón": self.salon
            })
        return horarios

def hay_conflictos(nueva_asignacion, asignaciones_existentes):
    """Verifica conflictos de profesor o salón"""
    for asignacion in asignaciones_existentes:
        for dia_nuevo, dur_nuevo in zip(nueva_asignacion.bloque["dias"], nueva_asignacion.bloque["horas"]):
            ini_nuevo = a_minutos(nueva_asignacion.hora_inicio)
            fin_nuevo = ini_nuevo + int(dur_nuevo * 60)
            
            for dia_exist, dur_exist in zip(asignacion.bloque["dias"], asignacion.bloque["horas"]):
                if dia_nuevo == dia_exist:
                    ini_exist = a_minutos(asignacion.hora_inicio)
                    fin_exist = ini_exist + int(dur_exist * 60)
                    
                    if not (fin_nuevo <= ini_exist or ini_nuevo >= fin_exist):
                        if nueva_asignacion.profesor == asignacion.profesor:
                            return True
                        if nueva_asignacion.salon == asignacion.salon:
                            return True
    
    return False

def generar_horario_optimizado(profesores_config, zona_config, intentos=200):
    """Genera horario optimizado"""
    mejor_asignaciones = None
    mejor_score = -1
    
    bloques = generar_bloques_horarios()
    horas_inicio = zona_config['horarios_inicio']
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for intento in range(intentos):
        progress_bar.progress((intento + 1) / intentos)
        status_text.text(f"Generando horarios... {intento+1}/{intentos}")
        
        asignaciones = []
        
        for profesor, prof_config in profesores_config.items():
            for curso_info in prof_config['cursos']:
                bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
                if not bloques_compatibles:
                    bloques_compatibles = bloques[:5]
                
                mejor_asignacion_curso = None
                
                for _ in range(30):
                    bloque = random.choice(bloques_compatibles)
                    hora_inicio = random.choice(horas_inicio)
                    salon = random.choice(SALONES)
                    
                    valido = True
                    for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                        if not horario_valido_zona(dia, hora_inicio, duracion, zona_config):
                            valido = False
                            break
                    
                    if not valido:
                        continue
                    
                    nueva_asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
                    
                    if not hay_conflictos(nueva_asignacion, asignaciones):
                        mejor_asignacion_curso = nueva_asignacion
                        break
                
                if mejor_asignacion_curso:
                    asignaciones.append(mejor_asignacion_curso)
        
        total_cursos = sum(len(prof['cursos']) for prof in profesores_config.values())
        if len(asignaciones) >= mejor_score:
            mejor_score = len(asignaciones)
            mejor_asignaciones = asignaciones
            
            if len(asignaciones) == total_cursos:
                status_text.text(f"✅ Solución completa encontrada en intento {intento+1}")
                break
    
    progress_bar.progress(1.0)
    status_text.text(f"Completado. Cursos asignados: {mejor_score}/{total_cursos}")
    
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    """Exporta horario a DataFrame"""
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    return pd.DataFrame(registros)

# ========================================================
# INTERFAZ PRINCIPAL
# ========================================================

def main():
    st.set_page_config(
        page_title="Sistema de Horarios - Matemáticas RUM",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Sistema de Generación de Horarios")
    st.markdown("### Departamento de Matemáticas - RUM")
    
    # ===== PASO 1: SELECCIÓN DE ZONA =====
    st.markdown("---")
    st.markdown("## 🗺️ Paso 1: Seleccionar Zona del Campus")
    
    col1, col2 = st.columns(2)
    
    with col1:
        zona_central = st.button(
            "🏛️ ZONA CENTRAL",
            use_container_width=True,
            type="primary" if st.session_state.get('zona_seleccionada') == 'Central' else "secondary"
        )
        if zona_central:
            st.session_state.zona_seleccionada = 'Central'
        
        if st.session_state.get('zona_seleccionada') == 'Central':
            st.info(ZonaConfig.CENTRAL['descripcion'])
    
    with col2:
        zona_periferica = st.button(
            "🏘️ ZONA PERIFÉRICA",
            use_container_width=True,
            type="primary" if st.session_state.get('zona_seleccionada') == 'Periférica' else "secondary"
        )
        if zona_periferica:
            st.session_state.zona_seleccionada = 'Periférica'
        
        if st.session_state.get('zona_seleccionada') == 'Periférica':
            st.info(ZonaConfig.PERIFERICA['descripcion'])
    
    # Verificar que se haya seleccionado zona
    if 'zona_seleccionada' not in st.session_state:
        st.warning("⚠️ Por favor selecciona una zona para continuar")
        return
    
    zona_config = ZonaConfig.CENTRAL if st.session_state.zona_seleccionada == 'Central' else ZonaConfig.PERIFERICA
    
    # ===== PASO 2: CARGAR ARCHIVO =====
    st.markdown("---")
    st.markdown("## 📁 Paso 2: Cargar Archivo de Cursos")
    
    uploaded_file = st.file_uploader(
        "Subir Excel (.xlsx) o CSV (.csv)",
        type=['xlsx', 'xls', 'csv'],
        help="Archivo del formulario de Google Forms con información de cursos"
    )
    
    # Session state
    if 'profesores_config' not in st.session_state:
        st.session_state.profesores_config = {}
    if 'horario_generado' not in st.session_state:
        st.session_state.horario_generado = None
    
    if uploaded_file is not None:
        if st.button("🔄 Procesar Archivo", type="primary"):
            with st.spinner("Procesando archivo..."):
                procesador = ProcesadorExcelFormulario(uploaded_file)
                if procesador.cargar_archivo():
                    if procesador.procesar_datos():
                        st.session_state.profesores_config = procesador.obtener_profesores_config()
                        st.success("✅ Archivo procesado correctamente")
                        st.balloons()
    
    # ===== PASO 3: GENERAR HORARIO =====
    if st.session_state.profesores_config:
        st.markdown("---")
        st.markdown("## 🚀 Paso 3: Generar Horario")
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Profesores", len(st.session_state.profesores_config))
        with col2:
            total_cursos = sum(len(p['cursos']) for p in st.session_state.profesores_config.values())
            st.metric("Cursos totales", total_cursos)
        with col3:
            st.metric("Zona", st.session_state.zona_seleccionada)
        
        intentos = st.slider("Iteraciones de optimización", 50, 500, 200, 50)
        
        if st.button("🎯 Generar Horario Optimizado", type="primary"):
            with st.spinner("Generando horario..."):
                asignaciones, score = generar_horario_optimizado(
                    st.session_state.profesores_config,
                    zona_config,
                    intentos
                )
                
                if asignaciones:
                    st.session_state.horario_generado = exportar_horario(asignaciones)
                    total_cursos = sum(len(p['cursos']) for p in st.session_state.profesores_config.values())
                    st.success(f"✅ Horario generado: {score}/{total_cursos} cursos asignados")
                    st.balloons()
                else:
                    st.error("❌ No se pudo generar horario")
    
    # ===== PASO 4: VISUALIZAR HORARIO =====
    if st.session_state.horario_generado is not None:
        st.markdown("---")
        st.markdown("## 📊 Paso 4: Visualizar Horario Generado")
        
        df_horario = st.session_state.horario_generado
        
        # Tabs de visualización
        tab1, tab2, tab3 = st.tabs(["📋 Tabla Completa", "👨‍🏫 Por Profesor", "🏛️ Por Salón"])
        
        with tab1:
            st.dataframe(df_horario, use_container_width=True)
            
            csv = df_horario.to_csv(index=False)
            st.download_button(
                "📥 Descargar CSV",
                csv,
                f"horario_{st.session_state.zona_seleccionada}_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                type="primary"
            )
        
        with tab2:
            profesor_filtro = st.selectbox(
                "Seleccionar profesor:",
                sorted(df_horario['Profesor'].unique())
            )
            df_filtrado = df_horario[df_horario['Profesor'] == profesor_filtro]
            st.dataframe(df_filtrado, use_container_width=True)
        
        with tab3:
            salon_filtro = st.selectbox(
                "Seleccionar salón:",
                sorted(df_horario['Salón'].unique())
            )
            df_filtrado = df_horario[df_horario['Salón'] == salon_filtro]
            st.dataframe(df_filtrado, use_container_width=True)
        
        # Estadísticas
        st.markdown("---")
        st.markdown("### 📈 Estadísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Clases programadas", len(df_horario))
        with col2:
            st.metric("Profesores activos", df_horario['Profesor'].nunique())
        with col3:
            st.metric("Salones utilizados", df_horario['Salón'].nunique())
        with col4:
            st.metric("Estudiantes totales", df_horario['Estudiantes'].sum())

if __name__ == "__main__":
    main()
