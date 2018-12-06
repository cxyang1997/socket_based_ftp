import socket
import sys
import os

HOST = '127.0.0.1'
PORT = 54321
BUFFER_SIZE = 1024

FILE_DIR = './client_file/'

MSG_SUCCESS = 'Success'
MSG_OKAY = 'Okay'
MSG_FILE_EXIST = "File Exist\n"
MSG_REWRITE = "Do you wish to overwrite the file contents? [y]/[n]\n"
MSG_ABORT = "Abort"


'''
Helpers
'''
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
    return 0


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
            print(byte2str(data))
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


if __name__ == "__main__":
    try:
        print('Client is starting')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((HOST, PORT))

        while True:
            cmd = input()
            s.send(str2byte(cmd))

            cmd_list = cmd.split()
            cmd_name = cmd_list[0].upper()

            if cmd_name == 'PUT':
                fname = cmd_list[1]
                if not file_exist(fname):
                    print('Error, File %s not found' % fname)
                    continue
                print('Transferring file to server.\n')
                put_file(s, fname)
                if s.recv(BUFFER_SIZE) != MSG_SUCCESS:
                    print('Error sending file. Please try again.\n')
                    break

            data = s.recv(BUFFER_SIZE)
            repr(data)

    except:
        exit()