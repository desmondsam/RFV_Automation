import visa_connections
import time

class VNAHandler(visa_connections.DeviceHandler):

    def set_timeout (self, timeout = 200000):
        self.timeout = timeout
    
    def set_single_sweep(self, single = True, channel=1):
        if(single):
            self.write(f'INIT{channel}:CONT OFF')
            self.plog(f'Channel {channel} Sweep mode set to Single')
        else:
            self.write(f'INIT{channel}:CONT ON')
            self.plog(f'Channel {channel} Sweep mode set to Continuous')
    
    def set_stimulus(self, startf='100 kHz', stopf='5 GHz', channel=1):
        self.write(f'SENS{channel}:FREQ:STAR {startf}')
        self.write(f'SENS{channel}:FREQ:STOP {stopf}')
        self.plog(f'Set Channel {channel} Start Frequency as {startf} and Stop Frequency as {stopf}')
    
    def set_pwr_bw(self, pwr=-20, bw='1 kHz', channel=1):
        self.write(f'SOUR:POW {pwr}')
        time.sleep(1)
        self.plog(f'Set Power to {pwr} dBm')
        self.write(f'SENS{channel}:BAND {bw}')
        time.sleep(1)
        self.plog(f'Set Channel {channel} bandwidth to {bw}')
    
    def set_average_sweep(self, avg_cnt=5, channel=1):
        self.write(f'SENS{channel}:AVER:COUN {avg_cnt}')
        self.write(f'SENS{channel}:AVER ON')
        self.write(f'SENS{channel}:AVER:CLE')
        time.sleep(1)
        self.plog(f'Set Channel {channel} to average {avg_cnt} times and start anew')
        self.write(f'SENS{channel}:SWE:COUN {avg_cnt}')
        self.plog(f'Set Channel {channel} Sweep Count to {avg_cnt}')
    
    def set_sweep_points(self, num_of_pts = 7001, channel=1):
        self.write(f'SENS{channel}:SWE:POIN {num_of_pts}')
        self.plog(f'Set Channel {channel} to have {num_of_pts} sweep points')

    def restart_sweep(self, channel=1):
        self.write(f'INIT{channel}')
        self.plog(f'Restarted Sweep on Channel {channel}')
    
    def save_csv(self, file_loc=r'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces', file_name='Ant_Loss', channel=1):
        self.write(f"MMEM:STOR:TRAC:CHAN {channel}, '{file_loc}\{file_name}.csv', FORM, LOGP")
        self.plog(f'CSV file saved as {file_name}')
        time.sleep(5)
    
    def get_screenshot(self, ss_loc=r'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces', ss_name='Ant_Loss'):
        self.write('HCOP:DEV:LANG PNG')
        self.write(f"MMEM:NAME '{ss_loc}\{ss_name}'")
        self.write("HCOP:DEST 'MMEM'")
        self.write('HCOP')
        self.plog(f'Screenshot Saved as {ss_name}')
        time.sleep(3)

if __name__ == '__main__':
    try:
        ### Inputs ###
        vna_ip = '192.168.255.203'
        csv_loc = r'\\tsclient\D\Remote_Devices\VNA\Data'
        fname = 'Pipe_1_Loss'
        ### End Inputs ###
        znb = VNAHandler(tcp_ip=vna_ip, cust_name='VNA')
        # print(znb.check_identity())
        # znb.clear()
        # znb.reset()
        # time.sleep(10)
        # znb.set_single_sweep()
        # znb.set_stimulus()
        # znb.set_pwr_bw()
        # znb.set_average_sweep()
        # znb.set_sweep_points()
        # znb.restart_sweep()
        # time.sleep(40)
        znb.save_csv(file_name=fname)
        znb.get_screenshot(ss_name=fname)
        znb.save_csv(file_name='test')
        znb.get_screenshot(ss_name='test')
        znb.close()
    except Exception as e:
        print(e)
        if(znb):
            znb.close()

    