# ---------------------------------
# Import Libraries
# ---------------------------------
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import requests
from skyfield.api import EarthSatellite, Loader
from datetime import datetime
import pydeck as pdk

# ---------------------------------
# Global Setup
# ---------------------------------
load = Loader(".")
planets = load('./de440s.bsp')   # Planet ephemerides
ts = load.timescale()
current_time = ts.now()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛰️ Hohmann Transfer", 
    "🌍 Planet Viewer", 
    "🛰️ LEO to MEO", 
    "📘 What is Hohmann Transfer?", 
    "🌐 Satellite Tracker"
])

# Constants
G = 6.67430e-11
M_earth = 5.972e24
R_earth = 6.371e6
earth_km = R_earth / 1000

# ---------------------------------
# TAB 1: Hohmann Transfer (LEO → GEO)
# ---------------------------------
with tab1:
    st.title("🛰️ Hohmann Transfer Orbit Simulator")
    st.markdown("Transfer between **LEO and GEO**. Customize the altitudes below:")

    with st.sidebar:
        st.header("Orbit Parameters")
        altitude1_km = st.number_input("Initial Orbit Altitude (LEO, km)", 100, 1600, 500)
        altitude2_km = st.number_input("Final Orbit Altitude (GEO, km)", 300, 40000, 35786)
        if altitude2_km <= altitude1_km:
            st.error("⚠️ Final orbit altitude must be greater than initial orbit altitude.")
            st.stop()

    # Orbit calculations
    altitude1 = altitude1_km * 1000
    altitude2 = altitude2_km * 1000
    r1, r2 = R_earth + altitude1, R_earth + altitude2
    v1, v2 = np.sqrt(G*M_earth/r1), np.sqrt(G*M_earth/r2)
    a_transfer = (r1 + r2) / 2
    v_transfer1 = np.sqrt(G*M_earth * (2/r1 - 1/a_transfer))
    v_transfer2 = np.sqrt(G*M_earth * (2/r2 - 1/a_transfer))
    delta_v1, delta_v2 = v_transfer1 - v1, v2 - v_transfer2
    total_delta_v = abs(delta_v1) + abs(delta_v2)
    T_hours = (np.pi * np.sqrt(a_transfer**3 / (G * M_earth))) / 3600

    # Results
    st.subheader("🚀 Transfer Details")
    st.markdown(f"- **ΔV1:** {delta_v1:.2f} m/s")
    st.markdown(f"- **ΔV2:** {delta_v2:.2f} m/s")
    st.markdown(f"- **Total ΔV:** {total_delta_v:.2f} m/s")
    st.markdown(f"- **Transfer Time:** {T_hours:.2f} hours")

    # Plot orbits
    theta = np.linspace(0, 2*np.pi, 500)
    phi = np.linspace(0, np.pi, 300)
    r1_km, r2_km = r1/1000, r2/1000
    x_trans_km = (a_transfer*np.cos(phi) - (a_transfer-r1))/1000
    y_trans_km = (a_transfer*np.sqrt(1 - ((r1-r2)**2 / (4*a_transfer**2)))*np.sin(phi))/1000

    fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
    ax.set_facecolor("black")
    ax.plot(earth_km*np.cos(theta), earth_km*np.sin(theta), color='white', label="Earth")
    ax.plot(r1_km*np.cos(theta), r1_km*np.sin(theta), color='cyan', label="LEO")
    ax.plot(r2_km*np.cos(theta), r2_km*np.sin(theta), color='lime', label="GEO")
    ax.plot(x_trans_km, y_trans_km, color='orange', linestyle='--', label="Transfer")
    ax.plot(r1_km, 0, 'X', color='red', label="Burn 1")
    ax.plot(-r2_km, 0, 'X', color='purple', label="Burn 2")

    # Live satellites (ISS + Hubble)
    iss = EarthSatellite(
        "1 25544U 98067A   24150.51834491  .00008764  00000+0  16178-3 0  9992",
        "2 25544  51.6400 194.5001 0003734  49.0609  81.0082 15.50553277428470", "ISS", ts
    )
    hubble = EarthSatellite(
        "1 20580U 90037B   24150.37531449  .00002037  00000+0  10128-3 0  9997",
        "2 20580  28.4699 353.1648 0002581 345.4144  14.6761 15.09176310584847", "Hubble", ts
    )
    iss_pos = iss.at(current_time).position.km
    hubble_pos = hubble.at(current_time).position.km
    ax.plot(np.linalg.norm(iss_pos), 0, 'o', color='yellow', label="ISS")
    ax.plot(-np.linalg.norm(hubble_pos), 0, '*', color='magenta', label="Hubble")

    ax.legend(facecolor='black', edgecolor='white')
    ax.set_aspect('equal')
    st.pyplot(fig)

    # Satellite altitudes
    st.subheader("📡 Live Satellite Altitudes")
    st.markdown(f"- **ISS:** {np.linalg.norm(iss_pos) - earth_km:.2f} km")
    st.markdown(f"- **Hubble:** {np.linalg.norm(hubble_pos) - earth_km:.2f} km")

# ---------------------------------
# TAB 2: Planet Viewer
# ---------------------------------
with tab2:
    st.title("🌍 Real-Time Planetary Orbit Visualizer")
    sun, earth, mars, venus, jupiter = planets['Sun'], planets['Earth'], planets['Mars Barycenter'], planets['Venus'], planets['Jupiter Barycenter']

    earth_pos = earth.at(current_time).observe(sun).ecliptic_position().au
    mars_pos = mars.at(current_time).observe(sun).ecliptic_position().au
    venus_pos = venus.at(current_time).observe(sun).ecliptic_position().au
    jupiter_pos = jupiter.at(current_time).observe(sun).ecliptic_position().au

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor('black')
    theta = np.linspace(0, 2*np.pi, 300)
    radii = {'Venus': 0.72, 'Earth': 1.0, 'Mars': 1.52, 'Jupiter': 5.2}
    for planet, r in radii.items():
        ax.plot(r*np.cos(theta), r*np.sin(theta), linestyle='--', label=f"{planet} Orbit")
    ax.plot(venus_pos[0], venus_pos[1], 'o', color='orange', label="Venus")
    ax.plot(earth_pos[0], earth_pos[1], 'o', color='cyan', label="Earth")
    ax.plot(mars_pos[0], mars_pos[1], 'o', color='red', label="Mars")
    ax.plot(jupiter_pos[0], jupiter_pos[1], 'o', color='gold', label="Jupiter")
    ax.plot(0, 0, 'o', color='yellow', markersize=12, label="Sun")

    ax.axis('equal')
    ax.legend(facecolor='black', edgecolor='white')
    st.pyplot(fig)

# ---------------------------------
# TAB 3: LEO → MEO Transfer
# ---------------------------------
with tab3:
    st.title("🛰️ LEO to MEO Transfer")
    st.markdown("Simulate a transfer between **Low Earth Orbit and Medium Earth Orbit**.")

    with st.sidebar:
        st.header("Orbit Parameters")
        altitude1_km = st.number_input("Initial Orbit Altitude (LEO, km)", 100, 1600, 500, key="leo_input")
        altitude2_km = st.number_input("Final Orbit Altitude (MEO, km)", 2000, 20000, 10000, key="meo_input")
        if altitude2_km <= altitude1_km:
            st.error("⚠️ Final orbit altitude must be greater than initial orbit altitude.")
            st.stop()

    # Similar calculations to Tab 1
    altitude1, altitude2 = altitude1_km*1000, altitude2_km*1000
    r1, r2 = R_earth + altitude1, R_earth + altitude2
    v1, v2 = np.sqrt(G*M_earth/r1), np.sqrt(G*M_earth/r2)
    a_transfer = (r1 + r2)/2
    v_transfer1 = np.sqrt(G*M_earth * (2/r1 - 1/a_transfer))
    v_transfer2 = np.sqrt(G*M_earth * (2/r2 - 1/a_transfer))
    delta_v1, delta_v2 = v_transfer1-v1, v2-v_transfer2
    total_delta_v = abs(delta_v1)+abs(delta_v2)
    T_hours = (np.pi*np.sqrt(a_transfer**3/(G*M_earth)))/3600

    st.subheader("🚀 Transfer Details")
    st.markdown(f"- **ΔV1:** {delta_v1:.2f} m/s")
    st.markdown(f"- **ΔV2:** {delta_v2:.2f} m/s")
    st.markdown(f"- **Total ΔV:** {total_delta_v:.2f} m/s")
    st.markdown(f"- **Transfer Time:** {T_hours:.2f} hours")

# ---------------------------------
# TAB 4: Explanation
# ---------------------------------
with tab4:
    st.title("📘 What is a Hohmann Transfer Orbit?")
    st.markdown("""
    ### 🚀 Overview
    A **Hohmann Transfer Orbit** is a fuel-efficient way to move a spacecraft between two circular orbits using two burns.
    ...
    """)

