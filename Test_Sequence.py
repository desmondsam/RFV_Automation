import time
from General_Utils import print_and_log as plog
import Validate_Construct_Datasets
from operator import itemgetter

import Pwr_Supply
import RS_SMW_SigGen
import RS_FSV_SigAnalyzer

class TestSequence():
    def __init__(self, pwr_supp_ip, sig_gen_ip, sig_analyzer_ip, band, tGDelay, tGLength, trigSrc, loops, band_edges):
        self.pwr_supp = Pwr_Supply.PwrSupplyHandler(pwr_supp_ip, cust_name = 'UnitSupply')
        self.sig_gen = RS_SMW_SigGen.SMWHandler(sig_gen_ip, cust_name = 'SigGen')
        self.sig_analyzer = RS_FSV_SigAnalyzer.FSVHandler(sig_analyzer_ip, cust_name = 'SigAnalyzer')
        self.band = band
        self.tGDelay = tGDelay
        self.tGLength = tGLength
        self.trigSrc = trigSrc
        self.loops = loops
        self.sig_analyzer.create_new_mode(mode='NR5G', name='5G Meas')
        self.sig_analyzer.create_new_mode(mode = 'SANALYZER', name = 'Spec Meas')
        self.band_edges = band_edges
        self.rfbw = band_edges[1]-band_edges[0]
    
    def psup_on_seq(self, supp_volt, pwr_up_time):
        self.pwr_supp.set_curr()
        self.pwr_supp.set_volt(supp_volt)
        self.pwr_supp.turn_on()
        time.sleep(pwr_up_time)
        plog(self.pwr_supp.str_data())
    
    def gen_sig_seq(self, frequency, sig_file_name):
        #This should be a DU/RU sequence.
        #Temporarily it is a Sig Gen sequence
        self.sig_gen.set_frequency(freq = frequency)
        self.sig_gen.set_rf_level(-20)
        self.sig_gen.set_rf_lvl_offset(-1)
        self.sig_gen.configure_5g_dl_baseband(sig_file_name)
        self.sig_gen.set_5g_mod_state('ON')
        self.sig_gen.set_rf_state('ON')
    
    def deact_sig_seq(self):
        self.sig_gen.set_rf_state('OFF')
        self.sig_gen.set_5g_mod_state('OFF')
    
    def psup_off_seq(self):
        self.pwr_supp.turn_off()
        time.sleep(1)
        plog(self.pwr_supp.str_data())
    
    def pause_seq(self, pause_reason = None):
        plog('Sequence Paused {}'.format(pause_reason))
        input('Press Enter to Continue..')
        plog('Sequence Resumed')
        
    def run_sequences(self, sequences, pipe_list, supp_volt, pwr_up_time, freq_chnl, config_dl, refLvl, temp, floc, fname):
        results = []
        tm, duplex, bw, scs, pwr, noc, sem_mask = itemgetter('tm', 'duplex', 'bw', 'scs', 'power', 'noc', 'sem_mask')(config_dl)
        sig_file_name = f'NR-FR1-TM{tm}__{duplex}_{bw}MHz_{scs}kHz' # Pre-Defined file to be loaded
        try:
            for loop in range(1, self.loops+1):
                plog(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                for frequency in freq_chnl:
                    channel = freq_chnl[frequency]
                    if(sequences['PS_ON']):
                        self.psup_on_seq(supp_volt, pwr_up_time)
                    if(sequences['TX_ON']):
                        self.gen_sig_seq(frequency, sig_file_name)
                    if(sequences['TX_MEAS_OBW']):
                        self.sig_analyzer.sel_existing_mode('Spec Meas')
                        self.sig_analyzer.setup_OBW_spec(freq=frequency, bw=bw, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc=self.trigSrc)
                        for pipe in pipe_list:
                            plog(f'Switch to Pipe {pipe} in Switch Code')
                            plog('Set RefLvlOffs to value from Switch/PathLoss Code. Hardcoded now.')
                            refLvlOffs = 0 #Should be a value from Get Path Loss code
                            pipe_obw = self.sig_analyzer.meas_OBW(refLvl=refLvl, refLvlOffs=refLvlOffs)
                            status = Validate_Construct_Datasets.validate_data(pipe_obw, None, bw)
                            results.append(Validate_Construct_Datasets.generate_dataset(loop, pipe, frequency, channel, 'Occupied Bandwidth', 'Bandwidth', None, bw, pipe_obw, 'MHz', status, temp, tm, noc, bw, sig_file_name))
                    if(sequences['TX_MEAS_ACLR']):
                        self.sig_analyzer.sel_existing_mode('5G Meas')
                        self.sig_analyzer.setup_ACLR(freq=frequency, band=self.band, testModel=sig_file_name, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
                        for pipe in pipe_list:
                            plog(f'Switch to Pipe {pipe} in Switch Code')
                            plog('Set RefLvlOffs to value from Switch/PathLoss Code. Hardcoded now.')
                            refLvlOffs = 0 #Should be a value from Get Path Loss code
                            pipe_aclr = self.sig_analyzer.measure_ACLR(ref_lvl=refLvl, rlvlOffs=refLvlOffs)
                            results += Validate_Construct_Datasets.get_acp_dataset(pipe_aclr, pipe, frequency, loop, bw, pwr, temp, tm, noc, sig_file_name, channel)
                    if(sequences['TX_MEAS_OBUE']):
                        if(self.rfbw > 200):
                            fstart = self.band_edges[0] - 40
                            fstop = self.band_edges[1] + 40
                        else:
                            fstart = self.band_edges[0] - 10
                            fstop = self.band_edges[1] + 10
                        self.sig_analyzer.sel_existing_mode('5G Meas')
                        self.sig_analyzer.setup_OBUE_5g(tm=sig_file_name, freq=frequency, band=self.band, mask=sem_mask, fstart=fstart, fstop=fstop, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
                        for pipe in pipe_list:
                            plog(f'Switch to Pipe {pipe} in Switch Code')
                            plog('Set RefLvlOffs to value from Switch/PathLoss Code. Hardcoded now.')
                            refLvlOffs = 0 #Should be a value from Get Path Loss code
                            pipe_obue = self.sig_analyzer.meas_OBUE_5g(refLvl, refLvlOffs)
                            results += Validate_Construct_Datasets.get_sem_dataset(pipe_obue, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                    if(sequences['TX_MEAS_EVM']):
                        self.sig_analyzer.sel_existing_mode('5G Meas')
                        self.sig_analyzer.setup_EVM_FErr(sig_file_name=sig_file_name, noc=noc, freq=frequency, band=self.band)
                        for pipe in pipe_list:
                            plog(f'Switch to Pipe {pipe} in Switch Code')
                            plog('Set RefLvlOffs to value from Switch/PathLoss Code. Hardcoded now.')
                            refLvlOffs = 0 #Should be a value from Get Path Loss code
                            pipe_evm = self.sig_analyzer.measure_EVM_FErr(tm=tm, noc=noc, refLvl=refLvl, refLvlOffs=refLvlOffs)
                            results += Validate_Construct_Datasets.get_evm_dataset(pipe_evm, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                    if(sequences['TX_OFF']):
                        self.deact_sig_seq()
                    if(sequences['PS_OFF']):
                        self.psup_off_seq()
            Validate_Construct_Datasets.generate_excel(results, fname, floc)
        except KeyboardInterrupt:
            plog('Sequencer Interrupted Manually!')
            Validate_Construct_Datasets.generate_excel(results, fname, floc)
        except Exception as e:
            Validate_Construct_Datasets.generate_excel(results, fname, floc)
            plog('Sequencer Interrupted')
            plog (e)  
        
    def close_all(self):
        plog('Closing Connections to Instruments')
        self.pwr_supp.close()
        self.sig_gen.close()
        self.sig_analyzer.close()

def main():
    #### Inputs ####
    pwr_supp_ip = '192.168.255.1' #IP to the power supply connected to the RU
    sig_gen_ip = '192.168.255.10' #IP to the Sig Gen, currently the acting-RU
    sig_analyzer_ip = '192.168.255.53' # Signal Analyzer IP
    supp_volt = 54  # Voltage setting of power supply connected to the radio
    pwr_up_time = 10 # Time for radio to power up in seconds
    freq_chnl = {
        # 3460 : 'Bottom',
        # 3610 : 'Middle',
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
        'TX_MEAS_OBW' : True,
        'TX_MEAS_ACLR' : False,
        'TX_MEAS_OBUE' : False,
        'TX_MEAS_EVM' : False,
        'TX_OFF' : True,
        'PS_OFF' : False,
    }
    pipe_list = range(1, 3) #List of Pipes
    temp = 25 #Temperature Setting for Test Sequence. Could become a list.
    loops = 1
    band_edges = (3410, 3800)
    spreadsheet_loc = 'C:\MidasRFV\Test_Sequence_Data'
    spreadsheet_fname = 'Test_Seq_Data_Sep'
    #### End Inputs ####
    runner = TestSequence(pwr_supp_ip=pwr_supp_ip, sig_gen_ip=sig_gen_ip, sig_analyzer_ip=sig_analyzer_ip, band=band, tGDelay=tGDelay, tGLength=tGLength, trigSrc=trigSource, loops=loops, band_edges = band_edges)
    runner.run_sequences(sequences, pipe_list, supp_volt, pwr_up_time, freq_chnl, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname)
    runner.close_all()
    plog('Execution Completed')

if __name__ == "__main__":
    main()