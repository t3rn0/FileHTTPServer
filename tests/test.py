import file_server
from .multipart import MultiPartForm
import unittest
import threading
import os
import urllib.request
import time
import socket
import shutil


HOST = '127.0.0.1'
PORT = file_server.PORT
base_url = f'http://{HOST}:{PORT}'
file_server.STORAGE = storage = 'tests/test_storage/'


def is_available(host: str = HOST, port: int = PORT) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex((host, port))
    return res == 0


def _set_up(host: str = HOST, port: int = PORT, timeout: int = 10) -> None:
    daemon = threading.Thread(
        name='daemon_server',
        target=file_server.run
    )
    daemon.setDaemon(True)
    daemon.start()
    while not is_available() and timeout > 0:
        timeout -= 1
        time.sleep(1)
        return
    raise ConnectionError("can not set up server")


class Test(unittest.TestCase):
    _set_up()

    @classmethod
    def setUpClass(cls):
        try:
            os.mkdir(storage)
        except FileExistsError:
            pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(storage)

    # wrong GET request (E_URL_NOT_FOUND)
    def test_get_1(self):
        req = urllib.request.Request(base_url)
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertEqual(context.exception.code, 400)

    # wrong GET request (E_FILE_NOT_FOUND)
    def test_get_2(self):
        req = urllib.request.Request(f'{base_url}/download/')
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertEqual(context.exception.code, 400)

    # wrong GET request (E_FILE_NOT_SPECIFIED)
    def test_get_3(self):
        req = urllib.request.Request(f'{base_url}/download/some_file')
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertEqual(context.exception.code, 400)

    # wrong POST request (E_URL_NOT_FOUND)
    def test_post_1(self):
        data = urllib.parse.urlencode({}).encode()
        req = urllib.request.Request(f'{base_url}/', data=data)
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertEqual(context.exception.code, 400)

    # wrong POST request (E_CONTENT_TYPE)
    def test_post_2(self):
        data = urllib.parse.urlencode({}).encode()
        req = urllib.request.Request(f'{base_url}/upload', data=data)
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertEqual(context.exception.code, 400)

    # wrong POST request (E_NOT_ENOUGH_SPACE)
    def test_post_3(self):
        try:
            _temp_storage_limit = file_server.STORAGE_LIMIT
            file_server.STORAGE_LIMIT = 1024

            form = MultiPartForm()
            big_file = 'tests/test_sample'
            with open(big_file, 'rb') as f:
                form.add_file('some_file', big_file, fileHandle=f)
            data = bytes(form)
            req = urllib.request.Request(f'{base_url}/upload', data=data)
            req.add_header('content-type', form.get_content_type())
            req.add_header('content-length', len(data))

            with self.assertRaises(urllib.error.HTTPError) as context:
                urllib.request.urlopen(req)
            self.assertEqual(context.exception.code, 500)
        finally:
            file_server.STORAGE_LIMIT = _temp_storage_limit

    # valid post and get requests
    def test_post_and_get_text(self):
        form = MultiPartForm()
        some_file = 'tests/test_sample'
        with open(some_file, 'rb') as f:
            form.add_file('some_file', some_file, fileHandle=f)
        data = bytes(form)
        req = urllib.request.Request(f'{base_url}/upload', data=data)
        req.add_header('content-type', form.get_content_type())
        req.add_header('content-length', len(data))
        resp = urllib.request.urlopen(req)
        self.assertEqual(resp.code, 200)

        file_id = resp.read().decode().splitlines()[1]

        req = urllib.request.Request(f'{base_url}/download/{file_id}')
        resp = urllib.request.urlopen(req)
        with open(some_file, 'rb') as f:
            ref = f.read()
            downloaded = resp.read()
        self.assertEqual(ref, downloaded)

    def test_blocking(self):
        # blocking request
        req1 = urllib.request.Request(f'{base_url}/timeout=3')
        t = threading.Thread(target=urllib.request.urlopen, args=(req1,))
        t.start()

        # # some other request
        req2 = urllib.request.Request(base_url)
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req2)
        self.assertEqual(context.exception.code, 400)

        self.assertEqual(t.is_alive(), True)
        t.join()
