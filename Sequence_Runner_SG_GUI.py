import streamlit as st
import General_Utils
from PIL import Image
from streamlit import cli as stcli
import sys

from pyvisa.errors import VisaIOError
import Test_Sequencer_SigGenTX
import logging

@st.cache()
def init_logger(log_fname):
    formatter = logging.Formatter(fmt='%(asctime)s-%(name)s-%(levelname)s >>> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger('Sequencer_GUI')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_fname, 'w') 
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter('%(name)s >>> %(message)s')
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

def run_sequencer(log_file_loc,spreadsheet_loc,sig_gen_ip,sig_analyzer_ip,master_switch_ip,slave_switch_ip,band,tGDelay,tGLength,trigSource,loops,band_edges,switch_attenuation,cal_file_loc,cal_file_name,sequences,pipe_list,channels,config_dl,refLvl,temps,screenshot_loc,init_instruments,stat_bar):
    General_Utils.make_dir_if_not(log_file_loc)
    General_Utils.make_dir_if_not(spreadsheet_loc)
    curr_time = General_Utils.curr_date_time_str()
    log_fname = '{}\Logs_{}.log'.format(log_file_loc, curr_time)
    spreadsheet_fname = 'Test_Data_{}'.format(curr_time)
    logger = init_logger(log_fname)
    try:
        runner = Test_Sequencer_SigGenTX.TestSequence(
            sig_gen_ip=sig_gen_ip, 
            sig_analyzer_ip=sig_analyzer_ip, 
            m_switch_ip=master_switch_ip,
            s_switch_ip=slave_switch_ip, 
            band=band, 
            tGDelay=tGDelay, 
            tGLength=tGLength, 
            trigSrc=trigSource, 
            loops=loops, 
            band_edges = band_edges, 
            sw_att = switch_attenuation,
            cal_file_loc = cal_file_loc,
            cal_file_name = cal_file_name
            )
        start_time = General_Utils.curr_time()
        logger.info('Starting Test Sequence')
        runner.run_sequences(sequences, pipe_list, channels, config_dl, refLvl, temps, spreadsheet_loc, spreadsheet_fname, screenshot_loc, init_instruments)
        end_time = General_Utils.curr_time()
        logger.info(f'Sequence Completed | Time Elapsed = {end_time - start_time}')
        stat_bar.success(f'Sequence Completed | Time Elapsed = {end_time - start_time}')
    except VisaIOError:
        logger.error('Unable to Connect to one or more Instruments')
        stat_bar.error('Unable to Connect to one or more Instruments')
    except FileNotFoundError:
        logger.error('File Not Found! Make sure you have the right location and file name for the Cal File.')
        stat_bar.error('File Not Found! Make sure you have the right location and file name for the Cal File.')
    except Exception as e:
        logger.error(e)
        stat_bar.error(e)

def config_sidebar():
    image = Image.open(r'D:\PyScripts\Images\Mavenir_Logo.png')

    with st.sidebar:
        st.image(image)
        st.header('Sequence Selector')
        sequencer = st.radio('Select Sequencer', ['TX Sequencer', 'RX Sequencer'])
    
    return sequencer

def get_main_container(title = 'RAPTOR', subheader='RF - Automated Performance Tests On Radios'):
    st.title(title)
    st.subheader(subheader)
    return st.container()

def config_ant_dup_exp(antenna_config):
    ac_c1, ac_c2 = antenna_config.columns(2)
    num_of_pipes = ac_c1.selectbox('Number of Pipes', [32, 64], index=1)
    dup_sel = ac_c1.selectbox('Duplexing', ['TDD', 'FDD'])
    pipes_selector = ac_c2.radio('Antenna Selector', ['Single', 'All', 'Un-Ordered', 'Range'])
    if(pipes_selector == 'All'):
        pipe_sel = range(1, num_of_pipes+1)
    elif(pipes_selector == 'Un-Ordered'):
        pipe_sel = ac_c2.multiselect('Pipes', range(1,num_of_pipes+1))
    elif(pipes_selector == 'Single'):
        pipe_sel_singVal = ac_c2.selectbox('Pipe', range(1,num_of_pipes+1))
        pipe_sel = [pipe_sel_singVal]
    elif(pipes_selector == 'Range'):
        pipe_tup = ac_c2.slider('Pipes', min_value=1, max_value=num_of_pipes, value=(4, 8))
        pipe_sel = range(pipe_tup[0], pipe_tup[1]+1)
    return {
        'Pipes' : pipe_sel,
        'Duplex' : dup_sel
    }

def main():
    sequencer = config_sidebar()

    main_body = get_main_container(title='RAPTOR', subheader='RF - Automated Performance Tests On Radios')

    if(sequencer == 'TX Sequencer'):
        main_body.header('TX Sequencer Inputs')
        
        antenna_config = main_body.expander('Antenna & Duplexing', expanded=True)
        pipe_dup_dict = config_ant_dup_exp(antenna_config)
        pipe_list = pipe_dup_dict['Pipes']
        dup_sel = pipe_dup_dict['Duplex']
        
        seq_form = main_body.form('Seq_Form_Inputs')
        col1, col2 = seq_form.columns(2)

        inst_ips = col1.expander('Instrument IPs')
        pwr_supp_ip = inst_ips.text_input('Power Supply IP', '192.168.255.207')
        sig_analyzer_ip = inst_ips.text_input('Analyzer IP', '192.168.255.202')
        master_switch_ip = inst_ips.text_input('Master Switch IP', '192.168.255.204')
        slave_switch_ip = inst_ips.text_input('Slave Switch IP', '192.168.255.206')
        sig_gen_ip = inst_ips.text_input('Signal Generator IP', '192.168.255.201')
        chamber_ip = inst_ips.text_input('Temp Chamber IP', '')

        ru_du_config = col2.expander('RU & DU Configurations')
        radio_ip = ru_du_config.text_input('Radio IP', '10.11.1.100')
        du_ip = ru_du_config.text_input('DU IP', '10.69.91.91')
        supp_volt = ru_du_config.slider(label='Power Supply Voltage', max_value=60, value=48, step=1)
        pwr_up_time = ru_du_config.slider(label='Radio Power Up Time (seconds)', max_value=300, value=180, step=60)

        carr_config = col2.expander('Carrier Configuration')
        # tModels = carr_config.multiselect('Test Models', ['1_1','1_2','3_1','3_2','3_3','3_1a','2','2a'])
        tModels = carr_config.selectbox('Test Models', ['1_1','1_2','3_1','3_2','3_3','3_1a','2','2a'])
        bw_list = [*range(5,26,5), *range(30,101,10), 200, 400]
        bw = carr_config.selectbox('Bandwidth', bw_list, index=12)
        scs = carr_config.selectbox('Sub-Carrier Spacing', [15, 30, 60, 120], index=1)
        carr_pwr = carr_config.number_input('Configured Carrier Power (dBm)', value=36.99)
        noc = carr_config.selectbox('Number Of Carriers', [1])
        sem_mask = carr_config.selectbox('SEM Mask', ['CAT B'])

        analyzer_config = col1.expander('Analyzer Parameters')
        refLvl = analyzer_config.number_input('Reference Level', value=40, step=5)
        trigSource = analyzer_config.selectbox('Trigger Source', ['EXT', 'IMM'])
        if(dup_sel == 'TDD'):
            tGDelay = analyzer_config.text_input('Trigger Delay (ms/ns/us)', '5.005ms')
            tGLength = analyzer_config.text_input('Trigger Gate Length (ms/ns/us)', '3.615ms')
        else:
            tGDelay = None
            tGLength = None

        freq_config = col2.expander('Frequency Configuration')
        band_edges = freq_config.slider('Band Edges', min_value=3000, max_value=4000, value=(3700,3980))
        channels = freq_config.multiselect('Channels', ['Bottom', 'Middle', 'Top'], default='Middle')
        band = freq_config.selectbox('5G NR Band', ['N77', 'N78'], index=1)

        test_cases = col1.expander('Sequences')
        ru_on_chk = test_cases.checkbox('Radio Power On')
        tx_on_chk = test_cases.checkbox('Start Transmission')
        aclr_meas_chk = test_cases.checkbox('ACLR')
        obue_meas_chk = test_cases.checkbox('OBUE')
        evm_meas_chk = test_cases.checkbox('EVM')
        if(dup_sel == 'TDD'):
            oop_meas_chk = test_cases.checkbox('TX On Off Power')
        else:
            oop_meas_chk = False
        obw_meas_chk = test_cases.checkbox('Occupied Bandwidth')
        pcon_meas_chk = test_cases.checkbox('Power Consumption')
        tx_off_chk = test_cases.checkbox('Stop Transmission')
        ru_off_chk = test_cases.checkbox('Radio Power Off')

        tc_ss = col2.expander('Screenshots')
        aclr_ss_chk = tc_ss.checkbox('ACLR Screenshot')
        obue_ss_chk = tc_ss.checkbox('OBUE Screenshot')
        evm_ss_chk = tc_ss.checkbox('EVM Screenshot')
        if(dup_sel == 'TDD'):
            oop_ss_chk = tc_ss.checkbox('TX OOP Screenshot')
        else:
            oop_ss_chk = False
        obw_ss_chk = tc_ss.checkbox('OBW Screenshot')

        test_config = col1.expander('Test Parameters')
        temps = test_config.multiselect('Temperatures', [-40, 25, 55], default=25)
        switch_attenuation = test_config.slider(label='Master Switch Attenuation', min_value=10, max_value=70, value=20, step=10)
        loops = test_config.slider('Loops', min_value=1, max_value=100, step=1, value=1)
        init_instruments = test_config.checkbox('Initialize Instruments', value=True, help='Preset Instruments')
        
        floc_fname_exp = seq_form.expander('Files and Locations')
        screenshot_loc = floc_fname_exp.text_input('Screenshot Save Location', r'\\tsclient\D\Zulu_RFV\Test_Sequence_Data\Screenshots')
        spreadsheet_loc = floc_fname_exp.text_input('Spreadsheet Save Location', r'D:\Zulu_RFV\Test_Sequence_Data')
        cal_file_loc = floc_fname_exp.text_input('Calibration File Location', r'D:\Zulu_RFV\Calibration_and_Spurious_Files')
        cal_file_name = floc_fname_exp.text_input('Calibration File Name', 'Bench_42_DD_TX_Inband_Losses_SwAtt_20dB')
        log_file_loc = floc_fname_exp.text_input('Log File Location', r'D:\Zulu_RFV\Test_Sequence_Data\Logs')

        misc_info = seq_form.expander('Test Bench and Miscellaneous')
        bench_info = misc_info.text_input('Bench Info', 'HWIV_Lab_Bench')
        radio_name = misc_info.text_input('Radio Name', 'Zulu')
        radio_build = misc_info.text_input('Radio Build', 'R1D')
        radio_serial = misc_info.text_input('Radio Serial Number', '123456')
        radio_sw = misc_info.text_input('Radio Software Version', '6.4.8')
        tester = misc_info.text_input('Tester Name', 'RFV Tester')
        tester_comm = misc_info.text_input('Tester Comment', '')

        got_seq_inps = seq_form.form_submit_button('Validate Inputs')
        status_bar = main_body.empty()

        if(got_seq_inps):
            config_dl = {
                'tm' : tModels, # Test Model of signal
                'duplex' : dup_sel, # Duplexing
                'bw' : bw, # Carrier Bandwidth
                'scs' : scs, # Sub Carrier Spacing
                'power' : carr_pwr, # Configured Carrier Power
                'noc' : noc, # Number of Carriers
                'sem_mask' : sem_mask
            }
            sequences = {
                'TX_ON' : tx_on_chk,
                'ACLR' : {'measure':aclr_meas_chk, 'ss':aclr_ss_chk},
                'OBUE' : {'measure':obue_meas_chk, 'ss':obue_ss_chk},
                'EVM' : {'measure':evm_meas_chk, 'ss':evm_ss_chk},
                'ON_OFF_PWR' : {'measure':oop_meas_chk, 'ss':oop_ss_chk}, #TDD Only
                'OBW' : {'measure':obw_meas_chk, 'ss':obw_ss_chk},
                'TX_OFF' : tx_off_chk,
            }
            cal_file_loc = fr'{cal_file_loc}'
            spreadsheet_loc = fr'{spreadsheet_loc}'
            screenshot_loc = fr'{screenshot_loc}' #tsclient only works if you have active remote desktop to the FSV
            log_file_loc = fr'{log_file_loc}'
            ###Running
            run_sequencer(log_file_loc,spreadsheet_loc,sig_gen_ip,sig_analyzer_ip,master_switch_ip,slave_switch_ip,band,tGDelay,tGLength,trigSource,loops,band_edges,switch_attenuation,cal_file_loc,cal_file_name,sequences,pipe_list,channels,config_dl,refLvl,temps,screenshot_loc,init_instruments,status_bar)
            ###########################################################
            # st.write(dup_sel)
            # st.write(pipe_list)
        
if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0], "--logger.level=error"]
        sys.exit(stcli.main())