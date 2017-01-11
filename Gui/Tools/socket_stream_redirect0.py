"""
[partial] Tools for connecting streams of non-GUI programs to sockets
that a GUI (or other) can use to interact with the non-GUI program;
see Chapter 12 and PP4E\Sockets\Internet for a more complete treatment
"""
import sys
from socket import *


port = 50008
host = 'localhost'


def redirectOut(port=port, host=host):
    """
    connect caller's standard output stream to a socket for GUI to listen;
    start caller after listener started, else connect fails before accept
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, port))
    file = sock.makefile('w')
    sys.stdout = file


def redirectIn(port=port, host=host): ...
def redirectBothAsClient(port=port, host=host): ...
def redirectBothAsServer(port=port, host=host): ...
