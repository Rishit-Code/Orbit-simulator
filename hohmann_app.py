import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from skyfield.api import EarthSatellite, load

# Initialize timescale once
ts = load.timescale()
current_time = ts.now()

# Create tabs
tab1, tab2 = st.tabs(["🛰️ Hohmann Transfer", "🌍 Planet Viewer"])


# TAB 1: Hohmann Transfer
with tab1:
    st.title("🛰️ Hohmann Transfer Orbit Simulator")

    with st.sidebar:
        st.header("Orbit Parameters")
        altitude1_km = st.number_input("Initial Orbit Altitude (LEO, km)", 100, 100000, 500)
        altitude2_km = st.number_input("Final Orbit Altitude (GEO, km)", 300, 400000, 35786)
        if altitude2_km <= altitude1_km:
            st.error("⚠️ Final orbit altitude must be greater than initial orbit altitude.")
            st.stop()

    # Constants
    G = 6.67430e-11
    M_earth = 5.972e24
    R_earth = 6.371e6

    # Orbit math
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

    # Plot
    theta = np.linspace(0, 2*np.pi, 500)
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

    # ISS and Hubble
    iss = EarthSatellite(
        "1 25544U 98067A   24150.51834491  .00008764  00000+0  16178-3 0  9992",
        "2 25544  51.6400 194.5001 0003734  49.0609  81.0082 15.50553277428470",
        "ISS", ts
    )
    hubble = EarthSatellite(
        "1 20580U 90037B   24150.37531449  .00002037  00000+0  10128-3 0  9997",
        "2 20580  28.4699 353.1648 0002581 345.4144  14.6761 15.09176310584847",
        "Hubble", ts
    )
    iss_pos = iss.at(current_time).position.km
    hubble_pos = hubble.at(current_time).position.km
    ax.plot(np.linalg.norm(iss_pos), 0, 'o', color='yellow', label="ISS")
    ax.plot(-np.linalg.norm(hubble_pos), 0, '*', color='magenta', label="Hubble")

    ax.set_title("Hohmann Transfer Orbit", color='white')
    ax.set_xlabel("X (km)", color='white')
    ax.set_ylabel("Y (km)", color='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
    ax.grid(True, linestyle=':', color='gray')
    ax.set_aspect('equal')

    st.pyplot(fig)

    # Altitude output
    iss_alt_km = np.linalg.norm(iss_pos) - earth_km
    hubble_alt_km = np.linalg.norm(hubble_pos) - earth_km
    st.subheader("📡 Live Satellite Altitudes")
    st.markdown(f"- **ISS:** {iss_alt_km:.2f} km")
    st.markdown(f"- **Hubble:** {hubble_alt_km:.2f} km")


# TAB 2: Planet Viewer
with tab2:
    st.title("🌍 Real-Time Planetary Orbit Visualizer")

    from skyfield.api import Loader
    load = Loader('.')
    planets = load('./de440s.bsp')  # local version you uploaded

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
    
