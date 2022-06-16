"""
Author : DesmondD
Fetch Path Loss from a Excel file for the respective pipe and frequency
"""
import pandas as pd
import numpy as np

def fetch_loss(ant, freq, file_loc, fname):
    loss = 0
    df = pd.read_excel('{}\\{}.xlsx'.format(file_loc,fname))
    df_ant = df[df['Antenna']==ant]
    df_filtered = df_ant[(df_ant['Freq'] >= freq-0.5) & (df_ant['Freq'] <= freq+0.5)]
    loss = df_filtered['Loss'].mean()
    if(np.isnan(loss)):
        print('Unable to find matching antenna/frequency value. Returning 0 as loss value')
        loss=0
    return round(loss, 2)
       
if __name__ == "__main__":
    """Inputs"""
    ant = 1
    freq = 3840
    file_loc = r'D:\MidasRFV\Calibration_and_Spurious_Files'
    fname = f'Bench_42_DD_TX_Inband_Losses_SwAtt_20dB' 
    """End Inputs"""
    try: 
        print (fetch_loss(ant, freq, file_loc, fname))
    except FileNotFoundError:
        print ('Losses file unavailable at specified location')
    except Exception as e:
        print(e)
