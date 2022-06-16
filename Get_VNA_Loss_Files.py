import time
from pyvisa.errors import VisaIOError

import RS_ZNB
import KS_Switch

class LossFileGetter():
    def __init__(self, vna_ip, switch_ip, pipes, power, switch_attenuation):
        self.vna = RS_ZNB.VNAHandler(tcp_ip=vna_ip, cust_name='VNA')
        self.switch = KS_Switch.KSSwitchHandler(tcp_ip=switch_ip, cust_name='Switch')
        self.pipes = pipes
        self.power = power
        self.sw_att = switch_attenuation
    
    def pause_seq(self):
        print('Waiting to complete connections')
        input('Press Enter when ready..')

    def low_pass_losses(self, pipe, ss=False):
        self.vna.set_stimulus(startf='100 kHz', stopf='5 GHz')
        self.vna.restart_sweep()
        time.sleep(45)
        file_name = f'Losses_Low_Pass_SwAtt_{self.sw_att}dB_Ant{pipe}'
        if(ss):
            self.vna.get_screenshot(ss_name=file_name)
        self.vna.save_csv(file_name=file_name)

    def high_pass_losses(self, pipe, ss=False):
        self.vna.set_stimulus(startf='6 GHz', stopf='12 GHz')
        self.vna.restart_sweep()
        time.sleep(45)
        file_name = f'Losses_High_Pass_SwAtt_{self.sw_att}dB_Ant{pipe}'
        if(ss):
            self.vna.get_screenshot(ss_name=file_name)
        self.vna.save_csv(file_name=file_name)
    
    def init_vna_switch_tx(self):
        print('Initializing VNA and Switch Intruments for TX Calibration')
        self.vna.clear()
        self.vna.reset()
        self.switch.clear()
        self.switch.reset()
        time.sleep(15)
        self.switch.set_atten_val(att_name='ATT33', att_val=0)
        self.switch.set_atten_val(att_name='ATT36', att_val=self.sw_att)
        tot_sw_att = self.switch.get_total_att()
        print(f'Total Attenuation of Switch is {tot_sw_att} dB')
        self.switch.set_out_to_san()
        self.vna.set_single_sweep()
        self.vna.set_pwr_bw(pwr = self.power)
        self.vna.set_average_sweep()
        self.vna.set_sweep_points()

    def get_loss_files(self, low_pass=True, high_pass=False, ss=False):
        self.init_vna_switch_tx()
        for pipe in self.pipes:
            print(f'Make Cable Connections for Pipe {pipe}')
            self.pause_seq()
            self.switch.switch_ant(pipe) #Switch to Pipe
            if(low_pass): 
                self.low_pass_losses(pipe=pipe, ss=ss)
            if(high_pass): 
                self.high_pass_losses(pipe=pipe, ss=ss)
        self.close()

    def close(self):
        self.vna.close()
        self.switch.close()

def main():
    ### Inputs ###
    vna_ip = '192.168.255.203'
    switch_ip = '192.168.255.204'
    pipe_list = range(1, 33)
    power = 1 #Not more than 10 dBm 
    switch_attenuation = 20 #Steps of 10 dB up to 70 dB
    low_pass = True #100KHz to 5GHz
    high_pass = False #6GHz to 12GHz
    screenshots = False
    ### End Inputs ###
    # Default File Save Location in ZNB : r'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces'
    try:
        loss_files_getter = LossFileGetter(vna_ip=vna_ip, switch_ip=switch_ip, pipes=pipe_list, power=power, switch_attenuation=switch_attenuation)
        loss_files_getter.get_loss_files(low_pass=low_pass, high_pass=high_pass, ss=screenshots)
        loss_files_getter.close()
    except VisaIOError:
        print ('Unable to Connect to VNA or Switch')
    except Exception as e:
        print(e)
          


if __name__ == '__main__':
    main()