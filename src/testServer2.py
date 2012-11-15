import socket
import sys
import threading
 
 
def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen for upto 50 cnxns on port 8000
    sock.bind(('', 1337))
    sock.listen(50)
 
    while True:
        csock,caddr = sock.accept()
        print "Connection from: ", caddr
        # Start a thread to service each cnxn
        t = threading.Thread(target=handle_cnxn, args=(csock,))
        t.start()
 
 
def handle_cnxn(csock):
    print 'new connection!'
    shake1 = csock.recv(1024)
   
    shakelist = shake1.split("\r\n")
    # The body follows a \r\n after the 'headers'
    body = shake1.split("\r\n\r\n")[1]
    
    print 'Got handshake'
    # Extract key1 and key2
    for elem in shakelist:
        print elem
        if elem.startswith("Sec-WebSocket-Key:"):
            key = elem[24:]  # Sec-WebSocket-Key1: is 20 chars
        elif elem.startswith("Origin:"):
            ws_origin = elem[8:]
        elif elem.startswith("Host:"):
            ws_host = elem[6:]
        elif elem.startswith("GET "):
            ws_path = elem[4:-9]
        else:
            continue
 
    # Concat key1, key2, and the the body of the client handshake and take the md5 sum of it
    key = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    import hashlib, base64
    m = hashlib.sha1()
    m.update(key)
    d = base64.b64encode(m.digest())
    print "got key "+d
 
    # Send 'headers'
    # Modified to automatically adhere to the Same-Origin Policy.
    #   DO NOT USE IN PRODUCTION CODE!!!
    csock.send("HTTP/1.1 101 WebSocket Protocol Handshake\r\n")
    csock.send("Upgrade: WebSocket\r\n")
    csock.send("Connection: Upgrade\r\n")
    csock.send("Sec-WebSocket-Accept: " + d + "\r\n")
    csock.send("Sec-WebSocket-Origin: " + ws_origin + "\r\n")
    csock.send("Sec-WebSocket-Location: ws://" + ws_host + ws_path + "\r\n")
    csock.send("Sec-WebSocket-Protocol: chat\r\n")
    csock.send("\r\n")
    #Send digest
    csock.send(d)
 
    # Message framing - 0x00 utf-8-encoded-body 0xFF
    def send(data):
        first_byte = chr(0x00)
        payload = data.encode('utf-8')
        pl = first_byte + payload + chr(0xFF)
        csock.send(pl)
 
   
    from time import sleep
 
    # This is dependent on you - what you wish to send to the browser
    i = 0
    while True:
        send(u"%s" % (i))
        i += 1
        sleep(1)
 
if __name__ == "__main__":
    start()
