from pyModbusTCP.client import ModbusClient
import time
from pyModbusTCP import utils
import logging
from datetime import datetime

class Tenney_TempChamber():
    def __init__(self, tcpip=None):
        try:
            self.chamber = ModbusClient(host=tcpip, port=502, debug=False, timeout=30, unit_id=2)
        except ValueError:
            logging.error("Error with host or port params")
        self.logger = logging.getLogger('TempChamber')
    
    def plog(self, cust_str):
        print(cust_str)
        self.logger.info(cust_str)

    def open(self):
        self.chamber.open()
    
    def get_temperature(self):
        self.open()
        if self.chamber.is_open():
            register_vals = self.chamber.read_input_registers(13, 2)
            if(register_vals):
                float_val = [utils.decode_ieee(f) for f in utils.word_list_to_long(register_vals)]
            else:
                float_val = None
        self.close()
        return float_val[0]
    
    def set_temperature(self, temp=25.0):
        self.open()
        if self.chamber.is_open():
            input_reg_vals = self.chamber.read_input_registers(11, 2)
            self.chamber.write_multiple_registers(11, input_reg_vals)
            self.plog('Synchronized input and holding registers before writing new value')
            b32_l = [utils.encode_ieee(f) for f in [temp]]
            b16_l = utils.long_list_to_word(b32_l)
            self.chamber.write_multiple_registers(11, b16_l)
        self.close()
        self.plog(f'Chamber Temperature set to {temp}C')
    
    def toggle_chamb_light(self, light='ON'):
        if(light == 'ON'):
            light_bit = True
        else:
            light_bit = False
        self.open()
        if self.chamber.is_open():
            input_reg_vals = self.chamber.read_input_registers(0, 10)
            self.chamber.write_multiple_registers(0, input_reg_vals)
            reg_bits = self.chamber.read_coils(1, 16)
            reg_bits[13] = light_bit
            self.chamber.write_multiple_coils(1, reg_bits)
            # print(self.chamber.read_coils(1, 16))
        self.close()
        self.plog(f'Chamber Light Turned {light}')
    
    def get_chamber_status(self):
        self.open()
        if self.chamber.is_open():
            input_reg_vals = self.chamber.read_input_registers(0, 10)
            self.chamber.write_multiple_registers(0, input_reg_vals)
            reg_bits = self.chamber.read_coils(4, 16)
            time.sleep(5)
            print(reg_bits)
        self.close()
    
    def turn_chamber_on(self):
        self.open()
        if self.chamber.is_open():
            off_reg = [False for x in range(16)]
            self.chamber.write_multiple_coils(3, off_reg)
            reg_bits = self.chamber.read_coils(3, 16)
            print(f'Read {reg_bits}')
            reg_bits[13] = True
            self.chamber.write_multiple_coils(3, reg_bits)
            time.sleep(5)
            wreg_bits = self.chamber.read_coils(3, 16)
            print(f'Written {wreg_bits}')
            # print(self.chamber.read_input_registers(3))
        self.close()
    
    def turn_chamber_off(self):
        self.open()
        if self.chamber.is_open():
            off_reg = [False for x in range(16)]
            self.chamber.write_multiple_coils(3, off_reg)
            reg_bits = self.chamber.read_coils(3, 16)
            print(f'Read {reg_bits}')
            reg_bits[14] = True
            self.chamber.write_multiple_coils(3, reg_bits)
            time.sleep(5)
            wreg_bits = self.chamber.read_coils(3, 16)
            print(f'Written {wreg_bits}')
            # print(self.chamber.read_input_registers(3))
        self.close()
    
    def soak_at_Temp(self, temp, soak=60):
        Tnow = self.get_temperature()
        self.plog(f'Chamber temperature is now {Tnow}C')
        self.plog(f'Wait until Chamber temperature reaches {temp}C')
        start_time = datetime.now()
        self.set_temperature(temp)
        while(abs(Tnow-temp) >= 0.1):
            print('.', end='')
            time.sleep(2)
            Tnow = self.get_temperature()
        elapsed_time = datetime.now() - start_time
        self.plog(f'\nChamber temperature has reached {Tnow}C')
        self.plog(f'Time elapsed is {elapsed_time}')
        self.plog(f'Start soaking for {soak/60} min(s)')
        time.sleep(soak)
        self.plog('Soaking Complete')

    
    def close(self):
        self.chamber.close()

def main():
    TChamb = Tenney_TempChamber('192.168.255.101')
    # TChamb.set_temperature(35)
    # print(TChamb.get_temperature())
    # TChamb.toggle_chamb_light('OFF')
    # TChamb.get_chamber_status()
    # TChamb.turn_chamber_off()
    # TChamb.turn_chamber_on()
    TChamb.soak_at_Temp(temp=35, soak=60)
    TChamb.close()
if __name__ == '__main__':
    main()
