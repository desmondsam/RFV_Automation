"""
Author: Desmond Dhivyanathan
Sequencer to do In band TX/Downlink 38.141 Performance Tests
Recommended Python/Conda Environment: https://mavenir365.sharepoint.com/:u:/s/RadioUnit/ESTQrCngfLRIpEsyG1kmmZ8BCjFktAcy15dacMSJTGhsHA?e=Fxfp0k
"""
import time
from operator import itemgetter
import General_Utils
import Validate_Construct_Datasets
import Fetch_Path_Loss
import logging

from RS_SMW_SigGen import SMWHandler
from RS_FSV_SigAnalyzer import FSVHandler
from KS_Switch import KSSwitchHandler
from Pwr_Supply import PwrSupplyHandler
from Tenney_TempChamber import Tenney_TempChamber

class TestSequence():
    def __init__(self, sig_gen_ip, sig_analyzer_ip, m_switch_ip, s_switch_ip, pwr_supp_ip, chamber_ip, band, tGDelay, tGLength, trigSrc, loops, band_edges, sw_att, cal_file_loc, cal_file_name, test_info):
        self.logger = logging.getLogger('Sequencer_GUI.TestSequencer')
        self.sig_gen = SMWHandler(sig_gen_ip, cust_name = 'SigGen')
        self.sig_analyzer = FSVHandler(sig_analyzer_ip, cust_name = 'SigAnalyzer')
        self.m_switch = KSSwitchHandler(m_switch_ip, cust_name = 'MasterSwitch')
        self.s_switch = KSSwitchHandler(s_switch_ip, cust_name = 'SlaveSwitch')
        self.ru_pwr_supply = PwrSupplyHandler(pwr_supp_ip, cust_name = 'RUPwrSupply')
        self.temp_chamber = None
        if(chamber_ip):
            self.temp_chamber = Tenney_TempChamber(tcpip=chamber_ip)
        self.master_switch_ip = m_switch_ip
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
        self.m_switch.initialize()
        self.s_switch.initialize()
        self.sig_gen.initialize()
        time.sleep(30)
        self.m_switch.set_atten_val(att_name='ATT33', att_val=0)
        self.m_switch.set_atten_val(att_name='ATT36', att_val=self.sw_att)
        tot_sw_att = self.m_switch.get_total_att()
        self.plog(f'Total Attenuation of Switch is {tot_sw_att} dB')
        self.plog(f'Make sure you use cal/loss files you generated using {tot_sw_att} dB as switch attenuation')
        self.m_switch.set_out_to_san()
        self.sig_analyzer.set_ext_ref_clk()
        
    def setup_analyzer(self, sequences, frequency, bw, sig_file_name, sem_mask, noc):
        if(sequences['ACLR']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G ACLR')
            self.sig_analyzer.sel_existing_mode('5G ACLR')
            self.sig_analyzer.setup_ACLR(freq=frequency, band=self.band, testModel=sig_file_name, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
        if(sequences['OBUE']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G OBUE')
            self.sig_analyzer.sel_existing_mode('5G OBUE')
            if(self.rfbw > 200):
                fstart = self.band_edges[0] - 40
                fstop = self.band_edges[1] + 40
            else:
                fstart = self.band_edges[0] - 10
                fstop = self.band_edges[1] + 10
            self.sig_analyzer.setup_OBUE_5g(tm=sig_file_name, freq=frequency, band=self.band, mask=sem_mask, fstart=fstart, fstop=fstop, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc = self.trigSrc)
        if(sequences['EVM']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G EVM')
            self.sig_analyzer.sel_existing_mode('5G EVM')
            self.sig_analyzer.setup_EVM_FErr(sig_file_name=sig_file_name, noc=noc, freq=frequency, band=self.band, trigSrc=self.trigSrc)
        if(sequences['ON_OFF_PWR']['measure']):
            self.sig_analyzer.create_new_mode(mode='NR5G', name='5G TXOOP')
            self.sig_analyzer.sel_existing_mode('5G TXOOP')
            self.sig_analyzer.setup_tx_on_off_pwr(sig_file_name=sig_file_name, freq=frequency)
        if(sequences['OBW']['measure']):
            self.sig_analyzer.create_new_mode(mode = 'SANALYZER', name = 'Spec OBW')
            self.sig_analyzer.sel_existing_mode('Spec OBW')
            self.sig_analyzer.setup_OBW_spec(freq=frequency, bw=bw, tGDelay=self.tGDelay, tGLength=self.tGLength, trigSrc=self.trigSrc)

    def psup_on_seq(self, supp_volt, pwr_up_time):
        self.ru_pwr_supply.set_curr()
        self.ru_pwr_supply.set_volt(supp_volt)
        self.ru_pwr_supply.turn_on()
        time.sleep(pwr_up_time)
        self.plog(f'Waiting {pwr_up_time}s for the RU to boot up')
        self.plog(self.ru_pwr_supply.str_data())

    def gen_sig_seq(self, frequency, pwr, sig_file_name):
        #This should be a DU/RU sequence.
        #Temporarily it is a Sig Gen sequence
        self.sig_gen.set_frequency(freq = frequency, channel=1)
        self.sig_gen.set_frequency(freq = frequency, channel=2)
        self.sig_gen.set_rf_level(pwr, channel=1)
        self.sig_gen.set_rf_level(pwr, channel=2)
        self.sig_gen.configure_5g_dl_baseband(sig_file_name, chan=1)
        self.sig_gen.configure_5g_dl_baseband(sig_file_name, chan=2)
        self.sig_gen.set_5g_mod_state('ON', channel=1)
        self.sig_gen.set_5g_mod_state('ON', channel=2)
        self.sig_gen.set_rf_state('ON', channel=1)
        self.sig_gen.set_rf_state('ON', channel=2)
    
    def deact_sig_seq(self):
        self.sig_gen.set_rf_state('OFF', channel=1)
        self.sig_gen.set_rf_state('OFF', channel=2)
        self.sig_gen.set_5g_mod_state('OFF', channel=1)
        self.sig_gen.set_5g_mod_state('OFF', channel=2)
    
    def psup_off_seq(self):
        self.ru_pwr_supply.turn_off()
        time.sleep(1)
        self.plog(self.ru_pwr_supply.str_data())
    
    def pause_seq(self, pause_reason = None):
        self.plog('Sequence Paused {}'.format(pause_reason))
        input('Press Enter to Continue..')
        self.plog('Sequence Resumed')
    
    def save_screenshot(self, test, ss_loc, pipe, channel, loop):
        self.sig_analyzer.ss_loc = ss_loc
        self.sig_analyzer.ss_name = f'{test}_P{pipe}_{channel}_Run{loop}'
        self.sig_analyzer.get_screenshot()
        
    def run_sequences(self, sequences, pipe_list, supp_volt, pwr_up_time, channels, config_dl, refLvl, temps, floc, fname, ss_loc, init_instruments):
        results = []
        tm, duplex, bw, scs, pwr, noc, sem_mask = itemgetter('tm', 'duplex', 'bw', 'scs', 'power', 'noc', 'sem_mask')(config_dl)
        sig_file_name = f'NR-FR1-TM{tm}__{duplex}_{bw}MHz_{scs}kHz' # Pre-Defined file to be loaded
        if(init_instruments):
            self.initialize_instruments()
        try:
            for temp in temps:
                if(self.temp_chamber):
                    self.temp_chamber.soak_at_Temp(temp)
                    # self.plog(f'Set Chamber Temperature to {temp}C')
                for loop in range(1, self.loops+1):
                    self.plog(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                    if(sequences['RU_ON']):
                        self.psup_on_seq(supp_volt, pwr_up_time)
                    for channel in channels:
                        frequency = General_Utils.get_BMT_freqs(self.band_edges[0], self.band_edges[1], bw)[channel]
                        if(sequences['TX_ON']):
                            self.gen_sig_seq(frequency, pwr, sig_file_name)
                        self.setup_analyzer(sequences, frequency, bw, sig_file_name, sem_mask, noc)
                        for pipe in pipe_list:
                            if(pipe < 33):
                                self.m_switch.switch_ant(pipe)
                            else:
                                self.s_switch.slave_switch_ant(pipe, self.master_switch_ip)
                            refLvlOffs = abs(Fetch_Path_Loss.fetch_loss(ant=pipe, freq=frequency, file_loc=self.cal_floc, fname=self.cal_fname))
                            time.sleep(5)
                            if(sequences['ACLR']['measure']):
                                self.sig_analyzer.sel_existing_mode('5G ACLR')
                                pipe_aclr = self.sig_analyzer.measure_ACLR(ref_lvl=refLvl, rlvlOffs=refLvlOffs)
                                if(sequences['ACLR']['ss']):
                                    self.save_screenshot('ACLR', ss_loc, pipe, channel, loop)
                                results += Validate_Construct_Datasets.get_acp_dataset(pipe_aclr, pipe, frequency, loop, bw, pwr, temp, tm, noc, sig_file_name, channel)
                            if(sequences['OBUE']['measure']):
                                self.sig_analyzer.sel_existing_mode('5G OBUE')
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
                        Validate_Construct_Datasets.generate_excel(results, f'{fname}_WIP', floc, self.test_info)
                        if(sequences['TOT_POW_CON']):
                            pwr_con = self.ru_pwr_supply.get_Pwr()
                            curr_draw = self.ru_pwr_supply.get_current()
                            status = Validate_Construct_Datasets.validate_data(pwr_con, None, None)
                            results.append(Validate_Construct_Datasets.generate_dataset(loop, None, frequency, channel, 'Power Consumption', 'Pow_Con', None, None, pwr_con, 'W', status, temp, tm, noc, bw, sig_file_name))
                            results.append(Validate_Construct_Datasets.generate_dataset(loop, None, frequency, channel, 'Power Consumption', 'Current', None, None, curr_draw, 'A', None, temp, tm, noc, bw, sig_file_name))
                        if(sequences['TX_OFF']):
                            self.deact_sig_seq()
                            #TestMAC DU/RU
                    if(sequences['RU_OFF']):
                        self.psup_off_seq()
        except KeyboardInterrupt:
            self.plog('Sequencer Interrupted Manually!')
        except Exception as e:
            self.plog('Sequencer Interrupted')
            self.plog(e)  
        finally:
            Validate_Construct_Datasets.generate_excel(results, fname, floc, self.test_info)
            self.close_all()
        
    def close_all(self):
        self.plog('Closing Connections to Instruments')
        self.sig_gen.close()
        self.sig_analyzer.close()
        self.m_switch.close()
        self.s_switch.close()
        self.ru_pwr_supply.close()

def main():
    #### Inputs ####
    sig_gen_ip = '192.168.255.201' #IP to the Sig Gen, currently the acting-RU
    sig_analyzer_ip = '192.168.255.202' # Signal Analyzer IP
    master_switch_ip = '192.168.255.204' # Master Switch IP
    slave_switch_ip = '192.168.255.206' # Slave Switch IP
    pwr_supp_ip = '192.168.255.207' #IP to the power supply connected to the RU
    chamber_ip = None
    supp_volt = 48  # Voltage setting of power supply connected to the radio
    pwr_up_time = 2 # Time for radio to power up in seconds
    channels = ['Middle']
    config_dl = {
        'tm' : '3_3', # Test Model of signal
        'duplex' : 'FDD', # Duplexing
        'bw' : 100, # Carrier Bandwidth
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
        'RU_ON' : True,
        'TX_ON' : True,
        'ACLR' : {'measure':True, 'ss':True},
        'OBUE' : {'measure':False, 'ss':False},
        'EVM' : {'measure':False, 'ss':False},
        'ON_OFF_PWR' : {'measure':False, 'ss':False}, #TDD Only
        'OBW' : {'measure':False, 'ss':False},
        'TOT_POW_CON' : True,
        'TX_OFF' : True,
        'RU_OFF' : True,
    }
    pipe_list = [1]#range(1, 65) #List of Pipes
    temps = [25] #Temperature Setting for Test Sequence.
    loops = 1
    band_edges = (3700, 3980)
    switch_attenuation = 20
    cal_file_loc = r'D:\Zulu_RFV\Calibration_and_Spurious_Files'
    cal_file_name = f'Bench_42_DD_TX_Inband_Losses_SwAtt_20dB'
    spreadsheet_loc = r'D:\Zulu_RFV\Test_Sequence_Data'
    spreadsheet_fname = f'Test_Seq_Data_Zulu_TM31_Emulator'
    screenshot_loc = r'\\tsclient\D\Zulu_RFV\Test_Sequence_Data\Screenshots'
    init_instruments = True
    test_info = {
        'Bench_ID' : 'RFV_Lab_Bench_42',
        'Radio' : 'Zulu',
        'Variant' : 'R1D',
        'Serial_Num' : 'Z366801202148000097',
        'RU_SW' : '6.4.8',
        'DC_Voltage' : supp_volt,
        'Tester_Comment': None,
        'Tester' : 'DesmondD',
    }
    #### End Inputs ####
    runner = TestSequence(
        sig_gen_ip=sig_gen_ip, 
        sig_analyzer_ip=sig_analyzer_ip, 
        m_switch_ip=master_switch_ip,
        s_switch_ip=slave_switch_ip,
        pwr_supp_ip=pwr_supp_ip,
        chamber_ip=chamber_ip,  
        band=band, 
        tGDelay=tGDelay, 
        tGLength=tGLength, 
        trigSrc=trigSource, 
        loops=loops, 
        band_edges = band_edges, 
        sw_att = switch_attenuation,
        cal_file_loc = cal_file_loc,
        cal_file_name = cal_file_name,
        test_info = test_info
        )
    runner.run_sequences(sequences, pipe_list, supp_volt, pwr_up_time, channels, config_dl, refLvl, temps, spreadsheet_loc, spreadsheet_fname, screenshot_loc, init_instruments)
    # runner.close_all()
    # runner.plog('Execution Completed')

if __name__ == "__main__":
    main()