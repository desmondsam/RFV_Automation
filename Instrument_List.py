import pyvisa

def get_visa_device_list():
    rm = pyvisa.ResourceManager()
    print (rm.list_resources())

def main():
    get_visa_device_list()

if __name__ == "__main__":
    main()