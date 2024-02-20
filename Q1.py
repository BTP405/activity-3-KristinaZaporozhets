#Implement a client-server file transfer application where the client sends a file to the server using sockets. 
#Before transmitting the file, pickle the file object on the client side. On the server side, receive the pickled file object, unpickle it, and save it to disk.


#Requirements:
#The client should provide the file path of the file to be transferred.
#The server should specify the directory where the received file will be saved.
#Ensure error handling for file I/O operations, socket connections, and pickling/unpickling.
##############################################################################################################


##############################################################################################################

# server.py 
import socket
import pickle 


def saveFile(pickledF, savePath):
    try:
        unpickeledContents = pickle.loads(pickledF) # unpickle
        
        # save 
        with open(savePath, 'w') as fSave: 
            fSave.write(unpickeledContents)

    except pickle.PickleError as pe:
        print("Error occurred while pickling:", pe)
    except IOError as e:
        print("An I/O error occurred:", e)
    except Exception as e:
        print("Error occurred while saving file:", e)

def runServer(saveDir):
    # socket. --> servers as namespace, while socket.socket() is constructor of socket class
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname)
    server_address = ('localhost', 12345) 

    server_socket.bind(server_address)
    server_socket.listen(1)

    print('Server is listening for the incoming requests')

    while True:

        client_socket, client_address = server_socket.accept(); 

        try: 
            print('Connected to', client_address)
            # max amount of bytes 
            data = client_socket.recv(1024)

            # specify the directory and give the saved file a name 
            savePath = saveDir + "/received"
            saveFile(data, savePath)

            message = 'Message received by the server'
            client_socket.sendall(message.encode())

        except socket.error as se:
            print("Socket error:", se)
        except Exception as e:
            print("Error occurred:", e)        
        finally:
            client_socket.close()

if __name__ == "__main__": 
    # ASSIGN THE DIR VARIABLE STRING LITERAL VALUE OF DIRECTORY'S PATH  
    dir = "receivedFilesActivity3q1"
    runServer(dir)
#####################################################################################################

# client.py 
import socket
import pickle 

# serialization: the process of storing a data structure in memory so that you can load or 
# transmit it when required without losing its current state.

# if I want to store a dictionary in memory as dictionary and not as a string, I need to do serialization. 

# pickle a file object located at the file path 
def pickleFileSend(file_path, client_socket):

    try:
        # read the original file's contents that needs to be transmitted 
        with open(file_path, 'r') as fOriginal: 
            contents = fOriginal.read()

        # create a binary file that will contain pickled data that will be transmitted
        with open('transmit.pkl', 'w+b') as fPickled:
            pickle.dump(contents, fPickled) # pickle 
            fPickled.seek(0) # position cursor at the beginning of the file 
            pickledData = fPickled.read() # save pickled data 
            client_socket.sendall(pickledData) # trasnmit 
        
    except FileNotFoundError:
        print("Error: File not found.")
    except socket.error as se:
        print("Socket error:", se)
    except pickle.PickleError as pe:
        print("Error occurred while pickling:", pe)
    except Exception as e:
        print("Error occurred while sending file:", e)

def runClient(file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345) 

    client_socket.connect(server_address)

    try: 

        pickleFileSend(file_path, client_socket)

        data = client_socket.recv(1024)
        print('Received acknowledgment:', data.decode())

    except socket.error as se:
        print("Socket error:", se)
    except Exception as e:
        print("Error occurred:", e)
    finally: 
        client_socket.close()

if __name__ == "__main__":
    # ASSIGN THE FILE VARIABLE STRING LITERAL VALUE OF FILE'S PATH  
    file = "activity3q1.txt"
    runClient(file)
