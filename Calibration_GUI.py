import streamlit as st
from PIL import Image

st.title('Path Loss Calibration')

with st.sidebar:
    image = None
    try:
        image = Image.open('Mavenir_Logo.png')
    except FileNotFoundError:
        image = None
    if(image):
        st.image(image)
    st.header('Calibration Procedure')
    cal_proc = st.radio('Choose a Calibration Procedure', options=['SigGen/PowSensor', 'VNA'])
    ip_exp = st.expander('Update Device IP')
    ip_exp.text_input(label='Signal Generator IP', value='192.168.255.201', key='sig_gen_ip')
    ip_exp.text_input(label='Power Sensor ID', value='0x0AAD::0x0137::102850', key='pwr_sens_id')
    ip_exp.text_input(label='Master Switch IP', value='192.168.255.204', key='m_switch_ip')
    ip_exp.text_input(label='Slave Switch IP', value='192.168.255.206', key='s_switch_ip')
    ip_exp.text_input(label='Network Analyzer IP', value='192.168.255.203', key='vna_ip')

if(cal_proc == 'SigGen/PowSensor'):
    full_page = st.container()
    full_page.header('Using a signal generator and power sensor')