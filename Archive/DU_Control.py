"""
Author: Desmond Dhivyanathan
This is a work in progress. Program has not been verified. Use with caution
"""
import paramiko
import socket
import errno
import time
import io

class DU_Control():
    def __init__(self, tcpip_addr='192.168.255.180', tcpip_port='22', uname='root', pswd='mavenir', exec_chanl = False):
        self.du_shell = None
        self.exec_du_shell_chanl = None
        self.du_shell = self.openShellSession(tcpip_addr, tcpip_port, uname, pswd)
        if(exec_chanl):
            self.exec_du_shell_chanl = self.open_exec_chanl(tcpip_addr, tcpip_port, uname, pswd)
    
    def openShellSession(self, tcpip_addr, tcpip_port, uname, pswd):
        self.du_shell = None
        try:
            self.du_shell = createSSHClient(tcpip_addr, tcpip_port, uname, pswd)
        except:
            print ("ERROR: Open_Shell_Session: Could not open SSH Session.")
            return None
        return self.du_shell
    
    def open_exec_chanl(self, tcpip_addr, tcpip_port, uname, pswd):
        self.exec_channel = None
        try:
            self.exec_du_shell = paramiko.SSHClient()
            self.exec_du_shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.exec_du_shell.connect(tcpip_addr, tcpip_port, uname, pswd)
            # self.exec_du_shell.get_transport().auth_none(uname)
            self.exec_channel = self.exec_du_shell.invoke_shell()
        except:
            print ("ERROR: Open_Shell_Session: Could not open SSH Session.")
            return None
        return self.exec_channel
    
    def close(self):
        if self.du_shell:
            self.du_shell.close()
        if self.exec_du_shell_chanl:
            self.exec_du_shell_chanl.close()
    
    def shellRead(self, strCmd):
        try:
            stdin, stdout, stderr = self.du_shell.exec_command(strCmd)
        except socket.error as error:
            if error.errno == errno.WSAECONNRESET:
                print ('socket was closed')
                # print ('trying to reconnect after 2secs')0
                time.sleep(2)  # delay to allow IP stack to recover if overloaded
                # self.restartSession()
        except Exception as etext:
            print (f'shellRead EXCEPTION: {etext}')
        exit_status = stdout.channel.recv_exit_status()
        stdin.flush()
        stdin.channel.shutdown_write()
        strResponse = stdout.readlines()
        errorOutput = stderr.readlines()  
        return strResponse, errorOutput
    
    def read_exec_channel(self,time_out=1):
        ### Time Out is given in seconds
        buf = io.BytesIO()
        time_out = time_out * 20
        output = str()
        while time_out>0:
            time.sleep(0.05)
            ready = self.exec_du_shell_chanl.recv_ready()
            if ready:
                output = self.exec_du_shell_chanl.recv(9999)
                buf.write(output)
            else:
                time_out -= 1
        return buf.getvalue()
    
    def change_dir(self,dir_path=r'/data'):
        self.exec_du_shell_chanl.send('cd {}'.format(dir_path))
        self.exec_du_shell_chanl.send('\r')
        print (self.read_exec_channel())
    
    def execute_file(self, sh_file):
        command = r'./{}'.format(sh_file)
        self.exec_du_shell_chanl.send(command)
        self.exec_du_shell_chanl.send('\r')
        print (self.read_exec_channel())

    def exec_command(self,command,timeout=1):
        self.exec_du_shell_chanl.send(command)
        print (self.read_exec_channel(1))
        self.exec_du_shell_chanl.send('\r')
        output = self.read_exec_channel(timeout)
        print (output)
        return output

    def get_sw_info(self):
        sw_info = 'Unknown'
        respStr, respErr = self.shellRead('cat /etc/issue')
        sw_info = respStr[1].strip()
        return sw_info
                
    
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

if __name__ == '__main__':
    sess = DU_Control('10.69.91.51', '22', 'root', 'mavenir', exec_chanl=True)
    sess.change_dir()
    print(sess.get_sw_info())
    sess.close()