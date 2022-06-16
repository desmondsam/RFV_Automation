import visa_connections
import time

class PXAHandler(visa_connections.DeviceHandler):

    def __init__(self, tcp_ip, cust_name = 'PXA_Analyzer', ss_name = r'Default_Screenshot', ss_loc = r'\\tsclient\\C\\Screenshots'):
        super(PXAHandler, self).__init__(tcp_ip, cust_name = cust_name)
        self.ss_name = ss_name
        self.ss_loc = ss_loc
        self.set_timeout()
    
    def set_timeout (self, timeout = 200000):
        self.timeout = timeout
    
    def set_cable_loss(self, cable_loss):
        self.write(f'CORR:BTS:GAIN {cable_loss}')
        self.plog(f'Path Loss set to {cable_loss} dB')
    
    def set_ref_lvl(self, meas='ACP', refLvl=-20, perDiv=10):
        self.write(f':DISP:{meas}:WIND:TRAC:Y:RLEV {refLvl}')
        self.write(f':DISP:{meas}:WIND:TRAC:Y:PDIV {perDiv}')
        self.plog(f'Reference Level set to {refLvl} dBm and scale per division set to {perDiv} dB')

    def set_attenuation(self, attenuation = 0):
        self.write(f':POW:ATT {attenuation}')
        self.plog(f'Attenuation Manually set to {attenuation} dB')

    def create_new_mode(self, mode='NR5G'):
        self.write(f':INST:SEL {mode}')
        self.plog(f'Created New {mode} Mode')
    
    def create_new_window(self, mode='NR5G', meas='ACP', scr_name='5G ACLR'):
        self.write(':INST:SCR:CRE')
        self.write(f':INST:CONF:{mode}:{meas}')
        time.sleep(5)
        self.rename_screen(scr_name)
        self.plog(f'Created new window named {scr_name} in {mode} mode with {meas} measurement')

    def rename_screen(self, scr_name):
        self.write(f":INST:SCR:REN '{scr_name}'")

    def get_active_screen_name(self):
        scr_name = self.query(':INST:SCR:SEL?')
        return scr_name
    
    def select_screen(self, scr_name):
        self.write(f":INST:SCR:SEL '{scr_name}'")
        self.plog(f'Selected Window/Screen with the name {scr_name}')
    
    def reset_screens(self):
        scr_list = self.query(':INST:SCR:LIST?')
        if(',' in scr_list):
            self.write(':INST:SCR:DEL:ALL')
        self.write(':SYST:DEF ALL')
        curr_scr_name = self.get_active_screen_name().strip().replace('"', '')
        if(curr_scr_name != 'MyDefault'):
            self.rename_screen('MyDefault')
        self.plog(f'Analyzer reset to power ON state (One Spectrum Screen)')
    
    def set_5G_center_freq(self, freq):
        self.write(f':CCAR:REF {freq}MHz')
        self.plog(f'Center Frequency set to {freq} MHz')
    
    def set_atten_min_clip(self):
        self.write(f':POW:RANG:OPT IMM')
        self.plog(f'RF Attenuation set to minimum clipping')
    
    def configure_meas_standard(self, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1'):
        #Setting up Analyzer to Demodulate
        #TM can be '1_1', '1_2', '2', '2A', '3_1', '3_1A', '3_2', '3_3'
        #Duplex can be 'TDD' or 'FDD'
        #frange can be 'FR1' or 'FR2'
        rb_alloc = tm.replace('_', 'DOT')
        self.write(f'RAD:STAN:PRES:CARR B{bw}M')
        self.write(f'RAD:STAN:PRES:FREQ:RANG {frange}')
        self.write(f'RAD:STAN:PRES:DMOD {duplex}')
        self.write(f'RAD:STAN:PRES:SCS SCS{scs}K')
        self.write(f'RAD:STAN:PRES:RBAL DLTM{rb_alloc}')
        self.set_bts_type()
        self.set_bts_cat()
        self.write('RAD:STAN:PRES:IMM')
        self.plog(f'Measurement Standard Configured to {bw}MHz {duplex} TM{tm} carrier with SCS {scs}KHz')
    
    def set_bts_type(self, bts_type='FR1C'):
        self.write(f':RAD:STAN:PRES:DLIN:BS:TYPE {bts_type}')
        self.plog(f'BTS Type set to {bts_type}')

    def set_bts_cat(self, cat='BWAR'):
        self.write(f':RAD:STAN:PRES:DLIN:BS:CAT {cat}')
        self.plog(f'BTS Category set to {cat}')
    
    def set_noc(self, noc=2):
        self.write(f'CCAR:COUN {noc}')
        self.plog(f'Number of Carriers set to {noc}')
    
    def set_trace_type(self, meas='ACP', ttype='AVER'):
        self.write(f':TRAC:{meas}:TYPE {ttype}')
        self.plog(f'Trace type for {meas} Measurement set to {ttype}')
    
    def set_trig_src(self, meas='ACP', src='EXT1'):
        self.write(f':TRIG:{meas}:SOUR {src}')
        self.plog(f'Trigger Source for {meas} measurement set to {src}')

    def set_gate(self, src='EXT1', gdelay='80us', glength='3.615ms'):
        self.write(f':SWE:EGAT:SOUR {src}')
        self.write(':SWE:EGAT ON')
        self.write(f':SWE:EGAT:DEL {gdelay}')
        self.write(f':SWE:EGAT:LENG {glength}')
        self.plog(f'Gate set with {src}, delay {gdelay} and length {glength}')
    
    def set_single_sweep(self, single = True):
        if(single):
            self.write('INIT:CONT OFF')
            self.plog('Sweep mode set to Single')
        else:
            self.write('INIT:CONT ON')
            self.plog('Sweep mode set to Continuous')

    def get_one_measurement(self):
        self.write(':INIT:IMM; *WAI')
        time.sleep(3)
        self.plog('Initiating and completing One Measurement')

    def common_5g_setup(self, freq=3610, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1', trigSrc='EXT1', gateSrc=None, tGDelay=None, tGLength=None, frameSync=None, meas='ACP'):
        self.write(f'CONF:{meas}')
        self.set_single_sweep()
        self.set_5G_center_freq(freq)
        self.configure_meas_standard(bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm)
        self.set_trig_src(meas=meas, src=trigSrc)
        if(gateSrc and tGDelay and tGLength):
            self.set_gate(src=gateSrc, gdelay=tGDelay, glength=tGLength)
        if(frameSync):
            self.write(f':TRIG:FRAM:SYNC {frameSync}')

    def fetch_results(self, meas, cable_loss=15, waitTime=10):
        self.set_cable_loss(cable_loss=cable_loss)
        self.set_atten_min_clip()
        self.set_single_sweep()
        self.get_one_measurement()
        time.sleep(waitTime)
        return self.query_ascii_values(f'FETC:{meas}?')

    def setup_ACLR(self, freq=3610, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1', trigSrc='EXT1', gateSrc='EXT1', tGDelay='80us', tGLength='3.615ms', sweepTime='50ms'):
        self.common_5g_setup(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, gateSrc=gateSrc,tGDelay=tGDelay, tGLength=tGLength, meas='ACP')
        self.write(f':ACP:SWE:TIME {sweepTime}')
    
    def measure_ACLR(self, cable_loss=15):
        # self.write(':DISP:ACP:WIND:TRAC:Y:COUP ON') #Ref Level Sets to Auto Scaling by Default
        acp_vals = self.fetch_results(meas='ACP', cable_loss=cable_loss, waitTime=15)
        acp_indices = [1, 4, 6, 8, 10]
        acp_sel_vals = [round(acp_vals[index],2) for index in acp_indices]
        return acp_sel_vals
    
    def setup_OBW(self, freq=3610, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1', trigSrc='EXT1', gateSrc='EXT1', tGDelay='80us', tGLength='3.615ms'):
        self.common_5g_setup(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, gateSrc=gateSrc, tGDelay=tGDelay, tGLength=tGLength, meas='OBW')
    
    def measure_OBW(self, cable_loss = 15):
        obw_vals = self.fetch_results(meas='OBW', cable_loss=cable_loss, waitTime=5)
        obw_res = round(obw_vals[0]/1000000, 2) #Converting Hz to MHz and rounding it off
        return obw_res
    
    def setup_catB_SEM(self, freq=3610, fstart=3370, fstop=3840, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1', trigSrc='EXT1', gateSrc='EXT1', tGDelay='80us', tGLength='3.615ms'):
        self.common_5g_setup(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, gateSrc=gateSrc, tGDelay=tGDelay, tGLength=tGLength, meas='SEM')
        f_obue_start = int(freq - fstart - (bw/2))
        f_obue_stop = int(fstop - freq - (bw/2))
        f_last_offs = max(f_obue_start, f_obue_stop)
        self.write(':SEM:OFFS:TYPE ETOC')
        self.write(':SEM:DET:CARR AVER')
        self.write(':SEM:DET:OFFS POS')
        self.write(':SEM:OFFS:LIST:STAT ON, ON, ON, OFF, OFF, OFF')
        self.write(':SEM:OFFS:LIST:FREQ:STAR 50 kHz, 5.05 MHz, 10.5 MHz')
        self.write(f':SEM:OFFS:LIST:FREQ:STOP 5.05 MHz, 10.05 MHz, {f_last_offs} MHz')
        self.write(':SEM:OFFS:LIST:BAND 100.0 kHz, 100.0 kHz, 1.00 MHz')
        self.write(':SEM:OFFS:LIST:BAND:IMUL 1,1,1')
        self.write(':SEM:OFFS:LIST:SWE:TIME 200 ms, 200 ms, 200 ms')
    
    def meas_catB_SEM(self, freq=3610, bw=100, cable_loss=15):
        sem_vals = self.fetch_results(meas='SEM', cable_loss=cable_loss, waitTime=10)
        sem_indices = range(13,39,5)
        sem_abs_res = [round(sem_vals[ind], 2) for ind in sem_indices]
        sem_pk_freq_offs = [round(sem_vals[ind+1]/1e6, 2) for ind in sem_indices]
        sem_pk_freqs = []
        for pk in sem_pk_freq_offs:
            if (pk < 0):
                sem_pk_freqs.append((freq-(bw/2)+pk)*1e6)
            else:
                sem_pk_freqs.append((freq+(bw/2)+pk)*1e6)
        sem_margins = [round(sem_vals[ind]*-1, 2) for ind in range(70,70+6)]
        start_fs = self.query_ascii_values(':SEM:OFFS:LIST:FREQ:STAR?')
        stop_fs = self.query_ascii_values(':SEM:OFFS:LIST:FREQ:STOP?')
        start_f_sel = [round((bw/2)+(val/1e6), 2) for val in start_fs[:3]]
        stop_f_sel = [round((bw/2)+(val/1e6), 2) for val in stop_fs[:3]]
        rbws = self.query_ascii_values(':SEM:OFFS:LIST:BAND?')[:3]
        pipe_sem_res = []
        for ind in range(0, 6, 2):
            # print(ind, ind//2, ind+1, (ind+1)//2)
            pipe_sem_res.append([sem_abs_res[ind], sem_margins[ind], -start_f_sel[ind//2], -stop_f_sel[ind//2], rbws[ind//2], sem_pk_freqs[ind]])
            pipe_sem_res.append([sem_abs_res[ind+1], sem_margins[ind+1], start_f_sel[(ind+1)//2], stop_f_sel[(ind+1)//2], rbws[(ind+1)//2], sem_pk_freqs[ind+1]])
        return pipe_sem_res
    
    def setup_evm_ferr_tpdr(self, freq=3610, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1', trigSrc='EXT1'):
        self.common_5g_setup(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, frameSync=trigSrc, meas='EVM')
        # self.write('CONF:EVM')
        # self.set_single_sweep()
        # self.set_5G_center_freq(freq=freq)
        # self.configure_meas_standard(bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm)
        # self.set_trig_src(meas='EVM', src=trigSrc)
        # self.write(f':TRIG:FRAM:SYNC {trigSrc}')
    
    def meas_evm_ferr_tpdr(self, cable_loss=15):
        evm_vals = self.fetch_results(meas='EVM', cable_loss=cable_loss, waitTime=10)
        # ostp_res = self.query_ascii_values('FETC:EVM002103?')[0] #OSTP - Currently think it is same as evm_vals[22]
        inds = [1, 2, 3, 22]
        evm_res = [round(evm_vals[ind], 2) for ind in inds]
        return (evm_res)

    def setup_tx_oop(self, freq=3610, bw=100, frange='FR1', duplex='TDD', scs=30, tm='1_1', trigSrc='EXT1'):
        self.common_5g_setup(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, frameSync=trigSrc, meas='PVT')

    def meas_tx_oop(self, cable_loss=15):
        oop_vals = self.fetch_results(meas='PVT', cable_loss=cable_loss, waitTime=5)
        oop_res = []
        oop_res.append(round(oop_vals[7], 2))
        oop_res.append(round(oop_vals[6]*1e9, 2))
        oop_res.append(round(oop_vals[5]*1e9, 2))
        return oop_res

if __name__ == '__main__':
    freq = 3750
    duplex = 'TDD'
    frange = 'FR1'
    sweepTime = '75ms'
    bw = 100
    scs = 30
    tm='3_1a'
    trigSrc = 'EXT1'
    gateSrc = 'EXT1'
    gDelay = '80us'
    gLength = '3.615ms'
    cable_loss = 0

    try:
        pxa = PXAHandler(tcp_ip='192.168.255.210')
        # pxa.set_5G_center_freq(3450)
        # pxa.configure_meas_standard(tm='3_1a')
        # pxa.reset_screens()
        # pxa.create_new_window(mode='NR5G', meas='ACP', scr_name='5G ACLR')
        # pxa.create_new_window(mode='NR5G', meas='OBW', scr_name='5G OBW')
        # time.sleep(5)
        # pxa.reset_screens()
        # time.sleep(5)
        # print(pxa.get_active_screen_name())
        # pxa.create_new_window(mode='NR5G', meas='ACP', scr_name='5G ACLR')
        # pxa.select_screen('5G ACLR')
        # pxa.setup_ACLR(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, gateSrc=gateSrc, tGDelay=gDelay, tGLength=gLength, sweepTime=sweepTime)
        # pxa.create_new_window(mode='NR5G', meas='OBW', scr_name='5G OBW')
        # pxa.select_screen('5G OBW')
        # pxa.setup_OBW(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, gateSrc=gateSrc, tGDelay=gDelay, tGLength=gLength)
        # pxa.create_new_window(mode='NR5G', meas='SEM', scr_name='5G SEM')
        # pxa.select_screen('5G SEM')
        # pxa.setup_catB_SEM(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc, gateSrc=gateSrc, tGDelay=gDelay, tGLength=gLength)
        # pxa.create_new_window(mode='NR5G', meas='EVM', scr_name='5G EVM')
        # pxa.select_screen('5G EVM')
        # pxa.setup_evm_ferr_tpdr(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc)
        # pxa.create_new_window(mode='NR5G', meas='PVT', scr_name='5G OOP')
        # pxa.select_screen('5G OOP')
        # pxa.setup_tx_oop(freq=freq, bw=bw, frange=frange, duplex=duplex, scs=scs, tm=tm, trigSrc=trigSrc)
        pxa.select_screen('5G ACLR')
        acp_res = pxa.measure_ACLR(cable_loss=cable_loss)
        time.sleep(2)
        pxa.select_screen('5G OBW')
        obw_res = pxa.measure_OBW(cable_loss=cable_loss)
        time.sleep(2)
        pxa.select_screen('5G SEM')
        sem_res = pxa.meas_catB_SEM(freq=freq, bw=bw, cable_loss=cable_loss)
        time.sleep(2)
        pxa.select_screen('5G EVM')
        evm_res = pxa.meas_evm_ferr_tpdr(cable_loss=cable_loss)
        time.sleep(2)
        pxa.select_screen('5G OOP')
        oop_res = pxa.meas_tx_oop(cable_loss=cable_loss)
        time.sleep(2)
        print (acp_res)
        print (obw_res)
        print (sem_res)
        print (evm_res)
        print (oop_res)
        pxa.close()
    except Exception as e:
        print(e)
        if(pxa):
            pxa.close()
