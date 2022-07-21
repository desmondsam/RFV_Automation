import time
from operator import itemgetter
import Validate_Construct_Datasets
import Fetch_Path_Loss
import logging

import RS_FSV_SigAnalyzer
import KS_Switch

class TestSequence():
    def __init__(self, sig_analyzer_ip, switch_ip, s_switch_ip, band, tGDelay, tGLength, trigSrc, loops, band_edges, sw_att, cal_file_loc, cal_file_name, test_info):
        self.logger = logging.getLogger('Sequencer_GUI.TestSequencer')
        self.sig_analyzer = RS_FSV_SigAnalyzer.FSVHandler(sig_analyzer_ip, cust_name = 'SigAnalyzer')
        self.switch = KS_Switch.KSSwitchHandler(switch_ip, cust_name='Switch')
        self.s_switch = KS_Switch.KSSwitchHandler(s_switch_ip, cust_name = 'SlaveSwitch')
        self.master_switch_ip = switch_ip
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
        self.test_info = None
        if(test_info):
            self.test_info = test_info
    
    def plog(self, custom_str):
        self.logger.info(custom_str)
        print(custom_str)

    def initialize_instruments(self):
        self.plog('Initializing all instruments')
        self.sig_analyzer.initialize()
        self.switch.initialize()
        self.s_switch.initialize()
        time.sleep(30)
        self.switch.set_atten_val(att_name='ATT33', att_val=0)
        self.switch.set_atten_val(att_name='ATT36', att_val=self.sw_att)
        tot_sw_att = self.switch.get_total_att()
        self.plog(f'Total Attenuation of Switch is {tot_sw_att} dB')
        self.plog(f'Make sure you use cal/loss files you generated using {tot_sw_att} dB as switch attenuation')
        self.switch.set_out_to_san()
        self.sig_analyzer.set_ext_ref_clk()
        
    def setup_analyzer(self, sequences, frequency, bw, sig_file_name, sem_mask, noc, user_alloc_file):
        obue_sig_file_name = sig_file_name
        if(user_alloc_file):
            sig_file_name = None
        else:
            sig_file_name = sig_file_name
        if(sequences['ACLR']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G ACLR')
            self.sig_analyzer.sel_existing_mode('5G ACLR')
            self.sig_analyzer.setup_ACLR(freq=frequency, band=self.band, sig_file_name=sig_file_name, user_alloc=user_alloc_file, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
        if(sequences['OBUE']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G OBUE')
            self.sig_analyzer.sel_existing_mode('5G OBUE')
            if(self.rfbw > 200):
                fstart = self.band_edges[0] - 40
                fstop = self.band_edges[1] + 40
            else:
                fstart = self.band_edges[0] - 10
                fstop = self.band_edges[1] + 10
            self.sig_analyzer.setup_OBUE_5g(sig_file_name==obue_sig_file_name, user_alloc=None, freq=frequency, band=self.band, mask=sem_mask, fstart=fstart, fstop=fstop, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
        if(sequences['EVM']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G EVM')
            self.sig_analyzer.sel_existing_mode('5G EVM')
            self.sig_analyzer.setup_EVM_FErr(sig_file_name=sig_file_name, cust_alloc=user_alloc_file, noc=noc, freq=frequency, band=self.band, trigSrc=self.trigSrc)
        if(sequences['ON_OFF_PWR']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G TXOOP')
            self.sig_analyzer.sel_existing_mode('5G TXOOP')
            self.sig_analyzer.setup_tx_on_off_pwr(sig_file_name=sig_file_name, freq=frequency)
        if(sequences['OBW']['measure']):
            self.sig_analyzer.create_new_mode(mode = 'SANALYZER', name = 'Spec OBW')
            self.sig_analyzer.sel_existing_mode('Spec OBW')
            self.sig_analyzer.setup_OBW_spec(freq=frequency, bw=bw, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc=self.trigSrc)
   
    def pause_seq(self, pause_reason = None):
        self.plog('Sequence Paused : {}'.format(pause_reason))
        input('Press Enter to Continue..')
        self.plog('Sequence Resumed')
    
    def save_screenshot(self, test, ss_loc, pipe, channel, loop):
        self.sig_analyzer.ss_loc = ss_loc
        self.sig_analyzer.ss_name = f'{test}_P{pipe}_{channel}_Run{loop}'
        self.sig_analyzer.get_screenshot()
        
    def run_sequences(self, sequences, pipe_list, freq_chnl, config_dl, refLvl, temp, floc, fname, ss_loc, user_alloc_file):
        results = []
        tm, duplex, bw, scs, pwr, noc, sem_mask = itemgetter('tm', 'duplex', 'bw', 'scs', 'power', 'noc', 'sem_mask')(config_dl)
        sig_file_name = f'NR-FR1-TM{tm}__{duplex}_{bw}MHz_{scs}kHz' # Pre-Defined file to be loaded
        self.initialize_instruments()
        try:
            for loop in range(1, self.loops+1):
                self.plog(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                for frequency in freq_chnl:
                    channel = freq_chnl[frequency]
                    self.setup_analyzer(sequences, frequency, bw, sig_file_name, sem_mask, noc, user_alloc_file)
                    for pipe in pipe_list:
                        if(pipe < 33):
                            self.switch.switch_ant(pipe)
                        else:
                            self.s_switch.slave_switch_ant(pipe, self.master_switch_ip)
                        refLvlOffs = abs(Fetch_Path_Loss.fetch_loss(ant=pipe, freq=frequency, file_loc=self.cal_floc, fname=self.cal_fname))
                        time.sleep(5)
                        print('Waiting for DPD to Settle.')
                        if(sequences['ACLR']['measure']):
                            self.sig_analyzer.sel_existing_mode('5G ACLR')
                            # if(user_alloc_file):
                                # self.sig_analyzer.load_user_alloc(alloc_file=user_alloc_file)
                            pipe_aclr = self.sig_analyzer.measure_ACLR(ref_lvl=refLvl, rlvlOffs=refLvlOffs)
                            if(sequences['ACLR']['ss']):
                                self.save_screenshot('ACLR', ss_loc, pipe, channel, loop)
                            results += Validate_Construct_Datasets.get_acp_dataset(pipe_aclr, pipe, frequency, loop, bw, pwr, temp, tm, noc, sig_file_name, channel)
                        if(sequences['OBUE']['measure']):
                            self.sig_analyzer.sel_existing_mode('5G OBUE')
                            # if(user_alloc_file):
                                # self.sig_analyzer.load_user_alloc(alloc_file=user_alloc_file)
                            pipe_obue = self.sig_analyzer.meas_OBUE_5g(refLvl, refLvlOffs)
                            if(sequences['OBUE']['ss']):
                                self.save_screenshot('OBUE', ss_loc, pipe, channel, loop)
                            results += Validate_Construct_Datasets.get_sem_dataset(pipe_obue, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                        if(sequences['EVM']['measure']):
                            self.sig_analyzer.sel_existing_mode('5G EVM')
                            pipe_evm = self.sig_analyzer.measure_EVM_FErr(tm=tm, noc=noc, refLvl=refLvl, refLvlOffs=refLvlOffs)
                            if(sequences['EVM']['ss']):
                                self.save_screenshot('EVM', ss_loc, pipe, channel, loop)
                            results += Validate_Construct_Datasets.get_evm_dataset(pipe_evm, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                        if(sequences['ON_OFF_PWR']['measure']):
                            self.sig_analyzer.sel_existing_mode('5G TXOOP')
                            pipe_oop = self.sig_analyzer.meas_tx_on_off_pwr()
                            if(sequences['ON_OFF_PWR']['ss']):
                                self.save_screenshot('ON_OFF_PWR', ss_loc, pipe, channel, loop)
                            results += Validate_Construct_Datasets.get_oop_dataset(pipe_oop, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel)
                        if(sequences['OBW']['measure']):
                            self.sig_analyzer.sel_existing_mode('Spec OBW')
                            pipe_obw = self.sig_analyzer.meas_OBW(refLvl=refLvl, refLvlOffs=refLvlOffs)
                            if(sequences['OBW']['ss']):
                                self.save_screenshot('OBW', ss_loc, pipe, channel, loop)
                            status = Validate_Construct_Datasets.validate_data(pipe_obw, None, bw)
                            results.append(Validate_Construct_Datasets.generate_dataset(loop, pipe, frequency, channel, 'Occupied Bandwidth', 'Bandwidth', None, bw, pipe_obw, 'MHz', status, temp, tm, noc, bw, sig_file_name))
                    if(sequences['TOT_POW_CON']):
                        pwr_con = self.ru_pwr_supply.get_Pwr()
                        curr_draw = self.ru_pwr_supply.get_current()
                        status = Validate_Construct_Datasets.validate_data(pwr_con, None, None)
                        results.append(Validate_Construct_Datasets.generate_dataset(loop, None, frequency, channel, 'Power Consumption', 'Pow_Con', None, None, pwr_con, 'W', status, temp, tm, noc, bw, sig_file_name))
                        results.append(Validate_Construct_Datasets.generate_dataset(loop, None, frequency, channel, 'Power Consumption', 'Current', None, None, curr_draw, 'A', None, temp, tm, noc, bw, sig_file_name))
        except KeyboardInterrupt:
            self.plog('Sequencer Interrupted Manually!')
        except Exception as e:
            self.plog('Sequencer Interrupted')
            self.plog (e)  
        finally:
            Validate_Construct_Datasets.generate_excel(results, fname, floc, test_info=self.test_info)
            self.close_all()

    def close_all(self):
        self.plog('Closing Connections to Instruments')
        self.sig_analyzer.close()
        self.switch.close()
        self.s_switch.close()

def main():
    #### Inputs ####
    sig_analyzer_ip = '192.168.255.202' # Signal Analyzer IP
    switch_ip = '192.168.255.204'
    s_switch_ip = '192.168.255.206'
    freq_chnl = {
        # 3460 : 'Bottom',
        3840 : 'Middle',
        # 3750 : 'Top',
        # 634.5 : 'Middle',
    }
    config_dl = {
        'tm' : '1_1', # Test Model of signal
        'duplex' : 'TDD', # Duplexing
        'bw' : 100, # Carrier Bandwidth
        'scs' : 30, # Sub Carrier Spacing
        'power' : 38.75, # Configured Carrier Power
        'noc' : 1, # Number of Carriers
        'sem_mask' : 'CAT B'
    }
    band = 'N78'
    refLvl = 43.75 # Reference Level Setting for ACLR and OBUE
    tGDelay = '3ms' # Trigger Gate Delay
    tGLength = '3.5ms' # Trigger Gate Length
    trigSource = 'EXT'
    sequences = {
        'ACLR' : {'measure':True, 'ss':True},
        'OBUE' : {'measure':True, 'ss':True},
        'EVM' : {'measure':True, 'ss':True},
        'ON_OFF_PWR' : {'measure':False, 'ss':True}, #TDD Only
        'OBW' : {'measure':True, 'ss':True},
        'TOT_POW_CON' : False,
    }
    pipe_list = [33, 34, 49, 50]#range(1, 33) #List of Pipes
    temp = 25 #Temperature Setting for Test Sequence. Could become a list.
    loops = 1
    band_edges = (3700, 3980)
    switch_attenuation = 20
    user_alloc_file = r'C:\R_S\Instr\vr_testmac_qpsk.allocation'
    cal_file_loc = r'D:\Zulu_RFV\Calibration_and_Spurious_Files'
    cal_file_name = f'Bench_42_DD_TX_Inband_Losses_SwAtt_20dB'
    spreadsheet_loc = r'D:\Zulu_RFV\Test_Sequence_Data\LX2213MA64WA000110'
    spreadsheet_fname = 'Test_Seq_Data_QPSK'
    screenshot_loc = r'\\tsclient\D\Zulu_RFV\Test_Sequence_Data\Screenshots\LX2213MA64WA000110'
    test_info = {
        'Bench_ID' : 'RFV_Bench_41',
        'Radio' : 'Zulu',
        'Variant' : 'R1E',
        'Serial_Num' : 'LX2213MA64WA000110',
        'RU_SW' : '6.5.3',
        'DC_Voltage' : 48,
        'Tester_Comment': None,
        'Tester' : 'DesmondD',
    }
    #### End Inputs ####
    runner = TestSequence(
        sig_analyzer_ip=sig_analyzer_ip, 
        switch_ip = switch_ip,
        s_switch_ip = s_switch_ip,
        band=band, 
        tGDelay=tGDelay, 
        tGLength=tGLength, 
        trigSrc=trigSource, 
        loops=loops, 
        band_edges=band_edges,
        sw_att=switch_attenuation,
        cal_file_loc=cal_file_loc,
        cal_file_name=cal_file_name,
        test_info=test_info
        )
    runner.run_sequences(sequences, pipe_list, freq_chnl, config_dl, refLvl, temp, spreadsheet_loc, spreadsheet_fname, screenshot_loc, user_alloc_file)
    runner.close_all()
    print('Execution Completed')

if __name__ == "__main__":
    main()