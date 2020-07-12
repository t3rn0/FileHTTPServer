# FileHTTPServer
simple async file http server

#### usage
$ python3 file_server.py

#### defaults
port: 8000
storage folder: ./storage
storage limit: 10 ** 9
logs to: stdout & stderr

#### tests
$ python3 -m unittest tests/test.py

#### logs to file
$ python3 -u file_server.py &> logfile

#### arguments (port, storage limit)
$ python3 file_server.py 8001 --limit 1024
