"""Establish Instrument Connection"""
import pyvisa as visa
import logging

class DeviceHandler(object):
    def __init__ (self, tcp_ip = None, usb_id = None, cust_name = 'Device', parent_logger=None):
        if(parent_logger):
            self.logger = logging.getLogger(f'{parent_logger}.{cust_name}')
        else:
            self.logger = logging.getLogger(f'{cust_name}')
        if(tcp_ip):
            self.device = visa.ResourceManager().open_resource('TCPIP0::{}::inst0::INSTR'.format(tcp_ip))
            self.device_cust_name = cust_name
        elif(usb_id):
            self.device = visa.ResourceManager().open_resource('USB0::{}::INSTR'.format(usb_id))
            self.device_cust_name = cust_name            
        else:
            self.device = None
            print('Error: No valid instrument IP or USB ID given')
        

    def plog(self, custom_str):
        # print_and_log(custom_str, self.device_cust_name, log_only)
        print(f'{self.device_cust_name} : {custom_str}')
        self.logger.info(custom_str)

    def clear(self):
        self.device.write('*CLS')                                #Clear Status Register of device
        self.device.write('*WAI')                                #Wait till Clear command is complete

    def reset(self):
        self.device.write('*RST')                                #Reset the device
        self.device.write('*WAI')                                #Wait till Reset command is complete
    
    def initialize(self):
        self.clear()
        self.reset()
        self.plog('Initializing (Preset) Instrument')
        
    def query(self,SCPICmd):
        return self.device.query(SCPICmd)

    def write(self,SCPICmd):
        self.device.write(SCPICmd)

    def query_ascii_values(self,SCPICmd):
        return self.device.query_ascii_values(SCPICmd)

    def read_raw(self):
        return self.device.read_raw()
    
    def read_bytes(self):
        return self.device.read_bytes()
    
    def get_chunk_size(self):
        return self.device.chunk_size

    def close(self):
        self.device.close()
        self.plog('Closed Connection')
    
    def check_identity(self):
        return (self.query('*IDN?'))

def main():
    try:
        my_dev = DeviceHandler(tcp_ip='192.168.255.205', cust_name='SigGen')
        # my_dev = DeviceHandler(usb_id='0x0AAD::0x0137::102850', cust_name='PowSens')
        # print (my_dev.query('OUTP?'))
        if(my_dev.device):
            print (my_dev.device)
            print (my_dev.check_identity()) 
            my_dev.close()
        else:
            print('No device attribute')
    except visa.errors.VisaIOError as e:
        print(e)
        print('Check if IP is valid')
    except Exception as e:
        print(e)
        if(my_dev):
            my_dev.close()

if __name__ == "__main__":
    main()