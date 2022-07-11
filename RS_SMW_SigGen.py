import visa_connections
import time

class SMWHandler(visa_connections.DeviceHandler):

    def set_timeout (self,timeout = 200000):
        self.timeout = timeout
    
    def set_frequency(self, mode = 'FIX', freq = 3650, channel=1):
        self.write(f'SOUR{channel}:FREQ:{mode} {freq} MHz')
        self.plog(f'Channel {channel} Frequency set to {freq} MHz')
        time.sleep(2)
    
    def get_frequency(self, channel=1):
        freq = self.query_ascii_values(f'SOUR{channel}:FREQ?')[0]
        return round((freq/1e6),4)

    def set_rf_level(self, level = -10, channel=1):
        self.write(f'SOUR{channel}:POW:LEV:IMM:AMPL {level}')
        self.plog(f'Channel {channel} RF Level set to {level} dBm')
    
    def set_rf_lvl_offset(self, offs = 2, channel=1):
        self.write(f'SOUR{channel}:POW:OFFS {offs}')
        self.plog(f'Channel {channel} RF Level Offset set to {offs} dB')
    
    def get_rf_level(self, channel=1):
        lvl = self.query(f'SOUR{channel}:POW:LEV:IMM:AMPL?')
        return lvl

    def set_rf_state(self, state = 'ON', channel=1):
        self.write(f':OUTP{channel} {state}')
        self.plog(f'RF on channel {channel} turned {state}')
    
    def set_5g_mod_state(self, mod_5g = 'ON', channel=1):
        self.write(f':SOUR{channel}:BB:NR5G:STAT {mod_5g}')
        self.plog(f'5G Modulation (Baseband) on Channel {channel} turned {mod_5g}')
    
    def set_all_mod_rf_state(self, state):
        #For 2 channel signal generators only
        for channel in [1, 2]:
            self.set_5g_mod_state(mod_5g=state, channel=channel)
            self.set_rf_state(state=state, channel=channel)
    
    def recall_5g_mod_file(self, floc, fname, channel=1):
        self.write(f':SOUR{channel}:BB:NR5G:SETT:LOAD "{floc}/{fname}"')
        self.plog(f'5G state file {fname} recalled on Channel {channel}')
    
    def set_ref_clk_src(self, src='EXT'):
        self.write(f'ROSC:SOUR {src}')
        time.sleep(3)
        self.plog(f'Reference Clock Source set to {src}ERNAL')
    
    def set_5g_link_direction(self, link_direction = 'DOWN', channel=1):
        self.write(f':SOUR{channel}:BB:NR5G:LINK {link_direction}')
        self.plog(f'Channel {channel} 5G Modulation direction set to {link_direction}LINK')
    
    def load_5g_dl_test_model(self, tmodel, channel=1):
        self.write(f'SOUR{channel}:BB:NR5G:SETT:TMOD:DL "{tmodel}"')
        self.plog(f'Loaded 5G Predefined Downlink File {tmodel} on channel {channel}')
    
    def set_5g_trig_mode(self, trig_mode = 'AUTO', channel=1):
        self.write(f'SOUR{channel}:BB:NR5G:TRIG:SEQ {trig_mode}')
        time.sleep(3)
        self.plog(f'Channel {channel} 5G Trigger Mode set to {trig_mode}')
    
    def user_connector_direction(self, connector = 3, direction = 'OUTP'):
        #direction is INP for Input and OUTP for Output UNUS for Unused
        self.write('SOUR:INP:USER{}:DIR {}'.format(connector, direction))
        self.plog('Connector User {} set to direction {}UT'.format(connector, direction))
    
    def user_connector_output_signal(self, connector = 3, signal = 'MARKA', marker = 1):
        #signal = MARKA/SYNCOUT
        # marker = 1|2|3/None
        self.write('OUTP:USER{}:SIGN {}{}'.format(connector, signal, marker))
        self.plog('Connector User {} set to signal Baseband {} Marker {}'.format(connector, signal[-1], marker))
    
    def set_5g_trig_output_mode(self, output_mode = 'FRAM', channel=1):
        #Modes = FRAM/ULDL/SUBF
        self.write(f'SOUR{channel}:BB:NR5G:TRIG:OUTP:MODE {output_mode}')
        self.plog(f'Channel {channel} 5G Trigger output mode set to {output_mode}')
    
    def set_5g_clock_source(self, clock_src = 'INT', channel = 1):
        self.write(f'SOUR{channel}:BB:NR5G:CLOC:SOUR {clock_src}')
        self.plog(f'Channel {channel} 5G Clock Source set to {clock_src}ERNAL')
    
    def configure_5g_dl_baseband(self, sig_file_name, trig_connector = 3, trig_mode='AUTO', output_mode = 'FRAM', chan=1):
        self.plog('Configuring 5G Downlink Baseband')
        self.set_5g_link_direction(link_direction = 'DOWN', channel=chan)
        self.load_5g_dl_test_model(tmodel= sig_file_name, channel=chan)
        self.set_5g_trig_mode(trig_mode = trig_mode, channel=chan)
        self.user_connector_direction(connector = trig_connector, direction = 'OUTP')
        self.user_connector_output_signal(connector = trig_connector)
        self.set_5g_trig_output_mode(output_mode = output_mode, channel=chan)
        self.plog(f'Channel {chan} 5G Downlink Baseband Configuration Completed')
    
    def conf_5g_ul_381411_tcWizard(self, ruType='WIDE', testCase='TC72', tcw_rel=16):
        self.write(':SOUR:BB:NR5G:TCW:SPEC TS38141_1')
        self.plog('Setting up 38141.1 Test Case Wizard')
        self.write(f':SOUR:BB:NR5G:TCW:BSCL {ruType}')
        self.plog(f'Set up Test Case Wizard for {ruType} base station ')
        self.write(f':SOUR:BB:NR5G:TCW:TC TS381411_{testCase}')
        self.plog(f'Set up Test Case Wizard for section {testCase}')
        self.write(f':SOUR:BB:NR5G:TCW:REL REL{tcw_rel}')
        self.plog(f'Set up Test Case Wizard to Release{tcw_rel}')
        # time.sleep(3)

    def conf_5g_ul_wantedSig(self, freq=3605, bw=100, scs=30, cell_id=0, rb_offs=0, typeA_Pos=2):
        self.write(f':SOUR:BB:NR5G:TCW:WS:RFFR {freq} MHz')
        self.write(f':SOUR:BB:NR5G:TCW:WS:CBW BW{bw}')
        self.write(f':SOUR:BB:NR5G:TCW:WS:SCSP N{scs}')
        self.plog(f'TCW Wanted Signal set at {freq}MHz with channel BW {bw}MHz and scs {scs}kHz')
        self.write(f':SOUR:BB:NR5G:TCW:WS:CELL {cell_id}')
        self.write(f':SOUR:BB:NR5G:TCW:WS:RBOF {rb_offs}')
        self.write(f':SOUR:BB:NR5G:TCW:WS:TAP {typeA_Pos}')
        self.plog(f'TCW Wanted Signal set to cell id {cell_id}, with RB Offset {rb_offs} and DMRS Type A Position {typeA_Pos}')
        time.sleep(3)
    
    def conf_5g_ul_interfererSig(self, freq_alloc='HIGH', ueid=0, clid=0, fr_shift_m=None, rf_freq=None, test_req='BLPE'):
        if(freq_alloc):
            self.write(f':SOUR:BB:NR5G:TCW:FA:FRAL {freq_alloc}')
            self.write(f':SOUR:BB:NR5G:TCW:IS:UEID {ueid}')
            self.write(f':SOUR:BB:NR5G:TCW:IS:CLID {clid}')
            self.plog(f'TCW Interferer Signal set at {freq_alloc} with UE ID: {ueid} and cell id: {clid}')
            if(fr_shift_m):
                self.write(f':SOUR:BB:NR5G:TCW:IS:FRSH {fr_shift_m}')
        if(rf_freq):
            self.write(f':SOUR:BB:NR5G:TCW:IS:RFFR {rf_freq}')
            self.write(f':SOUR:BB:NR5G:TCW:IS:TREQ {test_req}')
        time.sleep(3)
    
    def conf_5g_ul_trigger(self, source='EGT1', delay_unit='TIME', delay_val='0us'):
        self.set_5g_trig_mode(trig_mode = 'AAUT')
        time.sleep(5)
        self.write(f':SOUR:BB:NR5G:TRIG:SOUR {source}')
        time.sleep(5)
        self.plog(f'5G Uplink Trigger source set to {source}')
        self.write(f':SOUR:BB:NR5G:TRIG:DEL:UNIT {delay_unit}')
        time.sleep(5)
        self.plog(f'5G Uplink Trigger Delay Unit set to {delay_unit}')
        if(delay_unit=='TIME'):        
            self.write(f':SOUR:BB:NR5G:TRIG:EXT:TDEL {delay_val}')
        else:
            self.write(f':SOUR:BB:NR5G:TRIG:EXT:DEL {delay_val}')
        self.plog(f'5G Uplink Trigger Delay set to {delay_val}')
    
    def sync_outp_ext_trig(self):
        self.write(':SOUR:BB:NR5G:TRIG:EXT:SYNC:OUTP 0')
        self.write(':SOUR:BB:NR5G:TRIG:EXT:SYNC:OUTP 1')
        self.plog('Toggled Sync Output to External Trigger')
    
    def set_ul_tm(self, user=0, cell=0, bwp=0, tm='FR1A15'):
        self.write(f':SOUR:BB:NR5G:UBWP:UUSER{user}:CELL{cell}:UL:BWP{bwp}:FRC:TYPE {tm}')
    
    def apply_testCaseWiz_settings(self):
        self.write(':SOUR:BB:NR5G:TCW:APPL')
        self.plog('Applied Test Case Wizard Settings')
    
    def general_tcw_setup(self, testCase, freq, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc=None, is_ueid=0, is_clid=0, fr_shift_m=None, is_rf_freq=None, treq='BLPE', tcw_rel=16):
        self.set_5g_link_direction(link_direction = 'UP')
        self.conf_5g_ul_381411_tcWizard(testCase=testCase, tcw_rel=tcw_rel)
        self.conf_5g_ul_wantedSig(freq=freq, bw=bw, scs=scs, cell_id=cid, rb_offs=rb_offs)
        if(freq_alloc):
            self.conf_5g_ul_interfererSig(freq_alloc=freq_alloc, ueid=is_ueid, clid=is_clid, fr_shift_m=fr_shift_m)
        if(is_rf_freq):
            self.conf_5g_ul_interfererSig(freq_alloc=None, rf_freq=is_rf_freq, test_req=treq)
        self.apply_testCaseWiz_settings()
        self.conf_5g_ul_trigger(source=trigSrc, delay_unit=trigDelUnit, delay_val=trigDelVal)

    def setup_Sensitivity(self, freq, bw, scs, cid, rb_offs, trigSrc, trigDelUnit, trigDelVal):
        self.plog('Configuring for Sensitivity Measurement')
        self.general_tcw_setup(testCase='TC72', freq=freq, bw=bw, scs=scs, cid=cid, rb_offs=rb_offs, trigSrc=trigSrc, trigDelUnit=trigDelUnit, trigDelVal=trigDelVal)
        self.set_rf_state()
    
    def setup_ACSelectivity(self, freq, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc='HIGH', is_ueid=0, is_clid=0):
        self.plog('Configuring for Adjacent Channel Selectivity Measurement')
        self.general_tcw_setup(testCase='TC741', freq=freq, bw=bw, scs=scs, cid=cid, rb_offs=rb_offs, trigSrc=trigSrc, trigDelUnit=trigDelUnit, trigDelVal=trigDelVal, freq_alloc=freq_alloc, is_ueid=is_ueid, is_clid=is_clid)
        self.set_rf_state()
        self.set_rf_state(channel=2)
    
    def setup_General_IBB(self, freq, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc='LOW', is_ueid=0, is_clid=0):
        self.plog('Configuring for General In Band Blocking Measurement')
        self.general_tcw_setup(testCase='TC742A', freq=freq, bw=bw, scs=scs, cid=cid, rb_offs=rb_offs, trigSrc=trigSrc, trigDelUnit=trigDelUnit, trigDelVal=trigDelVal, freq_alloc=freq_alloc, is_ueid=is_ueid, is_clid=is_clid)
        self.set_rf_state()
        self.set_rf_state(channel=2)
    
    def setup_NarrowBand_IBB(self, freq, bw, scs, cid, rb_offs, trigSrc, trigDelUnit, trigDelVal, freq_alloc, is_ueid=0, is_clid=0, fr_shift_m = 'FS0'):
        self.plog('Configuring for NarrowBand In Band Blocking Measurement')
        self.general_tcw_setup(testCase='TC742B', freq=freq, bw=bw, scs=scs, cid=cid, rb_offs=rb_offs, trigSrc=trigSrc, trigDelUnit=trigDelUnit, trigDelVal=trigDelVal, freq_alloc=freq_alloc, is_ueid=is_ueid, is_clid=is_clid, fr_shift_m=fr_shift_m)
        self.set_rf_state()
        self.set_rf_state(channel=2)
    
    def setup_OutOfBand_Blocking(self, freq, bw, scs, cid, rb_offs, trigSrc, trigDelUnit, trigDelVal, is_rf_freq, treq):
        self.plog('Configuring for Out of Band Blocking Measurement')
        self.general_tcw_setup(testCase='TC75', freq=freq, bw=bw, scs=scs, cid=cid, rb_offs=rb_offs, trigSrc=trigSrc, trigDelUnit=trigDelUnit, trigDelVal=trigDelVal, is_rf_freq=is_rf_freq, treq=treq)
        self.set_rf_state()
        self.set_rf_state(channel=2)
    
    def setup_ICSelectivity(self, freq, bw, scs, cid, rb_offs, trigSrc, trigDelUnit, trigDelVal, freq_alloc, is_ueid=0, is_clid=0):
        self.plog('Configuring for In Channel Selectivity Measurement')
        self.general_tcw_setup(testCase='TC78', freq=freq, bw=bw, scs=scs, cid=cid, rb_offs=rb_offs, trigSrc=trigSrc, trigDelUnit=trigDelUnit, trigDelVal=trigDelVal, freq_alloc=freq_alloc, is_ueid=is_ueid, is_clid=is_clid)
        self.set_rf_state()
        self.set_rf_state(channel=2)
    
    def manual_setup_ultest(self, floc, fname, trigDelay):
        self.set_ref_clk_src('EXT')
        self.recall_5g_mod_file(floc, fname)
        self.conf_5g_ul_trigger(delay_val=trigDelay)
        self.sync_outp_ext_trig()
        self.set_5g_mod_state('ON')
        self.set_rf_state('ON')
    
def main():
    try:
        smw_ip = '10.0.0.3' #####
        smw = SMWHandler(tcp_ip = smw_ip, cust_name='SigGen', parent_logger='Sig.GUI')
        # smw.set_rf_state('OFF')
        # smw.set_5g_mod_state('OFF')
        # smw.initialize()
        # time.sleep(15)
        # smw.set_frequency(freq = 3650, channel=1)
        # smw.set_frequency(freq=3750, channel=2)
        # time.sleep(2)
        # smw.set_rf_level(level = -20, channel=1)
        # smw.set_rf_level(level = -20, channel=2)
        # smw.configure_5g_dl_baseband(sig_file_name = 'NR-FR1-TM1_1__FDD_100MHz_30kHz', trig_connector=1, chan=1)
        # smw.configure_5g_dl_baseband(sig_file_name = 'NR-FR1-TM1_1__FDD_100MHz_30kHz', trig_connector=1, chan=2)
        # smw.set_5g_mod_state('ON', channel=1)
        # time.sleep(2)
        # smw.set_5g_mod_state('ON', channel=2)
        # time.sleep(2)
        # smw.set_rf_state('ON', channel=1)
        # time.sleep(2)
        # smw.set_rf_state('ON', channel=2)
        # time.sleep(2)
        # smw.setup_Sensitivity(freq=3750, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us')
        # smw.setup_ACSelectivity(freq=3605, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc='HIGH')
        # smw.setup_General_IBB(freq=3460, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc='HIGH')
        # smw.setup_NarrowBand_IBB(freq=3750, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc='LOW', fr_shift_m='FS1')
        # smw.setup_OutOfBand_Blocking(freq=3700, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', is_rf_freq='3200 MHz', treq='BLPE')
        # smw.setup_ICSelectivity(freq=3605, bw=100, scs=30, cid=0, rb_offs=0, trigSrc='EGT1', trigDelUnit='TIME', trigDelVal='0us', freq_alloc='LOW')
        # smw.conf_5g_ul_trigger('EGT1', 'TIME', '0us')
        # print('Waiting for 10 seconds')
        # time.sleep(10)
        # smw.set_rf_state('OFF')
        # print(smw.check_identity())
        # smw.set_ref_clk_src()
        # smw.set_5g_trig_mode(trig_mode='AUTO')
        # smw.user_connector_direction(connector=3, direction='OUTP')
        # smw.user_connector_output_signal(connector=3, signal='MARKA', marker=1)
        # smw.set_5g_trig_output_mode(output_mode = 'FRAM')
        # smw.set_frequency(freq=3650)
        # smw.set_rf_lvl_offset(-2)
        # smw.set_rf_level(level = -20)
        # smw.set_rf_state()
        # smw.set_5g_mod_state()
        # time.sleep(10)
        # smw.set_rf_state('OFF')
        # smw.set_5g_mod_state('OFF')
        # smw.set_rf_state('OFF', channel=2)
        # smw.set_5g_mod_state('OFF', channel=2)
        # smw.set_link_direction()
        # smw.load_5g_dl_test_model('NR-FR1-TM1_1__FDD_100MHz_30kHz')
        # smw.setup_General_IBB(freq=3840, trigDelVal='9.9875ms', freq_alloc='HIGH')
        # print(int(smw.get_frequency(2)))
        lower_start = int(smw.get_frequency(channel=2))
        print(lower_start)
        # inter_freq_list = range(lower_start, lower_stop-1, -1)
        inter_freq_list = range(lower_start, lower_start-6, -1)
        print(inter_freq_list[2])
        smw.close()
    except Exception as e:
        print(e)
        if(smw):
            smw.close()


if __name__ == "__main__":
    main()