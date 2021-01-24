from simple_automation.version import __version__
from simple_automation.group import Group
from simple_automation.host import Host
from simple_automation.task import Task
from simple_automation.context import Context
from simple_automation.exceptions import TransactionError
from simple_automation.vars import Vars
import argparse

class ArgumentParserError(Exception):
    pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

class Manager(Vars):
    def __init__(self):
        super().__init__()
        self.groups = {}
        self.hosts = {}
        self.tasks = {}
        self.set("simple_automation_managed", "This file is managed by simple automation.")

    def add_group(self, identifier):
        group = Group(self, identifier)
        if identifier in self.groups:
            raise Exception(f"Cannot register group: Duplicate identifier {identifier}")
        self.groups[identifier] = group
        return group

    def add_host(self, identifier, ssh_host):
        host = Host(self, identifier, ssh_host)
        if identifier in self.hosts:
            raise Exception(f"Cannot register host: Duplicate identifier {identifier}")
        self.hosts[identifier] = host
        return host

    def add_task(self, task_class):
        identifier = task_class.identifier
        if identifier in self.tasks:
            raise Exception(f"Cannot register task: Duplicate identifier {identifier}")
        task = task_class(self)
        self.tasks[identifier] = task
        return task

    def main(self, run):
        parser = ThrowingArgumentParser(description="Runs this simple automation script.")

        # General options
        parser.add_argument('-H', '--hosts', dest='hosts', default=None, type=list,
                help="Specifies a subset of hosts to run on. By default all hosts are selected.")
        parser.add_argument('-p', '--pretend', dest='pretend', default=False, type=list,
                help="Print what would be done instead of performing the actions.")
        parser.add_argument('--version', action='version',
                version='%(prog)s built with simple_automation version {version}'.format(version=__version__))

        try:
            args = parser.parse_args()
        except ArgumentParserError as e:
            print("error: " + str(e))

        # TODO ask for vault key, vaultdecrypt = ask = [openssl - ...], gpg = []
        # TODO ask for su key, becomekey=ask,command=[]
        # TODO becomemethod=su, sudo -u root, ...
        try:
            with Context(self.hosts["my_laptop"]) as c:
                c.pretend = args.pretend
                run(c)
        except TransactionError as e:
            print(f"[1;31merror:[m {str(e)}")
        except Exception as e:
            print(f"[1;31merror:[m {str(e)}")
            raise e
