import time
from operator import itemgetter
from General_Utils import print_and_log as plog
import Validate_Construct_Datasets

import RS_FSV_SigAnalyzer

class TestSequence():
    def __init__(self, sig_analyzer_ip, band, tGDelay, tGLength, trigSrc, loops, band_edges):
        self.sig_analyzer = RS_FSV_SigAnalyzer.FSVHandler(sig_analyzer_ip, cust_name = 'SigAnalyzer')
        self.band = band
        self.tGDelay = tGDelay
        self.tGLength = tGLength
        self.trigSrc = trigSrc
        self.loops = loops
        self.band_edges = band_edges
        self.rfbw = band_edges[1]-band_edges[0]

    def initialize_instruments(self):
        plog('Initializing all instruments')
        self.sig_analyzer.clear()
        self.sig_analyzer.reset()
        time.sleep(30)
        
    def setup_analyzer(self, sequences, frequency, bw, sig_file_name, sem_mask, noc):
        if(sequences['TX_MEAS_OBUE']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G OBUE')
            self.sig_analyzer.sel_existing_mode('5G OBUE')
            if(self.rfbw > 200):
                fstart = self.band_edges[0] - 40
                fstop = self.band_edges[1] + 40
            else:
                fstart = self.band_edges[0] - 10
                fstop = self.band_edges[1] + 10
            self.sig_analyzer.setup_OBUE_5g(tm=sig_file_name, freq=frequency, band=self.band, mask=sem_mask, fstart=fstart, fstop=fstop, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
        
        if(sequences['TX_MEAS_ACLR']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G ACLR')
            self.sig_analyzer.sel_existing_mode('5G ACLR')
            self.sig_analyzer.setup_ACLR(freq=frequency, band=self.band, testModel=sig_file_name, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
        if(sequences['TX_MEAS_EVM']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G EVM')
            self.sig_analyzer.sel_existing_mode('5G EVM')
            self.sig_analyzer.setup_EVM_FErr(sig_file_name=sig_file_name, noc=noc, freq=frequency, band=self.band, trigSrc=self.trigSrc)
        if(sequences['TX_ON_OFF_PWR']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G TXOOP')
            self.sig_analyzer.sel_existing_mode('5G TXOOP')
            self.sig_analyzer.setup_tx_on_off_pwr(sig_file_name=sig_file_name, freq=frequency)
        if(sequences['TX_MEAS_OBW']):
            self.sig_analyzer.create_new_mode(mode = 'SANALYZER', name = 'Spec OBW')
            self.sig_analyzer.sel_existing_mode('Spec OBW')
            self.sig_analyzer.setup_OBW_spec(freq=frequency, bw=bw, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc=self.trigSrc)
        if(sequences['TX_MEAS_SOBUE']):
            self.sig_analyzer.create_new_mode(mode = 'SANALYZER', name = 'Spec OBUE')
            self.sig_analyzer.sel_existing_mode('Spec OBUE')
            self.sig_analyzer.setup_obue_oob_spectrum(tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc=self.trigSrc)
   
    def pause_seq(self, pause_reason = None):
        plog('Sequence Paused {}'.format(pause_reason))
        input('Press Enter to Continue..')
        plog('Sequence Resumed')
        
    def run_sequences(self, sequences, pipe_list, freq_chnl, config_dl, refLvl, temp, floc, fname):
        results = []
        tm, duplex, bw, scs, pwr, noc, sem_mask = itemgetter('tm', 'duplex', 'bw', 'scs', 'power', 'noc', 'sem_mask')(config_dl)
        sig_file_name = f'NR-FR1-TM{tm}__{duplex}_{bw}MHz_{scs}kHz' # Pre-Defined file to be loaded
        self.initialize_instruments()
        try:
            for loop in range(1, self.loops+1):
                plog(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                for frequency in freq_chnl:
                    channel = freq_chnl[frequency]
                    self.setup_analyzer(sequences, frequency, bw, sig_file_name, sem_mask, noc)
                    refLvlOffs = 54.3
                    for pipe in pipe_list:
                        if(sequences['TX_MEAS_OBUE']):
                            self.sig_analyzer.sel_existing_mode('5G OBUE')
                            pipe_obue = self.sig_analyzer.meas_OBUE_5g(refLvl, refLvlOffs)
                            results += Validate_Construct_Datasets.get_sem_dataset(pipe_obue, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                        if(sequences['TX_MEAS_ACLR']):
                            self.sig_analyzer.sel_existing_mode('5G ACLR')
                            pipe_aclr = self.sig_analyzer.measure_ACLR(ref_lvl=refLvl, rlvlOffs=refLvlOffs)
                            results += Validate_Construct_Datasets.get_acp_dataset(pipe_aclr, pipe, frequency, loop, bw, pwr, temp, tm, noc, sig_file_name, channel)
                        if(sequences['TX_MEAS_EVM']):
                            self.sig_analyzer.sel_existing_mode('5G EVM')
                            pipe_evm = self.sig_analyzer.measure_EVM_FErr(tm=tm, noc=noc, refLvl=refLvl, refLvlOffs=refLvlOffs)
                            results += Validate_Construct_Datasets.get_evm_dataset(pipe_evm, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                        if(sequences['TX_ON_OFF_PWR']):
                            self.sig_analyzer.sel_existing_mode('5G TXOOP')
                            pipe_oop = self.sig_analyzer.meas_tx_on_off_pwr()
                            results += Validate_Construct_Datasets.get_oop_dataset(pipe_oop, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                        if(sequences['TX_MEAS_OBW']):
                            self.sig_analyzer.sel_existing_mode('Spec OBW')
                            pipe_obw = self.sig_analyzer.meas_OBW(refLvl=refLvl, refLvlOffs=refLvlOffs)
                            status = Validate_Construct_Datasets.validate_data(pipe_obw, None, bw)
                            results.append(Validate_Construct_Datasets.generate_dataset(loop, pipe, frequency, channel, 'Occupied Bandwidth', 'Bandwidth', None, bw, pipe_obw, 'MHz', status, temp, tm, noc, bw, sig_file_name))
                        if(sequences['TX_MEAS_SOBUE']):
                            self.sig_analyzer.sel_existing_mode('Spec OBUE')
                            sobue_offsets = Validate_Construct_Datasets.get_catb_offsets(self.band_edges, frequency, bw)
                            sobue_res = self.sig_analyzer.spec_obue_catb(sobue_offsets, refLvl=refLvl, refLvlOffs=refLvlOffs)
                            results += Validate_Construct_Datasets.get_sem_dataset(sobue_res, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel, tName='OBUE_Spectrum')
            Validate_Construct_Datasets.generate_excel(results, fname, floc)
            self.close_all()
        except KeyboardInterrupt:
            plog('Sequencer Interrupted Manually!')
            Validate_Construct_Datasets.generate_excel(results, fname, floc)
            self.close_all()
        except Exception as e:
            Validate_Construct_Datasets.generate_excel(results, fname, floc)
            plog('Sequencer Interrupted')
            plog (e)  
            self.close_all()
        
    def close_all(self):
        plog('Closing Connections to Instruments')
        self.sig_analyzer.close()

def main():
    #### Inputs ####
    sig_analyzer_ip = '192.168.255.202' # Signal Analyzer IP
    freq_chnl = {
        # 3460 : 'Bottom',
        # 3605 : 'Middle',
        3750 : 'Top',
        # 634.5 : 'Middle',
    }
    config_dl = {
        'tm' : '3_1a', # Test Model of signal
        'duplex' : 'FDD', # Duplexing
        'bw' : 20, # Carrier Bandwidth
        'scs' : 15, # Sub Carrier Spacing
        'power' : -20, # Configured Carrier Power
        'noc' : 1, # Number of Carriers
        'sem_mask' : 'CAT B'
    }
    band = 'N78'
    refLvl = -15 # Reference Level Setting for ACLR and OBUE
    tGDelay = None # Trigger Gate Delay
    tGLength = None # Trigger Gate Length
    trigSource = 'IMM'
    sequences = {
        'TX_MEAS_ACLR' : False,
        'TX_MEAS_OBUE' : True,
        'TX_MEAS_EVM' : False,
        'TX_ON_OFF_PWR' : False,
        'TX_MEAS_OBW' : False,
        'TX_MEAS_SOBUE' : False,
    }
    pipe_list = [1]#range(1, 2) #List of Pipes
    temp = 25 #Temperature Setting for Test Sequence. Could become a list.
    loops = 1
    band_edges = (3410, 3800)
    spreadsheet_loc = 'D:\MidasRFV\Test_Sequence_Data'
    spreadsheet_fname = 'Test_Seq_Data_FDD'
    #### End Inputs ####
    runner = TestSequence(
        sig_analyzer_ip=sig_analyzer_ip, 
        band=band, 
        tGDelay=tGDelay, 
        tGLength=tGLength, 
        trigSrc=trigSource, 
        loops=loops, 
        band_edges = band_edges, 
        )
    runner.run_sequences(sequences, pipe_list, freq_chnl, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname)
    runner.close_all()
    plog('Execution Completed')

if __name__ == "__main__":
    main()