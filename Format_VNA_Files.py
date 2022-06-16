import pandas as pd
import General_Utils

def hertz_to_MHz(val):
    return round((val/1000000), 2)

def secs_to_nanosecs(val):
    return round((val*1000000000), 2)

def trim_vna_file(ant, file_loc, filename):
    df = pd.read_csv('{}\\{}'.format(file_loc, filename), names = ['data'], header = None)
    ant_df = pd.DataFrame({'Antenna':ant}, index = range(len(df)))
    df = df.join(ant_df)
    df_dropped = df.drop([0, 1, 2])
    df_dropped[['Freq', 'Loss']] = df_dropped.data.str.split(";", n = 1, expand = True)
    df_dropped['Freq'] = df_dropped['Freq'].astype(float).apply(hertz_to_MHz)
    df_dropped['Loss'] = df_dropped.Loss.str.replace(";", "").astype(float).round(2)
    return (df_dropped)

def format_vna_file(file_loc, output_loc, antennas, freq_ranges, sw_att, bench_id):
    df_list = []
    output_name = f'Bench_{bench_id}_Losses_SwAtt_{sw_att}dB'
    for ant in antennas:
        for frange in freq_ranges:
            filename = f'Losses_{frange}_Pass_SwAtt_{sw_att}dB_Ant{ant}.csv'
            df_list.append(trim_vna_file(ant, file_loc, filename))
    df_final = pd.concat(df_list)
    General_Utils.data_to_excel(df_final, output_name, output_loc)
    print(f'Filename: {output_name}; Location: {output_loc}')


def trim_vna_delay_file(file_loc, filename, output_name):
    df = pd.read_csv('{}\\{}'.format(file_loc, filename), names = ['data'], header = None)
    df_dropped = df.drop([0, 1, 2])
    df_dropped[['Freq_MHz', 'Delay_ns']] = df_dropped.data.str.split(";", n = 1, expand = True)
    df_dropped['Freq_MHz'] = df_dropped['Freq_MHz'].astype(float).apply(hertz_to_MHz)
    df_dropped['Delay_ns'] = df_dropped.Delay_ns.str.replace(";", "").astype(float).apply(secs_to_nanosecs)
    General_Utils.data_to_excel(df_dropped, output_name, file_loc)

def trim_fsw_trace_file(file_loc, filename, output_name):
    df = pd.read_csv('{}\\{}'.format(file_loc, filename), names = ['Freq', 'Amplitude'], header = None)
    df_dropped = df.drop(range(31))
    df_dropped['Freq_MHz'] = df_dropped['Freq'].astype(float).apply(hertz_to_MHz).round(1)
    df_dropped['Amp_dB'] = df_dropped['Amplitude'].astype(float).round(2)
    General_Utils.data_to_excel(df_dropped, output_name, file_loc)

def main():
    """Inputs"""
    ### ZNB_Loss_File
    file_loc = r'D:\MidasRFV\Calibration_and_Spurious_Files\Raw_Files'
    antennas = range(1, 65)
    freq_ranges = ['Low'] #Low, High
    sw_att = 20 #Switch Attenuation
    output_loc = r'D:\MidasRFV\Calibration_and_Spurious_Files'
    bench_id = '42_DD_TX_Inband' #Test Bench Identifier
    """End Inputs"""
    try:
        format_vna_file(file_loc, output_loc, antennas, freq_ranges, sw_att, bench_id)
    except FileNotFoundError:
        print('File Not Found! Make sure you have the right location and file name and try again.')
    except Exception as e:
        print(f'Encountered {e}. Fix and Try again')

    

if __name__ == "__main__":
    main()    