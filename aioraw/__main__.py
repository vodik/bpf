import asyncio
import socket

import bpf
from hexdump import hexdump

from .aioraw import create_raw_endpoint
from .constants import ETH_P_IP


class RawProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        print("Capturing packets...")

    def data_received(self, data):
        hexdump(data)

    def connection_lost(self, exc):
        pass


def main():
    bootp = bpf.compile(f'''
        ldh [0x24]
        jneq #68, #7
        ldh [0x14]
        jset #0x1fff, #5
        ldb [0x17]
        jneq #{socket.IPPROTO_UDP}, #3
        ldh [0x0c]
        jneq #{ETH_P_IP}, #1
        ret #-1
        ret #0
    ''')

    loop = asyncio.get_event_loop()
    coro = create_raw_endpoint(loop, RawProtocol,
                               interface="wlp2s0",
                               program=bootp)

    loop.run_until_complete(coro)
    loop.run_forever()


if __name__ == '__main__':
    main()
