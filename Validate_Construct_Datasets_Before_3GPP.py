import General_Utils
from collections import namedtuple as nt

DataSet = nt('DataSet', [
            'Date',
            'Time',
            'Sequence', 
            'Pipe', 
            'Frequency',
            'Channel',
            'Test_Name',
            'Meas_Name',
            'Spec_Min',
            'Spec_Max',
            'Meas_Result',
            'Unit',
            'Status',
            'Temperature',
            'Test_Model',
            'Num_Of_Carriers',
            'Carrier_Bandwidth',
            'Configuration',
            'Peak_Frequency_MHz',
            'RBW_Hz'
            ])
Specs = nt('Specs', ['spec_min', 'spec_max'])

def get_acp_dataset(acp_res, pipe, freq, loop, bw, pwr, temp, tm, noc, sig_file_name, channel):
        acp_datasets = []
        opSmin = round(pwr - 0.8,2)
        opSmax = round(pwr + 0.8,2)
        status = validate_data(acp_res[0], opSmin, opSmax)
        pwr_res = generate_dataset(loop, pipe, freq, channel, 'Output Power', 'Channel Power', opSmin, opSmax, acp_res[0], 'dBm', status, temp, tm, noc, bw, sig_file_name)
        acp_datasets.append(pwr_res)
        for i in range(1, len(acp_res), 2):
            acp_datasets.append(construct_acp_dataset('Lower', i, acp_res, pipe, freq, loop, bw, temp, tm, noc, sig_file_name, channel))
            acp_datasets.append(construct_acp_dataset('Upper', i+1, acp_res, pipe, freq, loop, bw, temp, tm, noc, sig_file_name, channel))
        return acp_datasets
    
def construct_acp_dataset(offs, index, acp_res, pipe, freq, loop, bw, temp, tm, noc, sig_file_name, channel):
    if(bw < 40):
        spec = Specs(None, -44.2)
    else:
        spec = Specs(None, -43.8)
    res = acp_res[index]
    status = validate_data(res, spec.spec_min, spec.spec_max)
    if(index < 3):
        offset = 'Adjacent'
    else:
        offset = 'Alternate'
    measName = 'ACLR_{}_{}'.format(offset, offs)
    return generate_dataset(loop, pipe, freq, channel, 'ACLR', measName, spec.spec_min, spec.spec_max, res, 'dBc', status, temp, tm, noc, bw, sig_file_name)

def get_sem_dataset(pipe_obue, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel, tName='OBUE'):
    sem_datasets = []
    for ind in range(len(pipe_obue)):
        for i in [0, 1]:
            if(i==0):
                lmt = 'Abs'
                unit = 'dBm'
            elif(i==1):
                lmt = 'Margin'
                unit = 'dB'
            rlow = pipe_obue[ind][2]
            rhigh = pipe_obue[ind][3]
            meas = f'{rlow}MHz_to_{rhigh}MHz'
            spec = get_obue_spec(ind, lmt)
            measName = '{}_{}'.format(meas, lmt)
            res = pipe_obue[ind][i]
            rbw = pipe_obue[ind][4]
            pk_freq = round((pipe_obue[ind][5]/1e6),2)
            status = validate_data(res, spec.spec_min, spec.spec_max)
            sem_datasets.append(generate_dataset(loop, pipe, frequency, channel, tName, measName, spec.spec_min, spec.spec_max, res, unit, status, temp, tm, noc, bw, sig_file_name, pk_freq, rbw))
    return sem_datasets

def get_evm_dataset(pipe_evm, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel):
    evm_datasets = []
    spec = getEvmSpec(tm)
    for carr_evm in pipe_evm:
        for ind in range(1, len(carr_evm)):
            res = carr_evm[ind]
            status = validate_data(res, spec.spec_min, spec.spec_max)
            tName = 'EVM'
            unit = '%'
            if(ind == 1):
                measName = 'EVM_Average'
            elif(ind == 2):
                measName = 'EVM_Max'
            elif(ind == 3):
                spec = Specs(-70.5, 70.5)
                tName = 'Frequency Error'
                measName = 'Freq_Error'
                status = validate_data(res, spec.spec_min, spec.spec_max)
                unit = 'Hz'
            elif(ind == 4):
                spec = Specs(None, None)
                tName = 'TPDR'
                measName = f'OSTP_{tm}'
                status = None
                unit = 'dBm'
            evm_datasets.append(generate_dataset(loop, pipe, frequency, channel, tName, measName, spec.spec_min, spec.spec_max, res, unit, status, temp, tm, noc, bw, sig_file_name))
    return evm_datasets

def get_oop_dataset(pipe_oop, pipe, frequency, loop, bw, temp, tm, noc, sig_file_name, channel):
    oop_datasets = []
    tName = 'TX ON OFF Power'
    for ind in range(len(pipe_oop)):
        if(ind < 3):
            slot = 1
        else:
            slot = 2
        res = pipe_oop[ind]
        if ind in [0, 3]:
            unit = 'dBm/MHz'
            spec = Specs(None, -82.5)
            status = validate_data(res, spec.spec_min, spec.spec_max)
            measName = f'TX OFF PSD - Slot {slot}'
        elif ind in [1, 4]:
            measName = f'Falling Transient - Slot {slot}'
            unit = 'ns'
            spec = Specs(None, None)
            status = None
        else:
            measName = f'Rising Transient - Slot {slot}'
            unit = 'ns'
            spec = Specs(None, None)
            status = None
        oop_datasets.append(generate_dataset(loop, pipe, frequency, channel, tName, measName, spec.spec_min, spec.spec_max, res, unit, status, temp, tm, noc, bw, sig_file_name))
    return oop_datasets

def get_catb_offsets(band_edges, freq, bw):
    rfbw = band_edges[1] - band_edges[0]
    if(rfbw > 200):
        fstart = band_edges[0] - 40
        fstop = band_edges[1] + 40
    else:
        fstart = band_edges[0] - 10
        fstop = band_edges[1] + 10
    offset_prime = (bw/2)
    neg_offs_1_stop = freq-offset_prime-10.5
    neg_offs_3_stop = freq-offset_prime-0.05
    neg_offs_3_start = freq-offset_prime-5.05
    neg_offs_2_stop = neg_offs_3_start
    neg_offs_2_start = freq-offset_prime-10.05

    pos_offs_1_start = freq+offset_prime+0.05
    pos_offs_1_stop = freq+offset_prime+5.05
    pos_offs_2_start = pos_offs_1_stop
    pos_offs_2_stop = freq+offset_prime+10.05
    pos_offs_3_start = freq+offset_prime+10.5
    
    neg_offs_1 = [fstart, neg_offs_1_stop, 1000000, -15, round(fstart-freq,2), round(neg_offs_1_stop-freq,2)]
    neg_offs_2 = [neg_offs_2_start, neg_offs_2_stop, 100000, -12.2, round(neg_offs_2_start-freq,2), round(neg_offs_2_stop-freq,2)]
    neg_offs_3 = [neg_offs_3_start, neg_offs_3_stop, 100000, -12.2, round(neg_offs_3_start-freq,2), round(neg_offs_3_stop-freq,2)]

    pos_offs_1 = [pos_offs_1_start, pos_offs_1_stop, 100000, -12.2, round(pos_offs_1_start-freq,2), round(pos_offs_1_stop-freq,2)]
    pos_offs_2 = [pos_offs_2_start, pos_offs_2_stop, 100000, -12.2, round(pos_offs_2_start-freq,2), round(pos_offs_2_stop-freq,2)]
    pos_offs_3 = [pos_offs_3_start, fstop, 1000000, -15, round(pos_offs_3_start-freq,2), round(fstop-freq,2)]

    offsets = [neg_offs_1, neg_offs_2, neg_offs_3, pos_offs_1, pos_offs_2, pos_offs_3]
    return offsets

def getEvmSpec(tm):
        if(tm in ['1_1', '3_3']):
            specs = Specs(None, 18.5)
        elif(tm == '3_2'):
            specs = Specs(None, 13.5)
        elif(tm in ['3_1', '2']):
            specs = Specs(None, 9)
        elif(tm in ['3_1a', '2a']):
            specs = Specs(None, 4.5)
        return specs

def get_obue_spec(index, lmt):
    spec = Specs(None, None)
    if(index in [0, 5]):
        spec = Specs(None, -15)
    elif(index in [1, 4]):
        spec = Specs(None, -12.2)
    elif(index in [2, 3]):
        spec = Specs(None, -12.2)
    if(lmt == 'Margin'):
        spec = Specs(0, None)
    return spec

def generate_dataset(sequence, pipe, freq, channel, testName, measName, spec_min, spec_max, res, unit, status, temp, tm, noc, carrBw, sig_file_name, pk_freq=None, rbw=None):
    return DataSet(
        Date = General_Utils.curr_date_mdy(),
        Time = General_Utils.curr_time_ampm(),
        Sequence = sequence, 
        Pipe = pipe, 
        Frequency = freq,
        Channel = channel,
        Test_Name = testName,
        Meas_Name = measName,
        Spec_Min = spec_min,
        Spec_Max = spec_max,
        Meas_Result = res,
        Unit = unit,
        Status = status,
        Temperature = temp,
        Test_Model = tm,
        Num_Of_Carriers = noc,
        Carrier_Bandwidth = carrBw,
        Configuration = sig_file_name,
        Peak_Frequency_MHz = pk_freq,
        RBW_Hz = rbw,
    )

def validate_data(meas_res, spec_min, spec_max):
    if(spec_min != None and meas_res < spec_min): return 'FAIL'
    if(spec_max != None and meas_res > spec_max): return 'FAIL'
    return 'PASS'

def generate_excel(results, fname, floc, test_info=None):
    General_Utils.namTupList_to_spreadsheet(results, fname, floc, test_info=test_info)

def main():
    # smid = validate_data(46, 45.2, 46.8)
    # smax = validate_data(-53, None, -45)
    # smin = validate_data(46, 43, None)
    # sminzero = validate_data(4, 0, None)
    # smaxzero = validate_data(-4, None, 0)
    # print(f'Mid {smid}, Max {smax}, Min {smin} ZeroMin {sminzero} ZeroMax {smaxzero}')
    p_obue = [[-90.4, 78.52, -50.05, -55.05, 100000.0, 3695170000.0], [-92.0, 79.8, 50.05, 55.05, 100000.0, 3805050000.0], [-89.84, 77.64, -55.05, -60.05, 100000.0, 3691320000.0], [-91.56, 79.36, 55.05, 60.05, 100000.0, 3805830000.0], [-79.53, 64.53, -60.5, -380.0, 1000000.0, 3642000000.0], [-81.48, 66.48, 60.5, 380.0, 1000000.0, 4080750000.0]]
    a = get_sem_dataset(p_obue, 1, 3610, 1, 100, 25, '1_1', 1, 'TM_Name', 'Mid')
    # p_evm = [[1, 0.61, 0.62, -37.91]]
    # a = get_evm_dataset(p_evm, 1, 3640, 1, 100, 25, '1_1', 1, 'TM_Name', 'Mid')
    # a = get_catb_offsets((3410, 3800), 3460, 100)
    # a = get_oop_dataset([-89.82, 390.62, 398.76, -89.83, 504.56, 374.35], 1, 3450, 1, 100, 25, '1_1', 1, 'sig_name', 'Mid')
    print(a)

if __name__ == "__main__":
    main()