import visa_connections
import time

class PwrSupplyHandler(visa_connections.DeviceHandler):

    def set_timeout (self,timeout = 200000):
        self.timeout = timeout

    def turn_on(self):
        self.write('OUTP ON')
        time.sleep(1)
        self.plog ("Supply Turned ON")

    def turn_off(self):
        self.write('OUTP OFF')
        time.sleep(1)
        self.plog ("Supply Turned OFF")

    def get_voltage(self):
        volt = self.query_ascii_values('MEAS:VOLT?')
        time.sleep(2)
        return volt[0]

    def get_current(self):
        current = self.query_ascii_values('MEAS:CURR?')
        time.sleep(2)
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
        power = self.query_ascii_values('MEAS:POW?')[0]
        time.sleep(2)
        # return pwr[0]
        return power

    def reset(self):
        self.turn_off()
        time.sleep(5)
        self.turn_on()

    def set_volt(self, val = 48):
        self.write('VOLT {}'.format(val))
        self.plog ('Voltage limit Set to {}V'.format(val))

    def set_curr(self, val = 30):
        self.write('CURR {}'.format(val))
        self.plog ('Current limit Set to {}A'.format(val))
    
    def get_psup_data(self):
        volt = self.get_voltage()
        current = self.get_current()
        state = self.get_output_state()
        power = self.get_Pwr()
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
    unit_supp_ip = '192.168.255.207'
    #####End Inputs#####
    try:
        unit_supply = PwrSupplyHandler(tcp_ip = unit_supp_ip, cust_name='USupply')
        # unit_supply.set_volt()
        # unit_supply.set_curr()
        unit_supply.turn_on()
        print('Waiting for 5 seconds')
        time.sleep(10)
        # print(unit_supply.str_data())
        unit_supply.turn_off()
        # print(unit_supply.str_data())
        # unit_supply.reset()
        unit_supply.close()
    except:
        if(unit_supply):
            unit_supply.close()
    
