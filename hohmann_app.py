# Simple Orbital Transfer Calculator
# High School Physics Project

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Page setup
st.set_page_config(page_title="Orbital Transfer Calculator", page_icon="🛰️")

# Basic constants (simplified values)
EARTH_RADIUS = 6371  # km
GRAVITY = 9.81  # m/s²
EARTH_MASS = 5.97e24  # kg

# Main title
st.title("🛰️ Hohmann Transfer Orbit Calculator")
st.markdown("Learn how satellites move between different orbits around Earth!")

# Create two main sections
tab1, tab2 = st.tabs(["🚀 Calculate Transfer", "📚 What is This?"])

with tab1:
    st.header("Orbit Transfer Calculator")
    
    # Simple input section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Starting Orbit")
        start_altitude = st.slider("Altitude above Earth (km)", 200, 2000, 400)
        st.write(f"Satellite starts at {start_altitude} km above Earth")
    
    with col2:
        st.subheader("Target Orbit")
        end_altitude = st.slider("Target altitude (km)", 2000, 40000, 35786)
        st.write(f"Satellite ends at {end_altitude} km above Earth")
    
    # Make sure target is higher than start
    if end_altitude <= start_altitude:
        st.error("Target altitude must be higher than starting altitude!")
        st.stop()
    
    # Simple calculations
    start_radius = EARTH_RADIUS + start_altitude  # km
    end_radius = EARTH_RADIUS + end_altitude      # km
    
    # Convert to meters for physics calculations
    start_radius_m = start_radius * 1000
    end_radius_m = end_radius * 1000
    
    # Calculate orbital speeds (circular orbits)
    # v = sqrt(GM/r)
    GM = 3.986e14  # Earth's gravitational parameter (m³/s²)
    
    start_speed = np.sqrt(GM / start_radius_m) / 1000  # km/s
    end_speed = np.sqrt(GM / end_radius_m) / 1000      # km/s
    
    # Transfer orbit calculations
    transfer_radius = (start_radius_m + end_radius_m) / 2  # Semi-major axis
    
    # Speed needed at start of transfer
    speed_at_start = np.sqrt(GM * (2/start_radius_m - 1/transfer_radius)) / 1000
    # Speed needed at end of transfer  
    speed_at_end = np.sqrt(GM * (2/end_radius_m - 1/transfer_radius)) / 1000
    
    # Calculate the "kicks" needed (delta-v)
    kick_1 = speed_at_start - start_speed  # Speed up at start
    kick_2 = end_speed - speed_at_end      # Speed up at end
    total_kick = abs(kick_1) + abs(kick_2)
    
    # Transfer time (half the orbital period of transfer ellipse)
    transfer_time_seconds = np.pi * np.sqrt(transfer_radius**3 / GM)
    transfer_time_hours = transfer_time_seconds / 3600
    
    # Display results in a nice format
    st.header("Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("First Speed Boost", f"{kick_1:.2f} km/s", "At start of transfer")
        
    with col2:
        st.metric("Second Speed Boost", f"{kick_2:.2f} km/s", "At end of transfer")
        
    with col3:
        st.metric("Transfer Time", f"{transfer_time_hours:.1f} hours", "Half an orbit")
    
    st.info(f"**Total speed change needed:** {total_kick:.2f} km/s")
    
    # Create a simple visualization
    st.header("Orbit Visualization")
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('black')
    
    # Draw Earth
    earth_circle = plt.Circle((0, 0), EARTH_RADIUS, color='lightblue', label='Earth')
    ax.add_patch(earth_circle)
    
    # Draw orbits as circles
    angles = np.linspace(0, 2*np.pi, 100)
    
    # Starting orbit (green)
    start_x = start_radius * np.cos(angles)
    start_y = start_radius * np.sin(angles)
    ax.plot(start_x, start_y, 'g-', linewidth=2, label=f'Start Orbit ({start_altitude} km)')
    
    # End orbit (red)
    end_x = end_radius * np.cos(angles)
    end_y = end_radius * np.sin(angles)
    ax.plot(end_x, end_y, 'r-', linewidth=2, label=f'Target Orbit ({end_altitude} km)')
    
    # Transfer orbit (yellow dashed) - simplified as ellipse
    transfer_angles = np.linspace(0, np.pi, 50)  # Half orbit
    transfer_x = []
    transfer_y = []
    
    for angle in transfer_angles:
        # Simple ellipse calculation
        a = transfer_radius / 1000  # Semi-major axis in km
        b = np.sqrt(start_radius * end_radius)  # Semi-minor axis approximation
        x = a * np.cos(angle)
        y = b * np.sin(angle)
        transfer_x.append(x)
        transfer_y.append(y)
    
    ax.plot(transfer_x, transfer_y, 'y--', linewidth=3, label='Transfer Path')
    
    # Mark the burn points
    ax.plot(start_radius, 0, 'ro', markersize=10, label='Burn 1 (Speed up)')
    ax.plot(-end_radius, 0, 'ro', markersize=10, label='Burn 2 (Speed up)')
    
    ax.set_xlim(-end_radius*1.2, end_radius*1.2)
    ax.set_ylim(-end_radius*1.2, end_radius*1.2)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.set_title('Hohmann Transfer Orbit', color='white', fontsize=16)
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    # Fun facts section with dynamic content
    st.header("🎯 Dynamic Mission Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mission Status")
        if efficiency > 95:
            st.success("🏆 **MISSION SUCCESS!** Near-optimal fuel usage!")
        elif efficiency > 80:
            st.info("✅ **Good Transfer** - Acceptable fuel efficiency")
        elif efficiency > 60:
            st.warning("⚠️ **Inefficient Transfer** - Wasting fuel")
        else:
            st.error("🚨 **Poor Efficiency** - Major fuel waste!")
            
        # Fuel cost estimate (rough approximation)
        fuel_cost_optimal = 10000  # $10k per km/s delta-v (rough estimate)
        your_fuel_cost = fuel_cost_optimal * total_kick_kms / (abs(optimal_kick_1) + abs(optimal_kick_2))
        extra_cost = your_fuel_cost - fuel_cost_optimal
        
        if extra_cost > 1000:
            st.markdown(f"💰 **Extra fuel cost:** ~${extra_cost:,.0f}")
        else:
            st.markdown("💰 **Cost:** Near optimal!")
    
    with col2:
        st.subheader("Transfer Type")
        if 0.95 <= burn_1_multiplier <= 1.05 and 0.95 <= burn_2_multiplier <= 1.05:
            st.success("📐 **Classic Hohmann Transfer**")
            st.write("This is the textbook method!")
        elif burn_1_multiplier > 1.2:
            st.info("🚀 **Bi-elliptic Transfer Territory**")
            st.write("High energy but might be more efficient for very high orbits!")
        elif burn_1_multiplier < 0.8:
            st.warning("⏳ **Multi-orbit Transfer**")
            st.write("Multiple passes needed to reach target!")
        else:
            st.info("🔧 **Modified Transfer**")
            st.write("Custom trajectory - analyze the efficiency!")
    
    # Specific altitude-based fun facts
    if end_altitude == 35786:
        st.success("🎯 **Geostationary Mission!** Satellite will hover above the same Earth location.")
    elif end_altitude >= 20000:
        st.info("🛰️ **High Earth Orbit** - Used for GPS and communication satellites.")
    elif start_altitude <= 400:
        st.info("🌍 **Starting from ISS altitude!** That's where astronauts live and work.")
    
    # Dynamic transfer time analysis with better error handling
    if valid_orbit:
        optimal_time = np.pi * np.sqrt(((start_radius_km + end_radius_km)/2 * 1000)**3 / GM) / 3600
        if transfer_time_hours < optimal_time * 0.9:
            st.warning("⚡ **Faster than Hohmann!** High-energy transfer.")
        elif transfer_time_hours > optimal_time * 1.1 and transfer_time_hours < 100:
            st.info("🐌 **Slower than optimal** - Lower energy transfer.")
        elif transfer_time_hours >= 100:
            st.info("🕐 **Very long transfer** - High apogee orbit.")
    else:
        st.error("🚀 **Escape velocity reached!** Satellite leaving Earth orbit!")
    
    # Educational prompts
    st.subheader("🧪 Try These Experiments:")
    
    experiments = [
        "🔬 **Set both burns to 0.5** - What happens to the transfer?",
        "🚀 **Set Burn 1 to 2.0, Burn 2 to 0.5** - Can you still reach the target?",
        "⚖️ **Find the minimum total ΔV** - Try different combinations!",
        "🎯 **Match ISS to GEO** - Use 408 km start, 35,786 km end",
        "🌙 **Extreme case:** Try 400 km to 384,400 km (Moon distance!)"
    ]
    
    for exp in experiments:
        st.markdown(f"- {exp}")
    
    # Real-world connection
    if total_kick_kms > 15:
        st.error("⛽ **Fuel Alert!** This would require a huge rocket. Real missions use multiple stages!")
    elif total_kick_kms > 10:
        st.warning("🚀 **Big Rocket Needed** - This is why space is expensive!")
    else:
        st.success("✅ **Feasible Mission** - Modern rockets can handle this!")

with tab2:
    st.header("What is a Hohmann Transfer?")
    
    st.markdown("""
    ### 🚀 The Most Efficient Way to Change Orbits
    
    A **Hohmann Transfer** is like taking the most fuel-efficient highway between two circular orbits around Earth.
    
    #### How it works:
    1. **Start** in a low orbit (like where the ISS flies)
    2. **Fire rockets** to speed up and enter an elliptical transfer orbit
    3. **Coast** along the transfer path (no fuel needed!)
    4. **Fire rockets again** at the high point to circularize the orbit
    
    #### Why is this efficient?
    - Uses only **2 rocket burns** (minimum possible)
    - Follows natural orbital mechanics
    - Saves fuel compared to other methods
    
    #### Real-world examples:
    - 🛰️ **Communication satellites** use this to reach geostationary orbit
    - 🚀 **Space missions** to other planets use similar transfers
    - 🌕 **Moon missions** use a modified version
    
    ### The Physics (Simplified):
    - **Circular orbits**: Satellite goes same speed all the way around
    - **Elliptical orbits**: Satellite speeds up when closer to Earth, slows down when farther away
    - **Energy**: Higher orbits have more total energy (potential + kinetic)
    
    ### Try different altitudes above to see how:
    - Transfer time changes
    - Speed boosts needed change
    - The orbit shape changes
    """)
    
    st.info("💡 **Fun fact**: This transfer method was invented by Walter Hohmann in 1925, long before we had rockets powerful enough to use it!")
