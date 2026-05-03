import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Inserisci qui la classe NTC_Calcolatore_Avanzato definita prima
class NTC_Calcolatore_Avanzato:
    # ... (stessa logica del messaggio precedente) ...
    def __init__(self, vb0=25, qsk_base=1.0):
        self.rho = 1.25
        self.vb0 = vb0
        self.qsk = qsk_base

    def get_ce(self, z, cat):
        params = {
            'A': [0.16, 0.01, 2], 'B': [0.19, 0.05, 4], 
            'C': [0.20, 0.10, 5], 'D': [0.22, 0.30, 8], 'E': [0.23, 0.70, 12]
        }
        kr, z0, zmin = params[cat]
        ze = max(z, zmin)
        return (kr**2) * math.log(ze/z0) * (7 + math.log(ze/z0))

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="NTC 2018 Structural Tool", layout="wide")
st.title("calcNTC: Calcolo Carichi Ambientali (NTC 2018)")
st.sidebar.header("Parametri Sito e Progetto")

# Input Sidebar
altitudine = st.sidebar.number_input("Altitudine (m s.l.m.)", value=100)
zona_v = st.sidebar.selectbox("Zona Vento", options=[1, 2, 3, 4, 5, 6, 7, 8, 9], index=2)
cat_esp = st.sidebar.selectbox("Categoria Esposizione", options=['A', 'B', 'C', 'D', 'E'], index=1)
h_edificio = st.sidebar.slider("Altezza Edificio (m)", 2, 100, 15)

calc = NTC_Calcolatore_Avanzato()

# Layout a colonne
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Risultati Vento")
    ce = calc.get_ce(h_edificio, cat_esp)
    qb = 0.5 * 1.25 * (27**2) / 1000 # Esempio basato su NTC 2018
    pressione = qb * ce * 0.8
    
    st.metric("Pressione di Picco (Sopravento)", f"{pressione:.3f} kN/m²")
    st.info(f"Coefficiente di esposizione ce(z): {ce:.3f}")

with col2:
    st.subheader("❄️ Risultati Neve")
    qs = calc.calcola_neve_copertura(pend=15) # Rif. Cap. 3.4.3[cite: 1]
    st.metric("Carico Neve Copertura", f"{qs:.3f} kN/m²")
    st.write("Coefficiente di forma $\mu_1 = 0.8$ (Tetto piano/poco pendente)[cite: 1]")

# Grafico del profilo di pressione
st.divider()
st.subheader("Profilo di Pressione lungo l'altezza")
z_vals = np.linspace(0, h_edificio + 10, 50)
p_vals = [qb * calc.get_ce(z, cat_esp) * 0.8 for z in z_vals]

fig, ax = plt.subplots()
ax.plot(p_vals, z_vals, color='red', lw=2)
ax.set_xlabel("Pressione p [kN/m²]")
ax.set_ylabel("Altezza z [m]")
ax.grid(True, linestyle='--')
st.pyplot(fig)