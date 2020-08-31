import os
import time
import sqlite3
import threading


class SQLiteMixin(object):

    @property
    def dbcur(self):
        pid = (os.getpid(), threading.current_thread().ident)
        if not (self.conn and pid == self.last_pid):
            self.last_pid = pid
            self.conn = sqlite3.connect(self.path, isolation_level=None)
        return self.conn.cursor()


class SplitTableMixin(object):
    UPDATE_PROJECTS_TIME = 10 * 60

    def _tablename(self, project):
        if self.__tablename__:
            return '%s_%s' % (self.__tablename__, project)
        else:
            return project

    @property
    def projects(self):
        if time.time() - getattr(self, '_last_update_projects', 0) \
                > self.UPDATE_PROJECTS_TIME:
            self._list_project()
        return self._projects

    @projects.setter
    def projects(self, value):
        self._projects = value

    def _list_project(self):
        self._last_update_projects = time.time()
        self.projects = set()
        if self.__tablename__:
            prefix = '%s_' % self.__tablename__
        else:
            prefix = ''
        for project, in self._select('sqlite_master', what='name',
                                     where='type = "table"'):
            if project.startswith(prefix):
                project = project[len(prefix):]
                reveal_type(self.projects)