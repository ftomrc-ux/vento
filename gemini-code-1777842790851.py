import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

class NTC2018Vento:
    def __init__(self):
        self.rho = 1.25
        self.nu = 1.5e-5 

    def calcola_velocita_base(self, zona, altitudine):
        """Determina vb0, a0 e calcola vb - NTC 2018 Tab. 3.3.I"""
        # [vb0, a0]
        mappa_zone = {
            1: [25, 1000], 2: [25, 750], 3: [27, 500],
            4: [28, 500], 5: [28, 750], 6: [28, 500],
            7: [27, 1000], 8: [28, 1250], 9: [31, 1500]
        }
        vb0, a0 = mappa_zone.get(zona, [25, 500])
        
        if altitudine <= a0:
            vb = vb0
        else:
            vb = vb0 * (1 + 0.00001 * (altitudine - a0))
        return vb, vb0

    def get_ce(self, z, cat):
        """Coefficiente di esposizione ce(z) - NTC 2018 Tab. 3.3.II"""
        params = {
            'A': [0.16, 0.01, 2], 'B': [0.19, 0.05, 4], 
            'C': [0.20, 0.10, 5], 'D': [0.22, 0.30, 8], 'E': [0.23, 0.70, 12]
        }
        kr, z0, zmin = params.get(cat, params['B'])
        ze = max(z, zmin)
        return (kr**2) * 1.0 * math.log(ze/z0) * (7 + math.log(ze/z0))

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="NTC 2018 Vento Pro", layout="wide")
st.title("🌬️ Calcolatore Azione del Vento - NTC 2018")

# Sidebar - Input
st.sidebar.header("1. Parametri del Sito")
zona_v = st.sidebar.selectbox("Zona Vento (Italia)", options=[1, 2, 3, 4, 5, 6, 7, 8, 9], index=2)
altitudine = st.sidebar.number_input("Altitudine del sito [m s.l.m.]", value=0)
cat_esp = st.sidebar.selectbox("Categoria Esposizione", ['A', 'B', 'C', 'D', 'E'], index=1)

st.sidebar.header("2. Geometria Edificio")
tipo_edificio = st.sidebar.selectbox(
    "Tipologia Costruttiva", 
    ["Rettangolare (Parete Sopravento)", "Cilindrico (Silo/Camino)", "Tettoia Isolata"]
)
h_tot = st.sidebar.slider("Altezza Struttura (z) [m]", 2, 100, 15)

# Inizializzazione Motore
engine = NTC2018Vento()
vb, vb0 = engine.calcola_velocita_base(zona_v, altitudine)
qb = 0.5 * engine.rho * (vb**2) / 1000
ce_z = engine.get_ce(h_tot, cat_esp)

# Logica Cp/Cf
if tipo_edificio == "Rettangolare (Parete Sopravento)":
    cp = 0.8
    desc = "Coefficiente di pressione $c_{p,e}$ (Zona D)."
elif tipo_edificio == "Cilindrico (Silo/Camino)":
    diam = st.sidebar.number_input("Diametro Cilindro [m]", value=5.0)
    vz = vb * math.sqrt(ce_z)
    re = (diam * vz) / engine.nu
    cp = 0.7 if re > 1e6 else 1.2 
    desc = f"Coefficiente di forza $c_f$ basato su Reynolds ($Re = {re:.1e}$)."
else:
    phi = st.sidebar.slider("Grado di ostruzione (phi)", 0.0, 1.0, 0.5)
    cp = 1.2 + 0.3 * phi
    desc = "Coefficiente di pressione netta $c_{p,net}$ per tettoie."

# --- VISUALIZZAZIONE RISULTATI ---
st.subheader("📊 Risultati Analisi Vento")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Velocità di rif. (vb)", f"{vb:.2f} m/s")
    st.caption(f"Sito: Zona {zona_v}, vb0 = {vb0} m/s")

with col2:
    st.metric("Press. cinetica (qb)", f"{qb:.3f} kN/m²")
    st.caption(f"Densità aria: {engine.rho} kg/m³")

with col3:
    p_progetto = qb * ce_z * cp
    st.metric("Pressione Progetto (pe)", f"{p_progetto:.3f} kN/m²")
    st.write(desc)

# Grafico Profilo
st.divider()
st.subheader("📈 Profilo di Pressione lungo l'altezza")
z_range = np.linspace(0, h_tot + 5, 100)
p_range = [qb * engine.get_ce(z, cat_esp) * cp for z in z_range]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(p_range, z_range, color='blue', lw=2, label="Pressione pe(z)")
ax.fill_betweenx(z_range, p_range, color='blue', alpha=0.1)
ax.axhline(y=h_tot, color='red', linestyle='--', label="Quota calcolo")
ax.set_xlabel("Pressione [kN/m²]")
ax.set_ylabel("Altezza z [m]")
ax.legend()
ax.grid(True, linestyle=':', alpha=0.6)
st.pyplot(fig)