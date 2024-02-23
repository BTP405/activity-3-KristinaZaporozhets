#Real-Time Chat Application with Pickling:

#Develop a simple real-time chat application where multiple clients can communicate with each other via a central server using sockets. 
#Messages sent by clients should be pickled before transmission. The server should receive pickled messages, unpickle them, and broadcast them to all connected clients.


#Requirements:
#Implement separate threads for handling client connections and message broadcasting on the server side.
#Ensure proper synchronization to handle concurrent access to shared resources (e.g., the list of connected clients).
#Allow clients to join and leave the chat room dynamically while maintaining active connections with other clients.
#Use pickling to serialize and deserialize messages exchanged between clients and the server.

###########################################################################################

# server.py

import socket
import threading
import pickle

class ChatServer:

    # initialize attributes: clients, lock and server_socket
    def __init__(self):
        self.clients = []  
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))

    def start(self):
        self.server_socket.listen(5)
        print("Server is listening")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("Connected to", client_address)
            # each client will be handles in separate thread
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        # access lock and add new client 
        with self.lock: 
            self.clients.append(client_socket)
    
        try:
            while True:
                # receive, unpickle data 
                pickled_data = client_socket.recv(4096)
                if not pickled_data:
                    break
                message = pickle.loads(pickled_data)
                # check if client wants to leave the room 
                if message != "q":
                    print("Received message:", message)
                    # each broadcast will be handled in separate thread 
                    broadcast_thread = threading.Thread(target=self.broadcast, args=(message, client_socket,))
                    broadcast_thread.start()
                else:
                    break
                        
        except ConnectionResetError:
            print("Client disconnected")
        except pickle.PickleError as pe:
            print("Error occurred while pickling:", pe)
        except socket.error as se: 
            print("Socket error: ", se)
        except Exception as e:
            print("Error occurred:", e)
        finally:
            client_socket.close()
            with self.lock:
                self.clients.remove(client_socket)

    def broadcast(self, message, sender_socket):
        clientNum = 0; 
        with self.lock:
            for client_socket in self.clients:
                clientNum += 1
                if client_socket != sender_socket:
                    pickled_message = pickle.dumps(message)
                    client_socket.sendall(pickled_message)

if __name__ == "__main__":
    server = ChatServer()
    server.start()
###########################################################################################

# client.py 

import socket
import threading
import pickle

def receive_messages(client_socket):
    try:
        while True:
            # receive, unpickle data and display message 
            pickled_data = client_socket.recv(4096)
            message = pickle.loads(pickled_data)
            print(message)
            
    except ConnectionAbortedError:
        pass
    except Exception as e:
        print("Error receiving messages:", e)

    finally:
        client_socket.close()

def send_message(client_socket):
    print("To leave the chat room type: q")
    try:
        while True:
            message = input()
            #  check if client wants to leave the room
            if message == "q":
                break
            # pickle and send data 
            pickled_message = pickle.dumps(message)
            client_socket.sendall(pickled_message)

    except Exception as e:
        print("Error sending message:", e)
    finally:
        client_socket.close()

def runClient():    
    try: 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))

        # reive a message thread
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        # send a message thread
        send_thread = threading.Thread(target=send_message, args=(client_socket,))

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()
        
    except pickle.PickleError as pe:
        print("Error occurred while pickling:", pe)
    except socket.error as se: 
        print("Socket error: ", se)
    except Exception as e: 
        print("Error occurred:", e)

    finally: 
        print("Connection closed")

if __name__ == "__main__":
    runClient()
