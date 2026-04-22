import streamlit as st
import formulas
import pandas as pd

# 1. CONFIGURACIÓN ESTÉTICA Y DE PÁGINA
st.set_page_config(page_title="Hub Naval - B/C Cormorán", layout="wide", page_icon="🚢")

st.title("🚢 Hub Naval: Sistema de Gestión de Estabilidad")
st.subheader("B/C Cormorán - Herramienta de Cálculo Escalable")
st.markdown("---")

# 2. CARGA DEL MOTOR DE CÁLCULO (EXCEL)
@st.cache_resource
def cargar_motor_excel():
    return formulas.ExcelModel().loads('Hub_Naval.xlsx').finish()

try:
    with st.spinner("Inicializando motor hidrostático..."):
        modelo = cargar_motor_excel()
    st.sidebar.success("✅ Motor de cálculo conectado")
except Exception as e:
    st.error(f"Error crítico al cargar el motor Excel: {e}")
    st.stop()

# Inicializar la memoria (session_state) para todas las tablas dinámicas
if "resultados_M" not in st.session_state:
    st.session_state["resultados_M"] = {i: None for i in range(12, 17)}
if "resultados_L" not in st.session_state:
    filas_l = list(range(20, 29)) + list(range(32, 36)) + list(range(39, 64)) + list(range(67, 77)) + list(range(80, 82)) + list(range(85, 88)) + list(range(91, 96))
    st.session_state["resultados_L"] = {i: None for i in filas_l}
if "resultados_otros" not in st.session_state:
    st.session_state["resultados_otros"] = {i: {"MV": None, "ML": None, "MT": None} for i in range(99, 109)}
if "resultados_nav" not in st.session_state:
    st.session_state["resultados_nav"] = {"DRL": None, "TRL": None, "Ganancia": None, "DGC": None, "TGC": None}
if "resultados_dmax" not in st.session_state:
    st.session_state["resultados_dmax"] = {"S_Sal": None, "D_Lleg": None}
if "resultados_carga" not in st.session_state:
    st.session_state["resultados_carga"] = {i: {"ACT": None, "%ACT": None, "SAL": None} for i in range(173, 178)}
if "resultados_dist_consumos" not in st.session_state:
    st.session_state["resultados_dist_consumos"] = {i: {"dRest_HFO": None, "dRest_DO": None} for i in range(255, 264)}

# 3. CONTENEDOR DE DATOS GLOBAL
entradas_usuario = {}

opciones_estado = ["Full", "Slack", "Vacio"]
opciones_und_peso = ["Tm", "LT"]
opciones_und_vol = ["m3", "ft3"]

# =========================================================
# SECCIÓN 1: D ACTUAL Y BODEGAS
# =========================================================
st.header("1. D Actual y Estado de Bodegas")
col_d, _ = st.columns([1, 4])
entradas_usuario["'Interfaz'!F9"] = col_d.number_input("d actual (Celda F9)", value=1.025, format="%.4f")

st.markdown("#### Reparto en Bodegas")
cols_h_bod = st.columns([1, 1.5, 1.5, 1, 1, 1.5, 1, 1, 2])
for i, h in enumerate(["Bodega", "Estado", "D/V/%", "Und", "d/Fe", "Fe/d", "Und", "Und", "Desplazamiento"]):
    cols_h_bod[i].markdown(f"**{h}**")

for i in range(5):
    fila = 12 + i
    cols = st.columns([1, 1.5, 1.5, 1, 1, 1.5, 1, 1, 2])
    cols[0].markdown(f"<div style='padding-top: 10px;'><b>B{i+1}</b></div>", unsafe_allow_html=True)
    entradas_usuario[f"'Interfaz'!F{fila}"] = cols[1].selectbox(f"F{fila}", opciones_estado, key=f"F{fila}", label_visibility="collapsed")
    entradas_usuario[f"'Interfaz'!G{fila}"] = cols[2].number_input(f"G{fila}", value=0.00, key=f"G{fila}", label_visibility="collapsed")
    entradas_usuario[f"'Interfaz'!H{fila}"] = cols[3].selectbox(f"H{fila}", ["", "Tm", "LT", "ft3", "m3"], key=f"H{fila}", label_visibility="collapsed")
    entradas_usuario[f"'Interfaz'!I{fila}"] = cols[4].selectbox(f"I{fila}", ["d", "Fe"], key=f"I{fila}", label_visibility="collapsed")
    entradas_usuario[f"'Interfaz'!J{fila}"] = cols[5].number_input(f"J{fila}", value=0.00, key=f"J{fila}", label_visibility="collapsed")
    entradas_usuario[f"'Interfaz'!K{fila}"] = cols[6].selectbox(f"K{fila}", opciones_und_peso, key=f"K{fila}", label_visibility="collapsed")
    entradas_usuario[f"'Interfaz'!L{fila}"] = cols[7].selectbox(f"L{fila}", opciones_und_peso, key=f"L{fila}", label_visibility="collapsed")

    with cols[8]:
        c1, c2 = st.columns([1, 1])
        if c1.button("Calc.", key=f"btn_b_{fila}"):
            sol = modelo.calculate(inputs=entradas_usuario)
            st.session_state["resultados_M"][fila] = sol[f"'Interfaz'!M{fila}"].value[0, 0]
        if st.session_state["resultados_M"][fila] is not None:
            c2.success(f"{st.session_state['resultados_M'][fila]:.2f}")

# =========================================================
# SECCIONES 2 A 8: TANQUES Y CONSUMIBLES
# =========================================================
secciones_tanques = [
    ("2. Heavy Fuel Oil", 19, 0.950, 20, ["HFO Deep P 1", "HFO Deep S 1", "HFO Deep P 2", "HFO Deep S 2", "HFO Service Tk 1", "HFO Service Tk 2", "HFO Settling Tk 1", "HFO Settling Tk 2", "HFO Overflow Tk"]),
    ("3. Diesel Oil", 31, 0.850, 32, ["DO Deep Tk S", "DO Service Tk 1", "DO Service Tk 2", "DO Settling Tk"]),
    ("4. Water Ballast", 38, 1.025, 39, ["FPT", "WBT No.1 (P)", "WBT No.1 (S)", "WBT No.2 (P)", "WBT No.2 (S)", "WBT No.3 (P)", "WBT No.3 (S)", "WBT No.4 (P)", "WBT No.4 (S)", "WBT No.5 (P)", "WBT No.5 (S)", "WBT No.6 (P)", "WBT No.6 (S)", "WBT No.7 (P)", "WBT No.7 (S)", "Heeling Tk (P)", "Heeling Tk (S)", "WBT No.8 (P)", "WBT No.8 (S)", "WBT No.9 (P)", "WBT No.9 (S)", "APT", "Heeling Tk (P)", "Heeling Tk (S)", ""]),
    ("5. Lubricating Oil", 66, 0.900, 67, ["M/E LO Sump Tk", "G/E LO Sump Tk 1", "G/E LO Sump Tk 2", "G/E LO Sump Tk 3", "M/E LO Settling Tk", "M/E LO Storage Tk", "G/E LO Storage Tk", "LO Cyl Storage Tk", "LO Stern Tube Grav Tk 1", "LO Stern Tube Grav Tk 2"]),
    ("6. Fresh Water", 79, 1.000, 80, ["FWT (P)", "FWT (S)"]),
    ("7. Miscellaneous Oil", 84, 0.900, 85, ["Incinerator Waste Oil Tk", "Waste Oil Tk", "Bilge Water Tk"]),
    ("8. Miscellaneous Water", 90, 1.000, 91, ["Sewage Holding Tk", "Grey Water Tk (P)", "Grey Water Tk (S)", "Stern Tube CW Tk", "BWTS CW Tk"])
]

for titulo, celda_densidad, dens_defecto, fila_inicio, lista_tanques in secciones_tanques:
    st.markdown("---")
    st.header(titulo)
    col_d_sec, _ = st.columns([2, 8])
    entradas_usuario[f"'Interfaz'!I{celda_densidad}"] = col_d_sec.number_input(f"Densidad Global (I{celda_densidad})", value=dens_defecto, format="%.4f", key=f"dens_{titulo}")

    cols_h = st.columns([2.5, 1.2, 1, 1.2, 1.2, 1, 1, 2])
    for i, h in enumerate(["Tanque", "F/Slc", "%", "d", "Valor d", "Und", "Und", "D Tm ACT"]):
        cols_h[i].markdown(f"**{h}**")

    for i, nombre in enumerate(lista_tanques):
        fila = fila_inicio + i
        cols = st.columns([2.5, 1.2, 1, 1.2, 1.2, 1, 1, 2])
        cols[0].markdown(f"<div style='padding-top: 10px; font-size:14px;'>{nombre if nombre != '' else '...'}</div>", unsafe_allow_html=True)
        f_val = cols[1].selectbox(f"F{fila}", opciones_estado, key=f"F{fila}", label_visibility="collapsed")
        g_val = cols[2].number_input(f"G{fila}", value=0.00, key=f"G{fila}", label_visibility="collapsed")
        h_val = cols[3].selectbox(f"H{fila}", ["Igual", "Distinta"], key=f"H{fila}", label_visibility="collapsed")
        i_val = cols[4].number_input(f"I{fila}", value=0.00, format="%.4f", key=f"I{fila}", label_visibility="collapsed")

        entradas_usuario[f"'Interfaz'!F{fila}"] = f_val
        entradas_usuario[f"'Interfaz'!G{fila}"] = g_val
        entradas_usuario[f"'Interfaz'!H{fila}"] = h_val
        if h_val == "Distinta":
            entradas_usuario[f"'Interfaz'!I{fila}"] = i_val
        entradas_usuario[f"'Interfaz'!J{fila}"] = cols[5].selectbox(f"J{fila}", opciones_und_peso, key=f"J{fila}", label_visibility="collapsed")
        entradas_usuario[f"'Interfaz'!K{fila}"] = cols[6].selectbox(f"K{fila}", opciones_und_vol, key=f"K{fila}", label_visibility="collapsed")

        with cols[7]:
            c1, c2 = st.columns([1, 1])
            if c1.button("Calc.", key=f"btn_sec_{fila}"):
                with st.spinner(""):
                    sol = modelo.calculate(inputs=entradas_usuario)
                    st.session_state["resultados_L"][fila] = sol[f"'Interfaz'!L{fila}"].value[0, 0]
            if st.session_state["resultados_L"][fila] is not None:
                c2.success(f"{st.session_state['resultados_L'][fila]:.2f}")

# =========================================================
# SECCIÓN 9: OTROS PESOS
# =========================================================
st.markdown("---")
st.header("9. Otros Pesos")
cols_h_otros = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1, 1.2])
for i, h in enumerate(["Otros Pesos", "Peso (Tm)", "VCG", "MV", "LCG", "ML", "TCG", "MT", "Acción"]):
    cols_h_otros[i].markdown(f"**{h}**")

for i in range(10):
    fila = 99 + i
    cols = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1, 1.2])
    cols[0].markdown(f"<div style='padding-top: 10px; font-size:14px;'>Peso Nº {i+1}</div>", unsafe_allow_html=True)

    peso = cols[1].number_input(f"F{fila}", value=None, format="%.2f", key=f"F{fila}", label_visibility="collapsed")
    vcg  = cols[2].number_input(f"G{fila}", value=None, format="%.2f", key=f"G{fila}", label_visibility="collapsed")
    ph_mv = cols[3].empty()
    lcg  = cols[4].number_input(f"I{fila}", value=None, format="%.2f", key=f"I{fila}", label_visibility="collapsed")
    ph_ml = cols[5].empty()
    tcg  = cols[6].number_input(f"K{fila}", value=None, format="%.2f", key=f"K{fila}", label_visibility="collapsed")
    ph_mt = cols[7].empty()

    fila_completa = (peso is not None) and (vcg is not None) and (lcg is not None) and (tcg is not None)
    if fila_completa:
        entradas_usuario[f"'Interfaz'!F{fila}"] = peso
        entradas_usuario[f"'Interfaz'!G{fila}"] = vcg
        entradas_usuario[f"'Interfaz'!I{fila}"] = lcg
        entradas_usuario[f"'Interfaz'!K{fila}"] = tcg

    with cols[8]:
        if st.button("Calc.", key=f"btn_otros_{fila}"):
            if fila_completa:
                with st.spinner(""):
                    sol = modelo.calculate(inputs=entradas_usuario)
                    st.session_state["resultados_otros"][fila]["MV"] = sol[f"'Interfaz'!H{fila}"].value[0, 0]
                    st.session_state["resultados_otros"][fila]["ML"] = sol[f"'Interfaz'!J{fila}"].value[0, 0]
                    st.session_state["resultados_otros"][fila]["MT"] = sol[f"'Interfaz'!L{fila}"].value[0, 0]

    if st.session_state["resultados_otros"][fila]["MV"] is not None:
        ph_mv.success(f"{st.session_state['resultados_otros'][fila]['MV']:.2f}")
    if st.session_state["resultados_otros"][fila]["ML"] is not None:
        ph_ml.success(f"{st.session_state['resultados_otros'][fila]['ML']:.2f}")
    if st.session_state["resultados_otros"][fila]["MT"] is not None:
        ph_mt.success(f"{st.session_state['resultados_otros'][fila]['MT']:.2f}")

# =========================================================
# SECCIÓN 10: NAVEGACIÓN
# =========================================================
st.markdown("---")
st.header("10. Navegación")

lista_puertos = [
    "Otro", "Aarhus", "Abiyán", "Alejandría", "Algeciras", "Amberes", "Anchorage", "Ashdod", "Auckland",
    "Balboa", "Bangkok", "Barcelona", "Bilbao", "Bremen/Bremerhaven", "Brisbane", "Buenos Aires", "Busan",
    "Calcuta", "Callao", "Cartagena", "Chennai", "Chittagong", "Ciudad del Cabo", "Colombo", "Colón",
    "Dakar", "Durban", "El Pireo", "Estambul", "Felixstowe", "Fremantle", "Gdansk", "Génova", "Gioia Tauro",
    "Gotemburgo", "Guangzhou", "Guayaquil", "Haifa", "Halifax", "Hamburgo", "Ho Chi Minh", "Hong Kong",
    "Honolulu", "Houston", "Incheon", "Jakarta", "Jebel Ali (Dubai)", "Jeddah", "Kaohsiung", "Karachi", "Kobe",
    "La Spezia", "Laem Chabng", "Lagos", "Las Palmas", "Le Havre", "Lianyungang", "Lisboa", "Londres Gateway",
    "Long Beach", "Los Angeles", "Manila", "Manzanillo (México)", "Marsella", "Melbourne", "Mersin", "Miami",
    "Mombasa", "Montevideo", "Montreal", "Mundra", "Nagoya", "Nhava Sheva (Mumbai)", "Novorossiysk",
    "Nueva York / Nueva Jersey", "Oakland", "Osaka", "Penang", "Port Klang", "Port Said", "Qingdao",
    "Rotterdam", "Salalah", "San Antonio", "San Petersburgo", "Santos", "Savannah", "Seattle", "Shanghai",
    "Sines", "Singapur", "Southampton", "Surabaya", "Sydney", "Tanger Med", "Tanjung Pelepas",
    "Tanjung Priok (Yakarta)", "Tauranga", "Tenerife", "Tianjin", "Tokio", "Trieste", "Valencia",
    "Valparaíso", "Vancouver", "Veracruz", "Vigo", "Xiamen", "Yokohama"
]

col_orig, col_dest = st.columns(2)

with col_orig:
    st.subheader("Origen (A)")
    puerto_origen = st.selectbox("Puerto:", lista_puertos, key="puerto_a")
    entradas_usuario["'Interfaz'!F129"] = puerto_origen

    if puerto_origen == "Otro":
        st.write("Latitud")
        c1, c2, c3, c4 = st.columns(4)
        entradas_usuario["'Interfaz'!E132"] = c1.number_input("Grados (º)", value=0, step=1, key="lat_deg_a")
        entradas_usuario["'Interfaz'!F132"] = c2.number_input("Minutos (')", value=0, step=1, key="lat_min_a")
        entradas_usuario["'Interfaz'!G132"] = c3.number_input("Segundos ('')", value=0.0, format="%.2f", key="lat_sec_a")
        entradas_usuario["'Interfaz'!H132"] = c4.selectbox("N/S", ["N", "S"], key="lat_ns_a")

        st.write("Longitud")
        c5, c6, c7, c8 = st.columns(4)
        entradas_usuario["'Interfaz'!E134"] = c5.number_input("Grados (º)", value=0, step=1, key="lon_deg_a")
        entradas_usuario["'Interfaz'!F134"] = c6.number_input("Minutos (')", value=0, step=1, key="lon_min_a")
        entradas_usuario["'Interfaz'!G134"] = c7.number_input("Segundos ('')", value=0.0, format="%.2f", key="lon_sec_a")
        entradas_usuario["'Interfaz'!H134"] = c8.selectbox("E/W", ["W", "E"], key="lon_ew_a")

with col_dest:
    st.subheader("Destino (B)")
    puerto_destino = st.selectbox("Puerto:", lista_puertos, key="puerto_b")
    entradas_usuario["'Interfaz'!K129"] = puerto_destino

    if puerto_destino == "Otro":
        st.write("Latitud")
        c1, c2, c3, c4 = st.columns(4)
        entradas_usuario["'Interfaz'!J132"] = c1.number_input("Grados (º)", value=0, step=1, key="lat_deg_b")
        entradas_usuario["'Interfaz'!K132"] = c2.number_input("Minutos (')", value=0, step=1, key="lat_min_b")
        entradas_usuario["'Interfaz'!L132"] = c3.number_input("Segundos ('')", value=0.0, format="%.2f", key="lat_sec_b")
        entradas_usuario["'Interfaz'!M132"] = c4.selectbox("N/S", ["N", "S"], key="lat_ns_b")

        st.write("Longitud")
        c5, c6, c7, c8 = st.columns(4)
        entradas_usuario["'Interfaz'!J134"] = c5.number_input("Grados (º)", value=0, step=1, key="lon_deg_b")
        entradas_usuario["'Interfaz'!K134"] = c6.number_input("Minutos (')", value=0, step=1, key="lon_min_b")
        entradas_usuario["'Interfaz'!L134"] = c7.number_input("Segundos ('')", value=0.0, format="%.2f", key="lon_sec_b")
        entradas_usuario["'Interfaz'!M134"] = c8.selectbox("E/W", ["W", "E"], key="lon_ew_b")

st.markdown("#### Parámetros de Ruta")
col_vel, col_derrota, _ = st.columns([2, 2, 6])
entradas_usuario["'Interfaz'!F137"] = col_vel.number_input("V media (Kt)", value=15.0, format="%.2f", key="v_media")
entradas_usuario["'Interfaz'!F142"] = col_derrota.selectbox("Selector de Derrota", ["GC", "RL"], key="derrota")

if st.button("🗺️ Calcular Navegación", use_container_width=True):
    with st.spinner("Calculando distancias y tiempos de ruta..."):
        sol_nav = modelo.calculate(inputs=entradas_usuario)
        st.session_state["resultados_nav"]["DRL"]     = sol_nav["'Interfaz'!F139"].value[0, 0]
        st.session_state["resultados_nav"]["TRL"]     = sol_nav["'Interfaz'!F140"].value[0, 0]
        st.session_state["resultados_nav"]["Ganancia"]= sol_nav["'Interfaz'!H140"].value[0, 0]
        st.session_state["resultados_nav"]["DGC"]     = sol_nav["'Interfaz'!J139"].value[0, 0]
        st.session_state["resultados_nav"]["TGC"]     = sol_nav["'Interfaz'!J140"].value[0, 0]

if st.session_state["resultados_nav"]["DRL"] is not None:
    st.success("Cálculo de navegación completado")
    rn1, rn2, rn3 = st.columns(3)
    rn1.metric("D RL (Loxodrómica)",      f"{st.session_state['resultados_nav']['DRL']:.2f} nm")
    rn2.metric("T RL (días)",             f"{st.session_state['resultados_nav']['TRL']:.2f}")
    rn3.metric("Ganancia Loxo - Orto",    f"{st.session_state['resultados_nav']['Ganancia']:.2f} nm")
    rg1, rg2, _ = st.columns(3)
    rg1.metric("D GC (Ortodrómica)",      f"{st.session_state['resultados_nav']['DGC']:.2f} nm")
    rg2.metric("T GC (días)",             f"{st.session_state['resultados_nav']['TGC']:.2f}")

# =========================================================
# SECCIÓN 11: CONDICIÓN ACT (RESULTADOS GLOBALES)
# =========================================================
st.markdown("---")
st.header("11. Condición ACT (Dashboard de Resultados)")

if st.button("🚀 CALCULAR CONDICIÓN ACTUAL (ACT)", type="primary", use_container_width=True):
    with st.spinner("Compilando matriz de estabilidad y calculando parámetros globales..."):
        sol_global = modelo.calculate(inputs=entradas_usuario)
        st.success("✅ Diagnóstico de Estabilidad ACT Completado.")

        # Extraer valores para evitar conflicto de comillas en f-strings
        d_act      = sol_global["'Interfaz'!F115"].value[0, 0]
        vcg_act    = sol_global["'Interfaz'!F116"].value[0, 0]
        mv_act     = sol_global["'Interfaz'!F117"].value[0, 0]
        lcg_act    = sol_global["'Interfaz'!F118"].value[0, 0]
        ml_act     = sol_global["'Interfaz'!F119"].value[0, 0]
        tcg_act    = sol_global["'Interfaz'!F120"].value[0, 0]
        mt_act     = sol_global["'Interfaz'!F121"].value[0, 0]
        trim_act   = sol_global["'Interfaz'!F122"].value[0, 0]
        heel_act   = sol_global["'Interfaz'!F123"].value[0, 0]
        fs_act     = sol_global["'Interfaz'!I115"].value[0, 0]
        cmpr_act   = sol_global["'Interfaz'!I117"].value[0, 0]
        cmm_act    = sol_global["'Interfaz'!I118"].value[0, 0]
        cmpp_act   = sol_global["'Interfaz'!I119"].value[0, 0]
        cpr_act    = sol_global["'Interfaz'!I121"].value[0, 0]
        cm_act     = sol_global["'Interfaz'!I122"].value[0, 0]
        cpp_act    = sol_global["'Interfaz'!I123"].value[0, 0]
        gz30_act   = sol_global["'Interfaz'!L117"].value[0, 0]
        a030_act   = sol_global["'Interfaz'!L118"].value[0, 0]
        a040_act   = sol_global["'Interfaz'!L119"].value[0, 0]
        a3040_act  = sol_global["'Interfaz'!L120"].value[0, 0]
        gm_act     = sol_global["'Interfaz'!L121"].value[0, 0]

        st.markdown("### 📊 Datos Principales y Momentos")
        c1, c2, c3 = st.columns(3)
        c1.metric("Desplazamiento ACT (F115)",   f"{d_act:.2f} Tm")
        c2.metric("VCG (F116)",                  f"{vcg_act:.3f} m")
        c3.metric("Momento Vertical (F117)",     f"{mv_act:.2f} Tm·m")
        c1.metric("LCG (F118)",                  f"{lcg_act:.3f} m")
        c2.metric("Momento Longitudinal (F119)", f"{ml_act:.2f} Tm·m")
        c3.metric("TCG (F120)",                  f"{tcg_act:.3f} m")
        c1.metric("Momento Transversal (F121)",  f"{mt_act:.2f} Tm·m")
        c2.metric("Asiento Final / Trim (F122)", f"{trim_act:.3f} m")
        c3.metric("Escora Final / Heel (F123)",  f"{heel_act:.2f} °")
        st.divider()

        st.markdown("### ⚓ Calados y Superficies Libres")
        st.metric("Ángulo Escora por FS Φactsl (I115)", f"{fs_act:.2f} °")
        cm1, cm2, cm3 = st.columns(3)
        cm1.metric("CMpr (I117)", f"{cmpr_act:.3f}")
        cm2.metric("CMm (I118)",  f"{cmm_act:.3f}")
        cm3.metric("CMpp (I119)", f"{cmpp_act:.3f}")
        cp1, cp2, cp3 = st.columns(3)
        cp1.metric("Cpr (I121)", f"{cpr_act:.3f}")
        cp2.metric("Cm (I122)",  f"{cm_act:.3f}")
        cp3.metric("Cpp (I123)", f"{cpp_act:.3f}")
        st.divider()

        st.markdown("### 📈 Criterios de Estabilidad Intacta (Curva GZ)")
        gz1, gz2, gz3 = st.columns(3)
        gz1.metric("GZ 30 (L117)",        f"{gz30_act:.3f} m")
        gz2.metric("Área 0°-30° (L118)",  f"{a030_act:.3f} m·rad")
        gz3.metric("Área 0°-40° (L119)",  f"{a040_act:.3f} m·rad")
        gz1.metric("Área 30°-40° (L120)", f"{a3040_act:.3f} m·rad")
        gz2.metric("GM Fluido / Actual (L121)", f"{gm_act:.3f} m")

# =========================================================
# SECCIÓN 12: CONSUMOS DIARIOS
# =========================================================
st.markdown("---")
st.header("12. Consumos Diarios")
cd1, cd2, cd3, cd4, cd5, cd6 = st.columns(6)
entradas_usuario["'Interfaz'!E150"] = cd1.number_input("CMOxd HFO",    value=0.0, format="%.2f", key="cmo_hfo")
entradas_usuario["'Interfaz'!F150"] = cd2.number_input("CMOxd DO",     value=0.0, format="%.2f", key="cmo_do")
entradas_usuario["'Interfaz'!G150"] = cd3.number_input("CMOxd LO",     value=0.0, format="%.2f", key="cmo_lo")
entradas_usuario["'Interfaz'!H150"] = cd4.number_input("CMOxd Misc.O", value=0.0, format="%.2f", key="cmo_misco")
entradas_usuario["'Interfaz'!I150"] = cd5.number_input("CMOxd Misc.W", value=0.0, format="%.2f", key="cmo_miscw")
entradas_usuario["'Interfaz'!J150"] = cd6.number_input("CMOxd FW",     value=0.0, format="%.2f", key="cmo_fw")

# =========================================================
# SECCIÓN 13: D MÁXIMOS
# =========================================================
st.markdown("---")
st.header("13. D Máximos (Líneas de Carga)")
col_sal, col_cambio, col_lleg = st.columns(3)

zonas_carga    = ["TF", "F", "T", "S", "W"]
opciones_aplica = ["Aplica", "No Aplica"]

with col_sal:
    st.subheader("D Salida")
    entradas_usuario["'Interfaz'!G157"] = st.selectbox("D zona Sal", zonas_carga, key="d_zona_sal")
    c1, c2 = st.columns(2)
    c_max_sal  = c1.number_input("C max Sal", value=0.00, format="%.2f", key="c_max_sal")
    aplica_sal = c2.selectbox("Aplica/No", opciones_aplica, key="aplica_sal", label_visibility="collapsed")
    entradas_usuario["'Interfaz'!G158"] = aplica_sal
    if aplica_sal == "Aplica":
        entradas_usuario["'Interfaz'!F158"] = c_max_sal
    entradas_usuario["'Interfaz'!F159"] = st.number_input("d Salida", value=1.025, format="%.4f", key="d_salida_dens")

with col_cambio:
    st.subheader("Cambio a Zona de LLEG")
    c1, c2, c3 = st.columns(3)
    entradas_usuario["'Interfaz'!I158"] = c1.number_input("Grados",  value=0, step=1, key="gr_cambio",  label_visibility="collapsed")
    entradas_usuario["'Interfaz'!J158"] = c2.number_input("Minutos", value=0, step=1, key="min_cambio", label_visibility="collapsed")
    entradas_usuario["'Interfaz'!K158"] = c3.selectbox("N/S", ["N", "S"], key="ns_cambio", label_visibility="collapsed")
    entradas_usuario["'Interfaz'!J162"] = st.selectbox("Derrota Cambio", ["GC", "RL"], key="derrota_cambio")

with col_lleg:
    st.subheader("D LLEGADA")
    entradas_usuario["'Interfaz'!O157"] = st.selectbox("D zona Lleg", zonas_carga, key="d_zona_lleg")
    c1, c2 = st.columns(2)
    c_max_lleg  = c1.number_input("C max Lleg", value=0.00, format="%.2f", key="c_max_lleg")
    aplica_lleg = c2.selectbox("Aplica/No ", opciones_aplica, key="aplica_lleg", label_visibility="collapsed")
    entradas_usuario["'Interfaz'!O158"] = aplica_lleg
    if aplica_lleg == "Aplica":
        entradas_usuario["'Interfaz'!N158"] = c_max_lleg
    entradas_usuario["'Interfaz'!N159"] = st.number_input("d Llegada", value=1.025, format="%.4f", key="d_lleg_dens")

if st.button("⚖️ Calcular Calados Máximos", use_container_width=True):
    with st.spinner("Calculando..."):
        sol_dmax = modelo.calculate(inputs=entradas_usuario)
        st.session_state["resultados_dmax"]["S_Sal"]  = sol_dmax["'Interfaz'!F161"].value[0, 0]
        st.session_state["resultados_dmax"]["D_Lleg"] = sol_dmax["'Interfaz'!N161"].value[0, 0]

if st.session_state["resultados_dmax"]["S_Sal"] is not None:
    rm1, rm2 = st.columns(2)
    rm1.metric("S Sal",  f"{st.session_state['resultados_dmax']['S_Sal']:.3f} m")
    rm2.metric("D Lleg", f"{st.session_state['resultados_dmax']['D_Lleg']:.3f} m")

# =========================================================
# SECCIÓN 14: CARGA (SALIDA)
# =========================================================
st.markdown("---")
st.header("14. Carga (Condición de Salida)")

cols_h_carga = st.columns([1, 1, 1, 1.3, 1, 1, 1, 1, 1, 1, 1.2])
for i, h in enumerate(["Bodega", "ACT", "%ACT", "F/Slc", "D/V/%", "Und", "d/Fe", "Fe/d", "Und", "Und", "D Tm SAL"]):
    cols_h_carga[i].markdown(f"**{h}**")

ph_act_list, ph_pact_list, ph_sal_list = [], [], []

for i in range(5):
    fila = 173 + i
    cols = st.columns([1, 1, 1, 1.3, 1, 1, 1, 1, 1, 1, 1.2])
    cols[0].markdown(f"<div style='padding-top: 10px;'><b>B{i+1}</b></div>", unsafe_allow_html=True)

    ph_act_list.append(cols[1].empty())
    ph_pact_list.append(cols[2].empty())

    f_val = cols[3].selectbox(f"H{fila}", ["", "Full", "Slack", "Vacio"], key=f"H{fila}_carga", label_visibility="collapsed")
    i_val = cols[4].number_input(f"I{fila}", value=0.00, key=f"I{fila}_carga", label_visibility="collapsed")
    j_val = cols[5].selectbox(f"J{fila}", ["", "Tm", "LT", "ft3", "m3"], key=f"J{fila}_carga", label_visibility="collapsed")
    k_val = cols[6].selectbox(f"K{fila}", ["d", "Fe"], key=f"K{fila}_carga", label_visibility="collapsed")
    l_val = cols[7].number_input(f"L{fila}", value=0.00, key=f"L{fila}_carga", label_visibility="collapsed")
    m_val = cols[8].selectbox(f"M{fila}", ["Tm", "LT", "m3", "ft3"], key=f"M{fila}_carga", label_visibility="collapsed")
    n_val = cols[9].selectbox(f"N{fila}", ["Tm", "LT", "m3", "ft3"], key=f"N{fila}_carga", label_visibility="collapsed")
    ph_sal_list.append(cols[10].empty())

    if f_val != "":
        entradas_usuario[f"'Interfaz'!H{fila}"] = f_val
    entradas_usuario[f"'Interfaz'!I{fila}"] = i_val
    if j_val != "":
        entradas_usuario[f"'Interfaz'!J{fila}"] = j_val
    entradas_usuario[f"'Interfaz'!K{fila}"] = k_val
    entradas_usuario[f"'Interfaz'!L{fila}"] = l_val
    entradas_usuario[f"'Interfaz'!M{fila}"] = m_val
    entradas_usuario[f"'Interfaz'!N{fila}"] = n_val

    if st.session_state["resultados_carga"][fila]["ACT"] is not None:
        ph_act_list[i].markdown(f"{st.session_state['resultados_carga'][fila]['ACT']:.2f}")
        ph_pact_list[i].markdown(f"{st.session_state['resultados_carga'][fila]['%ACT']:.2f}%")
        ph_sal_list[i].success(f"{st.session_state['resultados_carga'][fila]['SAL']:.2f}")

if st.button("⚖️ Calcular Carga", use_container_width=True):
    with st.spinner("Calculando..."):
        sol_carga = modelo.calculate(inputs=entradas_usuario)
        for i in range(5):
            fila = 173 + i
            st.session_state["resultados_carga"][fila]["ACT"]  = sol_carga[f"'Interfaz'!F{fila}"].value[0, 0]
            st.session_state["resultados_carga"][fila]["%ACT"] = sol_carga[f"'Interfaz'!G{fila}"].value[0, 0]
            st.session_state["resultados_carga"][fila]["SAL"]  = sol_carga[f"'Interfaz'!O{fila}"].value[0, 0]
            ph_act_list[i].markdown(f"{st.session_state['resultados_carga'][fila]['ACT']:.2f}")
            ph_pact_list[i].markdown(f"{st.session_state['resultados_carga'][fila]['%ACT']:.2f}%")
            ph_sal_list[i].success(f"{st.session_state['resultados_carga'][fila]['SAL']:.2f}")

# =========================================================
# SECCIÓN 15: DISTRIBUCIÓN CONSUMOS
# =========================================================
st.markdown("---")
st.header("15. Distribución Consumos")

col_hfo, col_do = st.columns(2)

with col_hfo:
    st.subheader("Heavy Fuel Oil")
    op_hfo = ["", "Deep P 1", "Deep S 1", "Deep P 2", "Deep S 2", "Service Tk 1", "Service Tk 2", "Settling Tk 1", "Settling Tk 2", "Overflow Tk"]
    c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
    c1.markdown("**Tanque (E)**"); c2.markdown("**dmax (F)**"); c3.markdown("**dRest (G)**"); c4.markdown("**Acción**")

    for i in range(9):
        fila = 255 + i
        cx = st.columns([2, 1.5, 1.5, 1.5])
        t_hfo = cx[0].selectbox(f"E{fila}", op_hfo, key=f"E{fila}_dist", label_visibility="collapsed")
        d_hfo = cx[1].number_input(f"F{fila}", value=None, format="%.2f", key=f"F{fila}_dist", label_visibility="collapsed")
        ph_dr = cx[2].empty()

        if t_hfo != "":
            entradas_usuario[f"'Interfaz'!E{fila}"] = t_hfo
            if d_hfo is not None:
                entradas_usuario[f"'Interfaz'!F{fila}"] = d_hfo

        with cx[3]:
            if st.button("Calc.", key=f"btn_hfo_{fila}"):
                if t_hfo != "" and d_hfo is not None:
                    sol_dist = modelo.calculate(inputs=entradas_usuario)
                    st.session_state["resultados_dist_consumos"][fila]["dRest_HFO"] = sol_dist[f"'Interfaz'!G{fila}"].value[0, 0]
        if st.session_state["resultados_dist_consumos"][fila]["dRest_HFO"] is not None:
            ph_dr.success(f"{st.session_state['resultados_dist_consumos'][fila]['dRest_HFO']:.2f}")

with col_do:
    st.subheader("Diesel Oil")
    op_do = ["", "Deep S", "Service 1", "Service 2", "Settling"]
    d1, d2, d3, d4 = st.columns([2, 1.5, 1.5, 1.5])
    d1.markdown("**Tanque (I)**"); d2.markdown("**dmax (J)**"); d3.markdown("**dRest (K)**"); d4.markdown("**Acción**")

    for i in range(4):
        fila = 255 + i
        dx = st.columns([2, 1.5, 1.5, 1.5])
        t_do = dx[0].selectbox(f"I{fila}", op_do, key=f"I{fila}_dist", label_visibility="collapsed")
        d_do = dx[1].number_input(f"J{fila}", value=None, format="%.2f", key=f"J{fila}_dist", label_visibility="collapsed")
        ph_dd = dx[2].empty()

        if t_do != "":
            entradas_usuario[f"'Interfaz'!I{fila}"] = t_do
            if d_do is not None:
                entradas_usuario[f"'Interfaz'!J{fila}"] = d_do

        with dx[3]:
            if st.button("Calc.", key=f"btn_do_{fila}"):
                if t_do != "" and d_do is not None:
                    sol_dist = modelo.calculate(inputs=entradas_usuario)
                    st.session_state["resultados_dist_consumos"][fila]["dRest_DO"] = sol_dist[f"'Interfaz'!K{fila}"].value[0, 0]
        if st.session_state["resultados_dist_consumos"][fila]["dRest_DO"] is not None:
            ph_dd.success(f"{st.session_state['resultados_dist_consumos'][fila]['dRest_DO']:.2f}")

# =========================================================
# SECCIÓN 16: REPARTO
# =========================================================
st.markdown("---")
st.header("16. Reparto y Asiento Deseado")
col_rep1, col_rep2 = st.columns([1.5, 1])

with col_rep1:
    st.subheader("Reparto entre Bodegas")
    opciones_bodegas = ["", "B1", "B2", "B3", "B4", "B5"]
    cr = st.columns([1, 1.5, 1.5, 1, 1])
    cr[0].markdown("**Bodega**"); cr[1].markdown("**A Repartir en: (G)**"); cr[2].markdown("**Fe (H)**"); cr[3].markdown("**Und 1 (I)**"); cr[4].markdown("**Und 2 (J)**")

    for i in range(5):
        fila = 281 + i
        cols = st.columns([1, 1.5, 1.5, 1, 1])
        cols[0].markdown(f"<div style='padding-top: 10px;'><b>B{i+1}</b></div>", unsafe_allow_html=True)

        rep_bod = cols[1].selectbox(f"G{fila}", opciones_bodegas, key=f"G{fila}_rep", label_visibility="collapsed")
        if rep_bod != "":
            entradas_usuario[f"'Interfaz'!G{fila}"] = rep_bod

        entradas_usuario[f"'Interfaz'!H{fila}"] = cols[2].number_input(f"H{fila}", value=0.00, key=f"H{fila}_rep", label_visibility="collapsed")
        entradas_usuario[f"'Interfaz'!I{fila}"] = cols[3].selectbox(f"I{fila}", ["Tm", "LT", "m3", "ft3"], key=f"I{fila}_rep", label_visibility="collapsed")
        entradas_usuario[f"'Interfaz'!J{fila}"] = cols[4].selectbox(f"J{fila}", ["Tm", "LT", "m3", "ft3"], key=f"J{fila}_rep", label_visibility="collapsed")

with col_rep2:
    st.subheader("Asiento Deseado")
    tipo_asiento = st.selectbox("Parámetro (E293)", ["", "CMpr =", "CMm =", "CMpp =", "A =", "a ="], key="e293_rep")
    if tipo_asiento != "":
        entradas_usuario["'Interfaz'!E293"] = tipo_asiento

    valor_asiento = st.number_input("Valor (F293)", value=None, format="%.3f", key="f293_rep")
    if valor_asiento is not None:
        entradas_usuario["'Interfaz'!F293"] = valor_asiento

    entradas_usuario["'Interfaz'!G293"] = st.selectbox("Condición (G293)", ["Apopante", "Aproante", "Aguas Iguales"], key="g293_rep")

if st.button("🔄 Registrar Reparto", use_container_width=True):
    with st.spinner("Sincronizando reparto..."):
        modelo.calculate(inputs=entradas_usuario)
        st.success("Reparto registrado.")

# =========================================================
# SECCIÓN 17: CONDICIÓN SAL (RESULTADOS SALIDA)
# =========================================================
st.markdown("---")
st.header("17. Condición SAL (Dashboard de Salida)")

if st.button("🚢 CALCULAR CONDICIÓN SALIDA", type="primary", use_container_width=True):
    with st.spinner("Calculando parámetros de salida..."):
        sol_sal = modelo.calculate(inputs=entradas_usuario)
        st.success("✅ Diagnóstico de Salida Completado.")

        # Extraer valores para evitar conflicto de comillas en f-strings
        d_sal      = sol_sal["'Interfaz'!F298"].value[0, 0]
        vcg_sal    = sol_sal["'Interfaz'!F299"].value[0, 0]
        mv_sal     = sol_sal["'Interfaz'!F300"].value[0, 0]
        lcg_sal    = sol_sal["'Interfaz'!F301"].value[0, 0]
        ml_sal     = sol_sal["'Interfaz'!F302"].value[0, 0]
        tcg_sal    = sol_sal["'Interfaz'!F303"].value[0, 0]
        mt_sal     = sol_sal["'Interfaz'!F304"].value[0, 0]
        trim_sal   = sol_sal["'Interfaz'!F305"].value[0, 0]
        heel_sal   = sol_sal["'Interfaz'!F306"].value[0, 0]
        fs_sal     = sol_sal["'Interfaz'!I298"].value[0, 0]
        cmpr_sal   = sol_sal["'Interfaz'!I300"].value[0, 0]
        cmm_sal    = sol_sal["'Interfaz'!I301"].value[0, 0]
        cmpp_sal   = sol_sal["'Interfaz'!I302"].value[0, 0]
        cpr_sal    = sol_sal["'Interfaz'!I304"].value[0, 0]
        cm_sal     = sol_sal["'Interfaz'!I305"].value[0, 0]
        cpp_sal    = sol_sal["'Interfaz'!I306"].value[0, 0]
        gz30_sal   = sol_sal["'Interfaz'!L300"].value[0, 0]
        a030_sal   = sol_sal["'Interfaz'!L301"].value[0, 0]
        a040_sal   = sol_sal["'Interfaz'!L302"].value[0, 0]
        a3040_sal  = sol_sal["'Interfaz'!L303"].value[0, 0]
        gm_sal     = sol_sal["'Interfaz'!L304"].value[0, 0]

        st.markdown("### 📊 Datos Principales y Momentos")
        c1, c2, c3 = st.columns(3)
        c1.metric("Desplazamiento SAL (F298)",   f"{d_sal:.2f} Tm")
        c2.metric("VCG (F299)",                  f"{vcg_sal:.3f} m")
        c3.metric("Momento Vertical (F300)",     f"{mv_sal:.2f} Tm·m")
        c1.metric("LCG (F301)",                  f"{lcg_sal:.3f} m")
        c2.metric("Momento Longitudinal (F302)", f"{ml_sal:.2f} Tm·m")
        c3.metric("TCG (F303)",                  f"{tcg_sal:.3f} m")
        c1.metric("Momento Transversal (F304)",  f"{mt_sal:.2f} Tm·m")
        c2.metric("Asiento Final / Trim (F305)", f"{trim_sal:.3f} m")
        c3.metric("Escora Final / Heel (F306)",  f"{heel_sal:.2f} °")
        st.divider()

        st.markdown("### ⚓ Calados y Superficies Libres")
        st.metric("Ángulo Escora por FS Φsalsl (I298)", f"{fs_sal:.2f} °")
        cm1, cm2, cm3 = st.columns(3)
        cm1.metric("CMpr (I300)", f"{cmpr_sal:.3f}")
        cm2.metric("CMm (I301)",  f"{cmm_sal:.3f}")
        cm3.metric("CMpp (I302)", f"{cmpp_sal:.3f}")
        cp1, cp2, cp3 = st.columns(3)
        cp1.metric("Cpr (I304)", f"{cpr_sal:.3f}")
        cp2.metric("Cm (I305)",  f"{cm_sal:.3f}")
        cp3.metric("Cpp (I306)", f"{cpp_sal:.3f}")
        st.divider()

        st.markdown("### 📈 Criterios de Estabilidad Intacta (Curva GZ)")
        gz1, gz2, gz3 = st.columns(3)
        gz1.metric("GZ 30 (L300)",        f"{gz30_sal:.3f} m")
        gz2.metric("Área 0°-30° (L301)",  f"{a030_sal:.3f} m·rad")
        gz3.metric("Área 0°-40° (L302)",  f"{a040_sal:.3f} m·rad")
        gz1.metric("Área 30°-40° (L303)", f"{a3040_sal:.3f} m·rad")
        gz2.metric("GM Fluido / Actual (L304)", f"{gm_sal:.3f} m")

# =========================================================
# SECCIÓN 18: CONDICIÓN LLEG (RESULTADOS LLEGADA)
# =========================================================
st.markdown("---")
st.header("18. Condición LLEG (Dashboard de Llegada)")

if st.button("🏁 CALCULAR CONDICIÓN LLEGADA", type="primary", use_container_width=True):
    with st.spinner("Calculando parámetros de llegada..."):
        sol_lleg = modelo.calculate(inputs=entradas_usuario)
        st.success("✅ Diagnóstico de Llegada Completado.")

        # Extraer valores para evitar conflicto de comillas en f-strings
        d_lleg     = sol_lleg["'Interfaz'!F312"].value[0, 0]
        vcg_lleg   = sol_lleg["'Interfaz'!F313"].value[0, 0]
        mv_lleg    = sol_lleg["'Interfaz'!F314"].value[0, 0]
        lcg_lleg   = sol_lleg["'Interfaz'!F315"].value[0, 0]
        ml_lleg    = sol_lleg["'Interfaz'!F316"].value[0, 0]
        tcg_lleg   = sol_lleg["'Interfaz'!F317"].value[0, 0]
        mt_lleg    = sol_lleg["'Interfaz'!F318"].value[0, 0]
        trim_lleg  = sol_lleg["'Interfaz'!F319"].value[0, 0]
        heel_lleg  = sol_lleg["'Interfaz'!F320"].value[0, 0]
        fs_lleg    = sol_lleg["'Interfaz'!I312"].value[0, 0]
        cmpr_lleg  = sol_lleg["'Interfaz'!I314"].value[0, 0]
        cmm_lleg   = sol_lleg["'Interfaz'!I315"].value[0, 0]
        cmpp_lleg  = sol_lleg["'Interfaz'!I316"].value[0, 0]
        cpr_lleg   = sol_lleg["'Interfaz'!I318"].value[0, 0]
        cm_lleg    = sol_lleg["'Interfaz'!I319"].value[0, 0]
        cpp_lleg   = sol_lleg["'Interfaz'!I320"].value[0, 0]
        gz30_lleg  = sol_lleg["'Interfaz'!L314"].value[0, 0]
        a030_lleg  = sol_lleg["'Interfaz'!L315"].value[0, 0]
        a040_lleg  = sol_lleg["'Interfaz'!L316"].value[0, 0]
        a3040_lleg = sol_lleg["'Interfaz'!L317"].value[0, 0]
        gm_lleg    = sol_lleg["'Interfaz'!L318"].value[0, 0]

        st.markdown("### 📊 Datos Principales y Momentos")
        c1, c2, c3 = st.columns(3)
        c1.metric("Desplazamiento LLEG (F312)",  f"{d_lleg:.2f} Tm")
        c2.metric("VCG (F313)",                  f"{vcg_lleg:.3f} m")
        c3.metric("Momento Vertical (F314)",     f"{mv_lleg:.2f} Tm·m")
        c1.metric("LCG (F315)",                  f"{lcg_lleg:.3f} m")
        c2.metric("Momento Longitudinal (F316)", f"{ml_lleg:.2f} Tm·m")
        c3.metric("TCG (F317)",                  f"{tcg_lleg:.3f} m")
        c1.metric("Momento Transversal (F318)",  f"{mt_lleg:.2f} Tm·m")
        c2.metric("Asiento Final / Trim (F319)", f"{trim_lleg:.3f} m")
        c3.metric("Escora Final / Heel (F320)",  f"{heel_lleg:.2f} °")
        st.divider()

        st.markdown("### ⚓ Calados y Superficies Libres")
        st.metric("Ángulo Escora por FS Φllegsl (I312)", f"{fs_lleg:.2f} °")
        cm1, cm2, cm3 = st.columns(3)
        cm1.metric("CMpr (I314)", f"{cmpr_lleg:.3f}")
        cm2.metric("CMm (I315)",  f"{cmm_lleg:.3f}")
        cm3.metric("CMpp (I316)", f"{cmpp_lleg:.3f}")
        cp1, cp2, cp3 = st.columns(3)
        cp1.metric("Cpr (I318)", f"{cpr_lleg:.3f}")
        cp2.metric("Cm (I319)",  f"{cm_lleg:.3f}")
        cp3.metric("Cpp (I320)", f"{cpp_lleg:.3f}")
        st.divider()

        st.markdown("### 📈 Criterios de Estabilidad Intacta (Curva GZ)")
        gz1, gz2, gz3 = st.columns(3)
        gz1.metric("GZ 30 (L314)",        f"{gz30_lleg:.3f} m")
        gz2.metric("Área 0°-30° (L315)",  f"{a030_lleg:.3f} m·rad")
        gz3.metric("Área 0°-40° (L316)",  f"{a040_lleg:.3f} m·rad")
        gz1.metric("Área 30°-40° (L317)", f"{a3040_lleg:.3f} m·rad")
        gz2.metric("GM Fluido / Actual (L318)", f"{gm_lleg:.3f} m")

st.markdown("---")
st.markdown("<div style='text-align: center; color: grey;'>Desarrollado para el TFG: Modelado y Resolución de Situaciones Críticas - B/C Cormorán</div>", unsafe_allow_html=True)
