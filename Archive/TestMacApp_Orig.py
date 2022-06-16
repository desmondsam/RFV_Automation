# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:47:00 2022

@author: repkoc
"""

import paramiko 
import time

class TestMacSSH():

    ip="10.69.91.51"; port=22; user="root";password="mavenir"

    def __init__(self,server = ip, port = 22, user = 'root', password = 'mavenir'):  
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(server, port, user, password)
        time.sleep(0.15)
        print('Connection to SSH established.\n')
        self.cmd = self.client.invoke_shell()
        
    
    
    def sshRead(self,buffersize):
        while not self.cmd.recv_ready():
            time.sleep(1)
        Out = self.cmd.recv(buffersize)
        return(Out)            
        
    def sshWrite(self,string):
        self.cmd.send('{}\n'.format(string))
        
    def sshClose(self):
        self.client.close()
        time.sleep(0.15)     
        print('Connection to SSH CLOSED.\n') 

    def changeDir(self,path):
        self.sshWrite(path+'\n')
        time.sleep(0.1)
#        print(self.sshRead(2000))

    def setEnv(self,env):    
        self.sshWrite(env+'\n')
        time.sleep(4)
        # print(self.sshRead(2000).decode('UTF-8'))
    
    def startL1(self):
        self.sshWrite(r'./l1.sh -xran &> output.log'+'\n')
        time.sleep(1)

    
    # sshWrite(cmd,"tail -f output.log"+'\n')
    # time.sleep(1)

    def startL1LogFile(self):    
        self.sshWrite("tail -f output.log"+'\n')
        # L1Out = self.sshRead(20).decode('UTF-8')
        # print(L1Out)
        time.sleep(0)
        
    def startL2(self):
        print("Starting L2 App ...")
        self.sshWrite("./l2.sh"+'\n')
        L2Out = self.sshRead(9).decode('UTF-8')
        print(L2Out)
        time.sleep(30)
        L2Out = self.sshRead(12000).decode('UTF-8')
        print(L2Out)
        self.sshWrite("phystart 4 0 0"+'\n')
        L2Out = self.sshRead(80).decode('UTF-8')
        print(L2Out)
        
    def testCase(self,testType,Numero,BW,testNum):    
        self.sshWrite("run {} {} {} {}".format(testType,Numero,BW,testNum)+'\n')
        time.sleep(30)
        L2Out = self.sshRead(12000).decode('UTF-8')
        print(L2Out)


    
    # print("\n\n")
    
    # x=sshRead()
    # # xs = x.decode('UTF-8')
    # xb = x.split(b'\n')  #makes array based on line return
    # print(xb)

    def blerQuery(self):

        self.sshWrite("tail -n 13 output.log")
        time.sleep(0.5)
        Out = self.sshRead(1300)
        #print(type(Out))
        
        while (Out.find(b'UL BLER') == -1):
            self.sshWrite("tail -n 13 output.log")
            time.sleep(0.5)
            Out = self.sshRead(1300)  
            
        Out = Out.decode('UTF-8').split('\n')
        
        l=0
        for i in range(0,len(Out)):
            if(Out[i].find('UL BLER') != -1):
                l=i+1
                #print(l)
        print("BLER = {}".format(Out[l].split()[5][0:-1])) 

    # def blerQuery(self):

    #     self.sshWrite("tail -n 13 output.log")
    #     time.sleep(0.5)
    #     Out = self.sshRead(1300)
    #     print(type(Out))
        
    #     while (Out.find(b'UL BLER') == -1):
    #         self.sshWrite("tail -n 13 output.log")
    #         time.sleep(0.5)
    #         Out = self.sshRead(1300)  
            
    #     Out = Out.decode('UTF-8').split('\n')
        
    #     l=0
    #     for i in range(0,len(Out)):
    #         if(Out[i].find('UL BLER') != -1):
    #             l=i+1
    #             print(l)
    #     print("BLER = {}".format(Out[l].split()[5][0:-1])) 



        
        # if (Out.find(b'UL BLER') == -1):
        #     print('UL BLER not found')
        # else:   
        #     Out2 = Out.split('\n')
        
        # l=0
        # for i in range(0,len(Out2)):
        #     if(Out2[i].find('UL BLER') != -1):
        #         l=i+1
        #         print(l)
        # print("BLER = {}".format(Out2[l].split()[5][0:-1]))        

        
        
    def KillProcess(self):
        self.sshWrite("^C\n")
        self.sshWrite("\x03")
        # time.sleep(0)
        # Out = self.sshRead(20)
        # print(Out)

        
    def killL2(self):
        self.sshWrite("exit\n")
        # time.sleep(0)
        # Out = self.sshRead(20)
        # print(Out)        
        
   

# l=0
# for i in range(5,len(xb)):
#     if(xb[i][0:5]==b" Cell"):
#         l=i+1
#         print("l=",l)
#         # print("xb{}={}".format(i,xb[i][0:6]))
#         # print("\n\n xb5=")
#         # print(xb[5][0:4])
#         break
# print(xb[l])  


# xs[l].decode('UTF-8').split()[5][0:-1]
    
# str(xs[l].split()[5])





    

# print (x)
