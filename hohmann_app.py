# ---------------------------------
# 1. Import Libraries
# ---------------------------------
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import requests
from skyfield.api import EarthSatellite, load, Loader
from datetime import datetime
import pydeck as pdk

# ---------------------------------
# 2. Load Planetary Data and Time
# ---------------------------------
loader = Loader(".")
planets = loader('./de440s.bsp')
ts = loader.timescale()
current_time = ts.now()

# ---------------------------------
# 3. Streamlit Tabs
# ---------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛰️ Hohmann Transfer",
    "🌍 Planet Viewer",
    "🛰️ LEO to MEO",
    "📘 What is Hohmann Transfer?",
    "🌐 Satellite Track"
])

# ---------------------------------
# TAB 1: Hohmann Transfer Orbit Simulator
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

    # Constants
    G = 6.67430e-11
    M_earth = 5.972e24
    R_earth = 6.371e6

    # Orbit calculations
    altitude1 = altitude1_km * 1000
    altitude2 = altitude2_km * 1000
    r1 = R_earth + altitude1
    r2 = R_earth + altitude2

    v1 = np.sqrt(G * M_earth / r1)
    v2 = np.sqrt(G * M_earth / r2)
    a_transfer = (r1 + r2) / 2
    v_transfer1 = np.sqrt(G * M_earth * (2 / r1 - 1 / a_transfer))
    v_transfer2 = np.sqrt(G * M_earth * (2 / r2 - 1 / a_transfer))
    delta_v1 = v_transfer1 - v1
    delta_v2 = v2 - v_transfer2
    total_delta_v = abs(delta_v1) + abs(delta_v2)
    T_hours = (np.pi * np.sqrt(a_transfer**3 / (G * M_earth))) / 3600

    # Display transfer details
    st.subheader("🚀 Transfer Details")
    st.markdown(f"- **ΔV1:** {delta_v1:.2f} m/s")
    st.markdown(f"- **ΔV2:** {delta_v2:.2f} m/s")
    st.markdown(f"- **Total ΔV:** {total_delta_v:.2f} m/s")
    st.markdown(f"- **Transfer Time:** {T_hours:.2f} hours")

    # Plotting
    theta = np.linspace(0, 2 * np.pi, 500)
    phi = np.linspace(0, np.pi, 300)
    r1_km = r1 / 1000
    r2_km = r2 / 1000
    earth_km = R_earth / 1000
    x_trans_km = (a_transfer * np.cos(phi) - (a_transfer - r1)) / 1000
    y_trans_km = (a_transfer * np.sqrt(1 - ((r1 - r2)**2 / (4 * a_transfer**2))) * np.sin(phi)) / 1000

    fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
    ax.set_facecolor("black")
    ax.plot(earth_km * np.cos(theta), earth_km * np.sin(theta), color='white', label="Earth Surface")
    ax.plot(0, 0, 'o', color='white', markersize=4, label="Earth Center")
    ax.plot(r1_km * np.cos(theta), r1_km * np.sin(theta), color='cyan', label="LEO")
    ax.plot(r2_km * np.cos(theta), r2_km * np.sin(theta), color='lime', label="GEO")
    ax.plot(x_trans_km, y_trans_km, color='orange', linestyle='--', label="Hohmann Transfer")
    ax.plot(r1_km, 0, 'X', color='red', label="Burn 1")
    ax.plot(-r2_km, 0, 'X', color='purple', label="Burn 2")

    st.pyplot(fig)

# ---------------------------------
# TAB 2: Planet Viewer
# ---------------------------------
with tab2:
    st.title("🌍 Real-Time Planetary Orbit Visualizer")

    sun = planets['Sun']
    earth = planets['Earth']
    mars = planets['Mars Barycenter']
    venus = planets['Venus']
    jupiter = planets['Jupiter Barycenter']

    earth_pos = earth.at(current_time).observe(sun).ecliptic_position().au
    mars_pos = mars.at(current_time).observe(sun).ecliptic_position().au
    venus_pos = venus.at(current_time).observe(sun).ecliptic_position().au
    jupiter_pos = jupiter.at(current_time).observe(sun).ecliptic_position().au

    theta = np.linspace(0, 2*np.pi, 300)
    radii = {'venus': 0.72, 'earth': 1.0, 'mars': 1.52, 'jupiter': 5.2}

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor('black')
    for planet, r in radii.items():
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        ax.plot(x, y, label=f"{planet.capitalize()} Orbit", linestyle='--')

    ax.plot(venus_pos[0], venus_pos[1], 'o', color='orange', label="Venus")
    ax.plot(earth_pos[0], earth_pos[1], 'o', color='cyan', label="Earth")
    ax.plot(mars_pos[0], mars_pos[1], 'o', color='red', label="Mars")
    ax.plot(jupiter_pos[0], jupiter_pos[1], 'o', color='gold', label="Jupiter")
    ax.plot(0, 0, 'o', color='yellow', label="Sun", markersize=12)

    ax.set_xlabel("X (AU)", color='white')
    ax.set_ylabel("Y (AU)", color='white')
    ax.set_title("Planetary Orbits & Real-Time Positions", color='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.axis('equal')
    ax.grid(True, linestyle=':', color='gray')
    ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
    st.pyplot(fig)

# ---------------------------------
# TAB 3: LEO to MEO Transfer
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

    # Orbit calculations
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
    T_hours = (np.pi * np.sqrt(a_transfer**3 / (G * M_earth))) / 3600

    st.subheader("🚀 Transfer Details")
    st.markdown(f"- **ΔV1:** {delta_v1:.2f} m/s")
    st.markdown(f"- **ΔV2:** {delta_v2:.2f} m/s")
    st.markdown(f"- **Total ΔV:** {total_delta_v:.2f} m/s")
    st.markdown(f"- **Transfer Time:** {T_hours:.2f} hours")

    phi = np.linspace(0, np.pi, 300)
    r1_km = r1 / 1000
    r2_km = r2 / 1000
    x_trans_km = (a_transfer * np.cos(phi) - (a_transfer - r1)) / 1000
    y_trans_km = (a_transfer * np.sqrt(1 - ((r1 - r2)**2 / (4 * a_transfer**2))) * np.sin(phi)) / 1000

    fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
    ax.set_facecolor("black")
    ax.plot(earth_km * np.cos(theta), earth_km * np.sin(theta), color='white', label="Earth Surface")
    ax.plot(0, 0, 'o', color='white', markersize=4, label="Earth Center")
    ax.plot(r1_km * np.cos(theta), r1_km * np.sin(theta), color='cyan', label="LEO")
    ax.plot(r2_km * np.cos(theta), r2_km * np.sin(theta), color='lime', label="MEO")
    ax.plot(x_trans_km, y_trans_km, color='orange', linestyle='--', label="Transfer Trajectory")
    ax.plot(r1_km, 0, 'X', color='red', label="Burn 1")
    ax.plot(-r2_km, 0, 'X', color='purple', label="Burn 2")

    ax.set_title("LEO to MEO Transfer", color='white')
    ax.set_xlabel("X (km)", color='white')
    ax.set_ylabel("Y (km)", color='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
    ax.grid(True, linestyle=':', color='gray')
    ax.set_aspect('equal')
    st.pyplot(fig)
