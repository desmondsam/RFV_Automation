import streamlit as st
from Pwr_Supply import PwrSupplyHandler
from KS_Switch import KSSwitchHandler
from RS_FSV_SigAnalyzer import FSVHandler
import Fetch_Path_Loss
import time
from PIL import Image
from pyvisa.errors import VisaIOError

st.title('Test Bench Control')
col1, col2 = st.columns(2)

with st.sidebar:
    image = None
    try:
        image = Image.open('Mavenir_Logo.png')
    except FileNotFoundError:
        image = None
    if(image):
        st.image(image)
    st.header('Devices')
    device = st.radio('Pick a Device', ['Power Supply', 'Switch', 'Analyzer'], help='KS Power Supply (N5767),  KS Switch  (or)  R&S FSV')

with col1:
    e11 = st.empty()
    e21 = st.empty()
    e31 = st.empty()
    e41 = st.empty()
    e51 = st.empty()
    e61 = st.empty()
    e71 = st.empty()

with col2:
    e12 = st.empty()
    e22 = st.empty()
    e32 = st.empty()
    e42 = st.empty()
    e52 = st.empty()
    e62 = st.empty()
    e72 = st.empty()

full_page = st.empty()
ip_exp = st.expander('Update Device IP')
info_bar = st.empty()
stat_bar = st.empty()

if(device == 'Power Supply'):
    e11.header('Power Supply')
    ip_val = ip_exp.text_input(label='Power Supply IP', value='192.168.255.207')
    try:
        usupp = PwrSupplyHandler(ip_val)
    except VisaIOError:
        stat_bar.error('Cannot communicate with current IP. Please update IP')
        usupp = None
    if(usupp and usupp.device):
        if 'ps_state' not in st.session_state:
            supp_state = usupp.query('OUTP?')
            st.session_state['ps_state'] = supp_state

        with st.sidebar:

            stat_b = st.empty()

        e12.header('DC Settings')

        pwr_sett_form = e22.form('DC Settings')
        volt_lmt = pwr_sett_form.slider(label='Voltage Limit', max_value=60, value=48, step=1)
        curr_lmt = pwr_sett_form.slider(label='Current Limit', max_value=26.0, value=26.0, step=0.25)
        set_limits = pwr_sett_form.form_submit_button('Set DC Limits')

        e21.write('**Turn Power Supply ON**')
        if e31.button('PS ON'):
            usupp.turn_on()
            stat_bar.success('Power Supply Turned On')
            st.session_state['ps_state'] = True

        e41.write('**Turn Power Supply OFF**')
        if e51.button('PS OFF'):
            usupp.turn_off()
            stat_bar.success('Power Supply Turned Off')
            st.session_state['ps_state'] = False

        e61.write('**Get Power Supply Data**')
        if e71.button('Get PS Data'):
            info_bar.info(usupp.str_data())
            stat_bar.success(f'Fetched Power Supply Data')
        
        if set_limits:
            usupp.set_volt(volt_lmt)
            usupp.set_curr(curr_lmt)
            stat_bar.success(f'Power Supply Limits set to Voltage : {volt_lmt} V, Current : {curr_lmt} A')
        
        if(st.session_state['ps_state']==True):
            stat_b.success('Supply is : ON')
        else:
            stat_b.error('Supply is : OFF')
        usupp.close()

elif(device == 'Switch'):
    e11.header('Switch')
    ipcol1, ipcol2 = ip_exp.columns(2)
    with ipcol1:
        m_switch_ip = st.text_input('Master Switch IP', '192.168.255.204')
    with ipcol2:
        s_switch_ip = st.text_input('Slave Switch IP', '192.168.255.206')
    
    try:
        mswitch = KSSwitchHandler(tcp_ip=m_switch_ip)
        try:
            sswitch = KSSwitchHandler(tcp_ip=s_switch_ip)
        except VisaIOError:
            stat_bar.warning('Cannot communicate with Slave Switch. Antenna Selection Limited to 32')
            sswitch = None
    except VisaIOError:
        stat_bar.error('Cannot communicate with Master Switch IP. Please update IP')
        mswitch = None
    
    if(mswitch and mswitch.device):
        sw_form = e21.form('Switch_Form')
        if(sswitch and sswitch.device):
            num_of_ant = 64
        else:
            num_of_ant = 32

        ant = sw_form.selectbox('Antenna', range(1,num_of_ant+1))
        switch_dir = sw_form.radio('Route Direction', ['To Analyzer', 'From Generator'])
        from_gen = False
        switched = sw_form.form_submit_button('Switch Port')

        e12.header('Internal Attenuation')
        sw_att_form = e22.form('Switch_Att_Form')
        att = sw_att_form.slider(label='Master Switch Attenuation', min_value=10, max_value=70, value=20, step=10)
        att_changed = sw_att_form.form_submit_button('Set Attenuation')

        if switched:
            if(switch_dir == 'To Analyzer'):
                mswitch.set_out_to_san()
            elif(switch_dir == 'From Generator'):
                mswitch.set_out_from_gen()
                from_gen = True
            if(ant < 33):
                mswitch.switch_ant(ant)
            else:
                if(sswitch and sswitch.device):
                    sswitch.slave_switch_ant(ant, master_switch_ip=m_switch_ip, rf_source=from_gen)
            stat_bar.success(f'Switched to Port {ant} directing {switch_dir}')
        
        if att_changed:
            mswitch.set_atten_val(att_name='ATT36', att_val=att)
            stat_bar.success(f'Master Switch Attenuation Set to {att} dB')
        
        mswitch.close()
        if(sswitch and sswitch.device):
            sswitch.close()

elif(device == 'Analyzer'):
    ip_val = ip_exp.text_input('Analyzer IP', '192.168.255.202')
    try:
        fsv = FSVHandler(tcp_ip=ip_val)
    except VisaIOError:
        stat_bar.error('Cannot communicate with Analyzer IP. Please update IP')
        fsv = None
    if(fsv and fsv.device):
        freq_form = full_page.form('Sanalyzer_Freq')
        freq_form.header('Spectrum Analyzer')
        ff_c1, ff_c2 = freq_form.columns(2)
        freq_val = ff_c1.number_input('Frequency(MHz)', value=3840)
        ant = ff_c1.selectbox('Antenna', range(1,65))

        loss_file_loc = ff_c2.text_input('Loss File Location', r'D:\MidasRFV\Calibration_and_Spurious_Files')
        loss_file_name = ff_c2.text_input('Loss File Name', r'Bench_42_DD_TX_Inband_Losses_SwAtt_20dB')
        upd_path_loss = ff_c2.checkbox('Update Path Loss')
        if ff_c1.form_submit_button('Set Frequency/Path Loss'):
            fsv.set_center_freq(freq_val)
            if(upd_path_loss):
                ref_lvl_offs = Fetch_Path_Loss.fetch_loss(ant, freq_val, file_loc=loss_file_loc, fname=loss_file_name)
                time.sleep(5)
                fsv.ref_lvl_offset(abs(ref_lvl_offs))
                info_bar.info(f'Reference Level Offset set to {ref_lvl_offs} dB')
            stat_bar.success(f'Center Frequency Set to {freq_val} MHz')
        fsv.close()