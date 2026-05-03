import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

class NTC2018Engine:
    def __init__(self, vb0=27, qsk=1.5):
        self.vb0 = vb0
        self.qsk = qsk
        self.rho = 1.25

    def get_ce(self, z, cat):
        """Calcola il coefficiente di esposizione ce(z) - NTC 2018 Tab. 3.3.II"""
        params = {
            'A': [0.16, 0.01, 2], 'B': [0.19, 0.05, 4], 
            'C': [0.20, 0.10, 5], 'D': [0.22, 0.30, 8], 'E': [0.23, 0.70, 12]
        }
        kr, z0, zmin = params[cat]
        ze = max(z, zmin)
        return (kr**2) * 1.0 * math.log(ze/z0) * (7 + math.log(ze/z0))

    def calcola_neve_copertura(self, pend=0):
        """Calcola il carico neve qs - NTC 2018 Cap. 3.4.3"""
        # Coefficiente di forma mu1 (Tab. 3.4.I)
        if 0 <= pend <= 30:
            mu = 0.8
        elif 30 < pend < 60:
            mu = 0.8 * (60 - pend) / 30
        else:
            mu = 0.0
        return self.qsk * mu

# --- CONFIGURAZIONE INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="NTC 2018 Calc", layout="wide")

st.title("🛡️ Calcolatore Carichi NTC 2018")
st.markdown("Verifica dei carichi da vento e neve secondo **NTC 2018** e **Circolare 2019**.")

# --- SIDEBAR INPUT ---
st.sidebar.header("Parametri di Progetto")
zona_v = st.sidebar.selectbox("Zona Vento", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=2)
cat_esp = st.sidebar.selectbox("Categoria Esposizione", ['A', 'B', 'C', 'D', 'E'], index=1)
h_tot = st.sidebar.slider("Altezza Struttura (m)", 2, 100, 20)
alpha = st.sidebar.number_input("Pendenza Copertura (°)", 0, 90, 15)

# Inizializzazione motore di calcolo
# Nota: Questi valori andrebbero calcolati dinamicamente da altitudine/zona
engine = NTC2018Engine(vb0=27, qsk=1.5)

# --- LAYOUT RISULTATI ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("🌬️ Azione del Vento")
    ce_z = engine.get_ce(h_tot, cat_esp)
    qb = 0.5 * engine.rho * (engine.vb0**2) / 1000
    p_vento = qb * ce_z * 0.8 # 0.8 è il cp standard sopravento
    
    st.metric("Pressione Vento (p_e)", f"{p_vento:.3f} kN/m²")
    st.caption(f"Dati: vb0={engine.vb0}m/s, ce={ce_z:.3f}, qb={qb:.3f}kN/m²")

with c2:
    st.subheader("❄️ Azione della Neve")
    q_neve = engine.calcola_neve_copertura(pend=alpha)
    
    st.metric("Carico Neve (q_s)", f"{q_neve:.3f} kN/m²")
    st.caption(f"Dati: qsk={engine.qsk}kN/m², mu1={q_neve/engine.qsk if engine.qsk !=0 else 0:.2f}")

# --- GRAFICO ---
st.divider()
st.subheader("Profilo di Pressione Vento vs Altezza")
z_steps = np.linspace(0, h_tot + 5, 100)
p_steps = [qb * engine.get_ce(z, cat_esp) * 0.8 for z in z_steps]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(p_steps, z_steps, color='navy', lw=2, label="Pressione p_e")
ax.fill_betweenx(z_steps, p_steps, color='skyblue', alpha=0.3)
ax.axhline(y=h_tot, color='red', linestyle='--', label="Altezza Edificio")
ax.set_xlabel("Pressione [kN/m²]")
ax.set_ylabel("Altezza z [m]")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)