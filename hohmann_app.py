import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from skyfield.api import EarthSatellite, load

# Initialize timescale once at the beginning
ts = load.timescale()

st.title("🛰️ Hohmann Transfer Orbit Simulator")

# --- Sidebar Input ---
with st.sidebar:
    st.header("Orbit Parameters")
    altitude1_km = st.number_input("Initial Orbit Altitude (LEO, km)", 100, 100000, 500)
    altitude2_km = st.number_input("Final Orbit Altitude (GEO, km)", 300, 400000, 35786)
    if altitude2_km <= altitude1_km:
        st.error("⚠️ Final orbit altitude must be greater than initial orbit altitude.")
        st.stop()

# --- Constants ---
G = 6.67430e-11         # Gravitational Constant (m^3 kg^-1 s^-2)
M_earth = 5.972e24      # Mass of Earth (kg)
R_earth = 6.371e6       # Mean Radius of Earth (m)

# TLEs for ISS and Hubble - **ATTENTION: These are outdated and will give inaccurate live positions.**
# For accurate "live" data, you would need to fetch the latest TLEs daily.
# Example: Manually update these lines before your competition.
iss_line1 = "1 25544U 98067A   24150.51834491  .00008764  00000+0  16178-3 0  9992"
iss_line2 = "2 25544  51.6400 194.5001 0003734  49.0609  81.0082 15.50553277428470"

hubble_line1 = "1 20580U 90037B   24150.37531449  .00002037  00000+0  10128-3 0  9997"
hubble_line2 = "2 20580  28.4699 353.1648 0002581 345.4144  14.6761 15.09176310584847"

# --- Orbit Calculations ---
altitude1 = altitude1_km * 1000  # Convert km to meters
altitude2 = altitude2_km * 1000

r1 = R_earth + altitude1 # Radius of initial orbit from Earth center
r2 = R_earth + altitude2 # Radius of final orbit from Earth center

# Circular orbit velocities
v1 = np.sqrt(G * M_earth / r1)
v2 = np.sqrt(G * M_earth / r2)

# Hohmann transfer parameters
a_transfer = (r1 + r2) / 2 # Semi-major axis of transfer ellipse
v_transfer1 = np.sqrt(G * M_earth * (2/r1 - 1/a_transfer)) # Velocity at periapsis of transfer
v_transfer2 = np.sqrt(G * M_earth * (2/r2 - 1/a_transfer)) # Velocity at apoapsis of transfer

# Delta-Vs required
delta_v1 = v_transfer1 - v1
delta_v2 = v2 - v_transfer2
total_delta_v = abs(delta_v1) + abs(delta_v2)

# Transfer time
T_transfer = np.pi * np.sqrt(a_transfer**3 / (G * M_earth)) # Time in seconds
T_hours = T_transfer / 3600 # Time in hours

# --- Display Transfer Details ---
st.subheader("🚀 Transfer Details")
st.markdown(f"- **ΔV1:** {delta_v1:.2f} m/s")
st.markdown(f"- **ΔV2:** {delta_v2:.2f} m/s")
st.markdown(f"- **Total ΔV:** {total_delta_v:.2f} m/s")
st.markdown(f"- **Transfer Time:** {T_hours:.2f} hours")

# --- Orbit Plot ---
theta = np.linspace(0, 2*np.pi, 500) # For circular orbits
phi = np.linspace(0, np.pi, 300)     # For transfer ellipse (half-circle)

# Convert all radii to kilometers for plotting
r1_km = r1 / 1000
r2_km = r2 / 1000
earth_km = R_earth / 1000

# Hohmann transfer ellipse coordinates (in km)
# This calculation plots the ellipse starting at r1 (positive X) and ending at -r2 (negative X)
x_trans_km = (a_transfer * np.cos(phi) - (a_transfer - r1)) / 1000
y_trans_km = (a_transfer * np.sqrt(1 - ((r1 - r2)**2 / (4 * a_transfer**2))) * np.sin(phi)) / 1000

# Create the matplotlib figure
fig, ax = plt.subplots(figsize=(8, 8), facecolor='black') # Adjust figure size and background
ax.set_facecolor("black") # Set axes background to black

# Plot Earth
ax.plot(earth_km * np.cos(theta), earth_km * np.sin(theta), color='white', label="Earth Surface")
ax.plot(0, 0, 'o', color='white', markersize=4, label="Earth Center") # Plot Earth center

# Plot Initial Orbit (LEO)
ax.plot(r1_km * np.cos(theta), r1_km * np.sin(theta), color='cyan', linewidth=1.5,
        label=f"LEO Orbit ({altitude1_km} km)")

# Plot Final Orbit (GEO)
ax.plot(r2_km * np.cos(theta), r2_km * np.sin(theta), color='lime', linewidth=1.5,
        label=f"GEO Orbit ({altitude2_km} km)")

# Plot Transfer Orbit
ax.plot(x_trans_km, y_trans_km, color='orange', linestyle='--', linewidth=2,
        label="Hohmann Transfer Trajectory")

# Plot Burn markers - CORRECTED BURN 2 LOCATION
ax.plot(r1_km, 0, 'X', color='red', markersize=10, mew=1.5, label="Burn 1 (ΔV₁)") # Burn 1 at LEO radius
ax.plot(-r2_km, 0, 'X', color='violet', markersize=10, mew=1.5, label="Burn 2 (ΔV₂)") # Burn 2 at GEO radius (negative X for this plot)

# Get live satellite positions
current_time = ts.now()

iss_sat = EarthSatellite(iss_line1, iss_line2, "ISS", ts)
iss_pos_3d_km = iss_sat.at(current_time).position.km
# Calculate the radial distance for ISS
iss_radial_distance_km = np.linalg.norm(iss_pos_3d_km)

hubble_sat = EarthSatellite(hubble_line1, hubble_line2, "Hubble", ts)
hubble_pos_3d_km = hubble_sat.at(current_time).position.km
# Calculate the radial distance for Hubble
hubble_radial_distance_km = np.linalg.norm(hubble_pos_3d_km)

# Plot ISS at its radial distance on the positive X-axis for 2D representation
ax.plot(iss_radial_distance_km, 0, marker='o', color='yellow', markersize=8,
        label="ISS (Live Position)", zorder=5) # zorder to ensure it's on top

# Plot Hubble at its radial distance on the negative X-axis for 2D representation (or positive if you prefer)
ax.plot(-hubble_radial_distance_km, 0, marker='*', color='magenta', markersize=10,
        label="Hubble (Live Position)", zorder=5) # zorder to ensure it's on top


# Styling for the plot
ax.set_title("Hohmann Transfer Orbit Simulation", color='white', fontsize=16)
ax.set_xlabel("X (km)", color='white', fontsize=12)
ax.set_ylabel("Y (km)", color='white', fontsize=12)
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['right'].set_color('white')
ax.grid(True, color='gray', linestyle=':', alpha=0.3)
ax.legend(facecolor='black', edgecolor='white', labelcolor='white', fontsize=10)
ax.set_aspect('equal', adjustable='box') # Ensure equal aspect ratio for circular orbits

# Display the plot in Streamlit
st.pyplot(fig)
plt.close(fig) # Close the figure to free up memory after plotting in Streamlit

# --- Skyfield Satellite Data Display ---
st.subheader("📡 Live Satellite Data")

# ISS Altitude
iss_altitude = iss_radial_distance_km - earth_km
st.markdown(f"**Current ISS Altitude:** {iss_altitude:.2f} km")
if abs(iss_altitude - altitude1_km) < 100:
    st.success("🛰️ ISS is near your initial orbit!")

# Hubble Altitude
hubble_altitude = hubble_radial_distance_km - earth_km
st.markdown(f"**Current Hubble Telescope Altitude:** {hubble_altitude:.2f} km")
if abs(hubble_altitude - altitude1_km) < 100:
    st.success("🔭 Hubble Telescope is near your initial orbit!")
