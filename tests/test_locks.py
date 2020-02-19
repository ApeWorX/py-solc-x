#!/usr/bin/python3

import multiprocessing as mp
import threading

import solcx


class ThreadWrap:
    def __init__(self, fn, *args, **kwargs):
        self.exc = None
        self.t = threading.Thread(target=self.wrap, args=(fn,) + args, kwargs=kwargs)
        self.t.start()

    def wrap(self, fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            self.exc = e

    def join(self):
        self.t.join()
        if self.exc is not None:
            raise self.exc


def test_threadlock(nosolc):
    threads = [ThreadWrap(solcx.install_solc, "0.5.0") for i in range(4)]
    for t in threads:
        t.join()


def test_processlock(nosolc):
    # have to use a context here to prevent a conflict with tqdm
    ctx = mp.get_context("spawn")
    threads = [ctx.Process(target=solcx.install_solc, args=("0.5.0",),) for i in range(4)]
    for t in threads:
        t.start()
    solcx.install_solc("0.5.0")
    for t in threads:
        t.join()
        assert t.exitcode == 0
