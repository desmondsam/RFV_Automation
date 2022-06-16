import time
from operator import itemgetter
from General_Utils import print_and_log as plog
import Validate_Construct_Datasets
import Fetch_Path_Loss

import Pwr_Supply
import RS_SMW_SigGen
import RS_FSV_SigAnalyzer
from KS_Switch import KSSwitchHandler

class TestSequence():
    def __init__(self, pwr_supp_ip, sig_gen_ip, sig_analyzer_ip, switch_ip, band, tGDelay, tGLength, trigSrc, loops, band_edges, sw_att, cal_file_loc, cal_file_name):
        # self.pwr_supp = Pwr_Supply.PwrSupplyHandler(pwr_supp_ip, cust_name = 'UnitSupply')
        self.sig_gen = RS_SMW_SigGen.SMWHandler(sig_gen_ip, cust_name = 'SigGen')
        self.sig_analyzer = RS_FSV_SigAnalyzer.FSVHandler(sig_analyzer_ip, cust_name = 'SigAnalyzer')
        self.switch = KSSwitchHandler(switch_ip, cust_name = 'Switch')
        self.band = band
        self.tGDelay = tGDelay
        self.tGLength = tGLength
        self.trigSrc = trigSrc
        self.loops = loops
        self.band_edges = band_edges
        self.rfbw = band_edges[1]-band_edges[0]
        self.sw_att = sw_att
        self.cal_floc = cal_file_loc
        self.cal_fname = cal_file_name

    def initialize_instruments(self):
        plog('Initializing all instruments')
        self.sig_analyzer.clear()
        self.sig_analyzer.reset()
        self.switch.clear()
        self.switch.reset()
        self.sig_gen.clear()
        self.sig_gen.reset()
        time.sleep(30)
        self.switch.set_atten_val(att_name='ATT33', att_val=0)
        self.switch.set_atten_val(att_name='ATT36', att_val=self.sw_att)
        tot_sw_att = self.switch.get_total_att()
        plog(f'Total Attenuation of Switch is {tot_sw_att} dB')
        plog(f'Make sure you use cal/loss files you generated using {tot_sw_att} dB as switch attenuation')
        self.switch.set_out_to_san()
        
    def setup_analyzer(self, sequences, frequency, bw, sig_file_name, sem_mask, noc):
        if(sequences['TX_MEAS_ACLR']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G ACLR')
            self.sig_analyzer.sel_existing_mode('5G ACLR')
            self.sig_analyzer.setup_ACLR(freq=frequency, band=self.band, testModel=sig_file_name, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
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
        self.initialize_instruments()
        try:
            for loop in range(1, self.loops+1):
                plog(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                if(sequences['PS_ON']):
                    self.psup_on_seq(supp_volt, pwr_up_time)
                for frequency in freq_chnl:
                    channel = freq_chnl[frequency]
                    if(sequences['TX_ON']):
                        self.gen_sig_seq(frequency, sig_file_name)
                        #time.sleep(dpd_settle_time)
                        #TestMAC DU/RU
                    self.setup_analyzer(sequences, frequency, bw, sig_file_name, sem_mask, noc)
                    
                    for pipe in pipe_list:
                        self.switch.switch_ant(pipe)
                        refLvlOffs = abs(Fetch_Path_Loss.fetch_loss(ant=pipe, freq=frequency, file_loc=self.cal_floc, fname=self.cal_fname))
                        time.sleep(5)
                        if(sequences['TX_MEAS_ACLR']):
                            self.sig_analyzer.sel_existing_mode('5G ACLR')
                            pipe_aclr = self.sig_analyzer.measure_ACLR(ref_lvl=refLvl, rlvlOffs=refLvlOffs)
                            results += Validate_Construct_Datasets.get_acp_dataset(pipe_aclr, pipe, frequency, loop, bw, pwr, temp, tm, noc, sig_file_name, channel)
                        if(sequences['TX_MEAS_OBUE']):
                            self.sig_analyzer.sel_existing_mode('5G OBUE')
                            pipe_obue = self.sig_analyzer.meas_OBUE_5g(refLvl, refLvlOffs)
                            results += Validate_Construct_Datasets.get_sem_dataset(pipe_obue, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
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
                    if(sequences['TOT_POW_CON']):
                        pwr_con = self.pwr_supp.get_Pwr[2]
                        status = Validate_Construct_Datasets.validate_data(pwr_con, None, None)
                        results.append(Validate_Construct_Datasets.generate_dataset(loop, None, frequency, channel, 'Power Consumption', 'Pow_Con', None, bw, pwr_con, 'W', status, temp, tm, noc, bw, sig_file_name))
                    if(sequences['TX_OFF']):
                        self.deact_sig_seq()
                        #TestMAC DU/RU
                if(sequences['PS_OFF']):
                    self.psup_off_seq()
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
        # self.pwr_supp.close()
        self.sig_gen.close()
        self.sig_analyzer.close()
        self.switch.close()

def main():
    #### Inputs ####
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
    cal_file_name = f'Bench_DD_Bench42_TX_Losses_SwAtt_20dB'
    spreadsheet_loc = 'D:\MidasRFV\Test_Sequence_Data'
    spreadsheet_fname = 'Test_Seq_Data_P_wSwitch'
    #### End Inputs ####
    runner = TestSequence(pwr_supp_ip=pwr_supp_ip, 
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
    runner.run_sequences(sequences, pipe_list, supp_volt, pwr_up_time, freq_chnl, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname)
    runner.close_all()
    plog('Execution Completed')

if __name__ == "__main__":
    main()