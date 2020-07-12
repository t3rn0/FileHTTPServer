from http.server import BaseHTTPRequestHandler, HTTPServer, test
from socketserver import ThreadingMixIn
import os
import uuid

from storage import get_size
from messages import *
import argparse


PORT = 8000

STORAGE = './storage/'
try:
    os.mkdir(STORAGE)
except FileExistsError:
    pass
STORAGE_SIZE = get_size(STORAGE)
STORAGE_LIMIT = 10 ** 9


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class Handler(BaseHTTPRequestHandler):
    MAX_HEADERS = 10

    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # only for testing purposes (/timeout=10)
        # blocking behaviour
        if self.path.startswith('/timeout'):
            import time
            try:
                timeout = int(self.path.split('=')[1])
                time.sleep(timeout)
                self._set_headers(200)
            except:
                self._set_headers(500)
            return

        # accept only GET to http://host:port/download/<file>
        if not self.path.startswith('/download/'):
            msg = E_URL_NOT_FOUND.format(self.path)
            self._set_headers(400)
            self.wfile.write(msg.encode())
            return

        file_name = self.path.split('/download/')[1]
        if file_name == '':
            msg = E_FILE_NOT_SPECIFIED
            self._set_headers(400)
            self.wfile.write(msg.encode())
            return
        if not os.path.isfile(STORAGE + file_name):
            msg = E_FILE_NOT_FOUND.format(file_name)
            self._set_headers(400)
            self.wfile.write(msg.encode())
            return

        self._set_headers(200)
        with open(STORAGE + file_name, 'rb') as f:
            for line in f:
                self.wfile.write(line)
        return

    def do_POST(self):
        # accept only POST to http://host:port/upload
        code, msg = self._post()
        self._set_headers(code)
        self.wfile.write(msg.encode())
        return

    def _post(self):
        global STORAGE_SIZE

        if self.path != '/upload':
            return 400, E_URL_NOT_FOUND + self.path

        rtype = self.headers.get_content_type()
        if rtype != 'multipart/form-data':
            return 400, E_CONTENT_TYPE

        remain_bytes = self.headers.get('content-length')
        if remain_bytes is None:
            return 400, E_HEADERS_CONTENT_LENGTH

        # check if storage is full
        remain_bytes = int(remain_bytes)
        if STORAGE_SIZE + remain_bytes > STORAGE_LIMIT:
            return 500, E_NOT_ENOUGH_SPACE
        boundary = self.headers.get_boundary().encode()
        line = self.rfile.readline()
        if boundary not in line:
            return 400, E_BOUNDARY
        remain_bytes -= len(line)

        headers = []
        while True:
            line = self.rfile.readline()
            remain_bytes -= len(line)
            headers.append(line)
            if line in (b'\r\n', b'', b'\n'):
                break
            if len(headers) > self.MAX_HEADERS:
                return 400, E_HEADERS

        file_id = uuid.uuid4().hex
        filename = STORAGE + file_id
        with open(filename, 'wb') as f:
            prev_line = self.rfile.readline()
            remain_bytes -= len(prev_line)
            while remain_bytes > 0:
                line = self.rfile.readline()
                remain_bytes -= len(line)
                if boundary in line:
                    break
                f.write(prev_line)
                prev_line = line

        file_size = os.path.getsize(filename)

        STORAGE_SIZE += file_size

        if file_size == 0:
            os.remove(filename)
            return 400, W_EMPTY_CONTENT
        msg = ''
        if remain_bytes:
            msg = W_UNRESOLVED_CONTENT
        msg += SUCCEED.format(file_id)
        return 200, msg


def run(HandlerClass=Handler, ServerClass=ThreadedHTTPServer):
    test(HandlerClass, ServerClass, port=PORT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', action='store',
                        default=PORT, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    parser.add_argument('--limit', action='store',
                        default=STORAGE_LIMIT, type=int,
                        nargs='?',
                        help='Specify storage limit in bytes [default: 10**9]')

    args = parser.parse_args()
    PORT = args.port
    STORAGE_LIMIT = args.limit
    run()
