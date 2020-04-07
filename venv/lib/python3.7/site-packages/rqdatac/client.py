# -*- coding: utf-8 -*-
import os
import warnings
import logging

from six.moves.urllib.parse import unquote, urlparse
from six import string_types

import socks
import socket

import rqdatac


if getattr(os, "register_at_fork", None):

    def _close_after_fork():
        global _CLIENT
        if _CLIENT is not _DUMMY and _CLIENT.PID != os.getpid():
            reset()

    os.register_at_fork(after_in_child=_close_after_fork)


class DummyClient:
    PID = -1

    def execute(self, *args, **kwargs):
        raise RuntimeError("rqdatac is not initialized")

    def reset(self):
        pass

    def close(self):
        pass

    execute_with_timeout = execute


_DUMMY = DummyClient()

_CLIENT = _DUMMY


def reset():
    """reset all collection to a server.
    this function is helpful when you fork a inited client
    """
    _CLIENT.reset()
    _CLIENT.PID = os.getpid()


def init(username=None, password=None, addr=("rqdatad-pro.ricequant.com", 16011), *_, **kwargs):
    """init to a remote server

    rqdatac connection is thread safe but not fork safe. Every thread have their own connection by
    default. you can set param 'use_pool' to True to use a socket pool instead.
    you can call function rqdatac.reset() to close all socket in child process. This behavior is
    auto called with python version equal or greater than 3.7 by os.register_at_fork.

    :param username: string
    :param password: string
    :param addr: ('127.0.0.1', 80) or '127.0.0.1:80'
    :param uri: rqdata://username:password@host:port or tcp://username:password@host:port
                you can set this value in environment with key 'RQDATAC2_CONF' or 'RQDATAC_CONF'
                username, password, or addr with override the uri setting.

    :param connect_timeout: socket connect connect timeout, default is 5 sec.
    :param timeout: socket time out, default is 60 sec.
    :param lazy: lazy request, if set this to True, you will immediately request rqdatad server.
                 set this to True if you wan't connection error raise in this function.
                 default is False.
    :param use_pool: use connection pool. default is False
    :param max_pool_size: max pool size, default is 8
    :param proxy_info: a tuple like (proxy_type, host, port, user, password) if use proxy, default is None

    """
    extra_args = {}
    uri = kwargs.pop("uri", None)
    use_pool = kwargs.pop("use_pool", False)
    connect_timeout = kwargs.pop("connect_timeout", None)
    if connect_timeout is not None:
        extra_args["connect_timeout"] = connect_timeout
    timeout = kwargs.pop("timeout", None)
    if timeout is not None:
        extra_args["timeout"] = connect_timeout
    max_pool_size = kwargs.pop("max_pool_size", None)
    if max_pool_size is not None and use_pool:
        extra_args["max_pool_size"] = max_pool_size
    proxy_info = kwargs.pop("proxy_info", None)
    if proxy_info is not None:
        if not isinstance(proxy_info, tuple) or len(proxy_info) != 5:
            raise ValueError("expected a tuple like (proxy_type, host, port, user, password)")
        proxy_type, proxy_host, proxy_port, proxy_user, proxy_password = proxy_info
        if proxy_type.upper() == "HTTP":
            proxy_type = socks.PROXY_TYPE_HTTP
        elif proxy_type.upper() == "SOCKS4":
            proxy_type = socks.PROXY_TYPE_SOCKS4
        elif proxy_type.upper() == "SOCKS5":
            proxy_type = socks.PROXY_TYPE_SOCKS5
        else:
            raise ValueError("proxy_type {} not supported".format(proxy_type))
        socks.set_default_proxy(proxy_type=proxy_type, addr=proxy_host, port=proxy_port,
                                username=proxy_user, password=proxy_password)
        socket.socket = socks.socksocket

    debug = kwargs.pop("debug", None)
    strict = kwargs.pop("strict", None)
    global _CLIENT
    if debug:
        logging.getLogger("rqdata").disabled = False
    else:
        logging.getLogger("rqdata").disabled = True

    if strict:
        _CLIENT = StrictClient()
        _CLIENT.PID = os.getpid()
        return

    if _CLIENT is not _DUMMY:
        reset()
        warn_reinit = True
    else:
        warn_reinit = False

    if not (username or password or uri):
        uri = os.environ.get("RQDATAC2_CONF") or os.environ.get("RQDATAC_CONF")

    if username and password and addr:
        scheme = "tcp"
        addr = parse_address(addr)
    elif uri:
        r = urlparse(unquote(uri))
        scheme = "tcp" if r.scheme == "rqdata" or r.scheme == "rqdatac" else r.scheme
        username = username or r.username
        password = password or r.password
        addr = parse_address((r.hostname, r.port))
    else:
        raise ValueError("username/password/addr or uri expected")

    if scheme == "tcp":
        if use_pool:
            from .connection_pool import ConnectionPool

            _CLIENT = ConnectionPool(
                addr,
                auth={"username": username, "password": password, "ver": rqdatac.__version__},
                **extra_args
            )
        else:
            from .thread_local import ThreadLocalConnection

            _CLIENT = ThreadLocalConnection(
                addr,
                auth={"username": username, "password": password, "ver": rqdatac.__version__},
                **extra_args
            )
    elif scheme == "http":
        raise NotImplementedError()
    else:
        raise ValueError("got unexpected schema %s" % scheme)

    _CLIENT.PID = os.getpid()

    if username == "license":
        quota = get_client().execute("user.get_quota")
        remaining_days = quota["remaining_days"]
        is_trial = quota["license_type"] == "TRIAL"
        if is_trial or 0 <= remaining_days <= 14:
            warnings.warn("Your account will be expired after  {} days. "
                          "Please call us at 0755-22676337 to upgrade or purchase or "
                          "renew your contract.".format(remaining_days))
    elif not kwargs.get("lazy", True):
        get_client().execute("get_all_trading_dates")

    if warn_reinit:
        warnings.warn("rqdatac is already inited. Settings will be changed.", stacklevel=0)
    return


class StrictClient:
    def __init__(self):
        import rqdatad.core.app
        import rqdatad.__main__
        import rqdatad.database

        app = rqdatad.core.app.app
        app.config = rqdatad.__main__.default_config_file()
        app.init()
        rqdatad.database.set_database_config(app.config)

        self.app = app

    def execute(self, api_name, *args, **kwargs):
        return self.app.debug_api(api_name, *args, **kwargs)

    def execute_with_timeout(self, timeout, api_name, *args, **kwargs):
        return self.execute(api_name, *args, **kwargs)

    def close(self):
        import asyncio

        loop = self.app.get_event_loop()
        loop.stop()
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.close()

    reset = close


def get_client():
    if _CLIENT.PID != os.getpid():
        reset()
    return _CLIENT


def parse_address(address):
    if isinstance(address, tuple):
        host, port = address
        return host, int(port)
    elif isinstance(address, string_types):
        if ":" not in address:
            return address
        host, port = address.rsplit(":", 1)
        return host, int(port)
    else:
        raise ValueError("address must be a str or tuple")
