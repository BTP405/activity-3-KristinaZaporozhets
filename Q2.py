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
# It is worth mentioning that client can not create an infinite number of tasks and expect their handling by working nodes.
# For this reason, workingNodes module was created holding maximum number of workers allowed and a list of ports. 
# client.py creates tasks using Task module, hodling Task class, which keeps track of the number of created instances of the class.
# client.py then puts tasks to task Queue and checks if the number of created tasks exceeds allowed number of working nodes, if does not
# it passes taskQueue and workerQueue to runClient function. 
# On the other hand, server.py creates as much runWorker processes (working nodes) as allowed by workingNodes module. 
# Each working module handles a task. 

# --- Serialization: 
# the serialization and deserialization protocol includes the pickle.dumps() and pickle.loads() 
# functions respectively, as the pickle module provides a convenient way to manage serialization of 
# objects. In this solution, the Task class was implemented, enabling the utilization of this 
# straightforward pickling procedure. 

# --- Modules: 
# I have created task.py module: 
#   The task.py module was imported into server.py module (for cases, when user-defined 
#   functions are used as a function attribute of Task instance) and client.py (to create tasks).
# I have created workingNodes.py module: 
#    The workingNodes.py was imported into server.py (to create working nodes) module and client.py (to check if number of created
#    tasks exceeds number of allowed working nodes) module.  

# --- Exception handling: 
# fault tolerance was insured by handling connection, timeouts, pickling/unpickling, and all the remaining exceptions. 

# --- Hard-coded values: 
# Note: there are some hard-coded values such as task1, task2, and port values and maximum number of workers in workingNodes module. 

# below is the code for the following files: task.py, client.py, server.py, workingNodes: 
##############################################################################################################

# task.py: 

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
import multiprocessing
import task
import workingNodes

def runClient(tasks, workers):    
    # the zip function creates tuples pairing corresponding 
    # elements from two or more iterables.
    while not tasks.empty() and not workers.empty():
        try: 
            task = tasks.get()
            worker = workers.get()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(worker)

            # pickle task   
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

    taskQueue = multiprocessing.Queue()
    # create a task with built-in function and list of arguments 
    task1 = task.Task(sum, nums)
    taskQueue.put(task1)
    # create a task with user-defined function and list of arguments 
    task2 = task.Task(task.myFunc, [1,2,3])
    taskQueue.put(task2)

    if task.Task.numInstances <= workingNodes.maxWorkerNum: 

        workerQueue = multiprocessing.Queue()
        for i in range(task.Task.numInstances): 
            workerQueue.put(('localhost', workingNodes.ports[i]))

        runClient(taskQueue, workerQueue)
    else: print("There is a limit of working nodes, which is: ", workingNodes.maxWorkerNum)
##############################################################################################################

# server.py

import socket
import pickle
import multiprocessing
import workingNodes

def doTask(Pickledtask):
    try: 
        unPickeledtask = pickle.loads(Pickledtask)
        result = unPickeledtask.function(unPickeledtask.args)
        return result
    except pickle.UnpicklingError as pe:
        print("Error unpickling task:", pe)
        return None
    except Exception as e:
        print("Error executing task:", e)
        return None
    
def runWorker(port):
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
            data = client_socket.recv(1024)

            res = doTask(data)

            message = 'Result: ' + str(res)
            client_socket.sendall(message.encode())

        except socket.error as se:
            print("Socket error:", se)
        except Exception as e:
            print("Error occurred:", e)        
        finally:
            client_socket.close()       

if __name__ == "__main__": 

    for p in workingNodes.ports: 
        worker_process = multiprocessing.Process(target=runWorker, args=(p,))
        worker_process.start()

    for i in range(workingNodes.maxWorkerNum):
        worker_process.join()
##############################################################################################################

# workingNodes.py

maxWorkerNum = 5; 
ports = [1025, 1026, 1027, 1028, 1029]





