#!/usr/bin/env python

VERSION = '0.3.0'

import ConfigParser as configparser
from docopt import docopt
import json
import os.path as path
import requests
import sys

urljoin = path.join

ACTION_ADD      = "add"
ACTION_REG      = "register"
ACTION_LS       = "ls"
ACTION_EDIT     = "edit"
ACTION_SEARCH   = "search"
ACTIONS = [
    ACTION_ADD,
    ACTION_REG,
    ACTION_LS,
    ACTION_EDIT,
    ACTION_SEARCH,
]

USAGE = """\
This is clone of todo.txt command line wrapper, but way better

Usage:
    %(FILE)s %(REG)s [options]
    %(FILE)s %(ADD)s <note> [options]
    %(FILE)s %(LS)s [options]
    %(FILE)s %(SEARCH)s [options]
    %(FILE)s %(EDIT)s <id> [options]

Options:
    -h  --help      Show this screen.
    -v  --version   Show version
    --config FILE   Path to config [Default: ~/.notes]
    --server URL    Server to work with [Default: http://note.snoopt.ru]
    --token TOKEN   Existing token
""" % dict(
    FILE    = __file__,
    ADD     = ACTION_ADD,
    LS      = ACTION_LS,
    EDIT    = ACTION_EDIT,
    REG     = ACTION_REG,
    SEARCH  = ACTION_SEARCH,
)

class ConfigError(Exception):
    pass

class NoConfigError(ConfigError):
    pass

class Config(object):
    CONFIG_SECTION = "Main"

    def __init__(self, filename, server, token):
        self.filename = path.expanduser(filename)
        self.server = server
        self.token = token

    def create(self):
        if path.exists(self.filename):
            raise ConfigError("Config [%s] already exists" % self.filename)

        if self.token is None:
            self.token = self.get_new_token()

        config = configparser.RawConfigParser()
        config.add_section(self.CONFIG_SECTION)
        config.set(self.CONFIG_SECTION, "server", self.server)
        config.set(self.CONFIG_SECTION, "token", self.token)

        with open(self.filename, 'w') as fp:
            config.write(fp)

    def get_new_token(self):
        url = urljoin(self.server, "generate_key")
        req = requests.get(url)
        data = json.loads(req.text)
        return data["token"]

    def load(self):
        if not path.exists(self.filename):
            raise NoConfigError("Config [%s] not found" % self.filename)

        config = configparser.RawConfigParser()
        config.read(self.filename)
        self.server = config.get(self.CONFIG_SECTION, "server")
        self.token = config.get(self.CONFIG_SECTION, "token")



class ActionManager(object):
    def __init__(self, config, args):
        self.config = config
        self.args = args

    def get_action(self):
        for action in ACTIONS:
            if self.args.get(action, None):
                return action
        return None


    def manage(self):
        action_map = {
            ACTION_REG:  self.register,
            ACTION_ADD: self.add,
            ACTION_LS: self.ls,
            ACTION_EDIT: self.edit,
            ACTION_SEARCH: self.search,
        }

        action = self.get_action()
        action_method = action_map[action]

        try:
            action_method()
        except Exception, e: # FIXME
            print e
            return 1

        return 0

    def add(self):
        url = urljoin(self.config.server, 'add')
        params = {"AUTH-TOKEN": self.config.token}
        requests.put(url, params = params)

    def edit(self):
        pass

    def ls(self):
        pass

    def search(self):
        pass

    def register(self):
        self.config.create()


if __name__ == "__main__":
    args = docopt(USAGE, version = VERSION)
    config = Config(
        args['--config'],
        args['--server'],
        args['--token'],
    )
    manager = ActionManager(config, args)
    sys.exit(manager.manage())
