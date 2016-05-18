#!/usr/bin/env python

from __future__ import print_function           # why? Read here : http://python3porting.com/noconv.html
import copy                                     # read here : https://docs.python.org/2/library/copy.html
import traceback                                # read : https://docs.python.org/2/library/traceback.html
import sqlite3                                  # read : https://docs.python.org/2/library/sqlite3.html
import logging                                  # read : https://docs.python.org/2/library/logging.html
import os                                       # read : https://docs.python.org/2/library/os.html
import functools                                # read : https://docs.python.org/2/library/functools.html
import re                                       # read : https://docs.python.org/2/library/re.html
import sys                                      # read : https://docs.python.org/2/library/sys.html
import importlib
import ipdb
import time
from glob import glob


from .server import CharmanderServer
from .dummyserver import DummyServer

from slackrtm import SlackClient
from slackrtm.server import SlackConnectionError, SlackLoginError


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DIR = functools.partial(os.path.join,CURRENT_DIR)

PYTHON_3 = sys.version_info[0] > 2

logger = logging.getLogger(__name__)

SLACK_TOKEN = ''

class InvalidExtensionDir(Exception):
    def __int__(self, extensiondir):
        '''
        :param extensiondir:  check if the extension directory is valid
        :return:
        '''
        message = "Unable to find extension directory {0}".format(extensiondir)
        super(InvalidExtensionDir, self).__init__(message)


def init_log(config):
    '''
    :param config: log configuration
    :return:
    '''
    loglevel = config.get("loglevel", logging.INFO)
    logformat = config.get("logformat", '%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    if config.get("logfile"):
        logging.basicConfig(filename=config.get("logfile"), format=logformat, level=loglevel)
    else:
        logging.basicConfig(format=logformat, level=loglevel)


def init_extensions(extensiondir):
    '''
    :param extensiondir: get all the extensions (python files) also check for errors
    :return:
    '''
    if extensiondir and not os.path.isdir(extensiondir):
        raise InvalidExtensionDir(extensiondir)

    if not extensiondir:
        extensiondir = DIR("extensions")

    logger.debug("externsiondir: {0}".format(extensiondir))

    if os.path.isdir(extensiondir):
        extensionfiles = glob(os.path.join(extensiondir, "[!_]*.py"))
        extensions = strip_extension(os.path.basename(e) for e in extensionfiles )
    else:

        logger.debug("trying to get pkg_resources")
        import pkg_resources
        try:
            extensions = strip_extension(
                pkg_resources.resource_listdir(__name__, "extensions"))
        except OSError:
            raise InvalidExtensionDir(extensiondir)

    hooks = {}

    old_path = copy.deepcopy(sys.path)
    sys.path.insert(0,extensiondir)

    for extension in extensions:
        logger.debug("extension: {0}".format(extension))
        try:
            mod = importlib.import_module(extension)
            modname = mod.__name__
            for hook in re.findall("on_(\w+)"," ".join(dir(mod))):
                hook_fun = getattr(mod, "on_"+hook)
                logger.debug("extension : attching %s hook for %s ", hook, modname)
                hooks.setdefault(hook, []).append(hook_fun)

            if mod.__doc__:
                firstline = mod.__doc__.split('\n')[0]
                hooks.setdefault('help', {})[modname] = firstline
                hooks.setdefault('extension Help', {})[modname] = mod.__doc__
        # we will have exntensions , they can have any number of errors
        # we have to make sure that they don't affect our servers
        except:
            logger.warning("import failed on module {0}, module not loaded".format(extension))
            logger.warning("{0}".format(sys.exc_info()[0]))
            logger.warning("{0}".format(traceback.format_exc()))

    sys.path = old_path
    return hooks


def strip_extension(list):
    '''
    :param list: Get list and strip the list
    :return:
    '''
    return (os.path.splitext(l)[0] for l in list)


def run_hook(hooks, hook, *args):
    '''
    :param hooks: Get hooks and loop through it
    :param hook:
    :param args:
    :return: return responses
    '''
    responses = []
    for hook in hooks.get(hook, []):
        try:
            h = hook(*args)
            if h:
                responses.append(h)
        except:
            logger.warning("Failed to run the extension {0}, module not loaded".format(hook))
            logger.warning("{0}".format(sys.exc_info()[0]))
            logger.warning("{0}".format(traceback.format_exc()))

    return responses


def handle_bot_message(event, server):
    '''
    :param event: Handle bot events
    :param server:
    :return:
    '''
    try:
        bot = server.slack.server.bots[event["bot_id"]]
    except KeyError:
        logger.debug('bot_meesage event {0} has no bot'.format(event))
        return
    return "\n".join(run_hook(server.hooks, "bot_message", event, server))


def handle_message(event, server):
    # Bot message handling
    subtype = event.get("subtype", "")
    if subtype == "message_changed":
        return

    if subtype == "bot_message":
        return handle_bot_message(event, server)

    try:
        msg_user = server.slack.server.users[event["user"]]
    except KeyError:
        logger.debug("event {0} has no user".format(event))
        return

    return "\n".join(run_hook(server.hooks, "message", event, server))

event_handlers = {
    "message": handle_message,
}


def handle_event(event, server):
    # Event Handling
    handler = event_handlers.get(event.get("type"))
    if handler:
        return handler(event, server)


def getif(config, name, envvar):
    if envvar in os.environ:
        config[name] = os.environ.get(envvar)


def init_config():
    # get and initialize all the configurations
    config = {}
    getif(config, "token", "SLACK_TOKEN")
    getif(config, "loglevel", "CHARMANDER_LOGLEVEL")
    getif(config, "logfile", "CHARMANDER_LOGFILE")
    getif(config, "logformat", "CHARMANDER_LOGFORMAT")
    return config


def loop(server , test_loop=None):
    """
    :param server: is a charmander server object
    :param test_loop: is the number of times to run the loop
    :return:
    """
    try:
        loop_without_activity = 0
        while test_loop is None or test_loop > 0:
            start = time.time()
            loop_without_activity += 1

            events = server.slack.rtm_read()
            for event in events:
                loop_without_activity = 0
                logger.debug("got {0}".format(event.get("type", event)))
                response = handle_event(event, server)
                if response:
                    server.slack.rtm_send_message(event["channel"], response)

            # Server.slack.post_message to send messages from a loop hook
            run_hook(server.hooks, "loop", server)
            # The Slack RTM API docs say:
            #
            # > When there is no other activity clients should send a ping
            # > every few seconds
            #
            # So, if we've gone >5 seconds without any activity, send a ping.
            # If the connection has broken, this will reveal it so slack can
            # quit
            if loop_without_activity > 5:
                server.slack.server.ping()
                loop_without_activity = 0

            end = time.time()
            runtime = start - end
            time.sleep(max(1-runtime, 0))

            if test_loop:
                test_loop -= 1
    except KeyboardInterrupt:
        if os.environ.get("CHARMANDER_DEBUG"):
            import ipdb; ipdb.set_trace()
        raise


def relevant_environ():
    return dict((key, os.environ[key])
                for key in os.environ
                if key.startswith("SLACK") or key.startswith("CHARMANDER"))


def init_server(args, config, Server=CharmanderServer, Client=SlackClient):
    # Initialize Server using SlackClient

    init_log(config)
    logger.debug("config: {0}".format(config))
    db = init_db(args.database_name)
    hooks = init_extensions(args.extensionpath)
    try:
        slack = Client(SLACK_TOKEN)
    except KeyError:
        logger.error(""" Charmander is unable to find a slack token. The environment variables charmander sees are:
        {0} and the current config is: {1}
        """.format(relevant_environ(), config))
        raise
    server = Server(slack, config, hooks, db)
    return server


def decode(str_, codec='utf-8'):
    # Decode string
    if PYTHON_3:
        return str_
    else:
        return str_.decode(codec)


def encode(str_, codec='utf-8'):
    # encode string
    if PYTHON_3:
        return str_
    else:
        return str_.encode(codec)


def main(args):
    config = init_config()
    if args.test:
        init_log(config)
        return repl(DummyServer(), args)
    elif args.command is not None:
        init_log(config)
        cmd = decode(args.command)
        print(run_cmd(cmd, DummyServer(), args.hook, args.extensionpath))

    server = init_server(args, config)

    try:
        server.slack.rtm_connect()

        run_hook(server.hooks, "init", server)

        loop(server)
    except SlackConnectionError:
        logger.warn("Unable to connect to slack. Bad Gateway? :( ")
        raise
    except SlackLoginError:
        logger.warn("Login Failed, invalid token <{0}>".format(config["token"]))


def run_cmd(cmd, server, hook, extennsionpath):
    # command line handling
    server.hooks = init_extensions(extennsionpath)
    event = {'type': hook, 'text': cmd, "user": "2", "ts": time.time(), "team": None, "channel": "repl_channel"}
    return encode(handle_event(event, server))


try:
    input = raw_input
except NameError:
    pass


def repl(server, args):
    try:
        while 1:
            cmd = decode(input("charmander> "))
            if cmd.lower() == "quit" or cmd.lower() == "exit":
                return

            print(run_cmd(cmd, server, args.hook, args.extensionpath))
    except (EOFError, KeyboardInterrupt):
        print()
        pass


def init_db(database_file):
    # initialize db
    return sqlite3.connect(database_file)