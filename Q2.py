#Distributed Task Queue with Pickling:

#Create a distributed task queue system where tasks are sent from a client to multiple worker nodes for processing using sockets. 
#Tasks can be any Python function that can be pickled. Implement both the client and worker nodes. 
#The client sends tasks (pickled Python functions and their arguments) to available worker nodes, and each worker node executes the task and returns the result to the client.

#Requirements:
#Implement a protocol for serializing and deserializing tasks using pickling.
#Handle task distribution, execution, and result retrieval in both the client and worker nodes.
#Ensure fault tolerance and scalability by handling connection errors, timeouts, and dynamic addition/removal of worker nodes.
##############################################################################################################

# --- Task distribution: 
# client.py sends tasks to server.py, while server.py creates seperate process for each task received from client. 

# --- Serialization: 
# the serialization and deserialization protocol includes the pickle.dumps() and pickle.loads() 
# functions respectively, as the pickle module provides a convenient way to manage serialization of 
# objects. In this solution, the Task class was implemented, enabling the utilization of this 
# straightforward pickling procedure. 

# --- Modules: 
# I have created task.py module: 
#   The task.py module was imported into server.py module (for cases, when user-defined 
#   functions are used as a function attribute of Task instance) and client.py (to create tasks).

# --- Exception handling: 
# fault tolerance was insured by handling connection, timeouts, pickling/unpickling, and all the remaining exceptions. 

# --- Hard-coded values: 
# Note: there are some hard-coded values such as task1, task2. 

# below is the code for the following files: task.py, client.py, server.py    
##############################################################################################################

# task.py: 

# definition of the task class: a task has a function and its arguments 

# definition of the task class: a task has a function and its arguments 

class Task:
    numInstances = 0
    def __init__(self, function, args): 
        self.function = function
        self.args = args
        Task.numInstances += 1

# definition of user-defined function: returns the product of multiplication 
# of all elements in the given list
def myFunc(nums): 
    res = 1
    for i in nums:
        res = i*res
    return res
##############################################################################################################

# client.py

import socket
import pickle
import task

def runClient(tasks, worker):    
        try: 
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(worker)

            for task in tasks: 
                pickledTask = pickle.dumps(task)
                client_socket.sendall(pickledTask)

                data = client_socket.recv(1024)
                print('Received acknowledgment:', data.decode())

        except socket.timeout as te:
              print("Connection timed out:", te)
        except socket.error as se: 
            print("Socket error: ", se)
        except Exception as e: 
            print("Error occurred:", e)

        finally: 
            client_socket.close()

if __name__ == "__main__": 

    # generate some numbers 
    nums = []
    for i in range(10): 
        nums.append(i)

    # create a task with built-in function and list of arguments 
    task1 = task.Task(sum, nums)
    # create a task with user-defined function and list of arguments 
    task2 = task.Task(task.myFunc, [1,2,3])
    taskQueue = [task1, task2] 


    worker = ('localhost', 1026)
    runClient(taskQueue, worker)
##############################################################################################################

# server.py

import socket
import pickle
import multiprocessing

# unpickle task and send result to client 
def worker(Pickledtask, client_socket):
    try: 
        unPickeledtask = pickle.loads(Pickledtask)
        result = unPickeledtask.function(unPickeledtask.args)

        message = 'Result: ' + str(result)
        client_socket.sendall(message.encode())
    except pickle.UnpicklingError as pe:
        print("Error unpickling task:", pe)
        return None
    except Exception as e:
        print("Error executing task:", e)
        return None
    finally:
        client_socket.close()
    
def runServer(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', port) 

    server_socket.bind(server_address)
    server_socket.listen(1)
    print('Server is listening for the incoming requests')

    while True: 
        client_socket, client_address = server_socket.accept(); 
        try: 
            print('Connected to', client_address)
            # max amount of bytes
            # process each task
            while True: 
                data = client_socket.recv(1024)
                if not data: 
                    break
                worker_process = multiprocessing.Process(target=worker, args=(data, client_socket))
                worker_process.start()
                
            worker_process.join()

        except socket.error as se:
            print("Socket error:", se)
        except Exception as e:
            print("Error occurred:", e)        


if __name__ == "__main__": 
    runServer(1026)

##############################################################################################################





