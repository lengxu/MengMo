#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: PortAgent.py
# Time: 2017/1/24

from libnmap.process import NmapProcess

__author__ = 'lightless'
__email__ = 'root@lightless.me'



if __name__ == '__main__':
    nm = NmapProcess("45.32.42.3", options="-sV")
    rc = nm.run()

    print nm.stdout
    print nm.stderr
