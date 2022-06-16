"""GUI/Input Part of Test_Sequence"""

from pyvisa.errors import VisaIOError
import Test_Sequencer_MeasureOnly
import logging
from General_Utils import print_and_log as plog
import General_Utils

def get_inputs_run():
    ### Inputs ###
    log_file_loc = 'D:\MidasRFV\Test_Sequence_Data\Logs'
    spreadsheet_loc = 'D:\MidasRFV\Test_Sequence_Data'
    sig_analyzer_ip = '10.69.91.49' # Signal Analyzer IP
    freq_chnl = {
        # 3460 : 'Bottom',
        # 3605 : 'Middle',
        # 3750 : 'Top',
        634.5 : 'Middle',
    }
    config_dl = {
        'tm' : '3_1a', # Test Model of signal
        'duplex' : 'FDD', # Duplexing
        'bw' : 20, # Carrier Bandwidth
        'scs' : 15, # Sub Carrier Spacing
        'power' : 37, # Configured Carrier Power
        'noc' : 1, # Number of Carriers
        'sem_mask' : 'CAT B'
    }
    band = 'N71'
    refLvl = 42 # Reference Level Setting for ACLR and OBUE
    tGDelay = None # Trigger Gate Delay
    tGLength = None # Trigger Gate Length
    trigSource = 'IMM'
    sequences = {
        'TX_MEAS_ACLR' : True,
        'TX_MEAS_OBUE' : True,
        'TX_MEAS_EVM' : True,
        'TX_ON_OFF_PWR' : False,
        'TX_MEAS_OBW' : True,
        'TX_MEAS_SOBUE' : False,
    }
    pipe_list = [1]#range(1, 2) #List of Pipes
    temp = 25 #Temperature Setting for Test Sequence. Could become a list.
    loops = 1
    band_edges = (617, 652)
    ### End Inputs ###
    # seq_start_time = datetime.now()
    General_Utils.make_dir_if_not(log_file_loc)
    General_Utils.make_dir_if_not(spreadsheet_loc)
    curr_time = General_Utils.curr_date_time_str()
    log_fname = '{}\Logs_{}.log'.format(log_file_loc, curr_time)
    spreadsheet_fname = 'Demo_FDD_{}'.format(curr_time)
    logging.basicConfig(
        filename=log_fname, 
        filemode = 'w', 
        format='%(asctime)s : %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p', 
        encoding='utf-8', 
        level=logging.DEBUG
    )
    try:
        runner = Test_Sequencer_MeasureOnly.TestSequence(
            sig_analyzer_ip=sig_analyzer_ip, 
            band=band, 
            tGDelay=tGDelay, 
            tGLength=tGLength, 
            trigSrc=trigSource, 
            loops=loops, 
            band_edges = band_edges, 
            )
        plog('Starting Test Sequence')
        runner.run_sequences(sequences, pipe_list, freq_chnl, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname)
        plog('Sequence Completed')
    except VisaIOError:
        print ('Unable to Connect to one or more Instruments')
    except FileNotFoundError:
        print('File Not Found! Make sure you have the right location and file name for the Cal File.')
    except Exception as e:
        print (e)

if __name__ == "__main__":
    get_inputs_run()