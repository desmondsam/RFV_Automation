import matplotlib.pyplot as plt
import pandas as pd

def get_pa_plots(file_loc, file_name, plot_name):
    my_data = pd.read_excel(fr'{file_loc}\{file_name}.xlsx')
    freq_list = my_data.Frequency.unique().tolist()
    fig, ax = plt.subplots()
    fig1, ax1 = plt.subplots()
    for freq in freq_list:
        df_temp = my_data[(my_data['Frequency']==freq)]
        ax.plot(df_temp['Output_Pwr'], df_temp['Gain'], label=f'{freq} MHz', marker='o')
        ax1.plot(df_temp['Output_Pwr'], df_temp['Efficiency'], label=f'{freq} MHz', marker='o')
    ax.legend()
    ax.set_title(f'P_Out vs Gain')
    ax.set_xlabel('P_Out (dBm)')
    ax.set_ylabel('Gain (dB)')
    fig.set_size_inches(12, 10)
    fig.savefig(fr'{file_loc}\{plot_name}_GvPOut', bbox_inches='tight')
    ax1.legend()
    ax1.set_title(f'P_Out vs Efficiency')
    ax1.set_xlabel('P_Out (dBm)')
    ax1.set_ylabel('Efficiency (%)')
    fig1.set_size_inches(12, 10)
    fig1.savefig(fr'{file_loc}\{plot_name}_EffVPOut', bbox_inches='tight')

if __name__ == '__main__':
    floc = r'D:\MidasRFV\Test_Sequence_Data'
    fname = r'Mod_Pwr_Swp_PA_SN12345_GainEff'
    plot_name = 'PA_Plot'
    get_pa_plots(floc, fname, plot_name)

    
    