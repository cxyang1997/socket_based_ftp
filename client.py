import socket
import sys
import os
import pickle

HOST = '127.0.0.1'
PORT = 54321
BUFFER_SIZE = 1024

FILE_DIR = './client_file/'

MSG_SUCCESS = 'Success'
MSG_OKAY = 'Okay'
MSG_FILE_EXIST = "File Exists. "
MSG_REWRITE = "Do you wish to overwrite the file contents? [y]/[n] "
MSG_ABORT = "Abort"
MSG_CANCEL = "Cancel"
MSG_READY = "Ready"
MSG_NOT_FOUND = "NOT FOUND"
MSG_CLOSE = "Closing"
MSG_ENTER_FILE = "No file"

'''
Helpers
'''
def int2byte(x):
    return x.to_bytes(4, byteorder='big')

def byte2int(xbytes):
    return int.from_bytes(xbytes, 'big')

def str2byte(sentence):
    return sentence.encode()


def byte2str(sentence):
    return sentence.decode('utf-8')


def file_exist(fname):
    return os.path.exists(FILE_DIR + fname)


def send_file(s, fname):
    file_dir = os.path.join(FILE_DIR, fname)

    with open(file_dir, 'rb') as file_to_send:
        for data in file_to_send:
            s.send(data)
    
    print('Send successfully!')
    return


def receive_file(s, fname):
    file_dir = os.path.join(FILE_DIR, fname)
    print('in')
    with open(file_dir, 'wb') as file_to_receive:
        while True:
            data = s.recv(BUFFER_SIZE)
            print('Receiving...')
            if not data:
                break
            file_to_receive.write(data)
            if len(data) < BUFFER_SIZE:
                break
    
    print('File received!')
    return 1


'''
PUT
'''
def put_file(s, fname):

    data = s.recv(BUFFER_SIZE)

    if byte2str(data) == MSG_OKAY:
        print('File not in the server\'s disk.')
        send_file(s, fname)
    else:
        send_msg = input(MSG_FILE_EXIST + MSG_REWRITE)
        s.send(str2byte(send_msg))

        if send_msg == 'y':
            data = s.recv(BUFFER_SIZE)
            # print(byte2str(data))
            if byte2str(data) == MSG_OKAY:
                send_file(s, fname)
            else:
                print('Operation Abort!\n')

        else:
            data = s.recv(BUFFER_SIZE)
            if byte2str(data) == MSG_ABORT:
                print('Unexpected response from server\n')
            else:
                print('Operation Abort!\n')
    
    return 

'''
GET
'''
def get_file(s, cmd_list):

    data = s.recv(BUFFER_SIZE)

    if byte2str(data) == MSG_ENTER_FILE:
        print('Please enter a file.')
    elif byte2str(data) == MSG_CANCEL:
        print('File not in the server\'s disk.')
    else:
        fname = cmd_list[1]
        if file_exist(fname):
            resp = input(MSG_REWRITE)
            s.send(str2byte(resp))
            if resp == 'y':
                receive_file(s, fname)
            else:
                print('Don\'t receive file.')
        else:
            s.send(str2byte('y'))
            receive_file(s, fname)


'''
LS
'''
def list_file(s):
    data = s.recv(BUFFER_SIZE)
    files = pickle.loads(data)
    for file_name in files:
        print(file_name)
    
    return


'''
MKDIR
'''
def mkdir(s, cmd_list):
    dir_name = cmd_list[1]

    data = s.recv(BUFFER_SIZE)
    if byte2str(data) == MSG_SUCCESS:
        print('Success.')
    else:
        print('mkdir: ' + dir_name + ': File exists')
    


'''
PWD
'''
def print_working_dir(s):
    data = s.recv(BUFFER_SIZE)
    print(byte2str(data))


'''
CD
'''
def change_dir(s):
    data = s.recv(BUFFER_SIZE)
    if byte2str(data) == MSG_NOT_FOUND:
        print('Directory not in the server\'s disk.')
    else:
        print('Directory changed!')


'''
EXIT
'''
def conn_exit(s):
    data = s.recv(BUFFER_SIZE)
    if byte2str(data) == MSG_CLOSE:
        print('Closing connection.')
        s.close()
        exit()
    else:
        print('Operation Abort!\n')
    

if __name__ == "__main__":
    try:
        print('Client is starting')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((HOST, PORT))

        print('Connected to %s on port' % HOST, PORT)

        while True:
            cmd = input('FTP>')

            byte_cmd = str2byte(cmd)
            len_cmd = len(byte_cmd)

            s.send(int2byte(len_cmd) + byte_cmd)

            cmd_list = cmd.split()
            cmd_name = cmd_list[0].upper()

            if cmd_name == 'PUT':
                fname = cmd_list[1]
                if not file_exist(fname):
                    print('Error, File %s not found' % fname)
                    continue
                print('Transferring file to server.\n')
                put_file(s, fname)
            elif cmd_name == 'GET':
                get_file(s, cmd_list)
            elif cmd_name == 'LS':
                list_file(s)
            elif cmd_name == 'MKDIR':
                mkdir(s, cmd_list)
            elif cmd_name == 'PWD':
                print_working_dir(s)
            elif cmd_name == 'CD':
                change_dir(s)
            elif cmd_name == 'EXIT':
                conn_exit(s)

    except:
        exit()