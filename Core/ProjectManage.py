#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: ProjectManage.py
# Time: 2017/2/1

import requests
from requests.exceptions import ConnectionError
from ipaddr import IPNetwork

from Utils.LogHelper import logger

__author__ = 'lightless'
__email__ = 'root@lightless.me'


class ProjectManage(object):

    def __init__(self):
        super(ProjectManage, self).__init__()

        # 存储所有的扫描任务
        self.all_tasks_list = list()

        # project id
        self.project_id = None

    def add_task(self, task=None):
        """
        向project中添加task
        添加多个URL或者多个IP段需要多次调用该函数
        :param task: URL 或者 IP 段
        :return: Bool
        """
        self.parse_task_type(task)
        pass

    @staticmethod
    def parse_task_type(task):
        """
        解析project类型
        :param task: 待处理的project target
        :return: None - 啥也不是 1 - IP task, 2 - URL task
        """
        try:
            IPNetwork(task)
            logger.info("Found IP Target: {0}".format(task))
            return 1
        except ValueError:
            # 不是IP地址，判断是否为URL
            if isinstance(task, str):
                if not task.startswith("https://") or not task.startswith("http://"):
                    task = "http://" + task
                try:
                    requests.head(task)
                    logger.info("Found URL Target: {0}".format(task))
                    return 2
                except ConnectionError:
                    return None
            else:
                return None


