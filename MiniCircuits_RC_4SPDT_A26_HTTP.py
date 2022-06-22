from urllib.request import urlopen
import sys
import pandas as pd
import time

class RC_4SPDT_A26():
    
    def __init__(self, IP_Address):
        self.IP_Address = IP_Address
        print("Object Created")
    
    #Sends a command and returns the result
    def Get_HTTP_Result(self, CmdToSend):

        # Specifies the IP address of the switch box
        CmdToSend = "http://" + self.IP_Address + "/:" + CmdToSend

        # Sends the HTTP command and try to read the result
        try:
            HTTP_Result = urlopen(CmdToSend, timeout=1)
            PTE_Return = HTTP_Result.read()

            # The switch displays a web GUI for unrecognised commands
            if len(PTE_Return) > 100:
                print("Error, command not found:", CmdToSend)
                PTE_Return = "Invalid Command!"

        # Catches an exception if URL is incorrect (incorrect IP or disconnected)
        except:
            print("Error, no response from device; check IP address and connections.")
            PTE_Return = "No Response!"
            sys.exit()      # Exit the script

        # Returns the response
        return PTE_Return
    
    #Gets the Serial Number and returns the Serial Number as an int and prints to console
    def get_serial_number(self):
        serial_number_byte = self.Get_HTTP_Result("SN?")
        serial_number_string = serial_number_byte.decode("utf-8")
        print("Serial Number: " + serial_number_string[3:])
        return self.convert_byte_to_int(serial_number_byte[3:])
    
    #Gets the Model Number and returns the Model Number as a string and prints to console
    def get_model_number(self):
        model_number_byte = self.Get_HTTP_Result("MN?")
        model_number_string = model_number_byte.decode("utf-8")
        print("Model Number: " + model_number_string[3:])
        return model_number_string[3:]
    
    #Sets all switches to the value that is passed in and prints the new value for each switch
    #Value passed in must be a int and must not be larger than 15 or smaller than 0
    #MSB is switch "D" and LSB is switch "A"
    def set_all_switches(self, value):
        status = self.Get_HTTP_Result("SETP=" + str(value))
        status = self.convert_byte_to_int(status)
        if status == 1:
            print("All switches were set: ")
            temp_value = value
            switches = ["A", "B", "C", "D"]
            for letter in switches:
                remainder = temp_value % 2
                temp_value = int(temp_value / 2)
                print("Switch " + letter + " was set to " + str(remainder))
            print("")
            
        else:
            print("Switches were not set successfully")
    
    #Sets one switch and prints the new value for that switch
    #Value passed in must be a int and must be either 0 or 1
    #Switch must be a string and either "A", "B", "C" or "D"

    def set_one_switch(self, switch, value):
        status = self.Get_HTTP_Result("SET" + switch + "=" + str(value))


        status = self.convert_byte_to_str(status)
        #print(status.decode("utf-8"))
        if status == 1:
            print("Switch " + switch + " was set to " + str(value))
        else:
            print("Switch was not set successfully")
    def ZTM_4SP8T_Clear (self):
        status = self.Get_HTTP_Result(":ClearAll")
        print(status.decode("utf-8"))
        if status.decode("utf-8") == "1 - Success":
            print("Clear All")
        else:
            print("Switch was not set successfully")

    def ZTM_8_Clear (self):
        status = self.Get_HTTP_Result(":ClearAll")
        self.set_one_switch_SPDT_2T("1A", 2)
        time.sleep(1)
        self.set_one_switch_SPDT_2T("1B", 2)
        time.sleep(1)
        self.set_one_switch_SPDT_2T("2A", 2)
        time.sleep(1)
        self.set_one_switch_SPDT_2T("2B", 2)
        time.sleep(1)
        print(status.decode("utf-8"))
        if status.decode("utf-8") == "1 - Success":
            print("Clear All")
        else:
            print("Switch was not set successfully")

    def set_one_switch_SP8T(self, switch, value):
        #status = self.Get_HTTP_Result("SET" + switch + "=" + str(value))
        #status = self.Get_HTTP_Result(":ClearAll")
        status = self.Get_HTTP_Result(":SP8T:" + str(switch) + ":State:" + str(value))

        #status = self.convert_byte_to_str(status)
        print(status.decode("utf-8"))
        if status.decode("utf-8") == "1 - Success":
            print("Switch " + str(switch) + " was set to channel " + str(value))
        else:
            print("Switch was not set successfully")


    def set_one_switch_SPDT_2T(self, switch, value):
        #status = self.Get_HTTP_Result("SET" + switch + "=" + str(value))
        #status = self.Get_HTTP_Result(":ClearAll")
        status = self.Get_HTTP_Result(":SPDT:" + str(switch) + ":State:" + str(value))
        #":SPDT:1A:State:1"
        #status = self.convert_byte_to_str(status)
        print(status.decode("utf-8"))
        if status.decode("utf-8") == "1 - Success":
            print("Switch " + str(switch) + " was set to channel " + str(value))
        else:
            print("Switch was not set successfully")

    def set_one_switch_SPDT_4T(self, switch, value):
        #status = self.Get_HTTP_Result("SET" + switch + "=" + str(value))
        #status = self.Get_HTTP_Result(":ClearAll")
        status = self.Get_HTTP_Result(":SP4T:" + str(switch) + ":State:" + str(value))
        #":SP4T:3:State:1"
        #status = self.convert_byte_to_str(status)
        print(status.decode("utf-8"))
        if status.decode("utf-8") == "1 - Success":
            print("Switch " + str(switch) + " was set to channel " + str(value))
        else:
            print("Switch was not set successfully")

    def set_one_switch_SPDT_6T(self, switch, value):
                # status = self.Get_HTTP_Result("SET" + switch + "=" + str(value))
                status = self.Get_HTTP_Result(":ClearAll")
                status = self.Get_HTTP_Result(":SP6T:" + str(switch) + ":State:" + str(value))
                # ":SP4T:3:State:1"
                # status = self.convert_byte_to_str(status)
                print(status.decode("utf-8"))
                if status.decode("utf-8") == "1 - Success":
                    print("Switch " + str(switch) + " was set to channel " + str(value))
                else:
                    print("Switch was not set successfully")


            
    #Gets the state of all switches and prints the value of each switch
    def get_all_switch_states(self):
        state = self.Get_HTTP_Result("SWPORT?")
        state = self.convert_byte_to_int(state)
        temp_value = state
        switches = ["A", "B", "C", "D"]
        for letter in switches:
            remainder = temp_value % 2
            temp_value = int(temp_value / 2)
            print("Switch " + letter + " is in state " + str(remainder))
        print("")
        return state
    
    #Gets the internal temperature based on which sensor that is passed in (1, 2 or 3)
    def get_internal_temperature(self, sensor_num):
        temp = self.Get_HTTP_Result("TEMP" + str(sensor_num) + "?")
        temp = temp.decode("utf-8")
        print(temp[1:])
        return(temp[1:])
    
    #Checks if overheating
    def heat_check(self):
        status = self.Get_HTTP_Result("HEATALARM?")
        if self.convert_byte_to_int(status) == 1:
            print("Device is overheating")
        else:
            print("Device temperature within normal limits")
    
    #Checks if the fan is on
    def fan_check(self):
        status = self.Get_HTTP_Result("FAN?")
        if self.convert_byte_to_int(status) == 1:
            print("Fan is on")
        else:
            print("Fan is off")
    
    #Gets the firmware version
    def get_firmware(self):
        version = self.Get_HTTP_Result("FIRMWARE?")
        version_string = version.decode("utf-8")
        print("Firmware version is " + version_string)
        return version_string
    
    #Gets the number of lifetime switching cycles for each switch
    def get_switching_cycles(self):
        switches = ["A", "B", "C", "D"] 
        for switch in switches:
            cycles = self.Get_HTTP_Result("SC" + switch + "?")
            cycles = self.convert_byte_to_int(cycles)
            if cycles >= 8000000:
                print("WARNING: Switch " + switch + " has done " + str(cycles) + " cycles. MAX ALLOWED IS 10000000.")
            else:
                print("Switch " + switch + " has done " + str(cycles) + " cycles")
        print("")
        
    #Sets the power up mode (ie) turn on to the last remembered state or the default state
    #Mode must be a string and either "ON" or "OFF"
    def set_power_up_mode(self, mode):
        status = self.Get_HTTP_Result("ONPOWERUP:LASTSTATE:" + mode)
        if self.convert_byte_to_int(status) == 1:
            if mode == "ON":
                print("Switches will power up with last remembered state")
            else:
                print("Switches will power up in default state")
        else:
            print("Command unsuccessful")
            
    #Gets the power up mode and will print the current mode
    def get_power_up_mode(self):
        status = self.Get_HTTP_Result("ONPOWERUP:LASTSTATE?")
        if self.convert_byte_to_int(status) == 0:
            print("Switches will power up in default state")
        else:
            print("Switches will power up with last remembered state")
        return status
            
    #Saves the switch counters into permanent memory if not done within the past 3 minutes
    def save_switch_counters(self):
        status = self.Get_HTTP_Result("SCOUNTERS:STORE:INITIATE")
        if self.convert_byte_to_int(status) == 1:
            print("Counters stored in permanent memory")
        else:
            print("Command failed or counters stored in permanent memory previously within the last 3 minutes")
            
    #Sets the IP Address to the value that is passed in
    #Address is a string in the form XXX.XXX.XXX.XXX
    def set_IP_address(self, address):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:IP:" + address)
        if status == 1:
            print("IP address of device is now: " + address)
        else:
            print("Setting IP Address unsuccessful")
            
    #Gets and prints the IP Address as a string
    def get_IP_address(self):
        address = self.Get_HTTP_Result("ETHERNET:CONFIG:IP?")
        address = address.decode("utf-8")
        print(address)
        return address
    
    #Sets and prints the new subnet mask to the value that is passed in
    #Subnet mask is a string in the form XXX.XXX.XXX.X
    def set_subnet_mask(self, subnet_mask):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:SM:" + subnet_mask)
        status = self.convert_byte_to_int(status)
        if status == 1:
            print("Subnet Mask is now: " + subnet_mask)
        else:
            print("Setting subnet mask unsuccessful")
    
    #Gets and prints the subnet mask as a string
    def get_subnet_mask(self):
        mask = self.Get_HTTP_Result("ETHERNET:CONFIG:SM?")
        mask = mask.decode("utf-8")
        print(mask)
        return mask
    
    #Sets and prints the new network gateway to the value that is passed in
    #Network gateway is a string in the form XXX.XXX.XXX.XXX
    def set_network_gateway(self, network_gateway):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:NG:" + network_gateway)
        status = self.convert_byte_to_int(status)
        if status == 1:
            print("Network gateway is now: " + network_gateway)
        else:
            print("Setting the network gateway unsuccessful")
    
    #Gets and prints the network gateway as a string
    def get_network_gateway(self):
        gateway = self.Get_HTTP_Result("ETHERNET:CONFIG:NG?")
        gateway = gateway.decode("utf-8")
        print(gateway)
        return gateway
    
    #Sets the http port to the value that is passed in
    #HTTP Port is a number
    def set_http_port(self, http_port):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:HTPORT:" + str(http_port))
        status = self.convert_byte_to_int(status)
        if status == 1:
            print("HTTP port set to " + str(http_port))
        else:
            print("Setting the http port was unsuccessful")
    
    #Gets and prints the HTTP port as a string
    def get_http_port(self):
        port = self.Get_HTTP_Result("ETHERNET:CONFIG:HTPORT?")
        port = port.decode("utf-8")
        print(port)
        return port   
    
    #Sets if password is required or not
    #Enabled = 0 means password not required and Enabled = 1 means password is required
    def set_password_required(self, enabled):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:PWDENABLED:" + str(enabled))
        status = self.convert_byte_to_int(status)
        if status == 1:
            if enabled == "1":
                print("Password requirment enabled")
            else:
                print("Password requirement disabled")
        else:
            print("Enabling/Disabling password unsuccessful")
                
    #Sets the password to what is passed in
    #Password is a string
    def set_password(self, password):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:PWD:" + password)
        status = self.convert_byte_to_int(status)
        if status == 1:
            print("Password set successfully.")
        else:
            print("Password set unsuccessful.")
        
    #Gets the current password
    def get_password(self):
        password = self.Get_HTTP_Result("ETHERNET:CONFIG:PWD?")
        password = password.decode("utf-8")
        return password
    
    #Sets the DHCP Status to either enabled or disabled
    #Value that is passed in must be int and either 0(disabled) or 1(enabled)
    def set_dhcp_status(self, dhcp_status):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:DHCPENABLED:" + str(dhcp_status))
        status = self.convert_byte_to_int(status)
        if status == 1:
            if dhcp_status == 1:
                print("DHCP enabled")
            else:
                print("DHCP disabled")
        else:
            print("Enabling/Disabling DHCP unsuccessful")
            
    #Gets and prints whether the DHCP is enabled or disabled
    #Returns a string, either "Enabled" or "Disabled"
    def get_dhcp_status(self):
        dhcp_status = self.Get_HTTP_Result("ETHERNET:CONFIG:DHCPENABLED?")
        dhcp_status = self.convert_byte_to_int(dhcp_status)
        if dhcp_status == 1:
            print("DHCP enabled")
            return "Enabled"
        else:
            print("DHCP disabled")
            return "Disabled"
        
    #Gets and prints the MAC Address
    #Returns a string
    def get_mac_address(self):
        mac_address = self.Get_HTTP_Result("ETHERNET:CONFIG:MAC?")
        mac_address = mac_address.decode("utf-8")
        print("MAC Address is: " + mac_address)
        return mac_address
    
    #Gets and prints the current Ethernet Settings
    #Returns three strings in the following order: IP Address, Subnet Mask, Network Gateway
    def get_current_ethernet_settings(self):
        current_settings = self.Get_HTTP_Result("ETHERNET:CONFIG:LISTEN?")
        current_settings = current_settings.decode("utf-8")
        current_settings = current_settings.split(";", 3)
        print("IP Address: " + current_settings[0])
        print("Subnet Mask: " + current_settings[1])
        print("Network Gateway: " + current_settings[2])
        return current_settings[0], current_settings[1], current_settings[2]
    
    #Updates the ethernet configuration so any changes can be applied
    def update_ethernet_settings(self):
        status = self.Get_HTTP_Result("ETHERNET:CONFIG:INIT")
        status = self.convert_byte_to_int(status)
        if status == 1:
            print("Ethernet settings updated")
        else:
            print("Ethernet settings not updated")
            
    #Convert a byte to an int
    def convert_byte_to_int(self, byte_value):
        string_value = byte_value.decode("utf-8")
        return int(string_value)
    
    #Wait for time period seconds that is passed in
    def wait(self, period):
        print("Waiting for " + str(period) + " seconds")
        time.sleep(period)
    
    #Read excel file that is located at the path that is passed in and returns a dataframe
    def read_file(self, file_path, sheet_name):
        return pd.read_excel(file_path, sheet_name = sheet_name)
    
    #Set Switches based on path number that is passed in
    def set_switches_excel(self, path_number, file_path, sheet_name):
        dataframe = self.read_file(file_path, sheet_name)
        data_series = dataframe.loc[path_number, "A":"D"]
        for switch in range(len(data_series)):
            self.set_one_switch(data_series.index[switch], data_series[data_series.index[switch]])
        print("Switches set")
        
if __name__ == "__main__":
    switch1 = RC_4SPDT_A26("10.0.0.51")
    switch2 = RC_4SPDT_A26("10.0.0.50")

    #sn = switch2.get_serial_number()
    #mn = switch2.get_model_number()
    #switch1.set_one_switch_SP8T(1, 1)
    #time.sleep(2)
    #switch1.set_one_switch_SP8T(2, 3)
    #time.sleep(2)
    #switch1.set_one_switch_SP8T(3, 4)
    #time.sleep(2)
    #switch1.set_one_switch_SP8T(4, 8)

    #switch2.set_one_switch_SPDT_2T("1A",2)
    #time.sleep(2)
    #switch2.set_one_switch_SPDT_4T(3,2)
    #time.sleep(2)
    #switch2.set_one_switch_SPDT_6T(4, 2)


    #switch.set_all_switches(10)
    #switch.get_all_switch_states()
    #switch.get_internal_temperature(1)
    #switch.heat_check()
    #switch.fan_check()
    #switch.get_firmware()
    #switch.get_switching_cycles()
    #switch.set_power_up_mode("OFF")
    #switch.get_power_up_mode()
    #switch.save_switch_counters()
    #switch.get_IP_address()
    #switch.get_subnet_mask()
    #switch.get_network_gateway()
    #switch.get_http_port()
    #switch.set_password_required(0)
    #switch.set_password("12345")
    #password = switch.get_password()
    #switch.get_dhcp_status()
    #mac_address = switch.get_mac_address()
    #ip_address, subnet_mask, network_gateway = switch.get_current_ethernet_settings()
    #file_path = r"C:\Users\ahmedz\OneDrive - Mavenir Ltd\Documents\MiniCircuits Switch Test Cases.xlsx"
    #sheet_name = "Sheet1"
    #switch.set_switches_excel(15, file_path, sheet_name)
    print("End")
else:
    print("Called by outside file")
