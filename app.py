import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Generación de Horarios Académicos - RUM",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Programas académicos del RUM organizados por colegio y nivel académico
PROGRAMAS_RUM = {
    "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
        "color": "#FF6B6B",
        "niveles": {
            "Bachilleratos en Administración de Empresas": [
                "Contabilidad",
                "Finanzas",
                "Gerencia de Recursos Humanos",
                "Mercadeo",
                "Gerencia de Operaciones",
                "Sistemas Computadorizados de Información",
                "Administración de Oficinas"
            ],
            "Maestrías en Administración de Empresas": [
                "Administración de Empresas (Programa General)",
                "Finanzas",
                "Gerencia Industrial",
                "Recursos Humanos"
            ]
        }
    },
    "COLEGIO DE ARTES Y CIENCIAS": {
        "color": "#4ECDC4",
        "niveles": {
            "Bachilleratos en Artes": [
                "Literatura Comparada",
                "Economía",
                "Inglés",
                "Historia",
                "Lengua y Literatura Francesa",
                "Estudios Hispánicos",
                "Filosofía",
                "Educación Física – Enseñanza",
                "Educación Física – Adiestramiento y Arbitraje",
                "Artes Plásticas",
                "Ciencias Políticas",
                "Psicología",
                "Ciencias Sociales",
                "Sociología",
                "Teoría del Arte"
            ],
            "Bachilleratos en Ciencias": [
                "Biología",
                "Microbiología Industrial",
                "Pre-Médica",
                "Biotecnología Industrial",
                "Química",
                "Geología",
                "Matemáticas",
                "Matemáticas – Ciencias de la Computación",
                "Educación Matemática",
                "Enfermería",
                "Física",
                "Ciencias Físicas"
            ],
            "Maestrías en Artes": [
                "Estudios Culturales y Humanísticos",
                "Estudios Hispánicos",
                "Educación en Inglés",
                "Kinesiología"
            ],
            "Maestrías en Ciencias": [
                "Biología",
                "Química",
                "Geología",
                "Ciencias Marinas",
                "Física",
                "Matemáticas Aplicadas",
                "Matemática Estadística",
                "Matemática Pura",
                "Enseñanza de las Matemáticas a nivel preuniversitario",
                "Computación Científica",
                "Psicología Escolar"
            ],
            "Doctorados en Filosofía": [
                "Ciencias Marinas",
                "Química Aplicada",
                "Psicología Escolar"
            ]
        }
    },
    "COLEGIO DE CIENCIAS AGRÍCOLAS": {
        "color": "#96CEB4",
        "niveles": {
            "Bachilleratos en Ciencias Agrícolas": [
                "Ciencias Agrícolas",
                "Agronomía",
                "Economía Agrícola",
                "Horticultura",
                "Ciencia Animal",
                "Protección de Cultivos",
                "Agronegocios",
                "Educación Agrícola",
                "Extensión Agrícola",
                "Suelos",
                "Sistemas Agrícolas y Ambientales",
                "Pre-Veterinaria (No conducente a grado)"
            ],
            "Maestrías en Ciencias": [
                "Agronomía",
                "Ciencias y Tecnología de Alimentos",
                "Economía Agrícola",
                "Educación Agrícola",
                "Extensión Agrícola",
                "Horticultura",
                "Ciencia Animal",
                "Protección de Cultivos",
                "Suelos"
            ]
        }
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#FFEAA7",
        "niveles": {
            "Bachilleratos en Ingeniería": [
                "Ingeniería Química",
                "Ingeniería Civil",
                "Ingeniería de Computadoras",
                "Ciencias e Ingeniería de la Computación",
                "Ingeniería Eléctrica",
                "Ingeniería Industrial",
                "Ingeniería Mecánica",
                "Ingeniería de Software",
                "Agrimensura y Topografía"
            ],
            "Maestrías en Ciencias": [
                "Bioingeniería",
                "Ingeniería Química",
                "Ingeniería Civil",
                "Ingeniería de Computadoras",
                "Ingeniería Eléctrica",
                "Ingeniería Industrial",
                "Ciencia e Ingeniería de Materiales",
                "Ingeniería Mecánica"
            ],
            "Maestrías en Ingeniería": [
                "Bioingeniería",
                "Ingeniería Química",
                "Ingeniería Civil",
                "Ingeniería de Computadoras",
                "Ingeniería Eléctrica",
                "Ingeniería Industrial",
                "Ciencia e Ingeniería de Materiales",
                "Ingeniería Mecánica"
            ],
            "Doctorados en Filosofía": [
                "Bioingeniería",
                "Ingeniería Química",
                "Ingeniería Civil",
                "Ingeniería Eléctrica",
                "Ingeniería Mecánica",
                "Ciencias e Ingeniería de la Información y la Computación"
            ]
        }
    }
}

def main():
    # Inicializar session state
    if 'programa_seleccionado' not in st.session_state:
        st.session_state.programa_seleccionado = None
    if 'colegio_seleccionado' not in st.session_state:
        st.session_state.colegio_seleccionado = None
    if 'nivel_seleccionado' not in st.session_state:
        st.session_state.nivel_seleccionado = None
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'seleccion'

    # Header principal
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🎓 Sistema de Generación de Horarios RUM</h1>
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem;">Recinto Universitario de Mayagüez - Optimización con Algoritmos Genéticos</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar con información del programa seleccionado
    with st.sidebar:
        st.markdown("### 📋 Estado Actual")
        
        if st.session_state.programa_seleccionado:
            st.success(f"**Programa:** {st.session_state.programa_seleccionado}")
            if st.session_state.nivel_seleccionado:
                st.info(f"**Nivel:** {st.session_state.nivel_seleccionado}")
            if st.session_state.colegio_seleccionado:
                st.info(f"**Colegio:** {st.session_state.colegio_seleccionado}")
        else:
            st.warning("No hay programa seleccionado")
        
        st.markdown("---")
        
        # Botón para volver a la selección
        if st.button("🔄 Cambiar Programa", use_container_width=True):
            st.session_state.pagina_actual = 'seleccion'
            st.session_state.programa_seleccionado = None
            st.session_state.colegio_seleccionado = None
            st.session_state.nivel_seleccionado = None
            st.rerun()

    # Contenido principal basado en la página actual
    if st.session_state.pagina_actual == 'seleccion':
        mostrar_seleccion_programa()
    elif st.session_state.pagina_actual == 'generador':
        mostrar_generador_horarios()

def mostrar_seleccion_programa():
    """Muestra la interfaz de selección de programa por colegio y nivel académico"""
    
    st.markdown("## 🏛️ Selecciona tu Programa Académico")
    st.markdown("Elige tu programa de estudio del Recinto Universitario de Mayagüez para generar horarios optimizados.")
    
    # Mostrar colegios
    for colegio, info in PROGRAMAS_RUM.items():
        with st.expander(f"🏛️ {colegio}", expanded=False):
            total_programas = sum(len(programas) for programas in info['niveles'].values())
            st.markdown(f"**{total_programas} programas disponibles en {len(info['niveles'])} niveles académicos**")
            
            # Mostrar niveles académicos
            for nivel, programas in info['niveles'].items():
                st.markdown(f"### 🎓 {nivel}")
                st.markdown(f"*{len(programas)} programas*")
                
                # Crear grid de programas para este nivel
                cols = st.columns(3)
                
                for idx, programa in enumerate(programas):
                    with cols[idx % 3]:
                        # Card del programa
                        card_html = f"""
                        <div style="
                            border: 1px solid {info['color']};
                            border-radius: 8px;
                            padding: 0.8rem;
                            margin: 0.3rem 0;
                            background: linear-gradient(135deg, {info['color']}15, {info['color']}08);
                            text-align: center;
                            min-height: 80px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <p style="color: #333; margin: 0; font-size: 0.85rem; font-weight: 500; line-height: 1.2;">{programa}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        if st.button(f"Seleccionar", key=f"btn_{colegio}_{nivel}_{programa}", use_container_width=True):
                            st.session_state.programa_seleccionado = programa
                            st.session_state.colegio_seleccionado = colegio
                            st.session_state.nivel_seleccionado = nivel
                            st.rerun()
                
                st.markdown("---")

    # Si se ha seleccionado un programa, mostrar confirmación y botón para continuar
    if st.session_state.programa_seleccionado:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.success(f"✅ **Programa:** {st.session_state.programa_seleccionado}")
            st.info(f"🎓 **Nivel:** {st.session_state.nivel_seleccionado}")
            st.info(f"🏛️ **Colegio:** {st.session_state.colegio_seleccionado}")
            
            if st.button("🚀 Continuar al Generador de Horarios", type="primary", use_container_width=True):
                st.session_state.pagina_actual = 'generador'
                st.rerun()

def mostrar_generador_horarios():
    """Muestra la interfaz del generador de horarios"""
    
    # Información del programa seleccionado
    colegio_info = None
    for colegio, info in PROGRAMAS_RUM.items():
        if colegio == st.session_state.colegio_seleccionado:
            colegio_info = info
            break
    
    if colegio_info:
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {colegio_info['color']}30, {colegio_info['color']}10);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            border-left: 5px solid {colegio_info['color']};
        ">
            <h3 style="margin: 0; color: #333;">📚 {st.session_state.programa_seleccionado}</h3>
            <p style="margin: 0.3rem 0; color: #666; font-size: 1rem;">🎓 {st.session_state.nivel_seleccionado}</p>
            <p style="margin: 0.3rem 0 0 0; color: #888; font-size: 0.9rem;">🏛️ {st.session_state.colegio_seleccionado}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📁 Cargar Datos para Generación de Horarios")
    
    # Instrucciones específicas por nivel académico
    with st.expander("📋 Instrucciones para tu programa"):
        st.markdown(f"""
        ### Configuración para {st.session_state.programa_seleccionado}
        **Nivel:** {st.session_state.nivel_seleccionado}
        
        **Formato del archivo Excel requerido:**
        - **Hoja:** Debe contener los datos de profesores y cursos
        - **Columnas requeridas:** Profesor, Curso/Materia, Créditos, Estudiantes
        
        **Consideraciones especiales para {st.session_state.nivel_seleccionado}:**
        """)
        
        if "Bachillerato" in st.session_state.nivel_seleccionado:
            st.markdown("""
            - Cursos básicos y de concentración
            - Horarios diurnos principalmente (7:30 AM - 5:00 PM)
            - Clases de 50 minutos o 1 hora 20 minutos
            - Laboratorios de 2-3 horas consecutivas
            """)
        elif "Maestría" in st.session_state.nivel_seleccionado:
            st.markdown("""
            - Cursos especializados y seminarios
            - Horarios flexibles (incluyendo nocturnos)
            - Clases de 2 horas 30 minutos típicamente
            - Tesis y proyectos de investigación
            """)
        elif "Doctorado" in st.session_state.nivel_seleccionado:
            st.markdown("""
            - Seminarios doctorales especializados
            - Horarios muy flexibles
            - Investigación dirigida
            - Defensa de disertación
            """)
        
        if "INGENIERÍA" in st.session_state.colegio_seleccionado:
            st.markdown("""
            
            **Adicional para Ingeniería:**
            - Laboratorios requieren equipos especializados
            - Talleres y proyectos necesitan espacios amplios
            - Coordinación con industria para prácticas
            """)
        elif "CIENCIAS AGRÍCOLAS" in st.session_state.colegio_seleccionado:
            st.markdown("""
            
            **Adicional para Ciencias Agrícolas:**
            - Trabajo de campo en horarios variables
            - Laboratorios con organismos vivos
            - Dependencia de condiciones climáticas
            """)

    # Upload del archivo Excel
    uploaded_file = st.file_uploader(
        "📁 Cargar archivo Excel con datos de profesores y cursos",
        type=['xlsx', 'xls'],
        help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes"
    )

    if uploaded_file is not None:
        st.success("✅ Archivo cargado correctamente")
        
        # Configuración de parámetros específicos por nivel
        st.markdown("### ⚙️ Configuración de Parámetros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Parámetros de Optimización")
            intentos = st.slider("Número de iteraciones", 50, 500, 200, 50)
            
            # Configuración específica por nivel
            if "Bachillerato" in st.session_state.nivel_seleccionado:
                creditos_max = st.number_input("Créditos máximos por profesor", 1, 20, 15)
            elif "Maestría" in st.session_state.nivel_seleccionado:
                creditos_max = st.number_input("Créditos máximos por profesor", 1, 15, 12)
            else:  # Doctorado
                creditos_max = st.number_input("Créditos máximos por profesor", 1, 10, 8)
            
        with col2:
            st.subheader("⏰ Restricciones de Horario")
            
            # Horarios por defecto según nivel
            if "Bachillerato" in st.session_state.nivel_seleccionado:
                hora_inicio_default = "07:30"
                hora_fin_default = "17:00"
            elif "Maestría" in st.session_state.nivel_seleccionado:
                hora_inicio_default = "08:00"
                hora_fin_default = "21:00"
            else:  # Doctorado
                hora_inicio_default = "09:00"
                hora_fin_default = "19:00"
            
            hora_inicio = st.time_input("Hora inicio mínima", datetime.strptime(hora_inicio_default, "%H:%M").time())
            hora_fin = st.time_input("Hora fin máxima", datetime.strptime(hora_fin_default, "%H:%M").time())
        
        # Botón para procesar
        if st.button("🎯 Generar Horario Optimizado", type="primary"):
            with st.spinner("Generando horario optimizado..."):
                st.success("🚀 Iniciando generación de horario...")
                
                # Crear datos de ejemplo específicos por nivel
                if "Bachillerato" in st.session_state.nivel_seleccionado:
                    ejemplo_horario = {
                        'Curso': ['Cálculo I', 'Física I', 'Química General', 'Lab. Química'],
                        'Profesor': ['Dr. Juan Pérez', 'Dra. María García', 'Dr. Carlos López', 'Dr. Carlos López'],
                        'Día': ['Lunes', 'Martes', 'Miércoles', 'Miércoles'],
                        'Hora Inicio': ['08:00', '10:00', '14:00', '16:00'],
                        'Hora Fin': ['09:20', '11:20', '15:20', '19:00'],
                        'Salón': ['Aula 101', 'Aula 102', 'Aula 201', 'Lab 301']
                    }
                elif "Maestría" in st.session_state.nivel_seleccionado:
                    ejemplo_horario = {
                        'Curso': ['Seminario Avanzado', 'Métodos de Investigación', 'Tesis I'],
                        'Profesor': ['Dr. Ana Rodríguez', 'Dr. Luis Martín', 'Dr. Ana Rodríguez'],
                        'Día': ['Lunes', 'Miércoles', 'Viernes'],
                        'Hora Inicio': ['18:00', '19:00', '14:00'],
                        'Hora Fin': ['20:30', '21:30', '17:00'],
                        'Salón': ['Aula Grad 1', 'Aula Grad 2', 'Oficina']
                    }
                else:  # Doctorado
                    ejemplo_horario = {
                        'Curso': ['Seminario Doctoral', 'Investigación Dirigida'],
                        'Profesor': ['Dr. Roberto Silva', 'Dr. Roberto Silva'],
                        'Día': ['Martes', 'Jueves'],
                        'Hora Inicio': ['15:00', '10:00'],
                        'Hora Fin': ['18:00', '13:00'],
                        'Salón': ['Sala Seminarios', 'Laboratorio']
                    }
                
                df_resultado = pd.DataFrame(ejemplo_horario)
                
                st.markdown("### 📊 Horario Generado")
                st.dataframe(df_resultado, use_container_width=True)
                
                # Botón de descarga
                csv = df_resultado.to_csv(index=False)
                filename = f"horario_{st.session_state.programa_seleccionado.replace(' ', '_')}_{st.session_state.nivel_seleccionado.replace(' ', '_')}.csv"
                st.download_button(
                    label="💾 Descargar horario (CSV)",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
    
    else:
        # Mostrar ejemplo de formato
        st.markdown("### 📊 Ejemplo de formato esperado:")
        
        ejemplo_data = {
            'Profesor': ['Dr. Juan Pérez', 'Dr. Juan Pérez', 'Dra. María García', 'Dra. María García'],
            'Curso': ['Cálculo I', 'Álgebra Lineal', 'Física I', 'Laboratorio de Física'],
            'Créditos': [4, 3, 4, 2],
            'Estudiantes': [35, 28, 30, 15]
        }
        
        df_ejemplo = pd.DataFrame(ejemplo_data)
        st.dataframe(df_ejemplo, use_container_width=True)

if __name__ == "__main__":
    main()

