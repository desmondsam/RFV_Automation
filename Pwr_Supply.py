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
        return round(power, 2)

    def reset(self):
        self.turn_off()
        time.sleep(2)
        self.turn_on()

    def set_volt(self, val = 48):
        self.write('VOLT {}'.format(val))
        self.plog ('Voltage limit Set to {}V'.format(val))

    def set_curr(self, val = 26.25):
        self.write('CURR {}'.format(val))
        self.plog ('Current limit Set to {}A'.format(val))
    
    def get_psup_data(self):
        volt = self.get_voltage()
        current = self.get_current()
        state = self.get_output_state()
        power = round(volt * current, 2)
        return {
            'voltage': volt, 
            'current': current, 
            'power': power,
            'state': state
        }
    
    def str_data(self):
        psup_data = self.get_psup_data()
        return('Voltage: {voltage} V\nCurrent: {current} A\nPower:{power} W\nState: {state}'.format(**psup_data))


if __name__ == "__main__":
    #####Inputs#####
    unit_supp_gpib = '10.0.0.77'
    #####End Inputs#####
    unit_supply = PwrSupplyHandler(tcp_ip = unit_supp_gpib, cust_name='USupply')
    # sysmod_supply = PwrSupplyHandler(smod_supp_gpib)
    #unit_supply.set_timeout()
    # if unit_supply.get_output_state() == 0:
    #     unit_supply.turn_on()
    #     time.sleep(120)
    # volt = unit_supply.get_voltage()
    # current = unit_supply.get_current()
    # print volt, current
    #unit_supply.turn_off()
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
    #unit_supply.turn_on()
    # sysmod_supply.set_volt()
    # sysmod_supply.set_curr()
    # current = sysmod_supply.get_current()
    # print current
    # print(unit_supply.str_data())
    # unit_supply.turn_off()
    # print(unit_supply.str_data())
    # print(unit_supply.get_psup_data()['voltage'])
    print(unit_supply.query('OUTP?'))
    unit_supply.close()
    # sysmod_supply.close()
    
