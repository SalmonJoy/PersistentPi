"""One HTTP POST, no redirects/retries. Construct only after separate authorization."""
from urllib.request import Request, build_opener, HTTPRedirectHandler
import threading
import http.client
import time
from ..contracts import canonical
from ..interfaces import decode_json
from .config import DEFAULT


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('M010_REDIRECT_NO_RETRY')


class NativeTransport:
    kind = 'admitted-cloud'

    def __init__(self, credential, admission, authorization=None, opener=None, request_limit=1):
        authorized = ((authorization == 'separately-authorized-operational-probe' and request_limit == 1)
                      or (authorization == 'separately-authorized-feasibility' and request_limit in (48, 72)))
        if not authorized or not admission.get('passed'):
            raise PermissionError('M010_PROBE_NOT_AUTHORIZED')
        if not isinstance(credential, str) or not credential or any(x in credential for x in '\r\n'):
            raise ValueError('M010_CREDENTIAL')
        self._credential = credential
        self._opener = opener
        self.sends = 0
        self.limit = request_limit
        self.lock = threading.Lock()
        self.receipts = {}
        self.last_receipt = None
        self.concurrency = admission.get('concurrency', 0)

    def send(self, payload, identity=None):
        raw = canonical(payload)
        if len(raw) > 16384:
            raise ValueError('M010_REQUEST_BYTES')
        with self.lock:
            if self.sends >= self.limit:
                raise PermissionError('M010_NO_EXTRA_REQUEST')
            self.sends += 1
        request = Request(DEFAULT['planner']['endpoint'], data=raw,
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._credential}, method='POST')
        if self._opener is not None:
            # Injection is for recording HTTP tests, not the live route.
            with self._opener.open(request, timeout=180) as receipt:
                if receipt.status != 200:
                    raise RuntimeError('M010_HTTP_STATUS')
                wire = receipt.read(65537)
                status, request_id = receipt.status, receipt.headers.get('x-request-id')
        else:
            wire, status, request_id = self._post(raw)
        if len(wire) > 65536:
            raise ValueError('M010_RESPONSE_BYTES')
        if self._credential.encode() in wire:
            raise ValueError('M010_SECRET_RESPONSE_QUARANTINED')
        try:
            text = wire.decode('utf-8')
            metadata = {'status': status, 'wire': text, 'request_id': request_id}
        except UnicodeDecodeError:
            metadata = {'status': status, 'wire_hex': wire.hex(), 'request_id': request_id}
        with self.lock:
            self.last_receipt = metadata
            if identity is not None:
                self.receipts[identity['request_id']] = metadata
        result = decode_json(wire.decode('utf-8'))
        if not isinstance(result, dict):
            raise ValueError('M010_PROVIDER_RESPONSE')
        if identity is not None:
            return result
        return result, metadata

    def _post(self, raw):
        connection = http.client.HTTPSConnection('ollama.com', timeout=180)
        began = time.monotonic()
        try:
            connection.connect()
            wire = connection.sock
            def remaining():
                left = 180 - (time.monotonic() - began)
                if left <= 0:
                    raise TimeoutError('M010_ABSOLUTE_DEADLINE')
                wire.settimeout(left)
            remaining()
            connection.request('POST', '/api/chat', raw,
                {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._credential})
            remaining()
            response = connection.getresponse()
            self.last_receipt = {'status': response.status, 'request_id': response.getheader('x-request-id'),
                                 'body_not_read': True}
            if response.status != 200:
                raise RuntimeError('M010_HTTP_STATUS_NO_RETRY')
            chunks, size = [], 0
            while size <= 65536:
                remaining()
                chunk = response.read1(65537 - size)
                if not chunk:
                    break
                chunks.append(chunk); size += len(chunk)
            return b''.join(chunks), response.status, response.getheader('x-request-id')
        finally:
            connection.close()
