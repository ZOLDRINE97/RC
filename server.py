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


# Verifica se o pedido e GET; caso nao seja, envia 501 Not Implemented e fecha a ligacao
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


# Trata o pedido HTTP: analisa o caminho pedido, verifica se o ficheiro existe e envia a resposta adequada (200 OK ou 404 Not Found)
def handleRequest(sentence):
    first_line = sentence.split('\r\n')[0]  # obter a primeira linha do pedido
    parts = first_line.split(' ')  # dividir a primeira linha em partes (metodo, caminho, versao)

    path = parts[1]  # obter o caminho do pedido
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

    # Verificar se o ficheiro existe
    if os.path.isfile(local_path):
        try:
            # Ler o conteudo do ficheiro
            with open(local_path, 'rb') as f:
                content = f.read()
            
            # Determinar o Content-Type com base na extensao
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
            # Erro ao ler o ficheiro
            error_response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\nContent-Length: 21\r\n\r\nInternal Server Error"
            try:
                connectionSocket.sendall(error_response.encode())
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                print(f"Client closed connection before 500 could be sent: {addr}")
            print(f"Error reading file: {e}\n")
    else:
        # Ficheiro nao encontrado - 404 Not Found
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

BASEDIR = os.path.dirname(__file__)
print(f"Current working directory: {BASEDIR}")

# criar socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET para IPv4, SOCK_STREAM para TCP

# associar endereco e porta ao socket
HOST = ''  # localhost
PORT = 8080         # porta que vamos usar
server_socket.bind((HOST, PORT))

# colocar o socket em modo de escuta
server_socket.listen(0)
print(f"Server listening in http://{HOST}:{PORT}")



############################################
# ACEITAR CONEXÕES
############################################
while True:
    connectionSocket, addr = server_socket.accept()
    print(f"Connection from {addr} has been established.\n")
    connectionSocket.settimeout(2)
    try: 
        sentence,addrs = connectionSocket.recvfrom(4096)
        sentence = sentence.decode()
        if isGET(sentence):
            handleRequest(sentence)
    except:
        print("Timeout :/")

    connectionSocket.close()
