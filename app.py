import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Page setup
st.set_page_config(page_title="Heat Exchanger Performance Calculator", layout="centered")

# Title and description
st.markdown("<h1 style='text-align: center; color: #004080;'>Heat Exchanger Performance Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analyze Heat Duty, LMTD, and Effectiveness of a Counter-flow Heat Exchanger</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Units selection
with st.expander("Choose Units"):
    unit_temp = st.radio("Temperature Unit", ["°C", "°F"], horizontal=True)
    unit_mass = st.radio("Mass Flow Rate Unit", ["kg/s", "lb/s"], horizontal=True)
    unit_cp = st.radio("Specific Heat Capacity Unit", ["kJ/kg°C", "J/kg°C", "BTU/lb°F"], horizontal=True)

# Helper functions for unit conversions
def to_celsius(temp):
    return (temp - 32) * 5 / 9 if unit_temp == "°F" else temp

def to_kg(mass):
    return mass * 0.453592 if unit_mass == "lb/s" else mass

def to_kj_per_kgC(cp):
    if unit_cp == "J/kg°C":
        return cp / 1000
    elif unit_cp == "BTU/lb°F":
        return cp * 4.1868
    return cp

# Input fields (blank by default)
st.markdown("### Input Parameters")
col1, col2 = st.columns(2)
with col1:
    Th_in_input = st.text_input(f"Hot Fluid Inlet Temperature ({unit_temp})", value="")
    Th_out_input = st.text_input(f"Hot Fluid Outlet Temperature ({unit_temp})", value="")
    m_hot_input = st.text_input(f"Mass Flow Rate of Hot Fluid ({unit_mass})", value="")
with col2:
    Tc_in_input = st.text_input(f"Cold Fluid Inlet Temperature ({unit_temp})", value="")
    Tc_out_input = st.text_input(f"Cold Fluid Outlet Temperature ({unit_temp})", value="")
    m_cold_input = st.text_input(f"Mass Flow Rate of Cold Fluid ({unit_mass})", value="")

Cp_input = st.text_input(f"Specific Heat Capacity ({unit_cp})", value="")
U_input = st.text_input("Overall Heat Transfer Coefficient (W/m²°C)", value="")
A_input = st.text_input("Heat Transfer Area (m²)", value="")

# Convert inputs safely
def to_float(val):
    try:
        return float(val)
    except:
        return None

Th_in = to_celsius(to_float(Th_in_input)) if to_float(Th_in_input) is not None else None
Th_out = to_celsius(to_float(Th_out_input)) if to_float(Th_out_input) is not None else None
m_hot = to_kg(to_float(m_hot_input)) if to_float(m_hot_input) is not None else None

Tc_in = to_celsius(to_float(Tc_in_input)) if to_float(Tc_in_input) is not None else None
Tc_out = to_celsius(to_float(Tc_out_input)) if to_float(Tc_out_input) is not None else None
m_cold = to_kg(to_float(m_cold_input)) if to_float(m_cold_input) is not None else None

Cp = to_kj_per_kgC(to_float(Cp_input)) if to_float(Cp_input) is not None else None
U = to_float(U_input)
A = to_float(A_input)

# Check if all inputs are filled and valid
inputs_filled = all(x is not None for x in [Th_in, Th_out, m_hot, Tc_in, Tc_out, m_cold, Cp, U, A])

if inputs_filled:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Results Summary")

    Q_hot = m_hot * Cp * (Th_in - Th_out)
    Q_cold = m_cold * Cp * (Tc_out - Tc_in)
    Q_avg = (Q_hot + Q_cold) / 2

    delta_T1 = Th_in - Tc_out
    delta_T2 = Th_out - Tc_in
    LMTD = (delta_T1 - delta_T2) / np.log(delta_T1 / delta_T2) if delta_T1 != delta_T2 else delta_T1

    C_min = min(m_hot * Cp, m_cold * Cp)
    effectiveness = Q_avg / (C_min * (Th_in - Tc_in))

    st.success(f"Heat Duty (Avg): {Q_avg:.2f} kW")
    st.success(f"Log Mean Temperature Difference (LMTD): {LMTD:.2f} °C")
    st.success(f"Effectiveness: {effectiveness:.2f}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Temperature Profile Graph")

    x = np.array([0, 1])
    T_hot = np.array([Th_in, Th_out])
    T_cold = np.array([Tc_in, Tc_out])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, T_hot, '-o', label='Hot Fluid', color='red')
    ax.plot(x, T_cold, '-o', label='Cold Fluid', color='blue')
    ax.fill_between(x, T_cold, T_hot, color='orange', alpha=0.2)
    ax.set_xlabel("Position Along Heat Exchanger")
    ax.set_ylabel(f"Temperature ({unit_temp})")
    ax.set_title("Temperature Distribution")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # Download button
    if st.button("Download Graph as PNG"):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="temperature_profile.png">Click here if download does not start automatically</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.info("Please fill all input fields with valid numeric values to see results and graph.")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: gray;'>Made by Huzaifa Shahid | AI Data Engineer | Jadavpur University </div>", unsafe_allow_html=True)