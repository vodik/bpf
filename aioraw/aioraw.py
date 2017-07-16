import asyncio
import socket

from .constants import ETH_P_ALL
from .constants import SO_BINDTODEVICE


@asyncio.coroutine
def create_raw_endpoint(loop, protocol_factory, *, interface=None,
                        program=None):
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                         socket.htons(ETH_P_ALL))

    if interface:
        ifname = interface.encode() + b'\0'
        sock.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, ifname)

    if program:
        from bpf import attach_program
        attach_program(sock, program)

    # sock.setblocking(False)
    return loop.create_connection(protocol_factory, sock=sock)
