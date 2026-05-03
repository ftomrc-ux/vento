import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class NTC_Calcolatore_Avanzato:
    def __init__(self, vb0=25, qsk_base=1.0):
        self.rho = 1.25
        self.vb0 = vb0
        self.qsk = qsk_base

    def get_ce(self, z, cat):
        """Rif. Tabella 3.3.II - Parametri rugosità"""
        params = {
            'A': [0.16, 0.01, 2], 'B': [0.19, 0.05, 4], 
            'C': [0.20, 0.10, 5], 'D': [0.22, 0.30, 8], 'E': [0.23, 0.70, 12]
        }
        kr, z0, zmin = params[cat]
        ze = max(z, zmin)
        return (kr**2) * math.log(ze/z0) * (7 + math.log(ze/z0))

    def calcola_neve_copertura(self, pend=0):
        """Cap. 3.4.3 - Carico Neve[cite: 1]"""
        # Determinazione coefficiente di forma mu1 (Tab. 3.4.I)[cite: 1]
        if 0 <= pend <= 30:
            mu = 0.8
        elif 30 < pend < 60:
            mu = 0.8 * (60 - pend) / 30
        else:
            mu = 0.0
        return self.qsk * mu

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="NTC 2018 Structural Tool", layout="wide")
st.title("🛡️ calcNTC: Strumento per Carichi Ambientali")
st.markdown("Calcolo del Vento e della Neve secondo le **NTC 2018** e **Circolare 2019**.")

st.sidebar.header("Parametri Sito")
zona_v = st.sidebar.selectbox("Zona Vento (NTC Tab. 3.3.I)", options=[1, 2, 3, 4, 5, 6, 7, 8, 9], index=2)
cat_esp = st.sidebar.selectbox("Categoria Esposizione", options=['A', 'B', 'C', 'D', 'E'], index=1)
h_edificio = st.sidebar.slider("Altezza Edificio (m)", 2, 100, 15)
pendenza = st.sidebar.number_input("Pendenza Tetto (gradi)", min_value=0, max_value=90, value=0)

# Inizializzazione calcolatore
calc = NTC_Calcolatore_Avanzato()

# Sezione Risultati
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Analisi Vento")
    ce = calc.get_ce(h_edificio, cat_esp)
    qb = 0.5 * 1.25 * (27**2) / 1000 # Esempio basato su vb=27m/s
    cp = 0.8 # Coefficiente sopravento standard
    pressione = qb * ce * cp
    
    st.metric("Pressione di Picco (p_e)", f"{pressione:.3f} kN/m²")
    st.write(f"**Velocità alla quota z:** {27 * math.sqrt(ce):.2f} m/s")

with col2:
    st.subheader("❄️ Analisi Neve")
    qs = calc.calcola_neve_copertura(pend=pendenza)
    st.metric("Carico Neve (q_s)", f"{qs:.3f} kN/m²")
    st.write(f"**Coefficiente di forma μ:** {qs/calc.qsk:.2f}")

# Grafico Profilo Vento
st.divider()
st.subheader("📈 Profilo di Pressione del Vento")
z_range = np.linspace(0, h_edificio + 5, 100)
p_range = [qb * calc.get_ce(z, cat_esp) * cp for z in z_range]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(p_range, z_range, color='#1E88E5', linewidth=2)
ax.fill_betweenx(z_range, p_range, alpha=0.2, color='#1E88E5')
ax.set_xlabel("Pressione [kN/m²]")
ax.set_ylabel("Altezza z [m]")
ax.grid(True, linestyle=':', alpha=0.6)
st.pyplot(fig)