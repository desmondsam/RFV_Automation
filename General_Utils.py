from pathlib import Path
from datetime import datetime
import pandas as pd
from ipaddress import ip_address
from math import log10

def make_dir_if_not(dir_path):
    Path(dir_path).mkdir(parents = True, exist_ok = True)

def curr_date_time_str():
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def curr_time_ampm():
    return datetime.now().time().strftime("%I:%M:%S %p")

def curr_time():
    return datetime.now()

def curr_date_mdy():
    return datetime.now().strftime('%m-%d-%Y')

def data_to_csv(df, filename, file_loc = r'D:\\PyScripts\\Data'):
    df.to_csv('{}\\{}.csv'.format(file_loc, filename), index = False)            
    print ("Data Saved to CSV")

def data_to_excel(df, filename, file_loc = r'D:\\PyScripts\\Data'):
    try:
        df.to_excel('{}\\{}.xlsx'.format(file_loc, filename), index = False)
    except PermissionError:
        from win32com.client.gencache import EnsureDispatch
        xl = EnsureDispatch("Excel.Application")
        for book in xl.Workbooks:
            if (book.Name == f'{filename}.xlsx'):
                book.Close()
        df.to_excel('{}\\{}.xlsx'.format(file_loc, filename), index = False)     
    print ("Data Saved to Excel")

def namTupList_to_spreadsheet(resList, filename, file_loc = r'D:\\PyScripts\\Data', test_info = None, file_type = 'excel'):
    df = pd.DataFrame()
    try:
        res_df = pd.DataFrame(resList, columns = resList[0]._fields)
        if(test_info):
            df = res_df.join(pd.DataFrame(test_info, index = range(len(res_df))))
        else:
            df = res_df
    except IndexError:
        print('Not a single row generated. Output will be a blank spreadsheet')
    except Exception as e:
        print(e)
        print('Generating empty spreadsheet')
    if(file_type == 'excel'):
        data_to_excel(df, filename, file_loc)
    else:
        data_to_csv(df, filename, file_loc)

def update_Master_Spreadsheet(df, master_nas_loc='', master_nas_name=''):
    #Make a copy of Master Before Append with a Timestamp
    master_df_nas = pd.read_excel(f'{master_nas_loc}\\{master_nas_name}.xlsx')
    updated_df = pd.concat([master_df_nas, df], axis=0, ignore_index=True)
    data_to_excel(updated_df, master_nas_name, master_nas_loc)
    pass

# def print_and_log(custom_str, dev_name = None, log_only = False, logger=None):
#     if(dev_name):
#         custom_str = '{}: {}'.format(dev_name, custom_str)
#     if(not log_only):
#         print(custom_str)
#     if(logger):
#         logger.info(custom_str)
    # logging.info(custom_str)

def get_BMT_freqs(fstart, fstop, bw):
    mid_freq = fstart + ((fstop - fstart)/2)
    bot_freq = fstart + (bw/2)
    top_freq = fstop - (bw/2)
    chan_freq_dict = {
        'Bottom':bot_freq,
        'Middle':mid_freq,
        'Top':top_freq,
    }
    return chan_freq_dict

def watts_to_dBm(power = 10):
    PdBm = 10*log10(power) + 30
    return round(PdBm, 2)

def dBm_to_watts(power=46.02):
    Pwatt = (10**(power/10))/1000
    return round(Pwatt,2)

def validate_ip_address(ip_addr):
    validity = False
    try:
        ip_address(ip_addr)
        validity = True
    except ValueError:
        validity = False
    return validity

if __name__ == '__main__':
    # df = pd.DataFrame()
    # data_to_excel(df, 'check_overwriting', 'C:\MidasRFV\Test_Sequence_Data')
    # get_BMT_freqs(3700, 3980, 100)
    # print(watts_to_dBm(5))
    # print(dBm_to_watts(36.99))
    # print(curr_date_mdy())
    # band_edges = (3700, 3980)
    # bw = 100
    # channels = ['Bottom', 'Middle', 'Top']
    # for channel in channels:
    #     fr = get_BMT_freqs(band_edges[0], band_edges[1], bw)[channel]
    #     print (fr)
    print(validate_ip_address('10.69.91.127'))