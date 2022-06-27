import visa_connections
import time

class KSSwitchHandler(visa_connections.DeviceHandler):

    def set_timeout (self, timeout = 200000):
        self.timeout = timeout
    
    def get_atten_val(self, att_name):
        att_val = self.query_ascii_values(f'ROUT:ATT? {att_name}')[0]
        time.sleep(2)
        return att_val
    
    def set_atten_val(self, att_name, att_val):
        self.write(f'ROUT:ATT {att_name}, {att_val}')
        time.sleep(2)
        self.plog(f'Switch Variable Attenuator {att_name} set to {att_val} dB')
    
    def get_total_att(self):
        att_33 = self.get_atten_val('ATT33')
        att_36 = self.get_atten_val('ATT36')
        time.sleep(2)
        return (att_33 + att_36)
    
    def set_out_to_san(self):
        self.write('ROUT:CLOS (@SW1(1), SW4(2), SW3(2), SW9(1))')
        time.sleep(2)
        self.plog('Switches set to output to Spectrum Analyzer')
    
    def get_switches_vals(self, ant):
        if ant in range(1, 9):
            sw8_val = 2
            sw_name = 'SW11'
        elif ant in range(9, 17):
            sw8_val = 3
            sw_name = 'SW5'
        elif ant in range(17, 25):
            sw8_val = 5
            sw_name = 'SW6'
        elif ant in range(25, 33):
            sw8_val = 6
            sw_name = 'SW7'

        if ant in [1, 9, 17, 25]:
            relay_val = 2
        elif ant in [2, 10, 18, 26]:
            relay_val = 3
        elif ant in [3, 11, 19, 27]:
            relay_val = 4
        elif ant in [4, 12, 20, 28]:
            relay_val = 5
        elif ant in [5, 13, 21, 29]:
            relay_val = 10
        elif ant in [6, 14, 22, 30]:
            relay_val = 9
        elif ant in [7, 15, 23, 31]:
            relay_val = 8
        elif ant in [8, 16, 24, 32]:
            relay_val = 7
        return[sw8_val, sw_name, relay_val]
    
    def switch_ant(self, ant):
        sw_vals = self.get_switches_vals(ant)        
        elem_list = f'(@SW8({sw_vals[0]}), {sw_vals[1]}({sw_vals[2]}))'
        self.write(f'ROUT:CLOS {elem_list}')
        time.sleep(2)
        self.plog(f'Switch has been set to output signal from antenna {ant}')
        
    def slave_switch_ant(self, slave_ant, master_switch_ip, rf_source = False):
        master_switch = KSSwitchHandler(tcp_ip = master_switch_ip, cust_name='Master_Switch')
        if(rf_source):
            master_switch.set_out_from_gen()
        else:
            master_switch.set_out_to_san()
        master_switch.connect_ext_chassis()
        master_switch.close()
        ant = slave_ant - 32
        self.switch_ant(ant)
        self.slave_connect_main_chassis()

    def query_switch_state(self, switch_name, nodes=[1, 2], op_cl='CLOS'):
        gen_str = '@'
        for node in nodes:
            gen_str += f'{switch_name}({node}),'
        gen_str = gen_str[:-1]
        state_res = self.query(f'ROUT:{op_cl}? ({gen_str})')
        time.sleep(2)
        return state_res
        # return gen_str
    
    def set_out_from_gen(self):
        self.write('ROUT:CLOS (@SW1(2), SW4(2), SW3(2), SW9(1))')
        time.sleep(2)
        self.plog('Switches set to output from Signal Generator')
    
    def connect_ext_chassis(self):
        self.write('ROUT:CLOS (@SW9(2))')
        time.sleep(2)
        self.plog('Connected to External Chassis Port')
    
    def slave_connect_main_chassis(self):
        self.write('ROUT:CLOS (@SW9(2))')
        time.sleep(2)
        self.plog('Connected to Main Chassis Port')


if __name__ == '__main__':
    try:
        ### Inputs ###
        switch_ip = '192.168.255.204'
        slave_switch_ip = '192.168.255.206'
        ant = 1
        from_sig_gen = False
        ### End Inputs ###
        switch = KSSwitchHandler(tcp_ip=switch_ip, cust_name='KS_Switch')
        switch_slave = KSSwitchHandler(tcp_ip=slave_switch_ip, cust_name='KS_Switch_Slave')
        # switch.clear()
        # switch.reset()
        # switch_slave.clear()
        # switch_slave.reset()
        # time.sleep(15)
        # switch.set_atten_val('ATT33', '0')
        # switch.set_atten_val('ATT36', '20')
        # print(switch.get_atten_val('ATT33'))
        # print(switch.get_atten_val('ATT36'))
        # print(switch.query_switch_state('SW1'))
        # print(switch.query_switch_state('SW4'))
        # print(switch.query_switch_state('SW3'))
        # print(switch.query_switch_state('SW9'))
        switch.set_out_to_san()
        if(from_sig_gen):
            switch.set_out_from_gen()
        if(ant < 33):
            switch.switch_ant(ant)
        else:
            switch_slave.slave_switch_ant(ant, switch_ip, rf_source=from_sig_gen)
        # print(f'Total Attenuation of Switch is {switch.get_total_att()} dB')
        switch.close()
        switch_slave.close()
    except Exception as e:
        print(e)
        if(switch):
            switch.close()
        if(switch_slave):
            switch_slave.close()
        