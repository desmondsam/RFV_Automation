import time
from pyvisa.errors import VisaIOError

import RS_ZNB
import KS_Switch

class LossFileGetter():
    def __init__(self, vna_ip, master_switch_ip, slave_switch_ip, pipes, power, switch_attenuation, sweep_pts=7001, sweep_wait_time=45):
        self.vna = RS_ZNB.VNAHandler(tcp_ip=vna_ip, cust_name='VNA')
        self.master_switch = KS_Switch.KSSwitchHandler(tcp_ip=master_switch_ip, cust_name='Master_Switch')
        self.slave_switch = KS_Switch.KSSwitchHandler(tcp_ip=slave_switch_ip, cust_name='Slave_Switch')
        self.master_switch_ip = master_switch_ip
        self.pipes = pipes
        self.power = power
        self.sw_att = switch_attenuation
        self.sweep_points = sweep_pts
        self.sweep_time = sweep_wait_time
    
    def pause_seq(self):
        print('Waiting to complete connections')
        input('Press Enter when ready..')

    def low_pass_losses(self, pipe, ss=False):
        self.vna.set_stimulus(startf='100 kHz', stopf='5 GHz')
        self.vna.restart_sweep()
        time.sleep(self.sweep_time)
        file_name = f'Losses_Low_Pass_SwAtt_{self.sw_att}dB_Ant{pipe}'
        if(ss):
            self.vna.get_screenshot(ss_name=file_name)
        self.vna.save_csv(file_name=file_name)

    def high_pass_losses(self, pipe, ss=False):
        self.vna.set_stimulus(startf='6 GHz', stopf='12 GHz')
        self.vna.restart_sweep()
        time.sleep(self.sweep_time)
        file_name = f'Losses_High_Pass_SwAtt_{self.sw_att}dB_Ant{pipe}'
        if(ss):
            self.vna.get_screenshot(ss_name=file_name)
        self.vna.save_csv(file_name=file_name)
    
    def init_vna_switch_tx(self):
        print('Initializing VNA and Switch Intruments for TX Calibration')
        self.vna.clear()
        self.vna.reset()
        self.master_switch.clear()
        self.master_switch.reset()
        self.slave_switch.clear()
        self.slave_switch.reset()
        time.sleep(15)
        self.master_switch.set_atten_val(att_name='ATT33', att_val=0)
        self.master_switch.set_atten_val(att_name='ATT36', att_val=self.sw_att)
        tot_sw_att = self.master_switch.get_total_att()
        print(f'Total Attenuation of Switch is {tot_sw_att} dB')
        self.master_switch.set_out_to_san()
        self.vna.set_single_sweep()
        self.vna.set_pwr_bw(pwr = self.power)
        self.vna.set_average_sweep()
        self.vna.set_sweep_points()

    def get_loss_files(self, low_pass=True, high_pass=False, ss=False):
        self.init_vna_switch_tx()
        for pipe in self.pipes:
            print(f'Make Cable Connections for Pipe {pipe}')
            self.pause_seq()
            if(pipe < 33):
                self.master_switch.switch_ant(pipe) #Switch to Pipe
            else:
                self.slave_switch.slave_switch_ant(slave_ant=pipe, master_switch_ip=self.master_switch_ip)
            if(low_pass): 
                self.low_pass_losses(pipe=pipe, ss=ss)
            if(high_pass): 
                self.high_pass_losses(pipe=pipe, ss=ss)
        self.close()

    def close(self):
        self.vna.close()
        self.master_switch.close()
        self.slave_switch.close()

def main():
    ### Inputs ###
    vna_ip = '192.168.255.203'
    master_switch_ip = '192.168.255.204'
    slave_switch_ip = '192.168.255.206'
    pipe_list = [64]#range(33, 65)
    power = 1 #Not more than 10 dBm 
    switch_attenuation = 20 #Steps of 10 dB up to 70 dB
    sweep_points = 7001 #Number of Sweep Points
    sweep_wait_time = 45 #Time to wait for the sweep to be complete. Coupled with Number of points. More points = More time.
    low_pass = True #100KHz to 5GHz
    high_pass = False #6GHz to 12GHz
    screenshots = False #Set to True for screenshot of each sweep
    ### End Inputs ###
    # Default File Save Location in ZNB : r'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces'
    try:
        loss_files_getter = LossFileGetter(
            vna_ip=vna_ip,
            master_switch_ip=master_switch_ip,
            slave_switch_ip=slave_switch_ip,
            pipes=pipe_list,
            power=power,
            switch_attenuation=switch_attenuation,
            sweep_pts=sweep_points,
            sweep_wait_time=sweep_wait_time
            )
        loss_files_getter.get_loss_files(low_pass=low_pass, high_pass=high_pass, ss=screenshots)
        loss_files_getter.close()
    except VisaIOError:
        print ('Unable to Connect to VNA or Switch')
    except Exception as e:
        print(e)
          


if __name__ == '__main__':
    main()