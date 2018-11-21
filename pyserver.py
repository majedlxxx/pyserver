#!/usr/bin/python3
import socket
import threading
import time   

#preferences
Port= 4000
IP="127.0.0.1"
QueueSize=100  #Maximum number of simultaneous clients
BufferSize=100 #Bytes to be received from a client (optional)
TimeLimitPerClient=20 #time in seconds
Log= True #keep it False if you don't want to log activities
LogsFile="ServerLogs" #file name to store the logs in (optional)



ConnectedClients=[]
ClientsQueueLock=threading.Lock()


def addAClient(client):
	ClientsQueueLock.acquire()
	ConnectedClients.append(client)
	ClientsQueueLock.release()


def removeClient(client):
	ClientsQueueLock.acquire()
	ConnectedClients.remove(client)
	ClientsQueueLock.release()




def receive(client,buffSize):
	try:
		msg=client.recv(buffSize).decode("ascii")[:-1]
		return  msg
	except:
		client.close()
		return ""


def send(client,msg):
	try:
		client.send(msg.encode("ascii"))
		return True
	except: 
		client.close()
		return False




def logToFile(toLog):
	if Log==False:
		return
	f=open(LogsFile,"a")
	f.write(time.ctime()+": "+str(toLog)+"\n")
	f.close()


def end():
	while True:
		for client in ConnectedClients:
			if client[1]._closed==True:
				removeClient(client)
				break
			if time.time()-client[0]> TimeLimitPerClient:
				send(client[1],"time limit reached")
				client[1].shutdown(socket.SHUT_RDWR)
				removeClient(client)
				break


def work(client,addr):
	#modify this 
	msg=receive(client,BufferSize)
	logToFile(str(addr)+" => "+msg)
	send(client,"working")

	#no need to modify
	client.close()




if __name__=='__main__':
	s=socket.socket()
	s.bind((IP,Port))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.listen(100)
	logToFile("The server is running at port: "+str(Port)+"\n*****\n")
	terminator=threading.Thread(target=end)
	terminator.start()

	while True:
		if len(ConnectedClients)>=QueueSize:	
			logToFile("***Warning: Queue limit reached")
			while len(ConnectedClients)>=QueueSize:
				pass
		client,addr=s.accept()
		worker=threading.Thread(target=work,args=(client,addr))
		worker.deamon=True
		addAClient((time.time(),client,worker))
		worker.start()	
		print("connected: ",len(ConnectedClients),"/",QueueSize)






