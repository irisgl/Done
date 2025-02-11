# html_utils.py

import os

def serve_html(start_response, file_path='./static/client.htm'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            response_body = file.read()
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]
    except IOError:
        status = '404 Not Found'
        response_body = "File not found.".encode('utf-8')
        response_headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]
