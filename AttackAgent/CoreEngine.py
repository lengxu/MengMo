#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: CoreEngine.py
# Time: 2017/1/27

import Queue
import time
import threading

from models import DBSession
from models import MengMoAttackTasks
from Utils.LogHelper import logger
from ShareMemory.Settings import settings

__author__ = 'lightless'
__email__ = 'root@lightless.me'


class AttackAgentCoreEngine(object):

    def __init__(self):
        super(AttackAgentCoreEngine, self).__init__()

        # 数据库连接
        self.session = DBSession()

        # 任务队列
        self.task_queue = Queue.Queue()

        # 停止信号
        self.end_process = False

        # 线程池大小
        self.thread_pool_size = settings.ATTACK_AGENT_THREAD_POOL_SIZE

        # 当前存活线程计数
        self.alive_thread_count = 0

        # 当前线程列表
        self.thread_list = list()

        # 线程分发器
        self.main_loop = threading.Thread(target=self.__main_loop, name="AttackAgentMainLoop")
        self.main_loop.start()

    def stop(self):
        logger.info("接受到停止信号, 等待AttackAgent停止")
        self.end_process = True

    def add_task(self, task=None):
        """
        添加任务
        如果没有指定plugin，则自动根据端口和协议选择
        :param task: dict(target_type, target, port, service, plugin, options)
        :return:
        """
        if task is None:
            return False, "dict(target_type, target, port, service, plugin, options) need, NoneType Found."
        if "target_type" not in task.keys():
            return False, "No `target_type` found."
        if "target" not in task.keys():
            return False, "No `target` found."
        if "port" not in task.keys():
            return False, "No `service` found."

        self.task_queue.put(task)
        return True, "success."

    def update_thread_status(self):
        """
        更新线程计数
        :return:
        """
        alive_count = 0
        for thread in self.thread_list:
            # 如果线程存活，那么加1数量
            if thread.is_alive():
                alive_count += 1
            else:
                # 死掉的线程从列表里删掉
                logger.debug("从thread_list中移除线程{0}".format(thread.name))
                self.thread_list.remove(thread)
                # 更新存活线程总数
        self.alive_thread_count = alive_count

    def __main_loop(self):
        """
        线程分发器
        :return:
        """
        logger.info("Attack Agent Started.")

        while not self.end_process:
            time.sleep(1)

            # 更新线程计数器
            self.update_thread_status()

            # 判断当前是否存在空余任务位置
            # 如果没有空余位置了，继续等待
            # 否则获取任务信息
            if self.alive_thread_count >= self.thread_pool_size:
                continue

            # 判断当前是否有任务，没有任务的话继续等待
            if self.task_queue.empty():
                logger.debug("任务队列为空, 等待任务信息, 当前存活线程: {0}".format(self.alive_thread_count))
                continue

            # 获取攻击任务
            attack_task = self.task_queue.get()
            target_type = attack_task.get("target_type", "")
            if target_type == 1:
                target_type = "IP"
            elif target_type == 2:
                target_type = "URL"
            # target = attack_task.get("target", "")
            # target_port = attack_task.get("target_port", "")
            # target_service = attack_task.get("target_service", "")
            # target_plugin = attack_task.get("target_plugin", "")
            # target_options = attack_task.get("target_options", "")

            # 执行攻击任务
            attack_thread = threading.Thread(
                target=self.attack_thread_func, name="{0}_attack_thread".format(target_type), args=(attack_task, )
            )
            attack_thread.start()
            self.thread_list.append(attack_thread)

    def attack_thread_func(self, task):

        # 获取数据库连接
        session = DBSession()

        # 获取使用的插件信息
        service = task.get("target_service", "").lower()
        port = task.get("target_port", "")

        logger.info("获取服务banner: {0}".format(service))
        logger.info("获取服务端口: {0}".format(port))

        if service != "":
            # 根据服务信息选择攻击插件
            logger.info("根据banner自动选择攻击脚本")
            if "ssh" in service.lower():
                logger.info("SSH Plugin Start.")
                pass

        elif port != "":
            # 根据端口号选择攻击插件
            if int(port) == 22:
                pass
        else:
            return False

