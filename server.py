from os import path
import socket
import os

# Verify if the request is a GET request, if not, send a 501 Not Implemented response and close the connection
def isGET(sentence):
    if sentence.startswith("GET") == True:
        print(f"Received GET request from {addr}:\n{sentence}\n")
    else:
        print(f"[NOT GET] Received from {addr}:\n{sentence}\n")
        connectionSocket.send("HTTP/1.1 501 Not Implemented\r\n\r\n".encode())
        connectionSocket.close()

# Handle the HTTP request by parsing the requested path, checking if the file exists, and sending the appropriate response (200 OK with content or 404 Not Found)
def handleRequest(sentence):
    first_line = sentence.split('\r\n')[0] # pegar a primeira linha da requisição
    parts = first_line.split(' ') # dividir a primeira linha em partes (método, caminho, versão)

    path = parts[1] # pegar o caminho da requisição

    if path == '/':
        path = 'index.html'

    local_path = os.path.normpath(os.path.join(os.getcwd(), path.lstrip('/')))



############################################
# WEB SERVER CONFIGURATION
############################################
print("Starting the server...")
HOST = '127.0.0.1'  # localhost
PORT = 8080         # porta que vamos usar
BASEDIR = os.path.dirname(__file__)
print(f"Current working directory: {BASEDIR}")

# criar socket 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET para IPv4, SOCK_STREAM para TCP

#associar endereço e porta ao socket
server_socket.bind((HOST, PORT))

# colocar o socket em modo de escuta
server_socket.listen()
print(f"Server listening in http://{HOST}:{PORT}")



############################################
# ACEITAR CONEXÕES
############################################
while True:
    connectionSocket, addr = server_socket.accept()
    print(f"Connection from {addr} has been established.\n")
    
    sentence = connectionSocket.recv(1024).decode()
    isGET(sentence)
    handleRequest(sentence)

    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()



############################################
# RESPONDER AO PEDIDO HTTP
############################################
    
