from os import path
import socket
import os

# Mapeamento de extensões para Content-Type
MIME_TYPES = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'javascript': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}

STATIC_DIR = os.path.normpath(os.path.join(os.getcwd(), 'static'))

# Verify if the request is a GET request, if not, send a 501 Not Implemented response and close the connection
def isGET(sentence):
    if sentence.startswith("GET") == True:
        print(f"Received GET request from {addr}:\n{sentence}\n")
        return True
    else:
        print(f"[NOT GET] Received from {addr}:\n{sentence}\n")
        try:
            connectionSocket.sendall("HTTP/1.1 501 Not Implemented\r\n\r\n".encode())
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            print(f"Client closed connection before 501 could be sent: {addr}")
        # connectionSocket.close()
        return False

# Handle the HTTP request by parsing the requested path, checking if the file exists, and sending the appropriate response (200 OK with content or 404 Not Found)
def handleRequest(sentence):
    first_line = sentence.split('\r\n')[0]  # pegar a primeira linha da requisição
    parts = first_line.split(' ')  # dividir a primeira linha em partes (método, caminho, versão)

    path = parts[1]  # pegar o caminho da requisição
    path = path.split('?', 1)[0]  # ignorar query string

    if path == '/': # Se o caminho for '/', servir o index.html por padrão
        path = 'server.html' 

    local_path = os.path.normpath(os.path.join(STATIC_DIR, path.lstrip('/'))) 

    # Garantir que só servimos ficheiros dentro de static
    if os.path.commonpath([STATIC_DIR, local_path]) != STATIC_DIR:
        forbidden_message = "403 Forbidden"
        response_header = f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\nContent-Length: {len(forbidden_message)}\r\n\r\n"
        try:
            connectionSocket.sendall(response_header.encode())
            connectionSocket.sendall(forbidden_message.encode())
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            print(f"Client closed connection during 403 response: {addr}")
        print(f"Blocked path traversal: {local_path}\n")
        return

    # Verificar se o arquivo existe
    if os.path.isfile(local_path):
        try:
            # Ler o conteúdo do arquivo
            with open(local_path, 'rb') as f:
                content = f.read()
            
            # Determinar o Content-Type baseado na extensão
            file_extension = os.path.splitext(local_path)[1].lstrip('.').lower()
            content_type = MIME_TYPES.get(file_extension, 'application/octet-stream')
            
            # Construir a resposta HTTP 200 OK
            response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n"
            connectionSocket.sendall(response_header.encode())
            connectionSocket.sendall(content)
            
            print(f"Sent 200 OK: {local_path}\n")
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            print(f"Client closed connection while sending file: {local_path}")
        except Exception as e:
            # Erro ao ler o arquivo
            error_response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\nContent-Length: 21\r\n\r\nInternal Server Error"
            try:
                connectionSocket.sendall(error_response.encode())
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                print(f"Client closed connection before 500 could be sent: {addr}")
            print(f"Error reading file: {e}\n")
    else:
        # Arquivo não encontrado - 404 Not Found
        not_found_message = "404 Not Found"
        response_header = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: {len(not_found_message)}\r\n\r\n"
        try:
            connectionSocket.sendall(response_header.encode())
            connectionSocket.sendall(not_found_message.encode())
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            print(f"Client closed connection during 404 response: {addr}")
        print(f"File not found: {local_path}\n")



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
    if isGET(sentence):
        handleRequest(sentence)

    connectionSocket.close()
