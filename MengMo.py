#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: MengMo.py
# Time: 2017/1/24

from Utils.LogHelper import logger
from ShareMemory import ShareData
from PortAgent.CoreEngine import PortAgentCoreEngine


__author__ = 'lightless'
__email__ = 'root@lightless.me'


def main():
    logger.info("Starting MengMo...")
    logger.info("Starting Port Agent...")
    ShareData.port_agent_engine = PortAgentCoreEngine()


if __name__ == '__main__':
    main()
