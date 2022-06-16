import time
from pyvisa.errors import VisaIOError
from collections import namedtuple as nt
from General_Utils import namTupList_to_spreadsheet

from RS_SMW_SigGen import SMWHandler
from RS_PowerSensor import PowSensHandler
from KS_Switch import KSSwitchHandler
from KS_VXG_SigGen import VXGHandler

class LossFileGetter():
    def __init__(self, sig_gen_ip, powSens_id, master_switch_ip, pipes, freqs, slave_switch_ip = None, sig_gen = 'VXG', rf_level = 0, sig_gen_channels=[1, 2]):
        self.powSens = PowSensHandler(usb_id=powSens_id, cust_name='PowSensor')
        self.master_switch = KSSwitchHandler(tcp_ip=master_switch_ip, cust_name='Master_Switch')
        if(slave_switch_ip):
            self.slave_switch = KSSwitchHandler(tcp_ip=slave_switch_ip, cust_name='Slave_Switch')
        if(sig_gen == 'SMW'):
            self.sigGen = SMWHandler(tcp_ip=sig_gen_ip, cust_name=sig_gen)
        elif(sig_gen == 'VXG'):
            self.sigGen = VXGHandler(tcp_ip=sig_gen_ip, cust_name=sig_gen)
        self.master_switch_ip = master_switch_ip
        self.pipes = pipes
        self.freqs = freqs
        self.rf_level = rf_level
        self.sig_gen_channels = sig_gen_channels
        self.DataSet = nt('DataSet', [
            'Pipe', 
            'Frequency',
            'Loss',
        ])
    
    def pause_seq(self):
        print('Waiting to complete connections')
        input('Press Enter when ready..')

    def init_instruments_rx(self):
        print('Initializing SigGen, Power Sensor and Switch Intruments for TX Calibration')
        self.sigGen.initialize()
        self.master_switch.initialize()
        if(self.slave_switch):
            self.slave_switch.initialize()
        self.powSens.initialize()
        time.sleep(15)
        self.master_switch.set_out_from_gen()
        for channel in self.sig_gen_channels:
            self.sigGen.set_rf_level(level=self.rf_level, channel=channel)
        self.powSens.prep_measurement()

    def gen_loss_files(self, bench_id='42', floc=r'D:\MidasRFV\Calibration_and_Spurious_Files'):
        self.init_instruments_rx()
        results_wanted = []
        results_interferer = []
        for pipe in self.pipes:
            print(f'Make Cable Connections for Pipe {pipe}')
            self.pause_seq()
            if(pipe < 33):
                self.master_switch.switch_ant(pipe) #Switch to Pipe
            else:
                if(self.slave_switch):
                    self.slave_switch.slave_switch_ant(slave_ant=pipe, master_switch_ip=self.master_switch_ip, rf_source=True)
            for freq in self.freqs:
                self.powSens.set_freq(freq * 1000000)
                for channel in self.sig_gen_channels:
                    self.sigGen.set_frequency(freq = freq, channel=channel)
                    self.sigGen.set_rf_state(state='ON', channel=channel)
                    power = self.powSens.get_power()
                    if(channel == 1):
                        results_wanted.append(self.DataSet(Pipe = pipe, Frequency=freq, Loss=power))
                    else:
                        results_interferer.append(self.DataSet(Pipe = pipe, Frequency=freq, Loss=power))
                    self.sigGen.set_rf_state(state='OFF', channel=channel)
        wanted_fname = f'Bench_{bench_id}_Losses_{self.sigGen.device_cust_name}_WantedSignal'
        inerferer_fname = f'Bench_{bench_id}_Losses_{self.sigGen.device_cust_name}_Interferer'
        namTupList_to_spreadsheet(resList=results_wanted, filename=wanted_fname, file_loc=floc)
        if(results_interferer):
            namTupList_to_spreadsheet(resList=results_interferer, filename=inerferer_fname, file_loc=floc)
        self.close()

    def close(self):
        self.sigGen.close()
        self.master_switch.close()
        self.powSens.close()
        if(self.slave_switch):
            self.slave_switch.close()

def main():
    ### Inputs ###
    sig_gen = 'VXG' #VXG or SMW
    sig_gen_ip = '192.168.255.205' #Coupled with sig_gen. Use the right IP of the instrument
    powSens_id = '0x0AAD::0x0137::102850' #USB ID Phrase
    master_switch_ip = '192.168.255.204'
    slave_switch_ip = '192.168.255.206'
    pipe_list = [1]#range(1, 65)
    freqs = [3710, 3750, 3840, 3930, 3970]
    rf_lvl = 0
    sig_gen_channels = [1]
    output_loc = r'D:\MidasRFV\Calibration_and_Spurious_Files' #Calibration File Save Location
    bench_id = '42_DD_RX_Zulu_BMT' #Test Bench Identifier with Calibration Tags
    ### End Inputs ###
    try:
        loss_files_getter = LossFileGetter(
            sig_gen_ip = sig_gen_ip,
            powSens_id = powSens_id,
            master_switch_ip = master_switch_ip,
            pipes = pipe_list,
            freqs = freqs,
            slave_switch_ip = slave_switch_ip,
            sig_gen = sig_gen,
            rf_level = rf_lvl,
            sig_gen_channels = sig_gen_channels, 
            )
        loss_files_getter.gen_loss_files(bench_id=bench_id, floc=output_loc)
        loss_files_getter.close()
    except VisaIOError:
        print ('Unable to Connect to VNA or Switch')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()