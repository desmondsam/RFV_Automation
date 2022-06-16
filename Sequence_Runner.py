"""GUI/Input Part of Test_Sequence"""

from pyvisa.errors import VisaIOError
import Test_Sequencer
import logging
from General_Utils import print_and_log as plog
import General_Utils

def get_inputs_run():
    ### Inputs ###
    log_file_loc = 'D:\MidasRFV\Test_Sequence_Data\Logs'
    spreadsheet_loc = 'D:\MidasRFV\Test_Sequence_Data'
    pwr_supp_ip = '192.168.255.1' #IP to the power supply connected to the RU
    sig_gen_ip = '192.168.255.201' #IP to the Sig Gen, currently the acting-RU
    sig_analyzer_ip = '192.168.255.202' # Signal Analyzer IP
    switch_ip = '192.168.255.204' # Switch IP
    supp_volt = 54  # Voltage setting of power supply connected to the radio
    pwr_up_time = 10 # Time for radio to power up in seconds
    freq_chnl = {
        # 3460 : 'Bottom',
        # 3605 : 'Middle',
        3750 : 'Top',
    }
    config_dl = {
        'tm' : '1_1', # Test Model of signal
        'duplex' : 'TDD', # Duplexing
        'bw' : 100, # Carrier Bandwidth
        'scs' : 30, # Sub Carrier Spacing
        'power' : -20, # Configured Carrier Power
        'noc' : 1, # Number of Carriers
        'sem_mask' : 'CAT B'
    }
    band = 'N78'
    refLvl = -15 # Reference Level Setting for ACLR and OBUE
    tGDelay = '18us' # Trigger Gate Delay
    tGLength = '3.7ms' # Trigger Gate Length
    trigSource = 'EXT'
    sequences = {
        'PS_ON' : False,
        #Should Have a Talk to RU Sequence
        'TX_ON' : True,
        'TX_MEAS_ACLR' : True,
        'TX_MEAS_OBUE' : False,
        'TX_MEAS_EVM' : False,
        'TX_ON_OFF_PWR' : False,
        'TX_MEAS_OBW' : False,
        'TX_MEAS_SOBUE' : False,
        'TOT_POW_CON' : False,
        'TX_OFF' : True,
        'PS_OFF' : False,
    }
    pipe_list = [8, 27]#range(1, 2) #List of Pipes
    temp = 25 #Temperature Setting for Test Sequence. Could become a list.
    loops = 1
    band_edges = (3410, 3800)
    switch_attenuation = 10
    cal_file_loc = r'D:\MidasRFV\Calibration_and_Spurious_Files'
    cal_file_name = f'Bench_27_Losses_SwAtt_10dB'
    ### End Inputs ###
    # seq_start_time = datetime.now()
    General_Utils.make_dir_if_not(log_file_loc)
    General_Utils.make_dir_if_not(spreadsheet_loc)
    curr_time = General_Utils.curr_date_time_str()
    log_fname = '{}\Logs_{}.log'.format(log_file_loc, curr_time)
    spreadsheet_fname = 'Test_Data_{}'.format(curr_time)
    logging.basicConfig(
        filename=log_fname, 
        filemode = 'w', 
        format='%(asctime)s : %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p', 
        encoding='utf-8', 
        level=logging.DEBUG
    )
    try:
        runner = Test_Sequencer.TestSequence(pwr_supp_ip=pwr_supp_ip, 
            sig_gen_ip=sig_gen_ip, 
            sig_analyzer_ip=sig_analyzer_ip, 
            switch_ip=switch_ip, 
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
        plog('Starting Test Sequence')
        runner.run_sequences(sequences, pipe_list, supp_volt, pwr_up_time, freq_chnl, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname)
        plog('Sequence Completed')
    except VisaIOError:
        print ('Unable to Connect to one or more Instruments')
    except FileNotFoundError:
        print('File Not Found! Make sure you have the right location and file name for the Cal File.')
    except Exception as e:
        print (e)

if __name__ == "__main__":
    get_inputs_run()