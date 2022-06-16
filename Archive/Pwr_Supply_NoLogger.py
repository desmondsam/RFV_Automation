import visa_connections
import time

class PwrSupplyHandler(visa_connections.DeviceHandler):

    def set_timeout (self,timeout = 200000):
        self.timeout = timeout

    def turn_on(self):
        self.write('OUTP ON')
        time.sleep(1)
        print ("Supply Turned ON")

    def turn_off(self):
        self.write('OUTP OFF')
        time.sleep(1)
        print ("Supply Turned OFF")

    def get_voltage(self):
        volt = self.query_ascii_values('MEAS:VOLT?')
        time.sleep(1)
        return volt[0]

    def get_current(self):
        current = self.query_ascii_values('MEAS:CURR?')
        time.sleep(1)
        return current[0]

    def get_output_state(self):
        bool_state = self.query_ascii_values('OUTP?')
        time.sleep(1)
        if(int(bool_state[0]) == 0):
            output_state = 'OFF'
        else:
            output_state = 'ON'
        return (output_state)

    def get_Pwr(self):
        volt = self.get_voltage()
        current = self.get_current()
        power = volt * current
        return [volt, current, power]

    def reset(self):
        self.turn_off()
        time.sleep(2)
        self.turn_on()

    def set_volt(self, val = 48):
        self.write('VOLT {}'.format(val))
        print ('Voltage limit Set to {}V'.format(val))

    def set_curr(self, val = 26.25):
        self.write('CURR {}'.format(val))
        print ('Current limit Set to {}A'.format(val))
    
    def get_psup_data(self):
        volt = self.get_voltage()
        current = self.get_current()
        state = self.get_output_state()
        power = volt * current
        return {
            'voltage': volt, 
            'current': current, 
            'power': power,
            'state': state
        }
    
    def str_data(self):
        psup_data = self.get_psup_data()
        return('Voltage: {voltage}V, Current: {current}A, Power:{power}W, State: {state}'.format(**psup_data))


if __name__ == "__main__":
    #####Inputs#####
    unit_supp_gpib = '192.168.255.1'
    smod_supp_gpib = '15'
    #####End Inputs#####
    unit_supply = PwrSupplyHandler(tcp_ip = unit_supp_gpib)
    # sysmod_supply = PwrSupplyHandler(smod_supp_gpib)
    #unit_supply.set_timeout()
    # if unit_supply.get_output_state() == 0:
    #     unit_supply.turn_on()
    #     time.sleep(120)
    # volt = unit_supply.get_voltage()
    # current = unit_supply.get_current()
    # print volt, current
    # unit_supply.turn_off()
    # unit_supply.reset()
    # volt = sysmod_supply.get_voltage()
    # current = sysmod_supply.get_current()
    # print (volt, current)
    # unit_supply.turn_off()
    # print(unit_supply.query('*IDN?'))
    # sysmod_supply.turn_off()
    # sysmod_supply.turn_on()
    # unit_supply.set_volt()
    # unit_supply.set_curr()
    # unit_supply.turn_on()
    # sysmod_supply.set_volt()
    # sysmod_supply.set_curr()
    # current = sysmod_supply.get_current()
    # print current
    unit_supply.print_data()
    unit_supply.close()
    # sysmod_supply.close()
    
