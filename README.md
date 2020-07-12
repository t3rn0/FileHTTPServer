# FileHTTPServer
simple async file http server

#### usage
```
$ python3 file_server.py
$ curl -XPOST "http://host:port/upload" -F "=@path_to_local_file"
Succeeded: to download file use following file id
900fc0cc7f2748a68cc3bc0f6aed1380
http://<HOST>:<PORT>/download/900fc0cc7f2748a68cc3bc0f6aed1380
$ curl -XGET "http://host:port/download/900fc0cc7f2748a68cc3bc0f6aed1380" > new_file
```

#### defaults
- port: 8000
- storage folder: ./storage
- storage limit: 10 ** 9
- logs to: stdout & stderr

#### tests
```
$ python3 -m unittest tests/test.py
```

#### logs to file
```
$ python3 -u file_server.py &> logfile
```

#### arguments (port, storage limit)
```
$ python3 file_server.py 8001 --limit 1024
```
