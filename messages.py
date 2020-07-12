"""user messages"""

SUCCEED = 'Succeeded: to download file use following file id\n{0}\nhttp://<HOST>:<PORT>/download/{0}\n'
W_EMPTY_CONTENT = 'Empty file\n'
W_UNRESOLVED_CONTENT = 'It seems that you passed more that one file in form-data\n'
E_URL_NOT_FOUND = 'Url not found: {}\n'
E_HEADERS = 'Too many headers\n'
E_HEADERS_CONTENT_LENGTH = 'Can not find content-length header\n'
E_BOUNDARY = 'Content does not begin with boundary\n'
E_CONTENT_TYPE = 'Request type must be multipart/form-data\n'
E_NOT_ENOUGH_SPACE = 'Not enough space left in storage\n'
E_FILE_NOT_FOUND = 'File not found: {}\n'
E_FILE_NOT_SPECIFIED = 'Specify file in "/download/<file>"\n'
