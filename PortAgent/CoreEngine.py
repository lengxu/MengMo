#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: CoreEngine.py
# Time: 2017/1/26

import Queue
import time
import threading
import datetime

from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
from sqlalchemy.exc import SQLAlchemyError

from Utils.LogHelper import logger
from ShareMemory.Settings import settings
from models import MengMoPortTasks
from models import MengMoPortResults
from models import DBSession

__author__ = 'lightless'
__email__ = 'root@lightless.me'


class PortAgentCoreEngine(object):
    
    def __init__(self):
        super(PortAgentCoreEngine, self).__init__()

        # 存储task的队列
        self.task_queue = Queue.Queue()

        # 判断进程是否结束
        self.end_process = False

        # 线程池大小
        self.thread_pool_size = settings.PORT_AGENT_THREAD_POOL_SIZE

        # 存储线程的list
        self.thread_list = list()
        self.alive_thread_count = 0

        # db session
        self.session = DBSession()

        # 开启主循环, 线程分发器
        main_loop = threading.Thread(target=self.__run, name="PortAgentMainLoop")
        main_loop.start()

    def add_task(self, task=tuple()):
        # 添加一个端口扫描任务到引擎中
        # tuple("1.1.1.1", "-sV -p-")
        # tuple(ip, params)

        # 检查task类型是否合法
        if not isinstance(task, tuple):
            return False, "Wrong task type, tuple(ip, params) need, but {0} found.".format(type(task))

        # 检查task内容是否正确
        if len(task) == 2:
            self.task_queue.put(task)
            return True, "success"
        elif len(task) == 1:
            # 没有指定scan opt，使用默认opt
            self.task_queue.put((task[0], settings.PORT_AGENT_DEFAULT_SCAN_OPT))
            return True, "success with default scan opt."
        else:
            # task内容错误
            return False, "Wrong task type, tuple(ip, params) need."

    def stop(self):
        """
        结束PortAgent
        :return:
        """
        self.end_process = True

    def update_thread_status(self):
        """
        更新线程池状态
        :return:
        """
        alive_count = 0
        for th in self.thread_list:

            # 如果线程存活，那么加1数量
            if th.is_alive():
                alive_count += 1
            else:
                # 死掉的线程从列表里删掉
                logger.debug("从thread_list中移除线程{0}".format(th.name))
                self.thread_list.remove(th)
        # 更新存活线程总数
        self.alive_thread_count = alive_count

    def __run(self):
        """
        主循环，线程分发器
        :return:
        """
        logger.info("Port Agent started.")
        while not self.end_process:

            # sleep
            time.sleep(1)

            # 刷新当前线程状态
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

            # 获取端口扫描任务
            task = self.task_queue.get()
            target_ip = task[0]
            target_params = task[1]

            # 将该任务插入数据库
            port_task = MengMoPortTasks()
            port_task.task_name = "{0}_port_scan".format(target_ip)
            port_task.task_target_ip = target_ip
            port_task.task_params = target_params
            port_task.task_start = datetime.datetime.now()
            port_task.task_end = datetime.datetime.now()
            port_task.task_status = 1
            self.session.add(port_task)
            try:
                self.session.commit()
            except SQLAlchemyError as e:
                # 如果出错了, 继续搞下一个任务
                logger.error(e)
                self.session.rollback()
                continue
            task_id = port_task.id
            nmap_thread = threading.Thread(
                target=self.nmap_func, name="{ip}_port_scan_thread".format(ip=target_ip),
                args=(task, task_id)
            )
            self.thread_list.append(nmap_thread)
            nmap_thread.start()

    def nmap_func(self, task=tuple(), task_id=None):
        """
        真正的nmap扫描函数
        :param task_id:
        :param task:
        :return:
        """
        # 从数据库中查询出任务
        session = DBSession()
        qs = session.query(MengMoPortTasks).filter(
            MengMoPortTasks.is_deleted != 1, MengMoPortTasks.id == task_id
        )
        if not qs.first():
            return False

        logger.info("{ip}端口扫描开始".format(ip=task[0]))
        # 更新任务状态到RUNNING
        qs.update({"task_status": 2})
        try:
            session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            session.rollback()

        nm = NmapProcess(targets=task[0], options=task[1])
        nm.run()

        # 解析扫描结果
        nmap_report = NmapParser.parse(nm.stdout)
        for host in nmap_report.hosts:
            for open_port in host.get_open_ports():
                logger.info(open_port)
                banner = host.get_service(open_port[0]).banner
                service = host.get_service(open_port[0]).service

                # 将扫描结果添加到数据库中
                port_result = MengMoPortResults(
                    task_id, ip=task[0], open_port=open_port[0], banner=banner, service=service
                )
                session.add(port_result)
                try:
                    session.commit()
                except SQLAlchemyError as e:
                    logger.error(e)
                    session.rollback()

        # 根据返回值跟新任务状态到FINISHED 或 ERROR
        qs = session.query(MengMoPortTasks).filter(
            MengMoPortTasks.is_deleted != 1, MengMoPortTasks.id == task_id
        )
        if nm.rc == 0:
            qs.update({"task_status": 3})
        else:
            qs.update({"task_status": 4})
        try:
            session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            session.rollback()

        logger.info("{ip}端口扫描结束".format(ip=task[0]))
        session.close()


