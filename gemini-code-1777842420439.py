import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

class NTC2018Engine:
    def __init__(self, vb0=27, qsk=1.5):
        self.vb0 = vb0
        self.qsk = qsk
        self.rho = 1.25
        self.nu = 1.5e-5 # Viscosità aria per Reynolds

    def get_ce(self, z, cat):
        params = {
            'A': [0.16, 0.01, 2], 'B': [0.19, 0.05, 4], 
            'C': [0.20, 0.10, 5], 'D': [0.22, 0.30, 8], 'E': [0.23, 0.70, 12]
        }
        kr, z0, zmin = params[cat]
        ze = max(z, zmin)
        return (kr**2) * 1.0 * math.log(ze/z0) * (7 + math.log(ze/z0))

    def calcola_neve_copertura(self, pend=0):
        if 0 <= pend <= 30: mu = 0.8[cite: 1]
        elif 30 < pend < 60: mu = 0.8 * (60 - pend) / 30[cite: 1]
        else: mu = 0.0[cite: 1]
        return self.qsk * mu

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="NTC 2018 Pro", layout="wide")
st.title("🏛️ Progettazione Strutturale NTC 2018")

# Sidebar - Parametri Generali
st.sidebar.header("1. Localizzazione e Sito")
cat_esp = st.sidebar.selectbox("Categoria Esposizione", ['A', 'B', 'C', 'D', 'E'], index=1)
vb0 = st.sidebar.number_input("Velocità base vb0 [m/s]", value=27.0)
qsk = st.sidebar.number_input("Carico Neve suolo qsk [kN/m²]", value=1.5)

st.sidebar.header("2. Geometria Edificio")
tipo_edificio = st.sidebar.selectbox(
    "Tipologia Costruttiva (Rif. Circolare 2019)", 
    ["Rettangolare Chiuso", "Cilindrico (Silo/Camino)", "Tettoia Isolata"]
)

h_tot = st.sidebar.slider("Altezza Struttura (z) [m]", 2, 100, 15)

# Inizializzazione Motore
engine = NTC2018Engine(vb0=vb0, qsk=qsk)
qb = 0.5 * engine.rho * (vb0**2) / 1000
ce_z = engine.get_ce(h_tot, cat_esp)

# --- LOGICA GEOMETRIA ---
cp = 1.0 # Default
info_geo = ""

if tipo_edificio == "Rettangolare Chiuso":
    cp = 0.8 # Valore per parete sopravento (Zona D)
    info_geo = "Coefficiente di pressione esterno $c_{p,e}$ per parete sopravento (Cap. C3.3.10.1)."

elif tipo_edificio == "Cilindrico (Silo/Camino)":
    diam = st.sidebar.number_input("Diametro Cilindro [m]", value=5.0)
    vz = vb0 * math.sqrt(ce_z)
    re = (diam * vz) / engine.nu
    # Approssimazione curva Circolare C3.3.14
    cp = 0.7 if re > 1e6 else 1.2 
    info_geo = f"Calcolo basato su Numero di Reynolds: $Re = {re:.1e}$. Coefficiente di forza $c_f$ (Cap. C3.3.10.10)."

elif tipo_edificio == "Tettoia Isolata":
    phi = st.sidebar.slider("Grado di ostruzione (φ)", 0.0, 1.0, 0.5)
    cp = 1.2 + 0.3 * phi # Valore massimo cp,net
    info_geo = "Coefficiente di pressione netta $c_{p,net}$ per tettoia a falda singola (Cap. C3.3.10.4)."

# --- VISUALIZZAZIONE RISULTATI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌬️ Analisi del Vento")
    p_vento = qb * ce_z * cp
    st.metric("Pressione Progetto $p_e$", f"{p_vento:.3f} kN/m²")
    st.write(info_geo)

with col2:
    st.subheader("❄️ Analisi della Neve")
    alpha = st.number_input("Pendenza falda [°]", 0, 90, 0)
    qs = engine.calcola_neve_copertura(pend=alpha)
    st.metric("Carico Neve $q_s$", f"{qs:.3f} kN/m²")
    st.write("Coefficiente di forma $\mu_1$ calcolato secondo Par. 3.4.3.")

# Grafico Profilo
st.divider()
z_range = np.linspace(0, h_tot + 5, 100)
p_range = [qb * engine.get_ce(z, cat_esp) * cp for z in z_range]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(p_range, z_range, color='green', lw=2, label=f"Profilo Vento - {tipo_edificio}")
ax.fill_betweenx(z_range, p_range, color='green', alpha=0.1)
ax.axhline(y=h_tot, color='red', linestyle='--', label="Quota di calcolo")
ax.set_xlabel("Pressione [kN/m²]")
ax.set_ylabel("Altezza z [m]")
ax.legend()
st.pyplot(fig)