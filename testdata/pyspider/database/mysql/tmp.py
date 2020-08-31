import time
import mysql.connector

from pyspider.database.base.projectdb import ProjectDB as BaseProjectDB
from pyspider.database.basedb import BaseDB
from .mysqlbase import MySQLMixin


class ProjectDB(MySQLMixin, BaseProjectDB, BaseDB):
    __tablename__ = 'projectdb'

    def __init__(self, host='localhost', port=3306, database='projectdb',
                 user='root', passwd=None):
        self.database_name = database
        self.conn = mysql.connector.connect(user=user, password=passwd,
                                            host=host, port=port, autocommit=True)
        if database not in [x[0] for x in self._execute('show databases')]:
            self._execute('CREATE DATABASE %s' % self.escape(database))
        self.conn.database = database

        self._execute('''CREATE TABLE IF NOT EXISTS %s (
            `name` varchar(64) PRIMARY KEY,
            `group` varchar(64),
            `status` varchar(16),
            `script` TEXT,
            `comments` varchar(1024),
            `rate` float(11, 4),
            `burst` float(11, 4),
            `updatetime` double(16, 4)
            ) ENGINE=InnoDB CHARSET=utf8''' % self.escape(self.__tablename__))

    def insert(self, name, obj={}):
        obj = dict(obj)
        obj['name'] = name
        obj['updatetime'] = time.time()
        return self._insert(**obj)

    def update(self, name, obj={}, **kwargs):
        obj = dict(obj)
        reveal_type(obj)