import MiniCircuits_RC_4SPDT_A26_HTTP
import time


def get_switch_details(Pipe_number):
    #            (pipe#: 'SP8T#,SP8TCH#,SP2T#,SP2TCH#,SP4T#,SP4TCH#)
    Pipe_Details={'Pipe0': '1 1 1A 1 3 1 ',
                  'Pipe1': '1 2 1A 1 3 1',
                  'Pipe2': '1 3 1A 1 3 1',
                  'Pipe3': '1 4 1A 1 3 1',
                  'Pipe4': '1 5 1A 1 3 1',
                  'Pipe5': '1 6 1A 1 3 1',
                  'Pipe6': '1 7 1A 1 3 1',
                  'Pipe7': '1 8 1A 1 3 1',
                  'Pipe8': '2 1 1B 1 3 2',
                  'Pipe9': '2 2 1B 1 3 2',
                  'Pipe10': '2 3 1B 1 3 2',
                  'Pipe11': '2 4 1B 1 3 2',
                  'Pipe12': '2 5 1B 1 3 2',
                  'Pipe13': '2 6 1B 1 3 2',
                  'Pipe14': '2 7 1B 1 3 2',
                  'Pipe15': '2 8 1B 1 3 2',
                  'Pipe16': '3 1 2A 1 3 3',
                  'Pipe17': '3 2 2A 1 3 3',
                  'Pipe18': '3 3 2A 1 3 3',
                  'Pipe19': '3 4 2A 1 3 3',
                  'Pipe20': '3 5 2A 1 3 3',
                  'Pipe21': '3 6 2A 1 3 3',
                  'Pipe22': '3 7 2A 1 3 3',
                  'Pipe23': '3 8 2A 1 3 3',
                  'Pipe24': '4 1 2B 1 3 4',
                  'Pipe25': '4 2 2B 1 3 4',
                  'Pipe26': '4 3 2B 1 3 4',
                  'Pipe27': '4 4 2B 1 3 4',
                  'Pipe28': '4 5 2B 1 3 4',
                  'Pipe29': '4 6 2B 1 3 4',
                  'Pipe30': '4 7 2B 1 3 4',
                  'Pipe31': '4 8 2B 1 3 4'
                  }
    return Pipe_Details[Pipe_number]

def MN_Switch(pipe, ztm4sp8t_ip, ztm8_ip):
    details=get_switch_details(pipe)
    details= details.split(' ')
    print (len(details))
    # for i in range(0,len(details)):
    print (details)
    #details[4]
    switch1 = MiniCircuits_RC_4SPDT_A26_HTTP.RC_4SPDT_A26(ztm4sp8t_ip)
    switch2 = MiniCircuits_RC_4SPDT_A26_HTTP.RC_4SPDT_A26(ztm8_ip)

    #serial_number
    sn = switch1.get_serial_number()
    mn = switch1.get_model_number()

    #serial_number
    sn = switch2.get_serial_number()
    mn = switch2.get_model_number()


    switch2.ZTM_8_Clear()
    time.sleep(2)
    switch1.ZTM_4SP8T_Clear()


    switch1.set_one_switch_SP8T(details[0], details[1])
    time.sleep(2)
    switch2.set_one_switch_SPDT_2T((details[2]),(details[3]))
    time.sleep(2)
    switch2.set_one_switch_SPDT_4T((details[4]),(details[5]))


# MN_Switch("Pipe0")