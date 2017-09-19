import socket
import threading


def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen for upto 50 cnxns on port 8000
    sock.bind(('', 1337))
    sock.listen(50)

    print '[L] Socket Opened, listening for connections'

    while True:
        csock,caddr = sock.accept()
        print '[N] new connection from '+caddr[0]+':'+str(caddr[1])
        # Start a thread to service each cnxn
        t = threading.Thread(target=handle_cnxn, args=(csock,caddr,))
        t.start()
 
 
def handle_cnxn(csock, caddr):
    shake1 = csock.recv(1024)

    print caddr[0]+'-> '+shake1
   
    shakelist = shake1.split("\r\n")
    
    print 'Got handshake'
    # Extract key1 and key2
    for elem in shakelist:
        if elem.startswith("Sec-WebSocket-Key:"):
            client64Key = elem[19:]  # Sec-WebSocket-Key1: is 20 chars
            #print 'got key '+client64Key
        elif elem.startswith("Origin:"):
            ws_origin = elem[8:]
        elif elem.startswith("Host:"):
            ws_host = elem[6:]
        elif elem.startswith("GET "):
            ws_path = elem[4:-9]
        else:
            continue
 
    # Concat key1, key2, and the the body of the client handshake and take the md5 sum of it
    print 'got client key '+client64Key
    key = client64Key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    print 'got joint key '+key
    import hashlib, base64
    m = hashlib.sha1()
    m.update(key)
    d = base64.b64encode(m.digest())
    print 'got base64 hash '+d
 
    # Send 'headers'
    # Modified to automatically adhere to the Same-Origin Policy.
    #   DO NOT USE IN PRODUCTION CODE!!!
    csock.send("HTTP/1.1 101 WebSocket Protocol Handshake\r\n")
    csock.send("Upgrade: WebSocket\r\n")
    csock.send("Connection: Upgrade\r\n")
    csock.send("Sec-WebSocket-Accept: " + d + "\r\n")
    csock.send("Sec-WebSocket-Origin: " + ws_origin + "\r\n")
    csock.send("Sec-WebSocket-Location: ws://" + ws_host + ws_path + "\r\n")
    #csock.send("Sec-WebSocket-Protocol: chat\r\n")
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
        send(str(i))
        print caddr[0]+'-> '+str(i)
        shake1 = csock.recv(1024)
        print caddr[0]+'<- '+shake1
        i += 1
        sleep(1)
 
if __name__ == "__main__":
    start()
