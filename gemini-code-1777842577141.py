import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

class NTC2018Engine:
    def __init__(self, vb0=27.0, qsk=1.5):
        self.vb0 = vb0
        self.qsk = qsk
        self.rho = 1.25
        self.nu = 1.5e-5 

    def get_ce(self, z, cat):
        params = {
            'A': [0.16, 0.01, 2], 'B': [0.19, 0.05, 4], 
            'C': [0.20, 0.10, 5], 'D': [0.22, 0.30, 8], 'E': [0.23, 0.70, 12]
        }
        kr, z0, zmin = params.get(cat, params['B'])
        ze = max(z, zmin)
        return (kr**2) * 1.0 * math.log(ze/z0) * (7 + math.log(ze/z0))

    def calcola_neve(self, pend):
        if 0 <= pend <= 30:
            return 0.8 * self.qsk
        elif 30 < pend < 60:
            return 0.8 * ((60 - pend) / 30) * self.qsk
        else:
            return 0.0

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="NTC 2018 Pro", layout="wide")
st.title("🏛️ Progettazione Strutturale NTC 2018")

# Sidebar - Input
st.sidebar.header("1. Localizzazione e Sito")
cat_esp = st.sidebar.selectbox("Categoria Esposizione", ['A', 'B', 'C', 'D', 'E'], index=1)
vb0_input = st.sidebar.number_input("Velocità base vb0 [m/s]", value=27.0)
qsk_input = st.sidebar.number_input("Carico Neve suolo qsk [kN/m²]", value=1.5)

st.sidebar.header("2. Geometria Edificio")
tipo_edificio = st.sidebar.selectbox(
    "Tipologia Costruttiva", 
    ["Rettangolare Chiuso", "Cilindrico (Silo/Camino)", "Tettoia Isolata"]
)
h_tot = st.sidebar.slider("Altezza Struttura (z) [m]", 2, 100, 15)

# Inizializzazione Motore
engine = NTC2018Engine(vb0=vb0_input, qsk=qsk_input)
qb = 0.5 * engine.rho * (vb0_input**2) / 1000
ce_z = engine.get_ce(h_tot, cat_esp)

# Logica Geometria e Vento
if tipo_edificio == "Rettangolare Chiuso":
    cp = 0.8
    desc_vento = "Pressione esterna su parete sopravento (Zona D)."
elif tipo_edificio == "Cilindrico (Silo/Camino)":
    diam = st.sidebar.number_input("Diametro Cilindro [m]", value=5.0)
    vz = vb0_input * math.sqrt(ce_z)
    re = (diam * vz) / engine.nu
    cp = 0.7 if re > 1e6 else 1.2 
    desc_vento = f"Coefficiente di forza basato su Reynolds (Re = {re:.1e})."
else:
    phi = st.sidebar.slider("Grado di ostruzione (phi)", 0.0, 1.0, 0.5)
    cp = 1.2 + 0.3 * phi
    desc_vento = "Coefficiente di pressione netta per tettoia."

# --- VISUALIZZAZIONE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌬️ Azione del Vento")
    p_vento = qb * ce_z * cp
    st.metric("Pressione Progetto p_e", f"{p_vento:.3f} kN/m²")
    st.info(desc_vento)

with col2:
    st.subheader("❄️ Azione della Neve")
    alpha = st.number_input("Pendenza falda [°]", 0, 90, 0)
    qs = engine.calcola_neve(alpha)
    st.metric("Carico Neve q_s", f"{qs:.3f} kN/m²")
    st.info("Calcolo coefficiente mu1 basato sulla pendenza.")

# Grafico Profilo
st.divider()
z_range = np.linspace(0, h_tot + 5, 100)
p_range = [qb * engine.get_ce(z, cat_esp) * cp for z in z_range]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(p_range, z_range, color='green', lw=2)
ax.fill_betweenx(z_range, p_range, color='green', alpha=0.1)
ax.axhline(y=h_tot, color='red', linestyle='--')
ax.set_xlabel("Pressione [kN/m²]")
ax.set_ylabel("Altezza z [m]")
st.pyplot(fig)