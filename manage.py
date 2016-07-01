#!/usr/bin/env python
import os
import sys
from subprocess import Popen


def port_free(port=5006):
    import socket;
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    return result != 0;

if __name__ == "__main__":
    server = None
    if 'runserver' in sys.argv and port_free():
        server = Popen(['bokeh', 'serve',
                        '--allow-websocket-origin=localhost:8000',
                        '--allow-websocket-origin=127.0.0.1:8000']
                       )
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MeasMan.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
    if server:
        server.terminate()
