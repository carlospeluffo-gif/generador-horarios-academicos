import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os
from pathlib import Path
import hashlib

# ========================================================
# SISTEMA DE AUTENTICACIÓN Y CREDENCIALES ACTUALIZADO
# ========================================================

def generar_credenciales():
    """Genera el diccionario de credenciales basado en PROGRAMAS_RUM"""
    credenciales = {}
    
    # Mapear colegios a usuarios simplificados
    mapeo_usuarios = {
        "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": "Administración de Empresas",
        "COLEGIO DE ARTES Y CIENCIAS": "Artes y Ciencias", 
        "COLEGIO DE CIENCIAS AGRÍCOLAS": "Ciencias Agrícolas",
        "COLEGIO DE INGENIERÍA": "Ingeniería",
        "DEPARTAMENTO DE MATEMÁTICAS": "Matemáticas"
    }
    
    for colegio_completo, info in PROGRAMAS_RUM.items():
        usuario = mapeo_usuarios.get(colegio_completo, colegio_completo)
        
        # NUEVO: Manejo especial para Artes y Ciencias
        if colegio_completo == "COLEGIO DE ARTES Y CIENCIAS":
            for division, departamentos in info['divisiones'].items():
                for dept_nombre, dept_info in departamentos.items():
                    # Usuario = División + Departamento
                    usuario_dept = f"{division} - {dept_nombre}"
                    
                    for nivel, programas in dept_info['niveles'].items():
                        for programa in programas:
                            credenciales[f"{usuario_dept}|{programa}"] = {
                                'usuario': usuario_dept,
                                'contraseña': programa,
                                'colegio_completo': colegio_completo,
                                'division': division,
                                'departamento': dept_nombre,
                                'nivel': nivel,
                                'programa': programa
                            }
        else:
            # Manejo normal para otros colegios
            for nivel, programas in info['niveles'].items():
                for programa in programas:
                    credenciales[f"{usuario}|{programa}"] = {
                        'usuario': usuario,
                        'contraseña': programa,
                        'colegio_completo': colegio_completo,
                        'nivel': nivel,
                        'programa': programa
                    }
    
    return credenciales

def verificar_credenciales(usuario, contraseña):
    """Verifica las credenciales y retorna la información del programa"""
    credenciales = generar_credenciales()
    clave = f"{usuario}|{contraseña}"
    
    if clave in credenciales:
        return credenciales[clave]
    return None

def mostrar_login():
    """Interfaz de inicio de sesión"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 3rem;">🔐 Acceso al Sistema</h1>
        <p style="color: white; margin: 1rem 0 0 0; font-size: 1.3rem;">Sistema de Generación de Horarios RUM</p>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1rem;">Ingrese sus credenciales para acceder</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centrar el formulario de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Credenciales de Acceso")
        
        # Información de ayuda ACTUALIZADA
        with st.expander("ℹ️ ¿Cómo obtener mis credenciales?", expanded=False):
            st.markdown("""
            **Usuario:** Nombre de su colegio/departamento
            - Administración de Empresas
            - **Artes - [Departamento]** (ej: Artes - Humanidades)
            - **Ciencias - [Departamento]** (ej: Ciencias - Biología)
            - Ciencias Agrícolas
            - Ingeniería
            - Matemáticas
            
            **Contraseña:** Nombre exacto de su programa académico
            
            **Ejemplos:**
            - Usuario: `Artes - Humanidades`, Contraseña: `Literatura Comparada`
            - Usuario: `Ciencias - Biología`, Contraseña: `Biología`
            - Usuario: `Administración de Empresas`, Contraseña: `Contabilidad`
            """)
        
        # Formulario de login
        usuario = st.text_input("👤 Usuario (Colegio/Departamento)", placeholder="Ej: Artes - Humanidades", key="login_usuario")
        contraseña = st.text_input("🔑 Contraseña (Programa)", type="password", placeholder="Ej: Literatura Comparada", key="login_password")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Iniciar Sesión", type="primary", use_container_width=True, key="btn_login"):
                if usuario and contraseña:
                    info_usuario = verificar_credenciales(usuario, contraseña)
                    if info_usuario:
                        # Guardar información de sesión
                        st.session_state.usuario_autenticado = True
                        st.session_state.info_usuario = info_usuario
                        st.session_state.programa_seleccionado = info_usuario['programa']
                        st.session_state.colegio_seleccionado = info_usuario['colegio_completo']
                        st.session_state.nivel_seleccionado = info_usuario['nivel']
                        
                        # NUEVO: Guardar información de división y departamento para Artes y Ciencias
                        if 'division' in info_usuario:
                            st.session_state.division_seleccionada = info_usuario['division']
                            st.session_state.departamento_seleccionado = info_usuario['departamento']
                        
                        st.success("✅ Acceso autorizado. Redirigiendo...")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas. Verifique su usuario y contraseña.")
                else:
                    st.warning("⚠️ Por favor complete todos los campos.")
        
        # Mostrar programas disponibles para referencia ACTUALIZADO
        with st.expander("📚 Ver todos los programas disponibles"):
            credenciales = generar_credenciales()
            programas_por_colegio = {}
            
            for info in credenciales.values():
                if 'division' in info:
                    # Para Artes y Ciencias
                    clave_colegio = f"{info['division']} - {info['departamento']}"
                else:
                    # Para otros colegios
                    clave_colegio = info['usuario']
                
                if clave_colegio not in programas_por_colegio:
                    programas_por_colegio[clave_colegio] = []
                if info['programa'] not in programas_por_colegio[clave_colegio]:
                    programas_por_colegio[clave_colegio].append(info['programa'])
            
            for colegio, programas in sorted(programas_por_colegio.items()):
                if "Artes -" in colegio or "Ciencias -" in colegio:
                    emoji = "🎨" if "Artes -" in colegio else "🔬"
                else:
                    emoji = "🏛️"
                st.markdown(f"**{emoji} {colegio}**")
                for programa in sorted(programas):
                    st.markdown(f"  • {programa}")
                st.markdown("---")
        
        st.markdown("</div>", unsafe_allow_html=True)

def mostrar_header_usuario():
    """Muestra la información del usuario autenticado en el header"""
    if st.session_state.get('usuario_autenticado') and st.session_state.get('info_usuario'):
        info = st.session_state.info_usuario
        
        # NUEVO: Header mejorado para Artes y Ciencias
        if 'division' in info:
            titulo_programa = f"🎓 {info['programa']}"
            subtitulo = f"🏛️ {info['division']} - {info['departamento']} • 📚 {info['nivel']}"
            usuario_display = f"{info['division']} - {info['departamento']}"
        else:
            titulo_programa = f"🎓 {info['programa']}"
            subtitulo = f"🏛️ {info['usuario']} • 📚 {info['nivel']}"
            usuario_display = info['usuario']
        
        # Header con información del usuario
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: white; margin: 0;">{titulo_programa}</h2>
                    <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0;">{subtitulo}</p>
                </div>
                <div style="text-align: right;">
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Usuario: {usuario_display}</p>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Sesión activa ✅</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de cerrar sesión en sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Sesión Actual")
        st.sidebar.info(f"**Usuario:** {usuario_display}")
        st.sidebar.info(f"**Programa:** {info['programa']}")
        
        if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True, key="btn_logout"):
            # Limpiar session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ========================================================
# LISTA FIJA DE SALONES ACTUALIZADA
# ========================================================
AE_SALONES_FIJOS = [
    "AE 102", "AE 103", "AE 104", "AE 105", "AE 106", "AE 203C",
    "AE 236", "AE 302", "AE 303", "AE 304", "AE 305", "AE 306",
    "AE 338", "AE 340", "AE 341", "AE 402", "AE 403", "AE 404",
]

MATEMATICAS_SALONES_FIJOS = [
    "M 102", "M 104", "M 105", "M 110", "M 112", "M 203", "M 205", "M 210", 
    "M 213", "M 214", "M 215", "M 220", "M 222", "M 236", "M 238", "M 302", 
    "M 303", "M 304", "M 305", "M 306", "M 311", "M 315", "M 316", "M 317", 
    "M 338", "M 340", "M 341", "M 402", "M 403", "M 404"
]

# NUEVO: Salones compartidos para Artes y Ciencias
ARTES_CIENCIAS_SALONES_COMPARTIDOS = [
    "AC 101", "AC 102", "AC 103", "AC 104", "AC 105", "AC 106", "AC 107", "AC 108",
    "AC 201", "AC 202", "AC 203", "AC 204", "AC 205", "AC 206", "AC 207", "AC 208",
    "AC 301", "AC 302", "AC 303", "AC 304", "AC 305", "AC 306", "AC 307", "AC 308",
    "AC 401", "AC 402", "AC 403", "AC 404", "AC 405", "AC 406", "AC 407", "AC 408",
    "LAB 101", "LAB 102", "LAB 103", "LAB 104", "LAB 105", "LAB 106", "LAB 107", "LAB 108"
]

# ========================================================
# SISTEMA DE RESERVAS DE SALONES MEJORADO
# ========================================================

class SistemaReservasSalones:
    def __init__(self, archivo_reservas="reservas_salones_compartidos.json"):
        self.archivo_reservas = archivo_reservas
        self.reservas = self.cargar_reservas()
    
    def cargar_reservas(self):
        """Carga las reservas existentes desde el archivo JSON"""
        if os.path.exists(self.archivo_reservas):
            try:
                with open(self.archivo_reservas, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error al cargar reservas: {e}")
                return {}
        return {}
    
    def guardar_reservas(self):
        """Guarda las reservas en el archivo JSON"""
        try:
            with open(self.archivo_reservas, 'w', encoding='utf-8') as f:
                json.dump(self.reservas, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error al guardar reservas: {e}")
            return False
    
    def a_minutos(self, hhmm):
        """Convierte hora HH:MM a minutos desde medianoche"""
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def verificar_disponibilidad(self, salon, dia, hora_inicio, hora_fin, departamento_solicitante):
        """Verifica si un salón está disponible en un horario específico"""
        for reserva_key, reserva_info in self.reservas.items():
            if reserva_info.get('salon') == salon and reserva_info.get('dia') == dia:
                res_inicio = reserva_info['hora_inicio']
                res_fin = reserva_info['hora_fin']
                
                inicio_min = self.a_minutos(hora_inicio)
                fin_min = self.a_minutos(hora_fin)
                res_inicio_min = self.a_minutos(res_inicio)
                res_fin_min = self.a_minutos(res_fin)
                
                if not (fin_min <= res_inicio_min or inicio_min >= res_fin_min):
                    departamento_reserva = reserva_info.get('departamento', '')
                    return False, departamento_reserva
        
        return True, None
    
    def reservar_salon(self, salon, dia, hora_inicio, hora_fin, departamento, programa, curso, profesor):
        """Reserva un salón para un departamento específico"""
        clave_reserva = f"{salon}_{dia}_{hora_inicio}_{hora_fin}_{departamento}"
        
        self.reservas[clave_reserva] = {
            'salon': salon,
            'dia': dia,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'departamento': departamento,
            'programa': programa,
            'curso': curso,
            'profesor': profesor,
            'fecha_reserva': datetime.now().isoformat()
        }
        
        return self.guardar_reservas()
    
    def liberar_reservas_departamento(self, departamento):
        """Libera todas las reservas de un departamento específico"""
        claves_a_eliminar = []
        for clave, reserva in self.reservas.items():
            if reserva.get('departamento') == departamento:
                claves_a_eliminar.append(clave)
        
        for clave in claves_a_eliminar:
            del self.reservas[clave]
        
        return self.guardar_reservas()
    
    def obtener_reservas_departamento(self, departamento):
        """Obtiene todas las reservas de un departamento específico"""
        reservas_departamento = {}
        for clave, reserva in self.reservas.items():
            if reserva.get('departamento') == departamento:
                reservas_departamento[clave] = reserva
        return reservas_departamento
    
    def obtener_salones_disponibles(self, dia, hora_inicio, hora_fin, departamento, lista_salones):
        """Obtiene lista de salones disponibles para un horario específico"""
        salones_disponibles = []
        for salon in lista_salones:
            disponible, _ = self.verificar_disponibilidad(salon, dia, hora_inicio, hora_fin, departamento)
            if disponible:
                salones_disponibles.append(salon)
        return salones_disponibles
    
    def obtener_estadisticas_uso(self):
        """Obtiene estadísticas de uso de salones"""
        stats = {
            'total_reservas': len(self.reservas),
            'departamentos_activos': len(set(r.get('departamento', '') for r in self.reservas.values())),
            'salones_en_uso': len(set(r.get('salon', '') for r in self.reservas.values())),
            'reservas_por_departamento': {},
            'reservas_por_salon': {}
        }
        
        for reserva in self.reservas.values():
            departamento = reserva.get('departamento', 'Sin departamento')
            salon = reserva.get('salon', 'Sin salón')
            
            stats['reservas_por_departamento'][departamento] = stats['reservas_por_departamento'].get(departamento, 0) + 1
            stats['reservas_por_salon'][salon] = stats['reservas_por_salon'].get(salon, 0) + 1
        
        return stats

# ========================================================
# CONFIGURACIÓN RUM ACTUALIZADA CON ARTES Y CIENCIAS
# ========================================================

PROGRAMAS_RUM = {
    "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
        "color": "#FF6B6B",
        "salones_compartidos": len(AE_SALONES_FIJOS),
        "prefijo_salon": "AE",
        "sistema_reservas": True,
        "generacion_unificada": True,
        "horarios_exactos": True,
        "niveles": {
            "Bachilleratos en Administración de Empresas": [
                "Contabilidad", "Finanzas", "Gerencia de Recursos Humanos",
                "Mercadeo", "Gerencia de Operaciones", "Sistemas Computadorizados de Información",
                "Administración de Oficinas"
            ],
            "Maestrías en Administración de Empresas": [
                "Administración de Empresas (Programa General)", "Finanzas",
                "Gerencia Industrial", "Recursos Humanos"
            ]
        }
    },
    "DEPARTAMENTO DE MATEMÁTICAS": {
        "color": "#9B59B6",
        "salones_compartidos": len(MATEMATICAS_SALONES_FIJOS),
        "prefijo_salon": "M",
        "sistema_reservas": True,
        "generacion_unificada": True,
        "horarios_exactos": True,
        "niveles": {
            "Bachilleratos en Matemáticas": [
                "Matemáticas Aplicadas", "Matemáticas Puras", "Matemática Estadística",
                "Educación Matemática", "Ciencias de la Computación"
            ],
            "Maestrías en Matemáticas": [
                "Matemáticas Aplicadas", "Matemáticas Puras", "Matemática Estadística",
                "Computación Científica"
            ]
        }
    },
    # NUEVO: Estructura completa de Artes y Ciencias
    "COLEGIO DE ARTES Y CIENCIAS": {
        "color": "#4ECDC4",
        "salones_compartidos": len(ARTES_CIENCIAS_SALONES_COMPARTIDOS),
        "prefijo_salon": "AC",
        "sistema_reservas": True,  # ACTIVADO para manejo de salones compartidos
        "generacion_unificada": False,
        "horarios_exactos": False,
        "divisiones": {
            "Artes": {
                "Humanidades": {
                    "color": "#E74C3C",
                    "niveles": {
                        "Bachilleratos en Artes": [
                            "Literatura Comparada", "Lengua y Literatura Francesa", 
                            "Filosofía", "Artes Plásticas", "Teoría del Arte"
                        ],
                        "Maestrías en Artes": [
                            "Estudios Culturales y Humanísticos"
                        ]
                    }
                },
                "Economía": {
                    "color": "#F39C12",
                    "niveles": {
                        "Bachilleratos en Artes": ["Economía"]
                    }
                },
                "Inglés": {
                    "color": "#27AE60",
                    "niveles": {
                        "Bachilleratos en Artes": ["Inglés"],
                        "Maestrías en Artes": ["Educación en Inglés", "Literaturas en Inglés"]
                    }
                },
                "Sociales": {
                    "color": "#8E44AD",
                    "niveles": {
                        "Bachilleratos en Artes": [
                            "Historia", "Ciencias Políticas", "Ciencias Sociales", "Sociología"
                        ]
                    }
                },
                "Estudios Hispánicos": {
                    "color": "#E67E22",
                    "niveles": {
                        "Bachilleratos en Artes": ["Estudios Hispánicos"],
                        "Maestrías en Artes": ["Estudios Hispánicos"]
                    }
                },
                "Educación Física": {
                    "color": "#16A085",
                    "niveles": {
                        "Bachilleratos en Artes": [
                            "Educación Física – Pedagogía en Educación Física",
                            "Educación Física – Entrenamiento Deportivo"
                        ],
                        "Maestrías en Artes": ["Kinesiología"]
                    }
                },
                "Psicología": {
                    "color": "#9B59B6",
                    "niveles": {
                        "Bachilleratos en Artes": ["Psicología"],
                        "Maestrías en Ciencias": ["Psicología Escolar"],
                        "Doctorados en Filosofía": ["Psicología Escolar"]
                    }
                }
            },
            "Ciencias": {
                "Biología": {
                    "color": "#27AE60",
                    "niveles": {
                        "Bachilleratos en Ciencias": [
                            "Biología", "Microbiología Industrial", "Pre-Médica", "Biotecnología Industrial"
                        ],
                        "Maestrías en Ciencias": ["Biología"]
                    }
                },
                "Química": {
                    "color": "#E74C3C",
                    "niveles": {
                        "Bachilleratos en Ciencias": ["Química"],
                        "Maestrías en Ciencias": ["Química"],
                        "Doctorados en Filosofía": ["Química Aplicada"]
                    }
                },
                "Geología": {
                    "color": "#8E44AD",
                    "niveles": {
                        "Bachilleratos en Ciencias": ["Geología"],
                        "Maestrías en Ciencias": ["Geología"]
                    }
                },
                "Matemática": {
                    "color": "#3498DB",
                    "niveles": {
                        "Bachilleratos en Ciencias": [
                            "Matemáticas – Matemática Pura", "Matemáticas – Ciencias de la Computación", 
                            "Educación Matemática"
                        ],
                        "Maestrías en Ciencias": [
                            "Matemáticas Aplicadas", "Matemática Estadística", "Matemática Pura",
                            "Enseñanza de las Matemáticas a nivel preuniversitario", "Computación Científica"
                        ]
                    }
                },
                "Enfermería": {
                    "color": "#E91E63",
                    "niveles": {
                        "Bachilleratos en Ciencias": ["Enfermería"]
                    }
                },
                "Física": {
                    "color": "#FF5722",
                    "niveles": {
                        "Bachilleratos en Ciencias": ["Física", "Ciencias Físicas"],
                        "Maestrías en Ciencias": ["Física"]
                    }
                },
                "Ciencias Marinas": {
                    "color": "#00BCD4",
                    "niveles": {
                        "Maestrías en Ciencias": ["Ciencias Marinas"],
                        "Doctorados en Filosofía": ["Ciencias Marinas"]
                    }
                }
            }
        }
    },
    "COLEGIO DE CIENCIAS AGRÍCOLAS": {
        "color": "#96CEB4",
        "salones_compartidos": 15,
        "prefijo_salon": "CA",
        "sistema_reservas": False,
        "generacion_unificada": False,
        "horarios_exactos": False,
        "niveles": {
            "Bachilleratos en Ciencias Agrícolas": [
                "Ciencias Agrícolas", "Agronomía", "Economía Agrícola", "Horticultura",
                "Ciencia Animal", "Protección de Cultivos", "Agronegocios",
                "Educación Agrícola", "Extensión Agrícola", "Suelos",
                "Sistemas Agrícolas y Ambientales", "Pre-Veterinaria (No conducente a grado)"
            ],
            "Maestrías en Ciencias": [
                "Agronomía", "Ciencias y Tecnología de Alimentos", "Economía Agrícola",
                "Educación Agrícola", "Extensión Agrícola", "Horticultura",
                "Ciencia Animal", "Protección de Cultivos", "Suelos"
            ]
        }
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#FFEAA7",
        "salones_compartidos": 20,
        "prefijo_salon": "ING",
        "sistema_reservas": False,
        "generacion_unificada": False,
        "horarios_exactos": False,
        "niveles": {
            "Bachilleratos en Ingeniería": [
                "Ingeniería Química", "Ingeniería Civil", "Ingeniería de Computadoras",
                "Ciencias e Ingeniería de la Computación", "Ingeniería Eléctrica",
                "Ingeniería Industrial", "Ingeniería Mecánica", "Ingeniería de Software",
                "Agrimensura y Topografía"
            ],
            "Maestrías en Ciencias": [
                "Bioingeniería", "Ingeniería Química", "Ingeniería Civil",
                "Ingeniería de Computadoras", "Ingeniería Eléctrica", "Ingeniería Industrial",
                "Ciencia e Ingeniería de Materiales", "Ingeniería Mecánica"
            ],
            "Maestrías en Ingeniería": [
                "Bioingeniería", "Ingeniería Química", "Ingeniería Civil",
                "Ingeniería de Computadoras", "Ingeniería Eléctrica", "Ingeniería Industrial",
                "Ciencia e Ingeniería de Materiales", "Ingeniería Mecánica"
            ],
            "Doctorados en Filosofía": [
                "Bioingeniería", "Ingeniería Química", "Ingeniería Civil",
                "Ingeniería Eléctrica", "Ingeniería Mecánica",
                "Ciencias e Ingeniería de la Información y la Computación"
            ]
        }
    }
}

# ========================================================
# CONFIGURACIÓN DEL SISTEMA ACTUALIZADA
# ========================================================

class ConfiguracionSistema:
    def __init__(self, archivo_excel=None, programa_actual=None, colegio_actual=None, departamento_actual=None):
        self.archivo_excel = archivo_excel
        self.programa_actual = programa_actual
        self.colegio_actual = colegio_actual
        self.departamento_actual = departamento_actual  # NUEVO
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None
        self.es_generacion_unificada = False
        self.usa_horarios_exactos = False
        
        # Sistema de reservas si el colegio lo requiere
        self.usa_reservas = False
        if colegio_actual and colegio_actual in PROGRAMAS_RUM:
            colegio_info = PROGRAMAS_RUM[colegio_actual]
            self.usa_reservas = colegio_info.get('sistema_reservas', False)
            self.es_generacion_unificada = colegio_info.get('generacion_unificada', False)
            self.usa_horarios_exactos = colegio_info.get('horarios_exactos', False)
            self.sistema_reservas = SistemaReservasSalones() if self.usa_reservas else None
        
        # Restricciones globales por defecto
        self.restricciones_globales = {
            "horarios_prohibidos": self._obtener_horarios_prohibidos(),
            "hora_inicio_min": "07:00" if self.usa_horarios_exactos else "07:30",
            "hora_fin_max": "18:00" if self.usa_horarios_exactos else "19:30",
            "creditos_max_profesor": 15,
            "creditos_min_profesor": 8,
            "estudiantes_max_salon": 50,
            "horas_max_dia": 8,
            "dias_max_profesor": 5
        }
        
        # Pesos para restricciones suaves
        self.pesos_restricciones = {
            "horario_preferido": 30,
            "compactacion_horario": 20,
            "equilibrio_creditos": 25,
            "utilizacion_salones": 15,
            "estudiantes_por_salon": 10,
            "horas_consecutivas": 18,
            "distribucion_semanal": 12,
            "evitar_horas_pico": 8
        }
        
        if archivo_excel:
            self.cargar_desde_excel()
    
    def _obtener_horarios_prohibidos(self):
        """Obtiene horarios prohibidos según el colegio"""
        if self.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
            return {
                "Ma": [("10:00", "12:00")],
                "Ju": [("10:00", "12:00")]
            }
        elif self.colegio_actual == "DEPARTAMENTO DE MATEMÁTICAS":
            return {}
        elif self.colegio_actual == "COLEGIO DE ARTES Y CIENCIAS":
            # NUEVO: Horarios prohibidos para Artes y Ciencias
            return {
                "Ma": [("11:00", "12:30")],  # Hora de facultad
                "Ju": [("11:00", "12:30")]   # Hora de facultad
            }
        else:
            return {
                "Ma": [("10:30", "12:30")],
                "Ju": [("10:30", "12:30")]
            }
    
    def cargar_desde_excel(self):
        """Carga la configuración desde el archivo Excel"""
        try:
            excel_data = pd.read_excel(self.archivo_excel, sheet_name=None)
            
            st.write(f"📊 Hojas disponibles en el Excel: {list(excel_data.keys())}")
            
            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
                st.write(f"\n🔍 Analizando hoja '{nombre_hoja}':")
                st.write(f"Columnas: {list(df.columns)}")
                
                columnas_df = [col.lower().strip() for col in df.columns]
                
                if any('profesor' in col or 'docente' in col for col in columnas_df) and \
                   any('curso' in col or 'materia' in col or 'asignatura' in col for col in columnas_df):
                    hoja_cursos = df
                    st.success(f"✅ Hoja '{nombre_hoja}' seleccionada como fuente de datos")
                    break
            
            if hoja_cursos is None:
                st.error("❌ No se encontró una hoja con datos de cursos válidos")
                return
            
            self.cursos_df = hoja_cursos
            self.procesar_datos_excel()
            
        except Exception as e:
            st.error(f"❌ Error al cargar el archivo Excel: {e}")
            st.info("ℹ️ Usando configuración por defecto")
    
    def procesar_datos_excel(self):
        """Procesa los datos del Excel y crea la configuración de profesores"""
        if self.cursos_df is None:
            return
        
        df = self.cursos_df.copy()
        
        # Normalizar nombres de columnas
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        
        # Mapear columnas comunes
        mapeo_columnas = {
            'profesor': ['profesor', 'docente', 'teacher', 'instructor'],
            'curso': ['curso', 'materia', 'asignatura', 'subject', 'course'],
            'creditos': ['creditos', 'créditos', 'credits', 'horas'],
            'estudiantes': ['estudiantes', 'alumnos', 'students', 'enrollment', 'seccion'],
            'programa': ['programa', 'program', 'carrera', 'major'],
            'seccion': ['seccion', 'section', 'sec', 'grupo']
        }
        
        columnas_finales = {}
        for campo, posibles in mapeo_columnas.items():
            for col in df.columns:
                if any(pos in col for pos in posibles):
                    columnas_finales[campo] = col
                    break
        
        st.write(f"🔗 Mapeo de columnas: {columnas_finales}")
        
        if 'profesor' not in columnas_finales or 'curso' not in columnas_finales:
            st.error("❌ Error: No se encontraron las columnas básicas (profesor, curso)")
            return
        
        # Valores por defecto para columnas faltantes
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
            st.warning("⚠️ No se encontró columna de créditos, usando 3 por defecto")
        
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
            st.warning("⚠️ No se encontró columna de estudiantes, usando 30 por defecto")
        
        if 'programa' not in columnas_finales:
            df['programa_default'] = self.programa_actual or 'Programa General'
            columnas_finales['programa'] = 'programa_default'
        
        if 'seccion' not in columnas_finales:
            df['seccion_default'] = '001'
            columnas_finales['seccion'] = 'seccion_default'
        
        df = df.dropna(subset=[columnas_finales['profesor'], columnas_finales['curso']])
        
        profesores_unicos = df[columnas_finales['profesor']].unique()
        st.info(f"👨‍🏫 Profesores encontrados: {len(profesores_unicos)}")
        
        for profesor in profesores_unicos:
            if pd.isna(profesor) or str(profesor).strip() == '':
                continue
                
            profesor = str(profesor).strip()
            cursos_profesor = df[df[columnas_finales['profesor']] == profesor]
            
            cursos_lista = []
            creditos_totales = 0
            
            for _, fila in cursos_profesor.iterrows():
                curso_nombre = str(fila[columnas_finales['curso']]).strip()
                
                try:
                    creditos = int(float(fila[columnas_finales['creditos']]))
                except (ValueError, TypeError):
                    creditos = 3
                
                try:
                    estudiantes = int(float(fila[columnas_finales['estudiantes']]))
                except (ValueError, TypeError):
                    estudiantes = 30
                
                programa = str(fila[columnas_finales['programa']]).strip() if 'programa' in columnas_finales else self.programa_actual
                seccion = str(fila[columnas_finales['seccion']]).strip() if 'seccion' in columnas_finales else '001'
                
                if curso_nombre and curso_nombre != 'nan':
                    cursos_lista.append({
                        "nombre": curso_nombre,
                        "creditos": creditos,
                        "estudiantes": estudiantes,
                        "programa": programa,
                        "seccion": seccion
                    })
                    creditos_totales += creditos
            
            if cursos_lista:
                self.profesores_config[profesor] = {
                    "cursos": cursos_lista,
                    "creditos_totales": creditos_totales,
                    "horario_preferido": {},
                    "horario_no_disponible": {}
                }
                
                st.write(f"📚 {profesor}: {len(cursos_lista)} cursos, {creditos_totales} créditos totales")
        
        # Configurar salones según el colegio
        if self.colegio_actual and self.colegio_actual in PROGRAMAS_RUM:
            colegio_info = PROGRAMAS_RUM[self.colegio_actual]
            if self.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
                self.salones = AE_SALONES_FIJOS.copy()
            elif self.colegio_actual == "DEPARTAMENTO DE MATEMÁTICAS":
                self.salones = MATEMATICAS_SALONES_FIJOS.copy()
            elif self.colegio_actual == "COLEGIO DE ARTES Y CIENCIAS":
                # NUEVO: Salones compartidos para Artes y Ciencias
                self.salones = ARTES_CIENCIAS_SALONES_COMPARTIDOS.copy()
            else:
                num_salones = colegio_info.get('salones_compartidos', 15)
                prefijo = colegio_info.get('prefijo_salon', 'SALON')
                self.salones = [f"{prefijo}-{i+1:02d}" for i in range(num_salones)]
        else:
            num_salones = 15
            self.salones = [f"Salon {i+1}" for i in range(num_salones)]
        
        st.success(f"✅ Configuración completada: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

# ========================================================
# RESTO DEL CÓDIGO (GENERACIÓN DE BLOQUES, UTILS, ETC.)
# ========================================================
def generar_bloques():
    bloques = []
    id_counter = 1

    # Bloques de 4 créditos (4 días, 1 hora cada día)
    combinaciones_4dias = [
        ["Lu","Ma","Mi","Ju"],
        ["Lu","Ma","Mi","Vi"],
        ["Lu","Ma","Ju","Vi"],
        ["Lu","Mi","Ju","Vi"],
        ["Ma","Mi","Ju","Vi"],
    ]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4})
        id_counter += 1

    # Bloques de 4 créditos (2 días, 2 horas cada día)
    combinaciones_2dias = [
        ["Lu","Mi"],
        ["Lu","Vi"],
        ["Ma","Ju"],
        ["Mi","Vi"],
    ]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2,2], "creditos": 4})
        id_counter += 1

    # Bloques de 3 créditos
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3})
    id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3})
    id_counter += 1

    # Bloques de 5 créditos
    combinaciones_5creditos = [
        (["Lu","Mi","Vi"], [2,2,1]),
        (["Lu","Ma","Mi","Vi"], [1,1,1,2]),
        (["Lu","Ma","Ju","Vi"], [1,1,1,2]),
        (["Lu","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Ju","Vi"], [1.5,1.5,2]),
        (["Lu","Ma","Mi","Ju","Vi"], [1,1,1,1,1]),
        (["Lu","Ma","Mi"], [2,1,2]),
    ]
    for dias, horas in combinaciones_5creditos:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5})
        id_counter += 1

    # Bloques de 3 créditos (un solo día con 3 horas)
    for dia in ["Lu","Ma","Mi","Ju","Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3})
        id_counter += 1

    return bloques

# Tabla de créditos adicionales por tamaño de sección
tabla_creditos = {
    1: [(1,44,0),(45,74,0.5),(75,104,1),(105,134,1.5),(135,164,2),(165,194,2.5),
        (195,224,3),(225,254,3.5),(255,284,4),(285,314,4.5),(315,344,5),(345,374,5.5),
        (375,404,6),(405,434,6.5),(435,464,7),(465,494,7.5),(495,524,8)],
    2: [(1,37,0),(38,52,0.5),(53,67,1),(68,82,1.5),(83,97,2),(98,112,2.5),
        (113,127,3),(128,142,3.5),(143,157,4),(158,172,4.5),(173,187,5),(188,202,5.5),
        (203,217,6),(218,232,6.5),(233,247,7),(248,262,7.5),(263,277,8)],
    3: [(1,34,0),(35,44,0.5),(45,54,1),(55,64,1.5),(65,74,2),(75,84,2.5),
        (85,94,3),(95,104,3.5),(105,114,4),(115,124,4.5),(125,134,5),(135,144,5.5),
        (145,154,6),(155,164,6.5),(165,174,7),(175,184,7.5),(185,194,8)],
    4: [(1,33,0),(34,41,0.5),(42,48,1),(49,56,1.5),(57,63,2),(64,71,2.5),
        (72,78,3),(79,86,3.5),(87,93,4),(94,101,4.5),(102,108,5),(109,116,5.5),
        (117,123,6),(124,131,6.5),(132,138,7),(139,146,7.5),(147,153,8)],
    5: [(1,32,0),(33,38,0.5),(39,44,1),(45,50,1.5),(51,56,2),(57,63,2.5),
        (64,69,3),(70,75,3.5),(76,81,4),(82,88,4.5),(89,93,5),(94,99,5.5),
        (100,104,6),(105,110,6.5),(111,116,7),(117,122,7.5),(123,128,8)],
    6: [(1,32,0),(33,37,0.5),(38,42,1),(43,47,1.5),(48,52,2),(53,57,2.5),
        (58,62,3),(63,67,3.5),(68,72,4),(73,77,4.5),(78,82,5),(83,87,5.5),
        (88,92,6),(93,97,6.5),(98,102,7),(103,107,7.5),(108,112,8)]
}

def calcular_creditos_adicionales(horas_contacto, estudiantes):
    if horas_contacto not in tabla_creditos:
        return 0
    for minimo, maximo, creditos in tabla_creditos[horas_contacto]:
        if minimo <= estudiantes <= maximo:
            return creditos
    return 0

def generar_horas_inicio():
    """Genera las horas de inicio según el tipo de colegio"""
    if config and config.usa_horarios_exactos:
        return [f"{h:02d}:00" for h in range(7, 19)]
    else:
        horas_inicio = []
        for h in range(7, 20):
            for m in [0, 30]:
                if h == 19 and m > 20:
                    break
                horas_inicio.append(f"{h:02d}:{m:02d}")
        return horas_inicio

def a_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
    """Restricción: Las clases de 3 créditos con 3 horas consecutivas 
    SOLO pueden programarse después de las 15:30 (3:30 PM) de lunes a viernes."""
    if creditos == 3 and duracion == 3:
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi"]
        if dia in dias_semana:
            inicio_minutos = a_minutos(hora_inicio)
            limite = "15:00" if (config and config.usa_horarios_exactos) else "15:30"
            restriccion_minutos = a_minutos(limite)
            if inicio_minutos < restriccion_minutos:
                return False
    return True

def horario_valido(dia, hora_inicio, duracion, profesor=None, creditos=None):
    """Verifica si un horario es válido según las restricciones fuertes"""
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    if fin_min > a_minutos(config.restricciones_globales["hora_fin_max"]):
        return False
    
    if ini_min < a_minutos(config.restricciones_globales["hora_inicio_min"]):
        return False
    
    if creditos and not es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
        return False
    
    restricciones_horario = config.restricciones_globales["horarios_prohibidos"]
    if dia in restricciones_horario:
        for r_ini, r_fin in restricciones_horario[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False
    
    if profesor and profesor in config.profesores_config:
        prof_config = config.profesores_config[profesor]
        if dia in prof_config["horario_no_disponible"]:
            for r_ini, r_fin in prof_config["horario_no_disponible"][dia]:
                r_ini_min = a_minutos(r_ini)
                r_fin_min = a_minutos(r_fin)
                if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                    return False
    
    return True

def cumple_horario_preferido(dia, hora_inicio, duracion, profesor):
    """Verifica si un horario cumple las preferencias del profesor"""
    if profesor not in config.profesores_config:
        return False
    
    prof_config = config.profesores_config[profesor]
    if dia not in prof_config["horario_preferido"]:
        return False
    
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    for pref_ini, pref_fin in prof_config["horario_preferido"][dia]:
        pref_ini_min = a_minutos(pref_ini)
        pref_fin_min = a_minutos(pref_fin)
        if ini_min >= pref_ini_min and fin_min <= pref_fin_min:
            return True
    
    return False

# Clase para representar una asignación de clase
class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.programa = curso_info.get("programa", "Programa General")
        self.seccion = curso_info.get("seccion", "001")
        self.horas_contacto = int(sum(bloque["horas"]))
        self.creditos_extra = calcular_creditos_adicionales(self.horas_contacto, self.estudiantes)
        
    def get_horario_detallado(self):
        """Retorna lista de horarios detallados para cada día del bloque"""
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            bloque_prefijo = obtener_prefijo_salon(self.salon)
            
            horarios.append({
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Programa": self.programa,
                "Seccion": self.seccion,
                "Bloque": bloque_prefijo,
                "Dia": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Créditos Extra": self.creditos_extra,
                "Estudiantes": self.estudiantes,
                "Salon": self.salon
            })
        return horarios

def obtener_prefijo_salon(salon_str):
    """Obtiene el prefijo del salón"""
    if not salon_str:
        return "SALON"
    if " " in salon_str:
        return salon_str.split(" ")[0].strip()
    if "-" in salon_str:
        return salon_str.split("-")[0].strip()
    return salon_str.split()[0].strip()

# NUEVO: Generador con sistema de reservas para departamentos
def generar_horario_valido_con_reservas():
    """Genera un horario que cumple todas las restricciones fuertes Y verifica reservas de salones"""
    asignaciones = []
    horas_inicio = generar_horas_inicio()
    
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0
        intentos = 0
        max_intentos = 5000
        
        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            
            curso_info = prof_config["cursos"][cursos_asignados]
            bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            
            if not bloques_compatibles:
                bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            
            bloque = random.choice(bloques_compatibles)
            hora_inicio = random.choice(horas_inicio)
            
            # Verificar salones disponibles considerando reservas
            salones_disponibles = []
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                hora_fin_min = a_minutos(hora_inicio) + int(duracion * 60)
                hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
                
                # ACTUALIZADO: Usar departamento en lugar de programa para reservas
                departamento_key = config.departamento_actual or config.programa_actual
                salones_dia = config.sistema_reservas.obtener_salones_disponibles(
                    dia, hora_inicio, hora_fin, departamento_key, config.salones
                )
                
                if not salones_disponibles:
                    salones_disponibles = salones_dia
                else:
                    salones_disponibles = list(set(salones_disponibles) & set(salones_dia))
            
            if not salones_disponibles:
                continue
            
            salon = random.choice(salones_disponibles)
            
            # Verificar validez del horario
            valido = True
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                if not horario_valido(dia, hora_inicio, duracion, profesor, curso_info["creditos"]):
                    valido = False
                    break
            
            if not valido:
                continue
            
            nueva_asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
            
            if not hay_conflictos(nueva_asignacion, asignaciones):
                asignaciones.append(nueva_asignacion)
                cursos_asignados += 1
        
        if cursos_asignados < len(prof_config["cursos"]):
            return None
    
    return asignaciones

def generar_horario_valido():
    """Genera horario sin considerar reservas"""
    asignaciones = []
    horas_inicio = generar_horas_inicio()
    
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0
        intentos = 0
        max_intentos = 4000

        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            curso_info = prof_config["cursos"][cursos_asignados]
            bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            if not bloques_compatibles:
                bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            bloque = random.choice(bloques_compatibles)
            hora_inicio = random.choice(horas_inicio)
            salon = random.choice(config.salones)

            valido = True
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                if not horario_valido(dia, hora_inicio, duracion, profesor, curso_info["creditos"]):
                    valido = False
                    break
            if not valido:
                continue

            nueva_asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
            if not hay_conflictos(nueva_asignacion, asignaciones):
                asignaciones.append(nueva_asignacion)
                cursos_asignados += 1
        if cursos_asignados < len(prof_config["cursos"]):
            return None
    return asignaciones

def hay_conflictos(nueva_asignacion, asignaciones_existentes):
    """Verifica si hay conflictos de profesor o salón"""
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

def evaluar_horario(asignaciones):
    """Evalúa un horario considerando restricciones fuertes y suaves configurables"""
    if asignaciones is None:
        return -float('inf')
    
    penalizacion = 0
    bonus = 0
    
    # Verificar que cada profesor tenga todos sus cursos asignados
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = sum(1 for asig in asignaciones if asig.profesor == profesor)
        cursos_requeridos = len(prof_config["cursos"])
        if cursos_asignados != cursos_requeridos:
            penalizacion += abs(cursos_asignados - cursos_requeridos) * 2000
    
    # Verificar límite de créditos por profesor
    creditos_por_prof = {}
    for asig in asignaciones:
        creditos_por_prof.setdefault(asig.profesor, 0)
        creditos_por_prof[asig.profesor] += asig.creditos
    
    for profesor, prof_config in config.profesores_config.items():
        creditos_actuales = creditos_por_prof.get(profesor, 0)
        creditos_objetivo = prof_config["creditos_totales"]
        
        if creditos_actuales > config.restricciones_globales["creditos_max_profesor"]:
            penalizacion += (creditos_actuales - config.restricciones_globales["creditos_max_profesor"]) * 1000
        
        if creditos_actuales < config.restricciones_globales["creditos_min_profesor"]:
            penalizacion += (config.restricciones_globales["creditos_min_profesor"] - creditos_actuales) * 1000
        
        if creditos_actuales != creditos_objetivo:
            penalizacion += abs(creditos_actuales - creditos_objetivo) * 200
    
    # Verificar conflictos de horario
    for i, asig1 in enumerate(asignaciones):
        for j, asig2 in enumerate(asignaciones):
            if i >= j:
                continue
            if hay_conflictos(asig1, [asig2]):
                penalizacion += 5000
    
    # Verificar cumplimiento de restricción de 3 horas
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, duracion, asig.creditos):
                penalizacion += 10000
    
    # Restricciones suaves
    pesos = config.pesos_restricciones
    
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if cumple_horario_preferido(dia, asig.hora_inicio, duracion, asig.profesor):
                bonus += pesos["horario_preferido"]
        
        if asig.estudiantes > config.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += pesos["estudiantes_por_salon"] * (asig.estudiantes - config.restricciones_globales["estudiantes_max_salon"])
    
    return bonus - penalizacion

def buscar_mejor_horario(intentos=250):
    """Genera varios horarios y retorna el mejor según la evaluación"""
    mejor_asignaciones = None
    mejor_score = -float('inf')
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(intentos):
        progress_bar.progress((i + 1) / intentos)
        status_text.text(f"🔄 Generando horarios... {i+1}/{intentos}")
        
        try:
            if config.usa_reservas:
                asignaciones = generar_horario_valido_con_reservas()
            else:
                asignaciones = generar_horario_valido()
                
            score = evaluar_horario(asignaciones)
            if score > mejor_score:
                mejor_score = score
                mejor_asignaciones = asignaciones
        except Exception as e:
            st.warning(f"Error en iteración {i+1}: {e}")
            continue
    
    status_text.text(f"✅ Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    """Convierte las asignaciones a un DataFrame para visualización"""
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    df = pd.DataFrame(registros)

    # Limpiar columnas innecesarias
    for col in ["3h Consecutivas", "Restricción 15:30"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    return df

# Guardar y cargar horario generado (persistencia local)
def _nombre_archivo_horario(departamento):
    safe_dept = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in (departamento or "departamento"))
    return f"horario_{safe_dept}.json"

def guardar_horario_json(df_horario, departamento):
    try:
        ruta = _nombre_archivo_horario(departamento)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(df_horario.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error al guardar horario: {e}")
        return False

def cargar_horario_json(departamento):
    ruta = _nombre_archivo_horario(departamento)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            st.warning(f"Error al cargar horario guardado: {e}")
            return None
    return None

# ========================================================
# FUNCIONES DE VISUALIZACIÓN ACTUALIZADAS
# ========================================================

def generar_colores_cursos(df_horario):
    """Genera una paleta de colores única para cada curso"""
    cursos_unicos = df_horario['Curso'].unique()
    
    colores_base = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D5A6BD',
        '#AED6F1', '#A9DFBF', '#F9E79F', '#D7BDE2', '#A3E4D7'
    ]
    
    colores_cursos = {}
    for i, curso in enumerate(cursos_unicos):
        colores_cursos[curso] = colores_base[i % len(colores_base)]
    
    return colores_cursos

def crear_calendario_interactivo(df_horario, filtro_tipo="profesor", filtro_valor=None, chart_key="default"):
    """Crea un calendario visual estilo Google Calendar con Plotly"""
    # Filtros por tipo (profesor, programa, salon, departamento)
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_filtrado = df_horario[df_horario['Profesor'] == filtro_valor]
        titulo_calendario = f"📅 Calendario de {filtro_valor}"
    elif filtro_tipo == "programa" and filtro_valor and filtro_valor != "Todos los programas":
        df_filtrado = df_horario[df_horario['Programa'] == filtro_valor]
        titulo_calendario = f"📅 Calendario del Programa: {filtro_valor}"
    elif filtro_tipo == "salon" and filtro_valor and filtro_valor != "Todos los salones":
        df_filtrado = df_horario[df_horario['Salon'] == filtro_valor]
        titulo_calendario = f"🏫 Horario del Salón: {filtro_valor}"
    else:
        df_filtrado = df_horario
        titulo_calendario = "📅 Calendario Semanal de Clases - Vista Completa"
    
    # Generar colores para cada curso
    colores_cursos = generar_colores_cursos(df_horario)
    
    # Mapeo de días a números para el eje X
    dias_map = {'Lu': 1, 'Ma': 2, 'Mi': 3, 'Ju': 4, 'Vi': 5}
    dias_nombres = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    # Preparar columnas por salón para cada día
    salones_por_dia = {}
    for dia in dias_map.keys():
        salones_unicos = df_filtrado[df_filtrado['Dia'] == dia]['Salon'].unique().tolist()
        salones_por_dia[dia] = sorted(salones_unicos)
    
    # Crear figura
    fig = go.Figure()
    
    # Procesar cada clase para crear los bloques
    for _, fila in df_filtrado.iterrows():
        dia = fila['Dia']
        dia_num = dias_map[dia]
        
        # Columnas por salón
        salones_dia = salones_por_dia.get(dia, [])
        total_cols = max(len(salones_dia), 1)
        salon_idx = salones_dia.index(fila['Salon']) if fila['Salon'] in salones_dia else 0
        
        # Ancho por columna dentro del día
        dia_ancho_total = 0.9
        col_ancho = dia_ancho_total / total_cols
        x_center = (dia_num - 0.45) + (salon_idx + 0.5) * col_ancho
        x0 = x_center - (col_ancho * 0.45)
        x1 = x_center + (col_ancho * 0.45)
        
        # Convertir horas a minutos desde medianoche para el eje Y
        hora_inicio_min = a_minutos(fila['Hora Inicio'])
        hora_fin_min = a_minutos(fila['Hora Fin'])
        
        # Crear el bloque de la clase
        fig.add_shape(
            type="rect",
            x0=x0,
            y0=hora_inicio_min,
            x1=x1,
            y1=hora_fin_min,
            fillcolor=colores_cursos.get(fila['Curso'], "#667eea"),
            opacity=0.85,
            line=dict(color="#222", width=1),
        )
        
        # Texto mejorado con información del departamento
        texto_clase = f"<b>{fila['Curso']}</b><br>"
        texto_clase += f"📝 Sección: {fila.get('Seccion', '001')}<br>"
        texto_clase += f"👨‍🏫 {fila['Profesor']}<br>"
        texto_clase += f"🏫 {fila['Salon']}<br>"
        texto_clase += f"👥 {fila['Estudiantes']} estudiantes<br>"
        texto_clase += f"⏰ {fila['Hora Inicio']} - {fila['Hora Fin']}<br>"
        texto_clase += f"📚 {fila['Créditos']} créditos"
        
        # Mostrar sección en el bloque principal
        texto_bloque = f"<b>{fila['Curso']}</b><br>{fila['Hora Inicio']}-{fila['Hora Fin']}<br>Sec: {fila.get('Seccion', '001')}<br>{fila['Salon']}"
        
        # Añadir anotación centrada en el bloque
        fig.add_annotation(
            x=x_center,
            y=(hora_inicio_min + hora_fin_min) / 2,
            text=texto_bloque,
            showarrow=False,
            font=dict(color="white", size=11, family="Arial Black"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=4,
            hovertext=texto_clase
        )
    
    # Configurar el layout del calendario
    hora_min = 7 * 60 if config and config.usa_horarios_exactos else 7 * 60
    hora_max = 19 * 60 if config and config.usa_horarios_exactos else 20 * 60
    
    fig.update_layout(
        title={
            'text': titulo_calendario,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 26, 'color': '#2C3E50'}
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=dias_nombres[1:],
            range=[0.5, 5.5],
            showgrid=True,
            gridcolor='lightgray',
            title="Días de la Semana",
            title_font=dict(size=16, color='#34495E')
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[i*60 for i in range(7, 20)],
            ticktext=[f"{i:02d}:00" for i in range(7, 20)],
            range=[hora_max, hora_min],
            showgrid=True,
            gridcolor='lightgray',
            title="Hora del Día",
            title_font=dict(size=16, color='#34495E')
        ),
        plot_bgcolor='white',
        paper_bgcolor='#F8F9FA',
        width=1600,
        height=1000,
        showlegend=False,
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # Líneas de cuadrícula más prominentes para las horas
    for hora in range(8, 20):
        fig.add_hline(
            y=hora*60, 
            line_dash="dot", 
            line_color="gray", 
            opacity=0.5
        )
    
    return fig, colores_cursos

def mostrar_leyenda_cursos(colores_cursos, df_horario, filtro_tipo=None, filtro_valor=None):
    """Muestra una leyenda de colores para los cursos (filtrada si es necesario)"""
    if filtro_tipo and filtro_valor and filtro_valor not in ["Todos los profesores", "Todos los programas", "Todos los salones"]:
        if filtro_tipo == "profesor":
            cursos_filtrados = df_horario[df_horario['Profesor'] == filtro_valor]['Curso'].unique()
            titulo = f"🎨 Cursos de {filtro_valor}"
        elif filtro_tipo == "programa":
            cursos_filtrados = df_horario[df_horario['Programa'] == filtro_valor]['Curso'].unique()
            titulo = f"🎨 Cursos del Programa {filtro_valor}"
        elif filtro_tipo == "salon":
            cursos_filtrados = df_horario[df_horario['Salon'] == filtro_valor]['Curso'].unique()
            titulo = f"🎨 Cursos en {filtro_valor}"
        else:
            cursos_filtrados = df_horario['Curso'].unique()
            titulo = "🎨 Leyenda de Colores por Curso"
        
        colores_mostrar = {curso: color for curso, color in colores_cursos.items() if curso in cursos_filtrados}
    else:
        colores_mostrar = colores_cursos
        titulo = "🎨 Leyenda de Colores por Curso"
    
    st.subheader(titulo)
    
    num_cols = 3
    cols = st.columns(num_cols)
    
    for i, (curso, color) in enumerate(colores_mostrar.items()):
        with cols[i % num_cols]:
            st.markdown(
                f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    margin: 5px 0;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: {color}20;
                    border-left: 4px solid {color};
                ">
                    <div style="
                        width: 20px; 
                        height: 20px; 
                        background-color: {color}; 
                        margin-right: 10px;
                        border-radius: 3px;
                    "></div>
                    <span style="font-weight: 500; color: #2C3E50;">{curso}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

# NUEVO: Mostrar estado de reservas para departamentos
def mostrar_estado_reservas():
    """Muestra el estado actual de las reservas de salones"""
    if not config or not config.usa_reservas or not config.sistema_reservas:
        return
    
    st.subheader("🏫 Estado Actual de Reservas de Salones Compartidos")
    
    stats = config.sistema_reservas.obtener_estadisticas_uso()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total Reservas", stats['total_reservas'])
    with col2:
        st.metric("🏛️ Departamentos Activos", stats['departamentos_activos'])
    with col3:
        st.metric("🏫 Salones en Uso", stats['salones_en_uso'])
    with col4:
        disponibles = (len(config.salones) if config.salones else 0) - stats['salones_en_uso']
        st.metric("✅ Salones Disponibles", max(disponibles, 0))
    
    if stats['reservas_por_departamento']:
        st.write("**📊 Reservas por Departamento:**")
        for departamento, cantidad in stats['reservas_por_departamento'].items():
            st.write(f"• {departamento}: {cantidad} reservas")
    
    with st.expander("🔍 Ver todas las reservas activas"):
        if config.sistema_reservas.reservas:
            reservas_df = []
            for clave, reserva in config.sistema_reservas.reservas.items():
                reservas_df.append({
                    'Salón': reserva['salon'],
                    'Día': reserva['dia'],
                    'Hora Inicio': reserva['hora_inicio'],
                    'Hora Fin': reserva['hora_fin'],
                    'Departamento': reserva['departamento'],
                    'Programa': reserva['programa'],
                    'Curso': reserva['curso'],
                    'Profesor': reserva['profesor']
                })
            
            df_reservas = pd.DataFrame(reservas_df)
            st.dataframe(df_reservas, use_container_width=True)
        else:
            st.info("No hay reservas activas")

# ========================================================
# UI PRINCIPAL ACTUALIZADA PARA ARTES Y CIENCIAS
# ========================================================

config = None
bloques = []

def mostrar_generador_horarios_artes_ciencias():
    """Interfaz del generador de horarios específica para Artes y Ciencias"""
    # Mostrar header del usuario autenticado
    mostrar_header_usuario()
    
    # Obtener información del departamento
    info_usuario = st.session_state.info_usuario
    division = info_usuario.get('division', '')
    departamento = info_usuario.get('departamento', '')
    
    # Información del departamento
    st.info(f"🎯 **Generando horarios para**: {division} - {departamento}")
    st.info("🏫 **Salones Compartidos**: Los salones son compartidos entre todos los departamentos de Artes y Ciencias. El sistema evitará conflictos automáticamente.")
    
    st.markdown("## 📁 Cargar Datos para Generación de Horarios")

    # Sidebar de configuración
    st.sidebar.header("⚙️ Configuración del Sistema")
    
    # Upload del archivo Excel en sidebar
    uploaded_file = st.sidebar.file_uploader(
        "📁 Cargar archivo Excel con datos de profesores y cursos",
        type=['xlsx', 'xls'],
        help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes, Programa, Sección",
        key="file_uploader_artes_ciencias"
    )

    # Inicializar configuración al cargar archivo
    if uploaded_file is not None:
        with open("temp_excel.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        global config, bloques
        departamento_key = f"{division} - {departamento}"
        config = ConfiguracionSistema(
            "temp_excel.xlsx", 
            st.session_state.programa_seleccionado,
            st.session_state.colegio_seleccionado,
            departamento_key
        )
        bloques = generar_bloques()

        # Mostrar estado de reservas
        mostrar_estado_reservas()
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Liberar Reservas del Departamento", type="secondary", key="btn_liberar_reservas_dept"):
                if config.sistema_reservas.liberar_reservas_departamento(departamento_key):
                    st.success("✅ Reservas del departamento liberadas correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error al liberar reservas")
        with col2:
            st.info("💡 Libera las reservas si necesitas regenerar el horario del departamento")

        # Infraestructura
        st.sidebar.subheader("🏫 Infraestructura")
        st.sidebar.info("Salones compartidos (AC y LAB):")
        st.sidebar.write(", ".join(ARTES_CIENCIAS_SALONES_COMPARTIDOS[:10]) + "...")
        config.salones = ARTES_CIENCIAS_SALONES_COMPARTIDOS.copy()
        
        if config.profesores_config:
            st.success("✅ Archivo cargado correctamente")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👨‍🏫 Profesores", len(config.profesores_config))
            with col2:
                total_cursos = sum(len(prof['cursos']) for prof in config.profesores_config.values())
                st.metric("📚 Cursos", total_cursos)
            with col3:
                st.metric("🏫 Salones Totales", len(config.salones))
            
            with st.expander("📋 Ver datos cargados"):
                for profesor, data in config.profesores_config.items():
                    st.write(f"**{profesor}** ({data['creditos_totales']} créditos)")
                    for curso in data['cursos']:
                        programa_info = f" - {curso.get('programa', 'N/A')}"
                        seccion_info = f" (Sec: {curso.get('seccion', '001')})"
                        st.write(f"  - {curso['nombre']}{seccion_info}{programa_info} ({curso['creditos']} créditos, {curso['estudiantes']} estudiantes)")
            
            # Parámetros de Optimización
            st.sidebar.subheader("🎯 Parámetros de Optimización")
            intentos = st.sidebar.slider("Número de iteraciones", 50, 500, 250, 50, key="intentos_slider_ac")

            # Restricciones específicas para Artes y Ciencias
            with st.sidebar.expander("🔒 Restricciones Globales"):
                config.restricciones_globales["hora_inicio_min"] = st.time_input(
                    "Hora inicio mínima", 
                    datetime.strptime("07:30", "%H:%M").time(),
                    key="hora_inicio_min_ac"
                ).strftime("%H:%M")
                
                config.restricciones_globales["hora_fin_max"] = st.time_input(
                    "Hora fin máxima", 
                    datetime.strptime("19:30", "%H:%M").time(),
                    key="hora_fin_max_ac"
                ).strftime("%H:%M")
                
                config.restricciones_globales["creditos_max_profesor"] = st.number_input(
                    "Créditos máximos por profesor", 1, 20, 15, key="creditos_max_prof_ac"
                )
                
                config.restricciones_globales["estudiantes_max_salon"] = st.number_input(
                    "Estudiantes máximos por salón", 20, 150, 50, key="estudiantes_max_salon_ac"
                )
            
            # Preferencias de Profesores
            st.sidebar.subheader("👤 Preferencias de Profesores")
            profesor_seleccionado = st.sidebar.selectbox(
                "Seleccionar profesor para configurar",
                ["Ninguno"] + list(config.profesores_config.keys()),
                key="prof_pref_select_ac"
            )
            
            if profesor_seleccionado != "Ninguno":
                with st.sidebar.expander(f"Configurar {profesor_seleccionado}"):
                    st.write("**Horarios preferidos:**")
                    dias = ["Lu", "Ma", "Mi", "Ju", "Vi"]
                    for dia in dias:
                        col1_pref, col2_pref = st.columns(2)
                        with col1_pref:
                            inicio = st.time_input(f"{dia} inicio", key=f"pref_{profesor_seleccionado}_{dia}_inicio_ac")
                        with col2_pref:
                            fin = st.time_input(f"{dia} fin", key=f"pref_{profesor_seleccionado}_{dia}_fin_ac")
                        
                        if inicio != datetime.strptime("00:00", "%H:%M").time():
                            if profesor_seleccionado not in config.profesores_config:
                                config.profesores_config[profesor_seleccionado] = {"horario_preferido": {}}
                            if "horario_preferido" not in config.profesores_config[profesor_seleccionado]:
                                config.profesores_config[profesor_seleccionado]["horario_preferido"] = {}
                            config.profesores_config[profesor_seleccionado]["horario_preferido"][dia] = [
                                (inicio.strftime("%H:%M"), fin.strftime("%H:%M"))
                            ]
            
            # Botones de control del horario
            st.markdown("---")
            col_gen, col_borrar = st.columns(2)
            
            with col_gen:
                if st.button("🚀 Generar Horario Optimizado", type="primary", key="btn_generar_horario_ac"):
                    with st.spinner("Generando horario optimizado..."):
                        mejor, score = buscar_mejor_horario(intentos)
                        
                        if mejor is None:
                            st.error("❌ No se pudo generar un horario válido. Ajusta las restricciones o verifica conflictos de salones.")
                            st.info("💡 **Sugerencia**: Algunos salones pueden estar ocupados por otros departamentos. Verifica el estado de reservas arriba.")
                        else:
                            st.success(f"✅ Horario generado. Puntuación: {score}")
                            
                            # Guardar reservas del departamento
                            if guardar_reservas_horario_departamento(mejor, departamento_key):
                                st.success("🔄 Reservas de salones guardadas correctamente")
                            else:
                                st.warning("⚠️ Horario generado pero hubo problemas al guardar las reservas")
                            
                            # Guardar en session state para persistencia
                            st.session_state.asignaciones_actuales = mejor
                            st.session_state.horario_generado = exportar_horario(mejor)
                            st.rerun()
            
            with col_borrar:
                if st.button("🗑️ Borrar Horario Generado", type="secondary", key="btn_borrar_horario_ac"):
                    # Limpiar horario generado
                    if 'asignaciones_actuales' in st.session_state:
                        del st.session_state.asignaciones_actuales
                    if 'horario_generado' in st.session_state:
                        del st.session_state.horario_generado
                    st.success("✅ Horario borrado correctamente")
                    st.rerun()
            
            # Mostrar horario si existe
            if 'horario_generado' in st.session_state and st.session_state.horario_generado is not None:
                st.markdown("---")
                _mostrar_tabs_horario_departamental(st.session_state.horario_generado, division, departamento)
                _mostrar_botones_persistencia_departamental(st.session_state.horario_generado, departamento_key)
                
        else:
            st.error("❌ No se pudieron cargar los datos del archivo Excel")
    else:
        # Sin archivo cargado: intentar cargar horario guardado del departamento
        departamento_key = f"{division} - {departamento}"
        df_guardado = cargar_horario_json(departamento_key)
        if df_guardado is not None and not df_guardado.empty:
            st.success("✅ Se cargó el último horario guardado para tu departamento.")
            st.session_state.horario_generado = df_guardado
            _mostrar_tabs_horario_departamental(df_guardado, division, departamento)
            _mostrar_botones_persistencia_departamental(df_guardado, departamento_key)
        else:
            st.info("📁 Por favor, carga un archivo Excel para comenzar o guarda un horario para recuperarlo luego.")
            with st.expander("📋 Formato esperado del archivo Excel"):
                st.write("""
                El archivo Excel debe contener al menos las siguientes columnas:
                
                | Profesor | Curso/Materia | Créditos | Estudiantes | Programa | Sección |
                |----------|---------------|----------|-------------|----------|---------|
                | Juan Pérez | Literatura I | 3 | 25 | Literatura Comparada | 001 |
                | María García | Filosofía Antigua | 4 | 30 | Filosofía | 002 |
                
                **Notas:**
                - Los nombres de las columnas pueden variar (profesor/docente, curso/materia/asignatura, etc.)
                - Si faltan columnas de créditos, estudiantes, programa o sección, se usarán valores por defecto
                - El sistema detecta automáticamente las columnas relevantes
                - Incluir la columna Programa es importante para filtros por carrera
                """)

def _creditos_unicos_por_profesor(df):
    """Suma créditos por curso único para evitar doble conteo por filas."""
    if df.empty:
        return 0
    df_unique = df[['Profesor', 'Curso', 'Créditos']].drop_duplicates()
    return df_unique.groupby('Profesor')['Créditos'].sum()

# NUEVO: Pestañas específicas para departamentos
def _mostrar_tabs_horario_departamental(df_horario, division, departamento):
    """Renderiza las pestañas de visualización del horario para departamentos"""
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📅 Calendario Visual", 
        "📊 Horario Completo", 
        "👨‍🏫 Por Profesor", 
        "📚 Por Programa",
        "🏫 Por Salón", 
        "📈 Estadísticas"
    ])
    
    # PESTAÑA 1: CALENDARIO VISUAL CON FILTROS
    with tab1:
        st.subheader(f"📅 Vista de Calendario - {division} - {departamento}")
        
        st.info("✨ **Calendario Departamental**: Vista optimizada para tu departamento con salones compartidos.")
        
        col1_filtro, col2_filtro = st.columns([2, 1])
        with col1_filtro:
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="color: white; margin: 0; text-align: center; font-size: 1.1rem;">
                    🏛️ <strong>{division} - {departamento}</strong> - Calendario con salones compartidos
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2_filtro:
            tipo_filtro = st.selectbox(
                "🔍 Filtrar por:",
                ["Salón", "Profesor", "Programa"],
                key="tipo_filtro_calendario_dept"
            )
            
            if tipo_filtro == "Salón":
                salones_disponibles = ["Todos los salones"] + sorted(df_horario['Salon'].unique().tolist())
                filtro_valor = st.selectbox("🏫 Seleccionar salón:", salones_disponibles, key="filtro_salon_dept")
                fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, "salon", filtro_valor, "dept_calendar")
            elif tipo_filtro == "Profesor":
                profesores_disponibles = ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist())
                filtro_valor = st.selectbox("👨‍🏫 Seleccionar profesor:", profesores_disponibles, key="filtro_profesor_dept")
                fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, "profesor", filtro_valor, "dept_calendar")
            elif tipo_filtro == "Programa":
                programas_disponibles = ["Todos los programas"] + sorted(df_horario['Programa'].unique().tolist())
                filtro_valor = st.selectbox("📚 Seleccionar programa:", programas_disponibles, key="filtro_programa_dept")
                fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, "programa", filtro_valor, "dept_calendar")
        
        st.plotly_chart(fig_calendario, use_container_width=True, key="plotly_dept_calendar")
        mostrar_leyenda_cursos(colores_cursos, df_horario, tipo_filtro.lower(), filtro_valor)
        
        col1_info, col2_info = st.columns(2)
        with col1_info:
            st.info("💡 Tip: Los salones mostrados son compartidos con otros departamentos.")
        with col2_info:
            st.info("🔍 Zoom: Usa las herramientas de Plotly para hacer zoom y navegar.")
    
    # PESTAÑA 2: HORARIO COMPLETO
    with tab2:
        st.subheader("📊 Horario Completo del Departamento")
        
        df_ordenado = df_horario.sort_values(['Dia', 'Hora Inicio', 'Salon'])
        st.dataframe(df_ordenado, use_container_width=True, key="dataframe_dept")
        
        csv = df_ordenado.to_csv(index=False)
        st.download_button(
            label="💾 Descargar horario (CSV)",
            data=csv,
            file_name=f"horario_{division}_{departamento}.csv",
            mime="text/csv",
            key="download_csv_dept"
        )
    
    # PESTAÑA 3: POR PROFESOR
    with tab3:
        st.subheader("👨‍🏫 Horario por Profesor")
        
        profesor_individual = st.selectbox(
            "Seleccionar profesor:",
            sorted(df_horario['Profesor'].unique()),
            key="selector_profesor_dept"
        )
        
        if profesor_individual:
            df_prof = df_horario[df_horario['Profesor'] == profesor_individual]
            if not df_prof.empty:
                fig_prof, colores_prof = crear_calendario_interactivo(df_horario, "profesor", profesor_individual, "dept_prof")
                st.plotly_chart(fig_prof, use_container_width=True, key="plotly_dept_prof")
                
                df_prof_ordenado = df_prof.sort_values(['Dia', 'Hora Inicio'])
                st.dataframe(df_prof_ordenado, use_container_width=True, key="dataframe_dept_prof")
                
                # Métricas del profesor
                creditos_por_profesor = _creditos_unicos_por_profesor(df_prof)
                creditos_total_prof = int(creditos_por_profesor.get(profesor_individual, 0))
                
                col1_prof, col2_prof, col3_prof = st.columns(3)
                with col1_prof:
                    st.metric("📚 Total Cursos", df_prof['Curso'].nunique())
                with col2_prof:
                    st.metric("⏰ Horas Semanales", f"{df_prof['Duración'].sum():.1f}")
                with col3_prof:
                    st.metric("🎓 Créditos Totales", creditos_total_prof)
            else:
                st.warning(f"No se encontraron clases para {profesor_individual}")
    
    # PESTAÑA 4: POR PROGRAMA
    with tab4:
        st.subheader("📚 Horario por Programa/Carrera")
        
        st.info(f"🎯 **Vista por Programa**: Programas del departamento {departamento}")
        
        programa_individual = st.selectbox(
            "Seleccionar programa:",
            sorted(df_horario['Programa'].unique()),
            key="selector_programa_dept"
        )
        
        if programa_individual:
            df_programa = df_horario[df_horario['Programa'] == programa_individual]
            if not df_programa.empty:
                fig_programa, colores_programa = crear_calendario_interactivo(df_horario, "programa", programa_individual, "dept_programa")
                st.plotly_chart(fig_programa, use_container_width=True, key="plotly_dept_programa")
                
                df_programa_ordenado = df_programa.sort_values(['Dia', 'Hora Inicio'])
                st.dataframe(df_programa_ordenado, use_container_width=True, key="dataframe_dept_programa")
                
                # Métricas del programa
                col1_prog, col2_prog, col3_prog, col4_prog = st.columns(4)
                with col1_prog:
                    st.metric("📚 Total Cursos", df_programa['Curso'].nunique())
                with col2_prog:
                    st.metric("👨‍🏫 Profesores", df_programa['Profesor'].nunique())
                with col3_prog:
                    st.metric("🏫 Salones Usados", df_programa['Salon'].nunique())
                with col4_prog:
                    st.metric("👥 Total Estudiantes", int(df_programa['Estudiantes'].sum()))
            else:
                st.warning(f"No se encontraron clases para {programa_individual}")
    
    # PESTAÑA 5: POR SALÓN
    with tab5:
        st.subheader("🏫 Horario por Salón (Compartidos)")
        
        st.info("🏫 **Salones Compartidos**: Estos salones son utilizados por múltiples departamentos.")
        
        salon_individual = st.selectbox(
            "Seleccionar salón:",
            sorted(df_horario['Salon'].unique()),
            key="selector_salon_dept"
        )
        
        if salon_individual:
            df_salon = df_horario[df_horario['Salon'] == salon_individual]
            if not df_salon.empty:
                fig_salon, colores_salon = crear_calendario_interactivo(df_horario, "salon", salon_individual, "dept_salon")
                st.plotly_chart(fig_salon, use_container_width=True, key="plotly_dept_salon")
                
                df_salon_ordenado = df_salon.sort_values(['Dia', 'Hora Inicio'])
                st.dataframe(df_salon_ordenado, use_container_width=True, key=f"dataframe_salon_dept_{salon_individual}")
                
                # Métricas del salón
                col1_salon, col2_salon, col3_salon = st.columns(3)
                with col1_salon:
                    horas_uso = df_salon['Duración'].sum()
                    st.metric("⏰ Horas de uso semanal", f"{horas_uso:.1f}h")
                with col2_salon:
                    st.metric("📚 Cursos diferentes", df_salon['Curso'].nunique())
                with col3_salon:
                    st.metric("👨‍🏫 Profesores diferentes", df_salon['Profesor'].nunique())
            else:
                st.warning(f"No se encontraron clases para {salon_individual}")
        
        st.write(f"**🏫 Total de salones utilizados por el departamento:** {df_horario['Salon'].nunique()}")
    
    # PESTAÑA 6: ESTADÍSTICAS
    with tab6:
        st.subheader(f"📈 Estadísticas del Departamento - {departamento}")
        col1_met, col2_met, col3_met, col4_met = st.columns(4)
        with col1_met:
            st.metric("📚 Total Clases", len(df_horario))
        with col2_met:
            st.metric("👨‍🏫 Profesores", df_horario['Profesor'].nunique())
        with col3_met:
            st.metric("🏫 Salones Usados", df_horario['Salon'].nunique())
        with col4_met:
            total_estudiantes = df_horario['Estudiantes'].sum()
            st.metric("👥 Total Estudiantes", int(total_estudiantes))
        
        # Estadísticas por programa
        st.subheader("📊 Estadísticas por Programa/Carrera")
        stats_programa = df_horario.groupby('Programa').agg({
            'Curso': 'nunique',
            'Profesor': 'nunique',
            'Salon': 'nunique',
            'Estudiantes': 'sum',
            'Duración': 'sum'
        }).round(1)
        stats_programa.columns = ['Cursos', 'Profesores', 'Salones', 'Estudiantes', 'Horas Totales']
        st.dataframe(stats_programa, use_container_width=True)
        
        # Créditos por profesor
        creditos_prof = _creditos_unicos_por_profesor(df_horario)
        fig_creditos = px.bar(
            x=list(creditos_prof.index), 
            y=list(creditos_prof.values),
            title="Créditos por Profesor (por curso único)",
            color=list(creditos_prof.values),
            color_continuous_scale="viridis"
        )
        fig_creditos.update_layout(showlegend=False)
        st.plotly_chart(fig_creditos, use_container_width=True, key="plotly_creditos_dept")
        
        # Utilización de salones
        uso_salones = df_horario.groupby('Salon').agg({
            'Duración': 'sum',
            'Curso': 'nunique'
        }).round(1)
        uso_salones.columns = ['Horas Totales', 'Cursos Diferentes']
        
        fig_salones = px.bar(
            uso_salones,
            x=uso_salones.index,
            y='Horas Totales',
            title="Utilización de Salones por el Departamento",
            color='Horas Totales',
            color_continuous_scale="blues"
        )
        st.plotly_chart(fig_salones, use_container_width=True, key="plotly_salones_dept")

def _mostrar_botones_persistencia_departamental(df_horario, departamento_key):
    """Muestra los botones de persistencia para departamentos."""
    st.markdown("---")
    st.markdown("### 💾 Gestión de Horarios del Departamento")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Horario", type="primary", use_container_width=True, key="btn_guardar_dept"):
            if df_horario is None or df_horario.empty:
                st.error("No hay horario para guardar.")
            else:
                ok = guardar_horario_json(df_horario, departamento_key)
                if ok:
                    # Guardar reservas también
                    if config and config.usa_reservas and 'asignaciones_actuales' in st.session_state:
                        guardar_reservas_horario_departamento(st.session_state.asignaciones_actuales, departamento_key)
                    st.success("✅ Horario del departamento guardado correctamente.")
                else:
                    st.error("❌ Error al guardar el horario.")
    
    with col2:
        if st.button("🔄 Generar Nuevo Horario", use_container_width=True, key="btn_generar_nuevo_dept"):
            if not os.path.exists("temp_excel.xlsx"):
                st.warning("Primero carga un archivo Excel en la barra lateral para poder generar un nuevo horario.")
            else:
                # Limpiar horario actual
                if 'asignaciones_actuales' in st.session_state:
                    del st.session_state.asignaciones_actuales
                if 'horario_generado' in st.session_state:
                    del st.session_state.horario_generado
                st.info("🔄 Horario borrado. Usa el botón 'Generar Horario Optimizado' para crear uno nuevo.")
                st.rerun()
    
    with col3:
        if st.button("📤 Exportar Departamental", use_container_width=True, key="btn_exportar_dept"):
            st.info("📋 **Exportación Departamental**: Descarga el horario desde la pestaña 'Horario Completo' o usa las capturas del calendario visual.")

# NUEVA FUNCIÓN: Guardar reservas del horario por departamento
def guardar_reservas_horario_departamento(asignaciones, departamento_key):
    """Guarda las reservas de salones del horario generado por departamento"""
    if not config or not config.usa_reservas or not config.sistema_reservas:
        return True
    
    # Primero liberar reservas anteriores del departamento
    config.sistema_reservas.liberar_reservas_departamento(departamento_key)
    
    # Guardar nuevas reservas
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            hora_fin_min = a_minutos(asig.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            
            config.sistema_reservas.reservar_salon(
                salon=asig.salon,
                dia=dia,
                hora_inicio=asig.hora_inicio,
                hora_fin=hora_fin,
                departamento=departamento_key,
                programa=asig.programa,
                curso=asig.curso_nombre,
                profesor=asig.profesor
            )
    
    return True

# ========================================================
# MAIN ACTUALIZADO
# ========================================================

def main():
    st.set_page_config(
        page_title="Sistema de Generación de Horarios Académicos - RUM",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS personalizado
    st.markdown("""
    <style>
    .main > div { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] { background-color: #667eea; color: white; }
    </style>
    """, unsafe_allow_html=True)

    # Inicializar session state para autenticación
    if 'usuario_autenticado' not in st.session_state:
        st.session_state.usuario_autenticado = False
    if 'info_usuario' not in st.session_state:
        st.session_state.info_usuario = None

    # Sistema principal
    if not st.session_state.usuario_autenticado:
        # Pestaña de Login
        tab_login, tab_info = st.tabs(["🔐 Iniciar Sesión", "ℹ️ Información del Sistema"])
        
        with tab_login:
            mostrar_login()
        
        with tab_info:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;">
                <h1 style="color: white; margin: 0; font-size: 2.5rem;">🎓 Sistema de Horarios RUM</h1>
                <p style="color: white; margin: 1rem 0 0 0; font-size: 1.2rem;">Recinto Universitario de Mayagüez</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("## 🚀 Características del Sistema - Artes y Ciencias Actualizado")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### ✨ Funcionalidades Principales
                - 🔐 **Acceso por Departamento**: Sistema específico para cada departamento
                - 🏫 **Salones Compartidos**: Gestión automática de conflictos entre departamentos
                - 📅 **Calendario Departamental**: Vista optimizada por departamento
                - 🔄 **Filtros por Programa**: Visualización por carrera dentro del departamento
                - 💾 **Persistencia Departamental**: Guarda horarios por departamento
                - 📊 **Estadísticas Avanzadas**: Análisis específico del departamento
                """)
            
            with col2:
                st.markdown("""
                ### 🏛️ Estructura de Artes y Ciencias
                
                **🎨 División de Artes:**
                - Humanidades, Economía, Inglés, Sociales
                - Estudios Hispánicos, Educación Física, Psicología
                
                **🔬 División de Ciencias:**
                - Biología, Química, Geología, Matemática
                - Enfermería, Física, Ciencias Marinas
                
                ### 🎯 Nuevas Mejoras
                - **Gestión Departamental**: Cada departamento genera sus horarios independientemente
                - **Salones Compartidos**: Sistema de reservas para evitar conflictos
                - **Filtros por Carrera**: Vista específica por programa dentro del departamento
                """)
            
            st.markdown("---")
            st.info("💡 **Para comenzar**: Inicia sesión con las credenciales de tu departamento en la pestaña 'Iniciar Sesión'.")
    
    else:
        # Usuario autenticado: verificar si es Artes y Ciencias
        if st.session_state.colegio_seleccionado == "COLEGIO DE ARTES Y CIENCIAS":
            # Mostrar interfaz específica para Artes y Ciencias
            tab_horarios, tab_config, tab_ayuda = st.tabs(["📅 Generador de Horarios", "⚙️ Configuración", "❓ Ayuda"])
            
            with tab_horarios:
                mostrar_generador_horarios_artes_ciencias()
            
            with tab_config:
                st.markdown("## ⚙️ Configuración del Departamento")
                
                mostrar_header_usuario()
                
                info_usuario = st.session_state.info_usuario
                division = info_usuario.get('division', '')
                departamento = info_usuario.get('departamento', '')
                
                st.markdown("### 🔧 Configuraciones Disponibles")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    #### 🏛️ Información del Departamento
                    - **División:** {division}
                    - **Departamento:** {departamento}
                    - **Salones:** Compartidos entre departamentos
                    - **Sistema de Reservas:** Activo
                    """)
                    
                    st.success("✅ Sistema de reservas activo para salones compartidos")
                    st.info("🏫 Salones compartidos con otros departamentos de Artes y Ciencias")
                
                with col2:
                    st.markdown("""
                    #### ⏰ Restricciones Temporales
                    - Horarios prohibidos: Martes y Jueves 11:00-12:30 (Hora de facultad)
                    - Límites de horas por día configurables
                    - Restricciones de bloques de 3 horas después de 15:30
                    """)
                    
                    st.info(f"📚 Configurado para: {st.session_state.nivel_seleccionado}")
                    st.warning("⚠️ Horarios prohibidos: Martes y Jueves 11:00-12:30")
                
                st.markdown("---")
                st.markdown("### 📊 Estado del Sistema")
                
                if os.path.exists("temp_excel.xlsx"):
                    st.success("✅ Archivo de datos cargado")
                else:
                    st.warning("⚠️ No hay archivo de datos cargado")
                
                if 'horario_generado' in st.session_state:
                    st.success("✅ Horario generado disponible")
                else:
                    st.info("ℹ️ No hay horario generado")
            
            with tab_ayuda:
                st.markdown("## ❓ Ayuda - Artes y Ciencias")
                
                mostrar_header_usuario()
                
                st.markdown("### 🚀 Guía de Uso para Departamentos")
                
                with st.expander("1️⃣ Acceso por Departamento", expanded=True):
                    st.markdown("""
                    **Credenciales de Acceso:**
                    - Usuario: `[División] - [Departamento]` (ej: `Artes - Humanidades`)
                    - Contraseña: Nombre exacto del programa (ej: `Literatura Comparada`)
                    
                    **Ejemplos:**
                    - Artes - Humanidades | Literatura Comparada
                    - Ciencias - Biología | Biología
                    - Artes - Psicología | Psicología
                    """)
                
                with st.expander("2️⃣ Salones Compartidos"):
                    st.markdown("""
                    **Sistema de Reservas:**
                    - Los salones AC y LAB son compartidos entre todos los departamentos
                    - El sistema evita automáticamente conflictos de horarios
                    - Puedes ver el estado de reservas de otros departamentos
                    - Libera las reservas de tu departamento si necesitas regenerar horarios
                    """)
                
                with st.expander("3️⃣ Filtros por Programa"):
                    st.markdown("""
                    **Visualización por Carrera:**
                    - Cada departamento puede tener múltiples programas/carreras
                    - Usa los filtros para ver horarios específicos por programa
                    - El calendario muestra todos los programas del departamento
                    - Las estadísticas se desglosan por programa
                    """)
                
                with st.expander("4️⃣ Gestión Departamental"):
                    st.markdown("""
                    **Administración de Horarios:**
                    - Cada departamento gestiona sus horarios independientemente
                    - Los horarios se guardan por departamento
                    - Las reservas de salones se manejan automáticamente
                    - Coordina con otros departamentos para optimizar el uso de salones
                    """)
                
                st.markdown("---")
                st.markdown("### 🔧 Solución de Problemas Específicos")
                
                with st.expander("❌ No hay salones disponibles"):
                    st.markdown("""
                    **Posibles causas:**
                    - Otros departamentos están usando los salones en esos horarios
                    - Verifica el estado de reservas en la sección principal
                    - Coordina con otros departamentos para liberar salones
                    - Ajusta los horarios de tus cursos para evitar horas pico
                    """)
                
                with st.expander("🏫 Conflictos de salones"):
                    st.markdown("""
                    **Resolución de conflictos:**
                    - El sistema previene automáticamente conflictos
                    - Si hay problemas, libera las reservas de tu departamento
                    - Contacta otros departamentos si es necesario
                    - Usa horarios menos populares (temprano en la mañana o tarde)
                    """)
        
        else:
            # Para otros colegios, mostrar mensaje de redirección
            st.markdown("## 🔄 Sistema en Desarrollo")
            mostrar_header_usuario()
            
            st.info("""
            **Este demo está enfocado en el Colegio de Artes y Ciencias.**
            
            Para otros colegios, el sistema original sigue disponible. 
            Esta versión demuestra las nuevas funcionalidades para:
            
            - 🎨 División de Artes (7 departamentos)
            - 🔬 División de Ciencias (7 departamentos)
            - 🏫 Sistema de salones compartidos
            - 📊 Gestión departamental independiente
            """)
            
            st.markdown("### 🎯 Funcionalidades Implementadas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **✅ Completado:**
                - Sistema de autenticación por departamento
                - Gestión de salones compartidos
                - Reservas automáticas para evitar conflictos
                - Interfaz específica por departamento
                - Filtros por programa/carrera
                - Persistencia de datos por departamento
                """)
            
            with col2:
                st.markdown("""
                **🚀 Beneficios:**
                - Eliminación de conflictos de salones
                - Gestión independiente por departamento
                - Visualización optimizada por división
                - Coordinación automática entre departamentos
                - Estadísticas específicas por área
                """)

if __name__ == "__main__":
    main()
