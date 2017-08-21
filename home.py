
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from socket import *
import json
msg = 'M-SEARCH * HTTP/1.1\r\n' \
          'ST:wifi_bulb\r\n' \
          'MAN:"ssdp:discover"\r\n'

def _socket(sock, ip, port):
    if sock is None:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, port))
    return sock

cs = socket(AF_INET, SOCK_DGRAM)
cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
cs.settimeout(2)
cs.sendto(msg.encode(), ('239.255.255.250', 1982))
data, addr = (None, None)
while True:
    try:
        data, addr = cs.recvfrom(65507)
        print(data)
    except :
        break

capabilities = dict([x.strip("\r").split(": ") for x in data.decode().split("\n") if ":" in x])

from urllib.parse import urlparse
url = urlparse(capabilities['Location'])
open_socket = _socket(None, url.hostname, url.port)
cmd_id = 0

def turn_light(on="on"):
    global cmd_id
    command = {
                "id": cmd_id,
                "method": "set_power",
                "params": [on],
        }
    try:   
        open_socket.send((json.dumps(command) + "\r\n").encode("utf8"))
    except Exception as ex:
        print(ex)
    cmd_id = cmd_id + 1


app = Flask('sample')
@app.route('/')
def show_entries():
    return render_template('index.html')


@app.route('/turnon')
def turnon():
    turn_light("on")
    return render_template('index.html')


@app.route('/turnoff')
def turnoff():
    turn_light("off")
    return render_template('index.html')
