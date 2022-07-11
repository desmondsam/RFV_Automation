"""
Author: DesmondD
Sequencer to do In band RX/Uplink 38.141 Performance Tests
Recommended Python/Conda Environment: https://mavenir365.sharepoint.com/:u:/s/RadioUnit/ESTQrCngfLRIpEsyG1kmmZ8BCjFktAcy15dacMSJTGhsHA?e=Fxfp0k
"""
import time
import Fetch_Path_Loss
import General_Utils
import VC_Datasets_RX

from TestMacApp import TestMacSSH
from Pwr_Supply import PwrSupplyHandler
from Tenney_TempChamber import Tenney_TempChamber
from RS_SMW_SigGen import SMWHandler
import Mini_Circuit_SM

class RXTestSequencer():
    def __init__(self, du_ip, sig_gen_ip, ztm4sp8t_ip, ztm8_ip, loops, band_edges, xl_floc, xl_fname, cal_files_loc, wantSig_cal_fname, interSig_cal_fname, test_info):
        self.sig_gen = SMWHandler(sig_gen_ip, cust_name = 'SigGen')
        self.ztm4sp8t_ip = ztm4sp8t_ip
        self.ztm8_ip = ztm8_ip
        # self.ru_pwr_supply = PwrSupplyHandler(pwr_supp_ip, cust_name = 'RUPwrSupply')
        self.T1 = TestMacSSH(server = du_ip)
        self.T2 = TestMacSSH(server = du_ip)
        self.T3 = TestMacSSH(server = du_ip)
        # self.supp_volt = supp_volt
        # self.pwr_up_time = pwr_up_time
        self.cal_file_loc = cal_files_loc
        self.ws_cal_file = wantSig_cal_fname
        self.is_cal_file = interSig_cal_fname
        self.loops = loops
        self.band_edges = band_edges
        self.rfbw = band_edges[1]-band_edges[0]
        self.xl_floc = xl_floc
        self.xl_fname = xl_fname
        self.test_info = test_info
    
    def close(self):
        self.sig_gen.close()
        self.T1.sshClose()
        self.T2.sshClose()
        self.T3.sshClose()
    
    def initialize_instruments(self):
        print('Initializing all instruments')
        self.sig_gen.initialize()
        time.sleep(30)
    
    def pause_seq(self, pause_reason = None):
        print('Sequence Paused {}'.format(pause_reason))
        input('Press Enter to Continue..')
        print('Sequence Resumed')

    def config_DU_terminals(self, mode, timer, counter, testType, numero, bw, testNum, l1_home_dir, xranMod, envMod):
        self.T1.startTerm1(path=l1_home_dir, mod=xranMod, envMod=envMod)
        self.T2.startTerm2(path=l1_home_dir, envMod=envMod)
        self.T3.startTerm3(path=l1_home_dir, envMod=envMod, mode = mode, timer=timer, counter=counter, testType=testType, numero=numero, bw=bw, testNum=testNum)
        self.T2.sshRead(11050)
    
    def config_RU_RX_On(self):
        self.pause_seq('Activate Carriers on the RU')
    
    def config_RU_RX_Off(self):
        self.pause_seq('Deactivate Carriers on the RU')
       
    def meas_sensitivity(self, rf_lvl = -50):
        sensDict = {}
        step_size = 1
        sub_step_size = 0.1
        cycle = 1
        cycle_break = 99
        self.sig_gen.set_5g_mod_state('OFF')
        self.sig_gen.set_5g_mod_state('ON')
        self.sig_gen.sync_outp_ext_trig()
        while(cycle < cycle_break):
            self.sig_gen.set_rf_level(rf_lvl)
            time.sleep(20)
            bler = self.T2.blerQuery()
            sensDict[rf_lvl] = bler
            print(f'RF Level {rf_lvl}, BLER = {sensDict[rf_lvl]}')
            if(bler > 5):
                rf_lvl = round((rf_lvl + step_size),2)
                if(step_size==1):
                    step_size = sub_step_size
                else:
                    break
            rf_lvl = round((rf_lvl - step_size),2)
            cycle += 1
        # print(f'Search Complete | RF Level {rf_lvl}, BLER = {sensDict[rf_lvl]}')
        return [rf_lvl, sensDict[rf_lvl]]
    
    def meas_acs(self, freq, bw, ws_path_loss, is_path_loss, wavFloc, wavFname, tDelay, ws_rf_lvl):
        self.sig_gen.setup_ACSelectivity(freq=freq, bw=bw, trigDelVal=tDelay)
        self.sig_gen.recall_5g_mod_file(wavFloc, wavFname)
        self.sig_gen.set_rf_lvl_offset(ws_path_loss)
        self.sig_gen.set_rf_lvl_offset(is_path_loss, channel=2)
        self.sig_gen.set_rf_level(ws_rf_lvl)
        self.sig_gen.set_rf_level(-52, channel=2)
        time.sleep(20)
        pos_is_bler = self.T2.blerQuery()
        pos_is_freq = self.sig_gen.get_frequency(channel=2)
        print(f'Positive Interferer Freq {pos_is_freq}MHz | BLER {pos_is_bler}%')
        self.sig_gen.set_5g_mod_state('OFF', channel=1)
        self.sig_gen.set_5g_mod_state('OFF', channel=2)
        self.sig_gen.setup_ACSelectivity(freq=freq, bw=bw, trigDelVal=tDelay, freq_alloc='LOW')
        self.sig_gen.recall_5g_mod_file(wavFloc, wavFname)
        self.sig_gen.set_rf_lvl_offset(ws_path_loss)
        self.sig_gen.set_rf_lvl_offset(is_path_loss, channel=2)
        self.sig_gen.set_rf_level(ws_rf_lvl)
        self.sig_gen.set_rf_level(-52, channel=2)
        time.sleep(20)
        neg_is_bler = self.T2.blerQuery() 
        neg_is_freq = self.sig_gen.get_frequency(channel=2)
        print(f'Negative Interferer Freq {neg_is_freq}MHz | BLER {neg_is_bler}%')
        print([pos_is_bler, pos_is_freq], [neg_is_bler, neg_is_freq])
        self.sig_gen.set_rf_state('OFF')
        self.sig_gen.set_rf_state('OFF', channel=2)
        return[[pos_is_bler, pos_is_freq], [neg_is_bler, neg_is_freq]]
    
    def meas_gibb(self, freq, bw, ws_path_loss, is_path_loss, wavFloc, wavFname, tDelay, ws_rf_lvl):
        lower_res = []
        upper_res = []
        if(self.rfbw > 200):
            lower_stop = self.band_edges[0] - 60
            upper_stop = self.band_edges[1] + 60
        else:
            lower_stop = self.band_edges[0] - 20
            upper_stop = self.band_edges[1] + 20
        for is_pos in ['LOW', 'HIGH']:
            self.sig_gen.set_all_mod_rf_state('OFF')
            self.sig_gen.setup_General_IBB(freq=freq, bw=bw, trigDelVal=tDelay, freq_alloc=is_pos)
            self.sig_gen.recall_5g_mod_file(wavFloc, wavFname)
            self.sig_gen.set_rf_lvl_offset(ws_path_loss)
            self.sig_gen.set_rf_lvl_offset(is_path_loss, channel=2)
            self.sig_gen.set_rf_level(ws_rf_lvl)
            if(is_pos=='LOW'):
                lower_start = self.sig_gen.get_rf_level(channel=2)
                # inter_freq_list = range(lower_start, lower_stop-1, -1)
                inter_freq_list = range(lower_start, lower_start-6, -1)
                res_list = lower_res
            else:
                upper_start = self.sig_gen.get_rf_level(channel=2)
                # inter_freq_list = range(upper_start, upper_stop+1, 1)
                inter_freq_list = range(upper_start, upper_start+6, 1)
                res_list = upper_res
            for inter_freq in inter_freq_list:
                self.sig_gen.set_frequency(freq=inter_freq, channel=2)
                time.sleep(20)
                inter_bler = self.T2.blerQuery()
                res_list.append([inter_bler, inter_freq])
                print(f'{is_pos} Interferer Freq {inter_freq}MHz | BLER {inter_bler}%')
        return [lower_res, upper_res]



    def psup_on_seq(self):
        self.ru_pwr_supply.set_curr()
        self.ru_pwr_supply.set_volt(self.supp_volt)
        self.ru_pwr_supply.turn_on()
        time.sleep(self.pwr_up_time)
        print(f'Waiting {self.pwr_up_time}s for the RU to boot up')
        print(self.ru_pwr_supply.str_data())
    
    def psup_off_seq(self):
        self.ru_pwr_supply.turn_off()
        time.sleep(1)
        print(self.ru_pwr_supply.str_data())

    def run_sequences(self,sequences,pipes,freqs,temps,phyMode,phyTimer,phyCounter,tcType,tcNumero,bw,tcNum,l1_home_dir,xranMod,envMod,tDelay,wavFloc,wavFname,sens_start_lvl,ws_rf_lvl,init_instruments):
        results = []
        if(init_instruments):
            self.initialize_instruments()
        try:
            self.config_DU_terminals(mode=phyMode, timer=phyTimer, counter=phyCounter, testType=tcType, numero=tcNumero, bw=bw, testNum=tcNum, l1_home_dir=l1_home_dir, xranMod=xranMod, envMod=envMod)
            for temp in temps:
                print(f'Not Programmed: Set Chamber to {temp}C')
                for loop in range(1, self.loops+1):
                    print(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                    for pipe in pipes:
                        print(f'Testing: Switch to Pipe {pipe} and Set Path Loss in Sig Gen')
                        Mini_Circuit_SM.MN_Switch(f'Pipe{pipe-1}', self.ztm4sp8t_ip, self.ztm8_ip)
                        for freq in freqs:
                            ws_path_loss = Fetch_Path_Loss.fetch_loss(pipe, freq, self.cal_file_loc, self.ws_cal_file)
                            is_path_loss = Fetch_Path_Loss.fetch_loss(pipe, freq, self.cal_file_loc, self.is_cal_file)
                            if(sequences['Sensitivity']):
                                self.sig_gen.manual_setup_ultest(floc=wavFloc, fname=wavFname, trigDelay=tDelay)
                                self.sig_gen.set_frequency(freq=freq)   
                                self.sig_gen.set_rf_lvl_offset(offs=ws_path_loss, channel=1)
                                sens_res = self.meas_sensitivity(rf_lvl=sens_start_lvl)
                                status = VC_Datasets_RX.validate_data(meas_res=sens_res[0], spec_min=None, spec_max=-90)
                                results.append(VC_Datasets_RX.generate_dataset(loop=loop, pipe=pipe, testName='Sensitivity', measName='Static_Sensitivity', tx_freq=None, tx_pwr=None, tx_bw=bw, rx_freq=freq, rx_ws_lvl=sens_res[0], rx_bw=bw, rx_channel='Middle', test_mode='3GPP', bler=sens_res[1], spec_min=None, spec_max=-90, res=sens_res[0], unit='dBm', status=status, res_col='Wanted Sig Lvl'))
                            if(sequences['ACS']):
                                acs_res = self.meas_acs(freq, bw, ws_path_loss, is_path_loss, wavFloc, wavFname, tDelay, ws_rf_lvl)
                                for i in [0, 1]:
                                    if(i==0):
                                        mname = 'ACS - Positive Interferer'
                                    else:
                                        mname = 'ACS - Negative Interferer'
                                    res = acs_res[i][0]
                                    status = VC_Datasets_RX.validate_data(res, None, 5)
                                    results.append(VC_Datasets_RX.generate_dataset(loop=loop,pipe=pipe,testName='ACS',measName=mname,tx_freq=None,tx_pwr=None,tx_bw=bw,rx_freq=freq,rx_ws_lvl=ws_rf_lvl,rx_bw=bw,rx_channel='Middle',test_mode='3GPP',bler=res,spec_min=None,spec_max=5,res=res,unit='%',status=status,res_col='BLER',is_1_lvl=-52,is_1_freq=acs_res[i][1]))
                            if(sequences['GIBB']):
                                tname='General IBB'
                                gibb_res = self.meas_gibb(freq, bw, ws_path_loss, is_path_loss, wavFloc, wavFname, tDelay, ws_rf_lvl)
                                for i in [0, 1]:
                                    if(i==0):
                                        mname = 'General IBB - Lower'
                                    else:
                                        mname = 'General IBB - Upper'
                                    for iter_list in gibb_res[i]:
                                        res = iter_list[0]
                                        status = VC_Datasets_RX.validate_data(res, None, 5)
                                        results.append(VC_Datasets_RX.generate_dataset(loop=loop,pipe=pipe,testName=tname,measName=mname,tx_freq=None,tx_pwr=None,tx_bw=bw,rx_freq=freq,rx_ws_lvl=ws_rf_lvl,rx_bw=bw,rx_channel='Middle',test_mode='3GPP',bler=res,spec_min=None,spec_max=5,res=res,unit='%',status=status,res_col='BLER',is_1_lvl=-43,is_1_freq=iter_list[1]))
        except KeyboardInterrupt:
            print('Manual Interrupt')
        except Exception as e:
            # Validate_Construct_Datasets.generate_excel(results, fname, floc)
            print('Sequencer Interrupted')
            print(e)
        finally:
            General_Utils.namTupList_to_spreadsheet(results, self.xl_fname, self.xl_floc, self.test_info) 
            self.close()



def main():
    #### Inputs ####
    du_ip = '10.69.91.71'
    sig_gen_ip = '10.0.0.3'
    ztm4sp8t_ip = '10.0.0.51'
    ztm8_ip = '10.0.0.50'
    freqs = [3840]
    pipes = [1]
    temps = [25]
    loops = 1
    band_edges = (3700, 3980)
    phyMode = 4
    phyTimer = 0
    phyCounter = 0
    tcType = 2
    tcNumero = 1
    bw = 100
    tcNum = 33604
    l1_home_dir = r'/home/Load411/l1_package'
    xranMod='xran_mMIMO'
    envMod='-d'
    sens_start_lvl = -69
    ws_rf_lvl = -68
    tDelay = '9.9875ms'
    wavFloc = r'/var/user/chris' #r'C:\VXG Files'
    wavFname = '33604_qpsk_zulu'        #'1046-waveform.wfm'
    cal_files_loc = r'C:\Zulu\Cal_and_Spur_Files'
    ws_cal_fname = 'Bench_42_DD_RX_Zulu_BMT_Losses_VXG_WantedSignal'
    is_cal_fname = 'Bench_42_DD_RX_Zulu_BMT_Losses_VXG_Interferer'
    init_instruments = False
    sequences = {
        'RU_ON' : False,
        'RX_ON' : False,
        'Sensitivity' : True,
        'ACS' : True,
        'RX_OFF' : False,
        'RU_OFF' : False,
    }
    xl_loc = r'C:\Zulu\Test_Sequence_Data'
    xl_fname = f'Test_Seq_Data_Zulu_RX_{General_Utils.curr_date_time_str()}'
    test_info = {
        'Bench_ID' : 'RFV_Lab_Bench_39',
        'Radio' : 'Zulu',
        'Variant' : 'R1D',
        'Serial_Num' : 'Z12345',
        'RU_SW' : '6.4.8',
        'DC_Voltage' : None,
        'Tester_Comment': None,
        'Tester' : 'C_Repko',
    }
    #### End Inputs ####
    runner = RXTestSequencer(du_ip=du_ip,
        sig_gen_ip=sig_gen_ip,
        ztm4sp8t_ip = ztm4sp8t_ip,
        ztm8_ip = ztm8_ip,
        loops=loops,
        band_edges=band_edges,
        xl_floc = xl_loc,
        xl_fname = xl_fname,
        cal_files_loc = cal_files_loc,
        wantSig_cal_fname = ws_cal_fname,
        interSig_cal_fname = is_cal_fname,
        test_info=test_info,
        )
      
    # runner.config_RU()
    runner.run_sequences(
        sequences,
        pipes,
        freqs,
        temps,
        phyMode,
        phyTimer,
        phyCounter,
        tcType,
        tcNumero,
        bw,
        tcNum,
        l1_home_dir,
        xranMod,
        envMod,
        tDelay,
        wavFloc,
        wavFname,
        sens_start_lvl,
        ws_rf_lvl,
        init_instruments
        )
    

if __name__ == '__main__':
    main()