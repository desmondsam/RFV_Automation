# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:47:00 2022

@author: repkoc, Edited by DesmondD
"""
import paramiko 
import time
from scp import SCPClient
import re

class TestMacSSH():
    def __init__(self, server, port=22, user='root', password ='mavenir'):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(server, port, user, password)
        time.sleep(0.15)
        print('Connection to SSH established.')
        self.cmd = self.client.invoke_shell()
    
    def getFile(self, du_file, pc_file):
        scp = SCPClient(self.client.get_transport())
        scp.get(du_file, pc_file)
        print('File moved from DU to PC')
    
    def sshRead(self, buffer_size):
        while not self.cmd.recv_ready():
            time.sleep(1)
        Out = self.cmd.recv(buffer_size)
        return(Out)            
        
    def sshWrite(self, cmd_string):
        self.cmd.send(f'{cmd_string}\n')
        
    def sshClose(self):
        self.client.close()
        time.sleep(0.15)     
        print('Connection to SSH CLOSED.') 

    def changeDir(self, dir_path):
        self.sshWrite(f'cd {dir_path}')
        time.sleep(0.1)

    def setEnv(self, env=r'set_env_var.sh'):    
        self.sshWrite(f'source {env}')
        time.sleep(4)
    
    def startL1(self, mod='xran'):
        self.sshWrite(f'./l1.sh -{mod} &> output.log')
        time.sleep(1)

    def startL1LogFile(self):    
        self.sshWrite('tail -f output.log')
        
    def startL2(self):
        print("Starting L2 App ...")
        self.sshWrite('./l2.sh')
        L2Out = self.sshRead(9).decode('UTF-8')
        print(L2Out)
        time.sleep(30)
        L2Out = self.sshRead(12000).decode('UTF-8')
        print(L2Out)
        
    def phyStart(self, mode=4, timer=0, counter=0):
        self.sshWrite(f'phystart {mode} {timer} {counter}')
        # time.sleep(10)
        L2Out = self.sshRead(80).decode('UTF-8')
        print(L2Out)

    def testCase(self, testType, numero, bw, testNum):    
        self.sshWrite(f'run {testType} {numero} {bw} {testNum}')
        time.sleep(30)
        L2Out = self.sshRead(12000).decode('UTF-8')
        print(L2Out)

    def blerQuery(self):
        self.sshWrite("tail -n 13 output.log")
        time.sleep(0.5)
        Out = self.sshRead(10000)
        Out = Out.decode('UTF-8')
        
        while (re.findall(r'\d+\.+\d+%',Out)==[]):
            self.sshWrite("tail -n 13 output.log")
            time.sleep(0.5)
            Out = self.sshRead(10000)
            Out = Out.decode('UTF-8')
            
        bler = re.findall(r'\d+\.+\d+%',Out)[-1]
        # print(f'BLER = {bler}')
        return float(bler[:-1]) 

    def killProcess(self):
        self.sshWrite("^C\n")
        self.sshWrite("\x03")

    def killL2(self):
        self.sshWrite("exit\n")
    
    def startTerm1(self):
        self.changeDir(r'/data/storage/l1_package/')  #directory in raw text
        print("\n\nT1:",self.sshRead(100).decode('UTF-8'),"\n\n")
        self.setEnv()  #input in raw text
        print("\n\nT1:",self.sshRead(2000).decode('UTF-8'),"\n\n")
        self.changeDir(r'/data/storage/l1_package/bin/nr5g/gnb/l1')  #directory in raw text
        print("\n\nT1:",self.sshRead(100).decode('UTF-8'),"\n\n")
        self.startL1()
        print("\n\nT1:",self.sshRead(20).decode('UTF-8'),"\n\n")
        
    def startTerm2(self):
        
        self.changeDir(r'/data/storage/l1_package/')  #directory in raw text
        print("\n\nT2:",self.sshRead(100).decode('UTF-8'),"\n\n")
        self.setEnv()  #input in raw text
        print("\n\nT2:",self.sshRead(2000).decode('UTF-8'),"\n\n")
        self.changeDir(r'/data/storage/l1_package/bin/nr5g/gnb/l1')  #directory in raw text
        print("\n\nT2:",self.sshRead(100).decode('UTF-8'),"\n\n")
        self.startL1LogFile()
        print("\n\nT2:",self.sshRead(20).decode('UTF-8'),"\n\n")
        print("Waiting for PhyLayer prompt")
        time.sleep(30)
        print("\n\nT2:",self.sshRead(30000).decode('UTF-8'),"\n\n")
        self.killProcess()
        
    def startTerm3(self, mode=4, timer=0, counter=0, testType = 1, numero=0, bw=20, testNum=1046): 
          
        self.changeDir(r'/data/storage/l1_package/')  #directory in raw text
        print("\n\nT3:",self.sshRead(1000).decode('UTF-8'),"\n\n")
        self.setEnv()  #input in raw text
        print("\n\nT3:",self.sshRead(2000).decode('UTF-8'),"\n\n")
        self.changeDir(r'/data/storage/l1_package/bin/nr5g/gnb/testmac')  #directory in raw text
        print("\n\nT3:",self.sshRead(100).decode('UTF-8'),"\n\n")
        self.startL2()
        self.phyStart(mode, timer, counter)
        #print("\n\nT3:",T3.sshRead(68).decode('UTF-8'),"\n\n")
        self.testCase(testType=testType, numero=numero, bw=bw, testNum=testNum)
    
def main():
    # pass
    T1 = TestMacSSH(server = '10.69.91.51')
    T2 = TestMacSSH(server = '10.69.91.51')
    T3 = TestMacSSH(server = '10.69.91.51')
    T1.startTerm1()
    T2.startTerm2()
    T3.startTerm3()
    T2.sshRead(11050)
    count=0
    while (count < 5):
        count=count+1
        print(T2.blerQuery())
        time.sleep(10)
    input('Press Enter to Close Terminals and End this Test Run')
    T1.sshClose()
    T2.sshClose()
    T3.sshClose()

if __name__ == '__main__':
    main()

    
