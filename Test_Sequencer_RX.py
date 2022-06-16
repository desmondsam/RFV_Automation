"""
Author: DesmondD
Sequencer to do In band RX/Uplink 38.141 Performance Tests
Recommended Python/Conda Environment: https://mavenir365.sharepoint.com/:u:/s/RadioUnit/ESTQrCngfLRIpEsyG1kmmZ8BCjFktAcy15dacMSJTGhsHA?e=Fxfp0k
"""
import time
import General_Utils

from TestMacApp import TestMacSSH
from KS_VXG_SigGen import VXGHandler
from KS_Switch import KSSwitchHandler
from Pwr_Supply import PwrSupplyHandler
from Tenney_TempChamber import Tenney_TempChamber

class RXTestSequencer():
    def __init__(self, du_ip, sig_gen_ip, m_switch_ip, s_switch_ip, pwr_supp_ip, chamber_ip, supp_volt, pwr_up_time, cal_files_loc, wantSig_cal_fname, interSig_cal_fname):
        self.sig_gen = VXGHandler(sig_gen_ip, cust_name = 'SigGen')
        self.m_switch = KSSwitchHandler(m_switch_ip, cust_name = 'MasterSwitch')
        self.s_switch = KSSwitchHandler(s_switch_ip, cust_name = 'SlaveSwitch')
        self.ru_pwr_supply = PwrSupplyHandler(pwr_supp_ip, cust_name = 'RUPwrSupply')
        self.temp_chamber = None
        if(chamber_ip):
            self.temp_chamber = Tenney_TempChamber(tcpip=chamber_ip)
        self.master_switch_ip = m_switch_ip
        self.T1 = TestMacSSH(server = du_ip)
        self.T2 = TestMacSSH(server = du_ip)
        self.T3 = TestMacSSH(server = du_ip)
        self.supp_volt = supp_volt
        self.pwr_up_time = pwr_up_time
        self.cal_file_loc = cal_files_loc
        self.ws_cal_file = wantSig_cal_fname
        self.is_cal_file = interSig_cal_fname
    
    def close(self):
        self.sig_gen.close()
        self.m_switch.close()
        self.s_switch.close()
        self.ru_pwr_supply.close()
        self.T1.sshClose()
        self.T2.sshClose()
        self.T3.sshClose()
    
    def plog(self, custStr):
        General_Utils.print_and_log(custom_str=custStr, dev_name='Sequencer')
    
    def initialize_instruments(self):
        self.plog('Initializing all instruments')
        self.sig_gen.initialize()
        self.m_switch.initialize()
        self.s_switch.initialize()
        self.ru_pwr_supply.initialize()
        time.sleep(30)
        self.m_switch.set_out_from_gen()
    
    def pause_seq(self, pause_reason = None):
        self.plog('Sequence Paused {}'.format(pause_reason))
        input('Press Enter to Continue..')
        self.plog('Sequence Resumed')

    def config_DU_terminals(self, mode, timer, counter, testType, numero, bw, testNum):
        self.T1.startTerm1()
        self.T2.startTerm2()
        self.T3.startTerm3(mode = mode, timer=timer, counter=counter, testType=testType, numero=numero, bw=bw, testNum=testNum)
        self.T2.sshRead(11050)
    
    def config_RU_RX_On(self):
        self.pause_seq('Activate Carriers on the RU')
    
    def config_RU_RX_Off(self):
        self.pause_seq('Deactivate Carriers on the RU')
    
    def setup_sig_gen(self,trig_delay,trig_mode,trig_src,trig_cont_mode,trig_termination,trig_slope,sig_file_loc,sig_file_name):
        self.sig_gen.set_sig_file_mode(mode='WAV')
        self.sig_gen.load_wav_file(floc=sig_file_loc, fname=sig_file_name)
        self.sig_gen.set_wav_file_trig(mode=trig_mode, src=trig_src)
        self.sig_gen.config_cont_trig(cont_mode=trig_cont_mode)
        self.sig_gen.config_ext_trig(delay=trig_delay, termination=trig_termination, slope=trig_slope)
        self.sig_gen.ext_trig_playback_sync(sync='ON')
        self.sig_gen.sig_file_state(sig_state='ON')
        self.sig_gen.set_rf_state(state='ON')
        time.sleep(2)
    
    def setup_sig_gen_smw(self,floc,fname,trig_delay):
        self.sig_gen.manual_setup_ultest(floc, fname, trig_delay)
        self.sig_gen.set_rf_state(state='ON')
        self.sig_gen.set_5g_mod_state('ON')
        time.sleep(2)
    
    def meas_sensitivity(self, rf_lvl = -50):
        sensDict = {}
        step_size = 1
        sub_step_size = 0.1
        cycle = 1
        cycle_break = 999
        self.sig_gen.sig_file_state('OFF')
        self.sig_gen.sig_file_state('ON')
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
        print(f'Search Complete | RF Level {rf_lvl}, BLER = {sensDict[rf_lvl]}')
        return(rf_lvl)
    
    def psup_on_seq(self):
        self.ru_pwr_supply.set_curr()
        self.ru_pwr_supply.set_volt(self.supp_volt)
        self.ru_pwr_supply.turn_on()
        time.sleep(self.pwr_up_time)
        self.plog(f'Waiting {self.pwr_up_time}s for the RU to boot up')
        self.plog(self.ru_pwr_supply.str_data())
    
    def psup_off_seq(self):
        self.ru_pwr_supply.turn_off()
        time.sleep(1)
        self.plog(self.ru_pwr_supply.str_data())

    def run_sequences(self,sequences,pipes,freqs,temps,phyMode,phyTimer,phyCounter,tcType,tcNumero,bw,tcNum,tDelay,tMode,tSrc,tContMode,tTermination,tSlope,wavFloc,wavFname,sens_start_lvl,init_instruments):
        results = []
        if(init_instruments):
            self.initialize_instruments()
        try:
            for temp in temps:
                if(self.temp_chamber):
                    self.temp_chamber.soak_at_Temp(temp)
                    # self.plog(f'Set Chamber Temperature to {temp}C')
                #Might have to loop this as a list if doing multiple testcases
                self.config_DU_terminals(mode=phyMode, timer=phyTimer, counter=phyCounter, testType=tcType, numero=tcNumero, bw=bw, testNum=tcNum)
                self.setup_sig_gen(trig_delay=tDelay, trig_mode=tMode, trig_src=tSrc, trig_cont_mode=tContMode, trig_termination=tTermination, trig_slope=tSlope, sig_file_loc=wavFloc, sig_file_name=wavFname)
                for loop in range(1, self.loops+1):
                    self.plog(f'Collecting Data: Starting Loop {loop} of {self.loops}')
                    if(sequences['RU_ON']):
                        self.psup_on_seq()
                    for freq in freqs:
                        self.sig_gen.set_frequency(freq)
                        if(sequences['RX_ON']):
                            self.config_RU_RX_On()
                        for pipe in pipes:
                            if(pipe < 33):
                                self.m_switch.switch_ant(pipe)
                            else:
                                self.s_switch.slave_switch_ant(pipe, self.master_switch_ip, rf_source=True)
                            # ws_offset = 
                            # is_offset =
                            if(sequences['Sensitivity']):
                                results.append(self.meas_sensitivity(rf_lvl=sens_start_lvl))
                        if(sequences['RX_OFF']):
                            self.config_RU_RX_Off()
                    if(sequences['RU_OFF']):
                        self.psup_off_seq()
            print(results)
        except Exception as e:
            # Validate_Construct_Datasets.generate_excel(results, fname, floc)
            self.plog('Sequencer Interrupted')
            self.plog(e)  
            self.close()


def main():
    #### Inputs ####
    du_ip = '10.69.91.51'
    sig_gen_ip = '10.69.91.69'
    m_switch_ip = '192.168.255.204'
    s_switch_ip = '192.168.255.206'
    pwr_supp_ip = '192.168.255.207'
    chamber_ip = None
    supp_volt = 10  # Voltage setting of power supply connected to the radio
    pwr_up_time = 10 # Time for radio to power up in seconds
    freqs = [680.5]
    pipes = [1]
    temps = [25]
    phyMode = 4
    phyTimer = 0
    phyCounter = 0
    tcType = 1
    tcNumero = 0
    bw = 20
    tcNum = 1046
    sens_start_lvl = -55
    tDelay = '9.99985ms'
    tMode = 'CONT'
    tSrc = 'EXT'
    tContMode = 'TRIG'
    tTermination = 'HIGH'
    tSlope = 'POS'
    wavFloc = r'C:\VXG Files'
    wavFname = '1046-waveform.wfm'
    cal_files_loc = r'D:\MidasRFV\Calibration_and_Spurious_Files'
    ws_cal_fname = 'Bench_42_DD_RX_Zulu_BMT_Losses_VXG_WantedSignal'
    is_cal_fname = 'Bench_42_DD_RX_Zulu_BMT_Losses_VXG_Interferer'
    init_instruments = False
    sequences = {
        'RU_ON' : False,
        'RX_ON' : False,
        'Sensitivity' : True,
        'RX_OFF' : False,
        'RU_OFF' : False,
    }
    #### End Inputs ####
    runner = RXTestSequencer(du_ip=du_ip,
        sig_gen_ip=sig_gen_ip,
        m_switch_ip=m_switch_ip,
        s_switch_ip=s_switch_ip,
        pwr_supp_ip=pwr_supp_ip,
        chamber_ip=chamber_ip,
        supp_volt=supp_volt,
        pwr_up_time=pwr_up_time,
        cal_files_loc=cal_files_loc, 
        wantSig_cal_fname=ws_cal_fname, 
        interSig_cal_fname=is_cal_fname,
        )
    try:
        # runner.config_RU()
        runner.run_sequences(sequences,pipes,freqs,temps,phyMode,phyTimer,phyCounter,tcType,tcNumero,bw,tcNum,tDelay,tMode,tSrc,tContMode,tTermination,tSlope,wavFloc,wavFname,sens_start_lvl,init_instruments)
    except KeyboardInterrupt:
        print('Manual Interrupt')
        runner.close()
    except Exception as e:
        print(e)
        runner.close()

if __name__ == '__main__':
    main()