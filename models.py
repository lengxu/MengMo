#!/usr/bin/env python2
# coding: utf-8
# Created by PyCharm
# Project: MengMo
# Filename: models.py
# Time: 2017/1/26

import datetime

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import String
from sqlalchemy import DATETIME
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.mysql import TEXT

from ShareMemory.Settings import settings

__author__ = 'lightless'
__email__ = 'root@lightless.me'


ModelBase = declarative_base()


class MengMoPortTasks(ModelBase):
    """
    存储端口扫描任务信息
    """

    __tablename__ = 'mengmo_port_tasks'

    id = Column(BIGINT(20, unsigned=True), autoincrement=True, primary_key=True)
    task_name = Column(String(64), nullable=False)
    task_target_ip = Column(String(16), nullable=False)
    task_params = Column(String(256))
    task_start = Column(DATETIME, server_default=func.now())
    task_end = Column(DATETIME, server_default=func.now())
    # 1 - READY 尚未开始
    # 2 - RUNNING 扫描中
    # 3 - FINISHED 扫描完成
    # 4 - ERROR 扫描出错
    task_status = Column(TINYINT(2, unsigned=True), nullable=False)

    created_time = Column(DATETIME, server_default=func.now())
    updated_time = Column(DATETIME, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(TINYINT(2, unsigned=True), default="0", server_default="0")

    def __init__(self, task_name=None, task_ip=None, task_params=None, task_start=None, task_end=None, task_status=1):
        self.task_name = task_name
        self.task_target_ip = task_ip
        self.task_params = task_params
        self.task_start = task_start
        self.task_end = task_end
        self.task_status = task_status

    def __repr__(self):
        s = {
            1: 'READY',
            2: 'RUNNING',
            3: 'FINISHED',
            4: 'ERROR',
        }
        return "<MengMoPortTask [{status}] {ip} '{params}'>".format(
            status=s[self.task_status], ip=self.task_target_ip, params=self.task_params
        )


class MengMoPortResults(ModelBase):
    """
    存储端口扫描结果
    """

    __tablename__ = 'mengmo_port_results'

    id = Column(BIGINT(20, unsigned=True), autoincrement=True, primary_key=True)
    task_id = Column(BIGINT(20, unsigned=True))
    ip = Column(String(16), nullable=False)
    open_port = Column(String(6), nullable=False)
    banner = Column(TEXT(), nullable=True)
    service = Column(TEXT(), nullable=True)
    pushed_to_attack = Column(TINYINT(2, unsigned=True))

    created_time = Column(DATETIME, server_default=func.now())
    updated_time = Column(DATETIME, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(TINYINT(2, unsigned=True), default="0", server_default="0")

    def __init__(self, task_id, ip=None, open_port=None, service=None, banner=None, pushed_to_attack=0,
                 created_time=None, updated_time=None, is_deleted=0):
        self.task_id = task_id
        self.ip = ip
        self.open_port = open_port
        self.service = service
        self.banner = banner
        self.pushed_to_attack = pushed_to_attack
        self.created_time = created_time if created_time is not None else datetime.datetime.now()
        self.updated_time = updated_time if updated_time is not None else datetime.datetime.now()
        self.is_deleted = is_deleted

    def __repr__(self):
        return "<MengMoPortResults {ip} - {port} open>".format(ip=self.ip, port=self.open_port)


engine = create_engine(settings.MYSQL_DSN)
DBSession = sessionmaker(bind=engine)


if __name__ == '__main__':
    ModelBase.metadata.create_all(engine)