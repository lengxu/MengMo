#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: PortAgent.py
# Time: 2017/1/24

from CoreEngine import PortAgentCoreEngine

__author__ = 'lightless'
__email__ = 'root@lightless.me'


if __name__ == '__main__':

    port_agent_engine = PortAgentCoreEngine()
    port_agent_engine.add_task(("192.168.198.128", "-sV"))

    # nm = NmapProcess("45.32.42.3", options="-O -sV")
    # nm.run_background()
    #
    # while nm.is_running():
    #     time.sleep(1)
    #     print("running")
    #
    # nmap_report = NmapParser.parse(nm.stdout)
    #
    # for h in nmap_report.hosts:
    #     print(h)
    #     print(h.get_open_ports())
    #
    #     for p in h.get_open_ports():
    #         print(p)
    #         print(h.get_service(p[0]))

        # for os in h.os_class_probabilities():
        #     print(os)
            # print(os.osfamily)
            # print(os.osgen)
            # print(os.type)
            # print(os.vendor)
            # print(os.description)

