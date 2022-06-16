import visa_connections
import time

class VXGHandler(visa_connections.DeviceHandler):

    def set_timeout (self,timeout = 200000):
        self.timeout = timeout
    
    def set_frequency(self, freq = 3650, channel=1):
        self.write(f':RF{channel}:FREQ {freq} MHz')
        time.sleep(1)
        self.plog(f'Frequency on channel {channel} set to {freq} MHz')
        time.sleep(2)
    
    def set_rf_level(self, level = -10, channel=1):
        self.write(f':RF{channel}:POW {level}')
        time.sleep(1)
        self.plog(f'RF Level on channel {channel} set to {level} dBm')
    
    def set_rf_lvl_offset(self, offs = -2, channel=1):
        self.write(f'RF{channel}:POW:OFFS {offs}')
        self.plog(f'Channel {channel} RF Level Offset set to {offs} dB')
    
    def set_sig_file_mode(self, mode='WAV', channel=1):
        self.write(f'SIGN{channel}:MODE {mode}') #WAV | AWGN -> Waveform File or AWGN
        self.plog(f'Signal File mode on channel {channel} set to {mode}')

    def load_wav_file(self, floc=r'D:\Users\Instrument\Documents\Keysight\PathWave\SignalGenerator\Signal-Studio-waveforms', fname='NR-FR1-TM3_1a__FDD_100MHz_30kHz.wfm', channel=1):
        self.write(f"SIGN{channel}:WAV '{floc}\{fname}'")
        time.sleep(3)
        self.plog(f'{fname} Waveform file loaded on channel {channel}')
    
    def set_wav_file_trig(self, mode='CONT', src='IMM', channel=1):
        self.write(f'SIGN{channel}:WAV:TRIG:TYPE {mode}') #CONT|SING -> Continuous/Single
        self.plog(f'Channel {channel} Signal Wave File Trigger Mode set to {mode}')
        self.write(f'SIGN{channel}:WAV:TRIG {src}') #IMM | KEY | BUS | EXT -> Free Run/Key/Bus/External
        self.plog(f'Channel {channel} Signal Wave File Trigger Source set to {src}')

    def config_cont_trig(self, cont_mode='FREE', channel=1):
        self.write(f'SIGN{channel}:WAV:TRIG:TYPE:CONT {cont_mode}') #FREE|TRIG|RES -> Free Run, Trigger & Run or Reset & Run
        self.plog(f'Channel {channel} Signal File Continuous Trigger Mode set to {cont_mode}')
    
    def config_ext_trig(self, termination='NORM', level=0.5, slope='NEG', delay='0 s', hold_off='1ms', channel=1):
        self.write(f'SIGN{channel}:WAV:TRIG:EXT:TERM {termination}') #NORM | HIGH
        self.plog(f'Channel {channel} Signal File External Trigger Termination set to {termination}')
        self.write(f'SIGN{channel}:WAV:TRIG:EXT:LEV {level}v') #-3.5V to 3.5V
        self.plog(f'Channel {channel} Signal File External Trigger Level set to {level}')
        self.write(f'SIGN{channel}:WAV:TRIG:EXT:SLOP {slope}') #NEG | POS
        self.plog(f'Channel {channel} Signal File External Trigger Slope set to {slope}')
        self.write(f'SIGN{channel}:WAV:TRIG:EXT:DEL {delay}') #0s to 2s
        self.plog(f'Channel {channel} Signal File External Trigger delay set to {delay}')
        self.write(f'SIGN{channel}:WAV:TRIG:EXT:HOLD {hold_off}') #4ns to 10s
        self.plog(f'Channel {channel} Signal File External Trigger hold off set to {hold_off}')
    
    def ext_trig_delay_blanking(self, blanking='OFF', channel=1):
        self.write(f':SIGN:WAV:TRIG:EXT:DEL:RBL {blanking}')
        self.plog(f'Channel {channel} Signal File External Trigger Delay Blanking turned {blanking}')
    
    def ext_trig_playback_sync(self, sync='OFF', channel=1):
        self.write(f':SIGN{channel}:WAV:TRIG:EXT:SYNC:OUTP {sync}')
        self.plog(f'Channel {channel} Signal File External Trigger Playback Synchronization turned {sync}')
    
    def sig_file_state(self, sig_state = 'ON', channel=1):
        self.write(f'SIGN{channel} {sig_state}')
        self.plog(f'Signal File state on channel {channel} turned {sig_state}')
    
    def set_rf_state(self, state = 'ON', channel=1):
        self.write(f':RF{channel}:OUTP {state}')
        self.plog(f'RF on channel {channel} turned {state}')
    
    def mod_state(self, mod='ON', channel=1):
        self.write(f':RF{channel}:OUTP:MOD {mod}')
        self.plog(f'Output Modulation on channel {channel} turned {mod}')

def main():
    """Inputs"""
    vxg_ip = '192.168.255.205'
    freq = 680.5
    rf_level = -50
    trig_delay = '9.99985ms'
    trig_mode = 'CONT'
    trig_src = 'EXT'
    trig_cont_mode = 'TRIG'
    sig_file_loc = r'D:\Users\Instrument\Documents\Keysight\PathWave\SignalGenerator\Signal-Studio-waveforms'
    sig_file_name = '1046-waveform.wfm'
    wanted_channel = 1
    try:
        vxg = VXGHandler(tcp_ip=vxg_ip, cust_name='VXG')
        # print(vxg.check_identity())
        # vxg.initialize()
        # time.sleep(10)
        # vxg.set_sig_file_mode(channel=1)
        # vxg.load_wav_file(floc=sig_file_loc, fname=file_name, channel=1)
        # vxg.set_sig_file_mode(channel=2)
        # vxg.load_wav_file(floc=sig_file_loc, fname=file_name, channel=2)
        # vxg.set_rf_level(level=rf_level, channel=1)
        # vxg.set_rf_level(level=rf_level, channel=2)
        # vxg.set_frequency(freq=freq, channel=1)
        # vxg.set_frequency(freq=freq, channel=2)
        # vxg.sig_file_state(sig_state='OFF', channel=1)
        # vxg.sig_file_state(sig_state='OFF', channel=2)
        # vxg.set_rf_state(channel=1, state='OFF')
        # vxg.set_rf_state(channel=2, state='OFF')
        # vxg.set_wav_file_trig(mode='CONT', src='EXT', channel=1)
        # vxg.set_wav_file_trig(mode='CONT', src='EXT', channel=2)
        # vxg.config_cont_trig(cont_mode='RES', channel=1)
        # vxg.config_cont_trig(cont_mode='RES', channel=2)
        # vxg.config_ext_trig(termination='HIGH', level=1, slope='POS', delay = '1ms', hold_off='2ms', channel=1)
        # vxg.config_ext_trig(termination='HIGH', level=1.2, slope='POS', delay = '1ms', hold_off='2ms', channel=2)
        # vxg.ext_trig_delay_blanking('OFF', channel=1)
        # vxg.ext_trig_delay_blanking('OFF', channel=2)
        # vxg.config_cont_trig(cont_mode='TRIG', channel=1)
        # vxg.config_cont_trig(cont_mode='TRIG', channel=2)
        # vxg.ext_trig_playback_sync(sync='ON', channel=1)
        # vxg.ext_trig_playback_sync(sync='ON', channel=2)
        # time.sleep(3)
        # vxg.set_rf_state('OFF', channel=1)
        # vxg.set_rf_state('OFF', channel=2)
        # vxg.set_sig_file_mode()
        # vxg.load_wav_file(floc=sig_file_loc, fname=file_name)
        # vxg.set_wav_file_trig(mode=trig_mode, src=trig_src)
        # vxg.config_cont_trig(cont_mode=trig_cont_mode)
        # vxg.config_ext_trig(delay=trig_delay)
        # vxg.set_frequency(freq=freq)
        # vxg.set_rf_level(level=rf_level)
        # vxg.sig_file_state()
        # vxg.set_rf_state()
        # vxg.sig_file_state('OFF')
        vxg.initialize()
        time.sleep(10)
        # vxg.set_sig_file_mode(mode='WAV', channel=wanted_channel)
        # vxg.load_wav_file(floc=sig_file_loc, fname=sig_file_name, channel=wanted_channel)
        # vxg.set_wav_file_trig(mode=trig_mode, src=trig_src, channel=wanted_channel)
        # vxg.config_cont_trig(cont_mode=trig_cont_mode, channel=wanted_channel)
        # vxg.config_ext_trig(delay=trig_delay, termination='HIGH', slope='POS', channel=wanted_channel)
        # vxg.ext_trig_playback_sync(sync='ON', channel=wanted_channel)
        # vxg.set_frequency(freq=freq, channel=wanted_channel)
        # vxg.sig_file_state(sig_state='ON', channel=wanted_channel)
        # vxg.set_rf_lvl_offset(channel=1)
        # vxg.set_rf_lvl_offset(channel=2)
        # vxg.set_rf_state(state='ON', channel=1)
        # vxg.set_rf_state(state='ON', channel=2)
        # time.sleep(2)
        vxg.close()
    except Exception as e:
        print(e)
        if(vxg):
            vxg.close()

if __name__ == '__main__':
    main()
