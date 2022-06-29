import streamlit as st
from Pwr_Supply import PwrSupplyHandler
from KS_Switch import KSSwitchHandler

M_SWITCH_IP = '192.168.255.204'
S_SWITCH_IP = '192.168.255.206'
PWR_SUPP_IP = '192.168.255.207'

st.title('Bench Control GUI')
col1, col2 = st.columns(2)

with st.sidebar:
    st.header('Devices')
    device = st.radio('Pick a Device', ['Power Supply', 'Switch'])

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

info_bar = st.empty()
stat_bar = st.empty()

if(device == 'Power Supply'):
    e11.header('Power Supply')
    e12.header('Power Supply Data')
    # ps_ip_val = e21.text_input(label='Power Supply IP')
    # if e22.button('Update IP'):
        # PWR_SUPP_IP = ps_ip_val

    if e31.button('PS ON'):
        usupp = PwrSupplyHandler(tcp_ip=PWR_SUPP_IP)
        usupp.turn_on()
        usupp.close()
        stat_bar.success('Power Supply Turned On')

    if e41.button('PS OFF'):
        usupp = PwrSupplyHandler(tcp_ip=PWR_SUPP_IP)
        usupp.turn_off()
        usupp.close()
        stat_bar.success('Power Supply Turned Off')

    if e51.button('Get PS Data'):
        usupp = PwrSupplyHandler(tcp_ip=PWR_SUPP_IP)
        ps_data = usupp.get_psup_data()
        volt = ps_data['voltage']
        curr = ps_data['current']
        pwr = ps_data['power']
        state = ps_data['state']
        e32.text(f'Voltage : {volt} V')
        e42.text(f'Current : {curr} A')
        e52.text(f'Power : {pwr} W')
        e62.text(f'State: {state}')
        usupp.close()
        stat_bar.success('Fetched Power Supply Data')

elif (device == 'Switch'):
    info_bar.info('Press the **Switch Port** button for port and direction changes to take effect')
    e11.header('Switch')
    ant = e21.selectbox('Switch Ports', range(1,65))
    att = e41.selectbox('Master Switch Attenuation', range(10, 71, 10))
    if e61.button('Set Attenuation'):
        mswitch = KSSwitchHandler(tcp_ip=M_SWITCH_IP)
        mswitch.set_atten_val(att_name='ATT36', att_val=att)
        mswitch.close()
        stat_bar.success(f'Master Switch Attenuation Set to {att} dB')

    from_gen = False
    e12.header('Switch Routing')
    switch_dir = e22.radio('Route Direction', ['To Analyzer', 'From Generator'])
    if e52.button('Switch Port'):
        mswitch = KSSwitchHandler(tcp_ip=M_SWITCH_IP)
        sswitch = KSSwitchHandler(tcp_ip=S_SWITCH_IP)
        if(switch_dir == 'To Analyzer'):
            mswitch.set_out_to_san()
        elif(switch_dir == 'From Generator'):
            mswitch.set_out_from_gen()
            from_gen = True
        if(ant < 33):
            mswitch.switch_ant(ant)
        else:
            sswitch.slave_switch_ant(ant, master_switch_ip=M_SWITCH_IP, rf_source=from_gen)
        mswitch.close()
        sswitch.close()
        stat_bar.success(f'Switched to Port {ant} directing to {switch_dir}')

