import visa_connections
import time

class SMWHandler(visa_connections.DeviceHandler):

    def set_timeout (self,timeout = 200000):
        self.timeout = timeout
    
    def set_frequency(self, mode = 'FIX', freq = 3650):
        self.write('SOUR:FREQ:{} {} MHz'.format(mode, freq))
        print('Frequency set to {} MHz'.format(freq))
    
    def set_rf_level(self, level = -10):
        self.write('SOUR:POW:POW {}'.format(level))
        print('RF Level set to {} dBm'.format(level))
    
    def set_rf_lvl_offset(self, offs = 2):
        self.write('POW:OFFS {}'.format(offs))
        print('RF Level Offset set to {} dB'.format(offs))

    def set_rf_state(self, state = 'ON'):
        self.write(':OUTP {}'.format(state))
        print('RF turned {}'.format(state))
    
    def set_5g_mod_state(self, mod_5g = 'ON'):
        self.write('BB:NR5G:STAT {}'.format(mod_5g))
        print('5G Modulation (Baseband) turned {}'.format(mod_5g))
    
    def set_link_direction(self, link_direction = 'DOWN'):
        self.write(':BB:NR5G:LINK {}'.format(link_direction))
        print('5G Modulation direction set to {}LINK'.format(link_direction))
    
    def load_5g_dl_test_model(self, tmodel):
        self.write('SOUR:BB:NR5G:SETT:TMOD:DL "{}"'.format(tmodel))
    

def main():
    smw_ip = '192.168.255.10'
    smw = SMWHandler(tcp_ip = smw_ip)
    # smw.set_frequency(freq=3650)
    # smw.set_rf_lvl_offset(0)
    # smw.set_rf_level(level = -20)
    # smw.set_rf_state()
    # smw.set_5g_mod_state()
    # time.sleep(10)
    # smw.set_rf_state('OFF')
    # smw.set_5g_mod_state('OFF')
    # smw.set_link_direction()
    smw.load_5g_dl_test_model('NR-FR1-TM1_1__FDD_100MHz_30kHz')
    smw.close()

if __name__ == "__main__":
    main()