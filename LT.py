import pandas as pd

res_df = pd.read_excel(r'D:\MidasRFV\Test_Sequence_Data\Test_Data_20220413_112258.xlsx')
add_dict = {
    'Bench_ID' : 'RFV_Lab_Bench_42',
    'Radio' : 'Zulu',
    'Variant' : 'R1D',
    'Serial_Num' : 'Z12345',
    'Tester_Comment': None,
    'Tester' : 'DesmondD',
}
# print(len(df))
print('Nothin')
newdata_dataframe = pd.DataFrame(add_dict, index = range(len(res_df)))
df = res_df.join(newdata_dataframe)
print(df)
# from collections import namedtuple as nt
# Specs = nt('Specs', ['spec_min', 'spec_max'])
# DataSet = nt('DataSet', [
#             'Time',
#             'Sequence', 
#             'Pipe', 
#             'Frequency',
#             'Channel',
#             'Test_Name',
#             'Meas_Name',
#             'Spec_Min',
#             'Spec_Max',
#             'Meas_Result',
#             'Unit',
#             'Status',
#             'Temperature',
#             'Test_Model',
#             'Num_Of_Carriers',
#             'Carrier_Bandwidth',
#             'Configuration',
#             ])

# def get_obue_spec(index, lmt):
#     spec = Specs(None, None)
#     if(index in [0, 5]):
#         spec = Specs(None, -15)
#     elif(index in [1, 4]):
#         spec = Specs(None, -12.2)
#     elif(index in [2, 3]):
#         spec = Specs(None, -12.2)
#     if(lmt == 'Margin'):
#         spec = Specs(0, None)
#     return spec

# def generate_dataset(sequence, pipe, freq, channel, testName, measName, spec_min, spec_max, res, unit, status, temp, tm, noc, carrBw, sig_file_name):
#     return DataSet(
#         Time = 'Time',
#         Sequence = sequence, 
#         Pipe = pipe, 
#         Frequency = freq,
#         Channel = channel,
#         Test_Name = testName,
#         Meas_Name = measName,
#         Spec_Min = spec_min,
#         Spec_Max = spec_max,
#         Meas_Result = res,
#         Unit = unit,
#         Status = status,
#         Temperature = temp,
#         Test_Model = tm,
#         Num_Of_Carriers = noc,
#         Carrier_Bandwidth = carrBw,
#         Configuration = sig_file_name,
#     )

# sem_final_res = [
#     [-91.36, 76.36, -240.0, -60.5, 1000000.0, 3370716090.0],
#     [-99.85, 87.65, -60.05, -55.05, 100000.0, 3553200000.0],
#     [-99.97, 88.12, -55.05, -50.05, 100000.0, 3555200000.0],
#     [-99.75, 87.9, 50.05, 55.05, 100000.0, 3664800000.0],
#     [-99.6, 87.4, 55.05, 60.05, 100000.0, 3667300000.0],
#     [-91.09, 76.09, 60.5, 240.0, 1000000.0, 3837349069.0]
# ]

# for ind in range(len(sem_final_res)):
#     for i in [0, 1]:
#         if(i==0):
#             lmt = 'Abs'
#             unit = 'dBm'
#         elif(i==1):
#             lmt = 'Margin'
#             unit = 'dB'
#         rlow = sem_final_res[ind][2]
#         rhigh = sem_final_res[ind][3]
#         meas = f'{rlow}MHz_to_{rhigh}MHz'
#         spec = get_obue_spec(ind, lmt)
#         status = 'Chumma'
#         measName = 'SEM_{}_{}'.format(meas, lmt)
#         res = sem_final_res[ind][i]
#         print (generate_dataset(1, 1, 3610, 'Mid', 'OBUE', measName, spec.spec_min, spec.spec_max, res, unit, status, 25, '1_1', 1, 100, 'sig_file_name'))
        