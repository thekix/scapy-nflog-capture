# -*- coding: utf-8 -*-
from __future__ import print_function

import functools as ft
from threading import Thread
from collections import deque
import os

from scapy.all import conf, SuperSocket, ETH_P_ALL, Scapy_Exception
from scapy.layers.inet import IP
from nflog_cffi import NFLOG


class NFLOGReaderThread(Thread):
    """Necessary only because libnetfilter_log returns
    packets in batches, and scapy expects to poll/read them one-by-one."""

    daemon = True

    def __init__(self, queues, **nflog_kwargs):
        super(NFLOGReaderThread, self).__init__()
        self.queues, self.nflog_kwargs, self.pipe = queues, nflog_kwargs, deque()
        self.pipe_chk, self._pipe = os.pipe()
        self.pipe_chk, self._pipe = os.fdopen(self.pipe_chk, 'r'), os.fdopen(self._pipe, 'w')

    def run(self):
        nflog = NFLOG().generator(self.queues, extra_attrs = ['fts'], **self.nflog_kwargs)
        next(nflog)
        for pkt_info in nflog:
            self.pipe.append(pkt_info)
            self._pipe.write('.')  # block until other thread reads it
            self._pipe.flush()


class NFLOGListenSocket(SuperSocket):
    desc = 'read packets at layer 3 using Linux NFLOG'

    queues = range(4)

    def __init__(self, iface=None, type=ETH_P_ALL,
                 promisc=None, filter=None, nofilter=0, queues=None, nflog_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        if nflog_kwargs is None:
            nflog_kwargs = dict()
        self.type, self.outs = type, None
        if queues is None:
            queues = self.queues
        self.nflog = NFLOGReaderThread(queues, **nflog_kwargs)
        self.nflog.start()
        self.ins = self.nflog.pipe_chk

    def recv(self, **kwargs):
        self.ins.read(1)  # used only for poll/sync
        pkt, ts = self.nflog.pipe.popleft()
        if pkt is None:
            return
        try:
            pkt = IP(pkt)
        except KeyboardInterrupt:
            raise
        except:
            if conf.debug_dissector:
                raise
            pkt = conf.raw_layer(pkt)
        pkt.time = ts
        return pkt

    def send(self, pkt):
        raise Scapy_Exception(
            'Cannot send anything with {}'.format(self.__class__.__name__))

    def close(self):
        SuperSocket.close(self)


def install_nflog_listener(queues=None, **nflog_kwargs):
    """Install as default scapy L2 listener."""
    conf.L2listen = ft.partial(NFLOGListenSocket,
                               queues=queues,
                               nflog_kwargs=nflog_kwargs)


if __name__ == '__main__':
    from scapy.sendrecv import sniff

    def handler(m_pkt):
        print('Got packet, len: {}, ts: {}'.format(len(m_pkt), m_pkt.time))
        print('Payload:', bytes(m_pkt))

    # Listen the NFSLOG device and call the handler per packet
    install_nflog_listener()
    sniff(prn=handler, store=0)
