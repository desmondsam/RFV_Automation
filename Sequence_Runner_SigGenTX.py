"""GUI/Input Part of Test_Sequence"""

from pyvisa.errors import VisaIOError
import Test_Sequencer_SigGenTX
import logging
import General_Utils

def get_inputs_run():
    ### Inputs ###
    sig_gen_ip = '192.168.255.201' #IP to the Sig Gen, currently the acting-RU
    sig_analyzer_ip = '192.168.255.202' # Signal Analyzer IP
    master_switch_ip = '192.168.255.204' # Master Switch IP
    slave_switch_ip = '192.168.255.206' # Slave Switch IP
    channels = ['Top']
    config_dl = {
        'tm' : '3_1a', # Test Model of signal
        'duplex' : 'FDD', # Duplexing
        'bw' : 20, # Carrier Bandwidth
        'scs' : 30, # Sub Carrier Spacing
        'power' : -5, # Configured Carrier Power
        'noc' : 1, # Number of Carriers
        'sem_mask' : 'CAT B'
    }
    band = 'N78'
    refLvl = 0 # Reference Level Setting for ACLR and OBUE
    tGDelay = None # Trigger Gate Delay
    tGLength = None # Trigger Gate Length
    trigSource = 'IMM'
    #The following determines the test cases to be measured. Note that Analyzer related sequence keys have a dict to get screenshots.
    sequences = {
        'TX_ON' : True,
        'ACLR' : {'measure':True, 'ss':False},
        'OBUE' : {'measure':False, 'ss':False},
        'EVM' : {'measure':False, 'ss':False},
        'ON_OFF_PWR' : {'measure':False, 'ss':False}, #TDD Only
        'OBW' : {'measure':False, 'ss':False},
        'TX_OFF' : True,
    }
    pipe_list = [1]#range(1, 2) #List of Pipes
    temp = 25 #Temperature Setting for Test Sequence. Could become a list.
    loops = 1
    band_edges = (3410, 3800)
    switch_attenuation = 20
    cal_file_loc = r'D:\Zulu_RFV\Calibration_and_Spurious_Files'
    cal_file_name = f'Bench_42_DD_TX_Inband_Losses_SwAtt_20dB'
    spreadsheet_loc = r'D:\Zulu_RFV\Test_Sequence_Data'
    screenshot_loc = r'\\tsclient\D\Zulu_RFV\Test_Sequence_Data\Screenshots\Demo' #tsclient only works if you have active remote desktop to the FSV
    log_file_loc = 'D:\Zulu_RFV\Test_Sequence_Data\Logs'
    init_instruments = False
    ### End Inputs ###
    # seq_start_time = datetime.now()
    General_Utils.make_dir_if_not(log_file_loc)
    General_Utils.make_dir_if_not(spreadsheet_loc)
    curr_time = General_Utils.curr_date_time_str()
    log_fname = '{}\Logs_{}.log'.format(log_file_loc, curr_time)
    spreadsheet_fname = 'Test_Data_{}'.format(curr_time)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s-%(name)s-%(levelname)s >>> %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        # filename=log_fname,
        # filemode='w',
    )
    formatter = logging.Formatter(fmt='%(asctime)s-%(name)s-%(levelname)s >>> %(message)s')
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.INFO)
    # ch.setFormatter(formatter)
    fh = logging.FileHandler(log_fname, 'w') 
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(fh)
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(fh)
    # logger.addHandler(ch)
    try:
        runner = Test_Sequencer_SigGenTX.TestSequence(sig_gen_ip=sig_gen_ip, 
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
        logging.info('Starting Test Sequence')
        runner.run_sequences(sequences, pipe_list, channels, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname, screenshot_loc, init_instruments)
        end_time = General_Utils.curr_time()
        logging.info(f'Sequence Completed | Time Elapsed = {end_time - start_time}')
    except VisaIOError:
        logging.error('Unable to Connect to one or more Instruments')
    except FileNotFoundError:
        logging.error('File Not Found! Make sure you have the right location and file name for the Cal File.')
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    get_inputs_run()