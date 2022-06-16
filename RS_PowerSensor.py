import visa_connections
import time

class PowSensHandler(visa_connections.DeviceHandler):

    def set_freq(self, freq):
        self.write(f'FREQ {freq}')
        self.plog(f'Frequency Set to {freq} Hz')
    
    def get_power(self):
        self.get_one_measurement()
        power = round(self.query_ascii_values('FETC?')[0], 2)
        self.plog(f'Power Measured : {power}')
        return power
    
    def toggle_cont(self, cont='ON'):
        self.write(f'INIT:CONT {cont}')
        self.plog(f'Continuous measurement mode turned {cont}')
    
    def set_avg_count(self, avg_cnt = 10):
        self.write(f'AVER:COUN {avg_cnt}')
        self.plog(f'Average Count Set to {avg_cnt}')
    
    def set_pow_unit(self, unit='DBM'):
        self.write(f'UNIT:POW {unit}')
        self.plog(f'Power results measured in {unit} units')
    
    def prep_measurement(self, avg_cnt=5):
        self.set_pow_unit()
        self.set_avg_count(avg_cnt=avg_cnt)
    
    def get_one_measurement(self):
        self.toggle_cont('OFF')
        self.write('INIT')
        time.sleep(2)


def main():
    #### Inputs ####
    powsens_usb_id = '0x0AAD::0x0137::102850'
    #### End Inputs ####
    PowSens = PowSensHandler(usb_id=powsens_usb_id, cust_name='PowSens')
    # PowSens.initialize()
    # time.sleep(5)
    # PowSens.set_freq(3750e6)
    # PowSens.prep_measurement()
    print(PowSens.get_power())
    PowSens.close()

if __name__ == '__main__':
    main()