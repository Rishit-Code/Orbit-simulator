
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from skyfield.api import EarthSatellite, load

st.title("🛰️ Hohmann Transfer Orbit Simulator")

# Sidebar input
altitude1_km = st.number_input("Initial Orbit Altitude (LEO)", 100, 1000, 500)
altitude2_km = st.number_input("Final Orbit Altitude (GEO)", 20000, 40000, 35786)

# Constants
G = 6.67430e-11
M_earth = 5.972e24
R_earth = 6.371e6

altitude1 = altitude1_km * 1000
altitude2 = altitude2_km * 1000
r1 = R_earth + altitude1
r2 = R_earth + altitude2

v1 = np.sqrt(G * M_earth / r1)
v2 = np.sqrt(G * M_earth / r2)
a_transfer = (r1 + r2) / 2
v_transfer1 = np.sqrt(G * M_earth * (2/r1 - 1/a_transfer))
v_transfer2 = np.sqrt(G * M_earth * (2/r2 - 1/a_transfer))
delta_v1 = v_transfer1 - v1
delta_v2 = v2 - v_transfer2
total_delta_v = abs(delta_v1) + abs(delta_v2)
T_transfer = np.pi * np.sqrt(a_transfer**3 / (G * M_earth))
T_hours = T_transfer / 3600

st.subheader("🚀 Transfer Details")
st.markdown(f"- **ΔV1:** {delta_v1:.2f} m/s")
st.markdown(f"- **ΔV2:** {delta_v2:.2f} m/s")
st.markdown(f"- **Total ΔV:** {total_delta_v:.2f} m/s")
st.markdown(f"- **Transfer Time:** {T_hours:.2f} hours")

# Orbit plot
theta = np.linspace(0, 2*np.pi, 500)
phi = np.linspace(0, np.pi, 300)
r1_km, r2_km = r1 / 1000, r2 / 1000
earth_km = R_earth / 1000
x_trans_km = (a_transfer * np.cos(phi) - (a_transfer - r1)) / 1000
y_trans_km = (a_transfer * np.sqrt(1 - ((r1 - r2)**2 / (4 * a_transfer**2))) * np.sin(phi)) / 1000

fig, ax = plt.subplots(figsize=(7, 7), facecolor='black')
ax.set_facecolor("black")
ax.plot(earth_km * np.cos(theta), earth_km * np.sin(theta), color='white', label="Earth")
# Initial Orbit (LEO)
ax.plot(r1_km * np.cos(theta), r1_km * np.sin(theta), color='cyan', label=f"LEO Orbit ({altitude1_km} km)")
# Final Orbit (GEO)
ax.plot(r2_km * np.cos(theta), r2_km * np.sin(theta), color='lime', label=f"GEO Orbit ({altitude2_km} km)")
# Transfer Orbit
ax.plot(x_trans_km, y_trans_km, color='orange', linestyle='--', label="Hohmann Transfer")
# Burn markers
ax.plot(r1_km, 0, 'X', color='red', label="Burn 1")
ax.plot(r2_km, 0, 'X', color='violet', label="Burn 2")
# Styling 
ax.set_title("Hohmann Transfer Orbit", color='white')
ax.set_xlabel("X (km)", color='white')
ax.set_ylabel("Y (km)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.grid(True, color='gray', linestyle=':', alpha=0.3)
ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
st.pyplot(fig)
# Skyfield satellite data
st.subheader("📡 ISS Live Position")
ts = load.timescale()
line1 = "1 25544U 98067A   24150.51834491  .00008764  00000+0  16178-3 0  9992"
line2 = "2 25544  51.6400 194.5001 0003734  49.0609  81.0082 15.50553277428470"
sat = EarthSatellite(line1, line2, "ISS", ts)
t = ts.now()
position = sat.at(t).position.km
distance = np.linalg.norm(position)
altitude_iss = distance - earth_km

st.markdown(f"**Current ISS Altitude:** {altitude_iss:.2f} km")
if abs(altitude_iss - altitude1_km) < 100:
    st.success("🛰️ ISS is near your initial orbit!")
