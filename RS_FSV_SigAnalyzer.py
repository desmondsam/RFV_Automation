import visa_connections
import time
import pandas as pd

class FSVHandler(visa_connections.DeviceHandler):

    def __init__(self, tcp_ip, cust_name = 'FSV_Analyzer', parent_logger=None):
        super(FSVHandler, self).__init__(tcp_ip, cust_name = cust_name, parent_logger=parent_logger)
        self.ss_name = r'Default_FSV_Screenshot'
        self.ss_loc = r'C:\Data\Screenshots'
        self.set_timeout()
    
    def set_timeout (self, timeout = 200000):
        self.timeout = timeout
    
    def ref_lvl_offset(self, cable_loss):
        self.write('DISP:TRAC:Y:RLEV:OFFS {}dB'.format(cable_loss))
        self.plog('Reference Level Offset set to {} dB'.format(cable_loss))
    
    def set_center_freq(self, freq):
        self.write('FREQ:CENT {} MHz'.format(freq))                           
        self.plog('Center Frequency set to {} MHz'.format(freq))

    def set_start_stop_freq(self, start_freq, stop_freq):
        self.write('FREQ:STAR {} MHz'.format(start_freq))
        self.plog('Start Frequency set to {} MHz'.format(start_freq)) 
        self.write('FREQ:STOP {} MHz'.format(stop_freq))
        self.plog('Stop Frequency set to {} MHz'.format(stop_freq))
    
    def set_multi_carr_freqs(self, flist):
        for cc in range(1, len(flist)+1):
            self.write('FREQ:CENT:CC{} {}MHz'.format(cc, flist[cc-1]))
            self.plog('Carrier {} Frequency set to {} MHz'.format(cc, flist[cc-1]))
    
    def set_span(self, span = '100MHz'):
        self.write('FREQ:SPAN {}'.format(span))
        self.plog(f'Frequency Span set to {span}')
        
    def set_deploymenet_frange(self, freq = 4500):
        if(freq <= 3000):
            deploy = 'LOW'
        elif(freq > 6000):
            deploy = 'HIGH'
        else:
            deploy = 'MIDD'
        self.write('CONF:DL:DFR {}'.format(deploy))
        time.sleep(2)
        self.plog(f'Deployment Frequency Range set to {deploy}')
    
    def set_bts_type(self, bts = 'FR1C'):
        self.write('CONF:BST {}'.format(bts))
        self.plog(f'BTS Type Set to {bts}')
    
    def set_noc(self, noc = 2):
        self.write('CONF:NOCC {}'.format(noc))
        self.plog(f'Number of Carriers set to {noc}')
    
    def set_oper_band(self, band = 'N78'):
        self.write('CONF:OBAN {}'.format(band))
        self.plog(f'Operating band set to {band}')
    
    def set_ref_lvl(self, ref_lvl = 45):
        self.write('DISP:TRAC:Y:RLEV {}dBm'.format(ref_lvl))
        self.plog('Reference Level set to {} dBm'.format(ref_lvl))

    def set_atten_auto(self):
        self.write('INP:ATT:AUTO ON') #Based on RefLevel
        self.plog('RF Attenuation Set to Automatic')
    
    def set_atten(self, att_lvl = 23):
        self.write('INP:ATT {}dB'.format(att_lvl))
        self.plog('RF Attenuation Level set to {} dBm'.format(att_lvl))
    
    def set_up_trace(self, trace = 1, mode = 'WRIT', detector = 'RMS', averType = 'LOG'):
        self.plog(f'Setting up Trace {trace}')
        self.write('DISP:TRAC{}:MODE {}'.format(trace, mode))
        self.plog(f'Mode of Trace {trace} set to {mode}')
        self.write('DET{} {}'.format(trace, detector))
        self.plog(f'Detector of Trace {trace} set to {detector}')
        self.write('AVER:TYPE {}'.format(averType))
        self.plog(f'Trace averaging type set to {averType}')
    
    def set_single_sweep(self, single = True):
        if(single):
            self.write('INIT:CONT OFF')
            self.plog('Sweep mode set to Single')
        else:
            self.write('INIT:CONT ON')
            self.plog('Sweep mode set to Continuous')
    
    def set_noise_cancellation(self, correction = True):
        if(correction):
            self.write('POW:NCOR ON')
            self.plog('Noise Correction turned ON')
        else:
            self.write('POW:NCOR OFF')
            self.plog('Noise Correction turned OFF')
    
    def set_sweep_time(self, swt = '50ms'):
        self.write('SWE:TIME {}'.format(swt))
        self.plog(f'Sweep Time set to {swt}')
    
    def set_sweep_type(self, swp_type = 'AUTO'):
        self.write('SWE:TYPE {}'.format(swp_type))
        self.plog(f'Sweep Type set to {swp_type}')
    
    def set_rbw(self, rbw = '100 KHz'):
        self.write('BAND {}'.format(rbw))
        self.plog(f'RBW set to {rbw}')
    
    def set_vbw(self, vbw = '1 MHz'):
        self.write('BAND:VID {}'.format(vbw))
        self.plog(f'VBW set to {vbw}')
    
    def set_trig_source(self, src = 'EXT'):
        self.write('TRIG:SOUR {}'.format(src))
        self.plog(f'Trigger Source set to {src}')
    
    def set_trig_gate(self, gstate = 'ON', gtype = 'EDGE', gdelay = '86us', glength = '3.715ms'):
        self.write('SWE:EGAT {}'.format(gstate))
        self.write('SWE:EGAT:TYPE {}'.format(gtype))
        self.plog(f'Trigger Gate turned {gstate} with type set to {gtype}')
        self.write('SWE:EGAT:HOLD {}'.format(gdelay))
        self.write('SWE:EGAT:LENG {}'.format(glength))
        self.plog(f'Trigger Gate Delay set to {gdelay} and Gate Length set to {glength}')
        self.write(':SENS:SWE:EGAT:CONT:STAT ON')
        self.plog('Continuos Gate Turned ON')
    
    def set_ext_ref_clk(self, clksrc = 'EAUT'):
        self.write('ROSC:SOUR {}'.format(clksrc))
        self.plog(f'External Reference Clock Source set to {clksrc}')
    
    def get_one_measurement(self):
        self.write('INIT; *WAI')
        time.sleep(3)
        self.plog('Initiating and completing One Measurement')
    
    def all_markers_off(self):
        self.write('CALC:MARK:AOFF')
        self.plog('Turn All Markers OFF')
    
    def peak_search(self):
        self.all_markers_off()
        self.write('CALC:MARK1:MAX')
        peak_val = self.query_ascii_values('CALC:MARK1:Y?')
        return round(peak_val[0], 2)
    
    def peak_search_freq(self):
        self.all_markers_off()
        self.write('CALC:MARK1:MAX')
        peak_freq = self.query_ascii_values('CALC:MARK1:X?')
        # print (peak_freq)
        return round(peak_freq[0]/1000000, 2)
    
    def peak_search_xy(self):
        self.all_markers_off()
        self.write('CALC:MARK1:MAX')
        peak_freq = self.query_ascii_values('CALC:MARK1:X?')
        peak_val = self.query_ascii_values('CALC:MARK1:Y?')
        # print (peak_freq)
        return [round(peak_freq[0], 2), round(peak_val[0], 2)]
    
    def hzontal_disp_line(self, dline = 1, lvl = '-15 dBm'):
        self.write('CALC:DLIN{}:STAT OFF'.format(dline))
        self.write('CALC:DLIN{}:STAT ON'.format(dline))
        self.write('CALC:DLIN{} {}'.format(dline, lvl))
        self.plog(f'Configured Display Line {dline} at RF level {lvl}')
    
    def get_mode_list(self):
        modes_list = self.query('INST:LIST?')
        # mode_type_name = modes_list.split(',')
        # modes = [val.strip() for val in mode_type_name]
        # modes_f = [val.replace("'", "") for val in modes]
        return modes_list
    
    def del_mode_meas(self, name):
        self.write("INST:DEL '{}'".format(name))
        self.plog(f'Deleted Mode Measurement Page {name}')
    
    def create_new_mode(self, mode = 'NR5G', name = '5G Meas'):
        self.clear()
        self.write("INST:CRE {}, '{}'".format(mode, name))
        time.sleep(5)
        self.plog(f'Created a New Mode {mode} Window with the name {name}')
        # self.sel_existing_mode(name)
        # self.set_ext_ref_clk()
    
    def sel_existing_mode(self, mode_name):
        self.write("INST '{}'".format(mode_name))
        time.sleep(2)
        self.plog(f'Selected Window named {mode_name}')

    def get_screenshot(self):
        self.set_single_sweep()
        time.sleep(3)
        self.write('MMEM:NAME "{}\\{}"'.format(self.ss_loc, self.ss_name))
        self.write('HCOP:DEST1 MMEM')
        self.write('HCOP:DEV:LANG1 PNG')
        self.write('HCOP')
        self.plog('Screenshot Saved')
    
    def load_test_model(self, testModel, cc = 1):
        self.write(":MMEM:LOAD:TMOD:CC{} '{}'".format(cc, testModel))
        self.plog(f'Loaded Test Model File {testModel} for Carrier {cc}')
    
    def setup_ACLR(self, freq = 3640, band = 'N78', testModel = None, tGDelay = '86us', tGLength = '3.715ms', trigSrc = 'EXT', sweepTime = '50ms', sweepType = 'AUTO'):
        self.write('CONF:MEAS ACLR')
        self.set_center_freq(freq)
        if(testModel):
            self.load_test_model(testModel)
        self.plog('Configuring ACLR Measurement')
        self.set_deploymenet_frange(freq)
        self.set_bts_type()
        self.set_oper_band(band)
        self.write('CALC:MARK:FUNC:POW:SEL ACP')
        self.write('CALC:MARK:FUNC:POW:MODE WRIT')
        self.write('POW:ACH:PRES ACP')
        if(tGDelay and tGLength):
            self.set_trig_gate(gdelay = tGDelay, glength = tGLength)
        self.set_trig_source(trigSrc)
        self.set_sweep_time(sweepTime)
        self.set_sweep_type(sweepType)
        self.write(':SENS:POW:NCOR ON')
        self.set_rbw()
        self.set_vbw()
        time.sleep(5)
        self.plog('ACLR settings configured')
    
    def measure_ACLR(self, ref_lvl = 53, rlvlOffs = 45):
        self.measurement_prep(ref_lvl, rlvlOffs)
        acp_vals = self.query_ascii_values('CALC:MARK:FUNC:POW:RES? ACP')
        acp_res = [round(val, 2) for val in acp_vals]
        # print (acp_res)
        return acp_res

    def measurement_prep(self, refLvl, refLvlOffs, meas_time=10):
        self.ref_lvl_offset(refLvlOffs)
        self.set_ref_lvl(refLvl)
        self.set_single_sweep()
        self.get_one_measurement()
        time.sleep(meas_time)

    def measure_mc_ACLR(self, fList = None, band = 'N78', tmList = None, rlvlOffs = 45, telec = False, gaps = True, lte = False):
        self.write('CONF:MEAS MCAC')
        if(tmList):
            for cc in range(1, len(tmList)+1):
                self.load_test_model(testModel = tmList[cc-1], cc = cc)
        if(fList):
            self.set_multi_carr_freqs(fList)
        self.setupACLR(fList[0], band, rlvlOffs, telec, lte)
        acp_vals = self.query_ascii_values('CALC:MARK:FUNC:POW:RES? MCAC')
        acp_res = [round(val, 2) for val in acp_vals]
        if(gaps):
            gap_aclr_vals = self.query_ascii_values('CALC:MARK:FUNC:POW:RES? GACL')
            gap_aclr_res = [round(val, 2) for val in gap_aclr_vals]
        else:
            gap_aclr_res = [None, None, None, None]
        return acp_res[:8] + gap_aclr_res
    
    def setup_EVM_FErr(self, sig_file_name, noc = 1, freq = 3640, band = 'N78', sweepTime = '3.5s', trigSrc='EXT'):
        self.write('CONF:MEAS EVM')
        time.sleep(5)
        self.set_single_sweep()
        self.set_noc(noc)
        self.set_center_freq(freq) #Change to Multi-Carrier for 2C+
        for cc in range(1, noc+1):
            self.load_test_model(testModel = sig_file_name, cc = cc)
        self.set_oper_band(band)
        self.set_deploymenet_frange(freq)
        self.set_trig_source(trigSrc)
        self.set_sweep_time(sweepTime)
        for cc in range(1, noc+1):
            self.write('CONF:DL:CC{}:SSBL:DET AUTO'.format(cc))
            self.write('CONF:DL:CC{}:FRAM:BWP:DET AUTO'.format(cc))
            self.write('CONF:DL:CC{}:PLC:CID {}'.format(cc, cc))
    
    def measure_EVM_FErr(self, tm = '1_1', noc = 1, refLvl = 55, refLvlOffs = 45):
        self.measurement_prep(refLvl, refLvlOffs)
        if(tm in ['3_3', '1_1']):
            mod = 'QP'
        elif(tm == '3_2'):
            mod = 'ST'
        elif(tm == '3_1' or tm == '2'):
            mod = 'SF'
        elif(tm == '3_1a' or tm == '2a'):
            mod = 'TS'
        else:
            mod = 'QP'
        evm_res = []
        for cc in range(1, noc+1):
            evm_aver = self.query_ascii_values(':FETC:CC{}:ISRC:FRAM:SUMM:EVM:DS{}:AVER?'.format(cc, mod))[0]
            evm_max = self.query_ascii_values(':FETC:CC{}:ISRC:FRAM:SUMM:EVM:DS{}:MAX?'.format(cc, mod))[0]
            freqErr = self.query_ascii_values(':FETC:CC{}:ISRC:FRAM:SUMM:FERR:AVER?'.format(cc))[0]
            ostp = self.query_ascii_values(':FETC:CC{}:ISRC:FRAM:SUMM:OSTP:AVER?'.format(cc))[0]
            evm_res.append([cc, round(evm_aver, 2), round(evm_max, 2), round(freqErr, 2), round(ostp, 2)])
        return evm_res
    
    def setup_OBUE_5g(self, tm, freq = 3640, band = 'N78', mask = 'CAT B', fstart = 3370, fstop = 3840, tGDelay = '86us', tGLength = '3.715ms', trigSrc = 'EXT', sweepType = 'SWE'):
        self.write('CONF:MEAS ESP')
        self.set_center_freq(freq)
        self.set_single_sweep()
        offs_start = round((freq - fstart), 1)
        offs_stop = round((fstop - freq), 1)
        span = max(offs_start, offs_stop) * 2
        self.set_bts_type()
        self.set_oper_band(band)
        self.load_test_model(tm)
        self.write(f':SENS:POW:{mask}') #CAT:B OPT2
        self.set_span(f'{span} MHz')
        if(tGDelay and tGLength):
            self.set_trig_gate(gdelay = tGDelay, glength = tGLength)
        self.set_trig_source(trigSrc)
        self.set_sweep_type(sweepType)
        self.set_deploymenet_frange(freq)
        rng_count = int(self.query('ESP1:RANG:COUN?')) + 1
        for range_id in range(1, rng_count):
            self.write('ESP1:RANG{}:SWE:TIME 500ms'.format(range_id))
        self.write(':SENS:ESP1:RANG1:FREQ:STAR -{} MHz'.format(offs_start))
        time.sleep(2)
        self.write(':SENS:ESP1:RANG7:FREQ:STOP {} MHz'.format(offs_stop))
        time.sleep(2)
    
    def meas_OBUE_5g(self, refLvl = 55, refLvlOffs = 45):
        self.measurement_prep(refLvl, refLvlOffs)
        sem_res = self.query_ascii_values(':TRAC:DATA? LIST')
        sem_range_res = [sem_res[x:x+11] for x in range(0, len(sem_res), 11)]
        sem_final_res = []
        for range_res in sem_range_res:
            delta_to_lmt = range_res[7] * -1
            sem_final_res.append([round(range_res[5], 2), round(delta_to_lmt, 2), (range_res[1]/1e6), (range_res[2]/1e6), range_res[3], range_res[4]])
        # print(sem_final_res)
        return sem_final_res

    def mc_obue_5g(self, fList = None, tmList = None, bwList = None, rlvlOffs = 45):
        self.write('CONF:MEAS MCES')
        self.set_single_sweep()
        f3440 = '{} MHz'.format(int(fList[0] - 3440))
        f3840 = '{} MHz'.format(int(3840 - fList[1]))
        if(fList):
            self.set_multi_carr_freqs(fList)
        if(tmList):
            for cc in range(1, len(tmList)+1):
                self.load_test_model(testModel = tmList[cc-1], cc = cc)
        self.set_deploymenet_frange()
        self.set_bts_type()
        self.set_oper_band()
        self.write('POW:CAT B')
        self.set_span('720 MHz')
        self.ref_lvl_offset(rlvlOffs)
        self.set_ref_lvl(ref_lvl = 55)
        self.set_trig_source()
        self.set_trig_gate(gdelay = '86us', glength = '3.715ms')
        self.set_sweep_type('SWE')
        rng_count = int(self.query('ESP1:RANG:COUN?')) + 1
        for range_id in range(1, rng_count):
            self.write('ESP1:RANG{}:SWE:TIME 500ms'.format(range_id))
            self.write('ESP2:RANG{}:SWE:TIME 500ms'.format(range_id))
        self.write(':SENS:ESP1:RANG1:FREQ:STAR -{}'.format(f3440))
        self.write(':SENS:ESP2:RANG11:FREQ:STOP {}'.format(f3840))
        self.set_single_sweep(False)
        time.sleep(5)
        self.set_timeout(None)
        self.set_single_sweep()
        self.get_one_measurement()
        time.sleep(10)
        self.write('FORM:DATA ASC')
        sem_res = self.query_ascii_values(':TRAC:DATA? LIST')
        sem_range_res = [sem_res[x:x+11] for x in range(0, len(sem_res), 11)]
        sem_final_res = []
        for range_res in sem_range_res:
            sem_final_res.append([round(range_res[5], 2), round(range_res[7], 2)])
        # print(sem_final_res)
        return sem_final_res
    
    def setup_obue_oob_spectrum(self, swt='500ms', tGDelay='86us', tGLength='3.715ms', trigSrc='EXT'):
        if(tGDelay and tGLength):
            self.set_trig_gate(gdelay = tGDelay, glength = tGLength)
        self.set_trig_source(trigSrc)
        self.set_sweep_time(swt)
        self.set_up_trace()
        self.set_sweep_type()

    def spec_obue_catb(self, offsets, refLvl=55, refLvlOffs=45):
        spec_obue_res = []
        for offs in offsets:
            offStart = offs[0]
            offStop = offs[1]
            spec = offs[3]
            rbw = offs[2]
            res = self.meas_oob_spur(offStart, offStop, rbw, refLvl, refLvlOffs, spec)
            mirrorList = [res[1], spec-res[1], offs[4], offs[5], rbw, res[0]]
            spec_obue_res.append(mirrorList)
        return spec_obue_res

    def meas_oob_spur(self, startf, stopf, rbw, refLvl, refLvlOffs=0, spec=-15):
        self.set_start_stop_freq(startf, stopf)
        time.sleep(2)
        self.set_rbw(rbw)
        self.set_vbw(rbw*3)
        self.ref_lvl_offset(refLvlOffs)
        self.set_ref_lvl(refLvl)
        self.hzontal_disp_line(lvl=spec)
        self.set_single_sweep()
        self.get_one_measurement()
        time.sleep(10)
        res = self.peak_search_xy()
        return res
    
    def setup_spurs_emiss(self, xl_name, xl_cols=['Start', 'Stop', 'RBW', 'WA BS'], transducer=None):
        self.write('SWE:MODE:LIST')
        self.write(':INIT:SPUR')
        df = pd.read_excel(xl_name, skiprows=[0,1])
        df_spurs = df[xl_cols].dropna()
        start_fs = df_spurs['Start'].to_list()
        stop_fs = df_spurs['Stop'].to_list()
        rbws = df_spurs['RBW'].to_list()
        lims = df_spurs['WA BS'].to_list()
        range_count = len(start_fs)
        self.set_span(span='6GHz')
        self.set_single_sweep()
        self.write(f'LIST:RANG:COUN {range_count}')
        time.sleep(2)
        for ind in range(1, range_count+1):
            self.write(f':SENS:LIST:RANG{ind}:FREQ:STAR {start_fs[ind-1]} MHz')
            time.sleep(1)
            self.write(f':SENS:LIST:RANG{ind}:FREQ:STOP {stop_fs[ind-1]} MHz')
            time.sleep(1)
            self.write(f':SENS:LIST:RANG{ind}:BAND:RES {rbws[ind-1]}KHz')
            # print(f'Setting Range {ind} RBW to {rbws[ind-1]}KHz')
            time.sleep(1)
            self.write(f':SENS:LIST:RANG{ind}:LIM:STAR {lims[ind-1]}')
            time.sleep(1)
            self.write(f':SENS:LIST:RANG{ind}:LIM:STOP {lims[ind-1]}')
            time.sleep(1)
        self.write('SENS:LIST:XADJ')
        time.sleep(5)
        # self.get_one_measurement()
        # print(len(df_spurs['Start']))
    
    def meas_spurs_emiss(self, refLvl=-65, refLvlOffs=0):
        self.measurement_prep(refLvl, refLvlOffs, meas_time=15)
        spurs_vals = self.query_ascii_values(':TRAC:DATA? SPURIOUS')
        spurs_res = []
        spurs_peaks = []
        spurs_margins = []
        for ind in range(0, len(spurs_vals), 3):
            spurs_peaks.append(round(spurs_vals[ind],2))
            spurs_res.append(round(spurs_vals[ind+1],2))
            spurs_margins.append(round(spurs_vals[ind+2],2))
        return(spurs_res, spurs_peaks, spurs_margins)
    
    def spectrum_fcc_obue(self, band_edge, bw, channel = 'Bot', ref_lvl = 53, rbw = '100 KHz', vbw = '1 MHz', swt = '200ms', rlvlOffs = 45, trig = True):
        self.create_new_mode(mode = 'SANALYZER', name = 'Spec Meas')
        self.clear()
        self.sel_existing_mode('Spec Meas')
        if(channel == 'Bot'):
            self.set_start_stop_freq(band_edge - 7, band_edge + 1)
        else:
            self.set_start_stop_freq(band_edge - 1, band_edge + 7)
        time.sleep(2)
        self.ref_lvl_offset(rlvlOffs)
        self.set_ref_lvl(ref_lvl)
        if(trig):
            self.set_trig_source()
            self.set_trig_gate(gdelay = '86us', glength = '3.715ms')
        else:
            self.set_trig_source(src = 'IMM')
        self.set_rbw(rbw)
        self.set_vbw(vbw)
        self.set_up_trace()
        self.set_sweep_time(swt)
        self.set_sweep_type('FFT')
        for mkr_id in range(1, 7):
            if(mkr_id == 1):
                if(channel == 'Bot'):
                    self.write('CALC:MARK{}:X {}MHz'.format(mkr_id, band_edge - (bw/200)))
                else:
                    self.write('CALC:MARK{}:X {}MHz'.format(mkr_id, band_edge + (bw/200)))
                self.write('CALC:MARK{}:FUNC:BPOW:STAT ON'.format(mkr_id))
                self.write('CALC:MARK{}:FUNC:BPOW:SPAN {}KHz'.format(mkr_id, bw*10))
            else:
                if(channel == 'Bot'):
                    self.write('CALC:MARK{}:X {}MHz'.format(mkr_id, band_edge - (mkr_id - 1) - 0.5))
                else:
                    self.write('CALC:MARK{}:X {}MHz'.format(mkr_id, band_edge + (mkr_id - 1) + 0.5))
                self.write('CALC:MARK{}:FUNC:BPOW:STAT ON'.format(mkr_id))
                self.write('CALC:MARK{}:FUNC:BPOW:SPAN 1MHz'.format(mkr_id))
        res = self.get_bpow_mark_res(num_of_mkrs = 6)
        return res

    def get_bpow_mark_res(self, num_of_mkrs = 6):
        bpow_res = []
        self.set_single_sweep(False)
        time.sleep(5)
        self.set_single_sweep(True)
        self.get_one_measurement()
        time.sleep(5)
        for mkr_id in range(1, (num_of_mkrs+1)):
            bpow_res.append(round(self.query_ascii_values('CALC:MARK{}:FUNC:BPOW:RES?'.format(mkr_id))[0], 2))
        return bpow_res

    def setup_OBW_spec(self, freq, bw, tGDelay='86us', tGLength='3.715ms', trigSrc = 'EXT', sweepTime = '50ms', rbw='30KHz'):
        self.write(':CALC:MARK:FUNC:POW:SEL OBW')
        self.set_center_freq(freq)
        self.write(f':SENS:POW:ACH:BAND:CHAN {bw}MHz')
        self.set_span(span=f'{2*bw}MHz')
        self.set_rbw(rbw)
        self.set_up_trace(averType='POW')
        if(tGDelay and tGLength):
            self.set_trig_gate(gdelay = tGDelay, glength = tGLength)
        self.set_trig_source(trigSrc)
        self.set_sweep_time(sweepTime)
    
    def meas_OBW(self, refLvl=55, refLvlOffs=45):
        self.measurement_prep(refLvl, refLvlOffs)
        obw_res= self.query_ascii_values(':CALC:MARK:FUNC:POW:RES? OBW')
        return round(obw_res[0]/1000000, 2)

    def setup_tx_on_off_pwr(self, sig_file_name, freq = 3640, avg_cnt=10):
        self.write(':CONF:NR5G:MEAS TPOO')
        time.sleep(5)
        self.set_single_sweep()
        self.load_test_model(sig_file_name)
        self.set_center_freq(freq)
        self.write(f':CONF:NR5G:OOP:NFR {avg_cnt}')
    
    def meas_tx_on_off_pwr(self):
        tx_oop_res = []
        self.set_single_sweep()
        self.get_one_measurement()
        time.sleep(15)
        res = self.query_ascii_values(':TRAC6:DATA? LIST')
        inds = [3, 5, 6, 10, 12, 13]
        for ind in inds:
            if(ind in [3, 10]):
                tx_oop_res.append(round(res[ind], 2))
            else:
                tx_oop_res.append(round(res[ind]*1000000000, 2))
        return tx_oop_res

if __name__ == "__main__":
    ##### Inputs #####
    # fsv_ip = '192.168.255.51'
    # ssname = 'Midas_Test'
    # ssloc = r'\\tsclient\\C\\Screenshots_SigAnalyzer'
    # freq = 3640
    # tm = '1_1'
    # bw = 100
    # testModel = 'NR-FR1-TM{}__TDD_{}MHz_30KHz'.format(tm, bw)
    # freqs = [3420, 3579.99]
    # tml = [tm]
    # tModL = [testModel]
    # bws = [bw, bw]
    frequency = 3610 # Frequency of signal generated
    tm = '3_1a'
    duplex = 'TDD'
    bw = 100
    scs = 30
    sig_analyzer_ip = '10.0.0.78'
    band = 'N78'
    refLvl = 45
    refLvlOffs = 45
    tGDelay = '18us'
    tGLength = '3.7ms'
    noc = 1
    spurs_file = 'C:\MidasRFV\Midas_Colocate_Bands_and_Spur_Limits.xlsx'
    sig_file_name = f'NR-FR1-TM{tm}__{duplex}_{bw}MHz_{scs}kHz' # Pre-Defined file to be loaded
    #####End#####
    try:
        fsv = FSVHandler(tcp_ip=sig_analyzer_ip, cust_name='SigAnalyzer')
        print(fsv.check_identity())
        # print(fsv.measure_ACLR(0, 0))
        # print(fsv.get_mode_list())
        # fsv.create_new_mode()
        # fsv.sel_existing_mode('Spec OBUE')
        # fsv.set_rbw(1000000)
        # fsv.set_center_freq(frequency)
        # fsv.setup_OBUE_5g(sig_file_name, frequency, band)
        # print(fsv.meas_OBUE_5g(refLvl, refLvlOffs))
        # fsv.setup_EVM_FErr(sig_file_name, noc, frequency, band)
        # print(fsv.measure_EVM_FErr(tm, noc, refLvl, refLvlOffs))
        # fsv.setup_tx_on_off_pwr(sig_file_name, freq=frequency)
        # print(fsv.meas_tx_on_off_pwr())
        # fsv.clear()
        # fsv.reset()
        # time.sleep(30)
        # fsv.create_new_mode(mode='NR5G', name='5G ACLR')
        # fsv.sel_existing_mode('5G ACLR')
        # fsv.setup_ACLR(freq=frequency, band=band, testModel=sig_file_name, tGDelay=tGDelay, tGLength=tGLength)
        # fsv.create_new_mode(mode = 'SANALYZER', name = 'Spec Spurs')
        # fsv.sel_existing_mode('Spec Meas')
        # fsv.setup_OBW_spec(frequency, bw, tGDelay, tGLength)
        # print(fsv.meas_OBW(-15, 0))
        # import Validate_Construct_Datasets
        # offsets = Validate_Construct_Datasets.get_catb_offsets((3410, 3800), 3460, 100)
        # print(fsv.spec_obue_catb(offsets, refLvl=refLvl, refLvlOffs=refLvlOffs, tGDelay=tGDelay, tGLength=tGLength))
        # fsv.spec_obue_setup(3370, 3840, 3750)
        # fsv.setup_spurs_emiss(xl_name=spurs_file)
        # print(fsv.meas_spurs_emiss())
        # fsv.ss_loc = r'\\tsclient\D\MidasRFV\Test_Sequence_Data\Screenshots'
        # fsv.get_screenshot()
        # fsv.initialize()
        # time.sleep(15)
        # fsv.set_ext_ref_clk()
        # fsv.set_center_freq(freq=frequency)
        fsv.close()
    except Exception as e:
        print(e)
        if(fsv):
            fsv.close()