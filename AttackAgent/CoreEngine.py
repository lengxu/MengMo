#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: CoreEngine.py
# Time: 2017/1/27

import Queue
import threading

from Utils.LogHelper import logger

__author__ = 'lightless'
__email__ = 'root@lightless.me'


class AttackAgentCoreEngine(object):

    def __init__(self):
        super(AttackAgentCoreEngine, self).__init__()

        # 任务队列
        self.task_queue = Queue.Queue()

        # 停止信号
        self.end_process = False

        # 线程分发器
        self.main_loop = threading.Thread(target=self.__main_loop, name="AttackAgentMainLoop")
        self.main_loop.start()

    def stop(self):
        logger.info("接受到停止信号, 等待AttackAgent停止")
        self.end_process = True

    def add_task(self, task=tuple()):
        pass

    def __main_loop(self):
        pass

