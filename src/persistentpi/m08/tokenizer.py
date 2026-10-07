"""Read the installed frozen GGUF tokenizer; ASCII Qwen2 byte-BPE counting.

The experiment uses ASCII authored prompts/repairs. Non-ASCII is rejected rather
than silently substituting a different Unicode pre-tokenizer.
"""
import hashlib
import json
from pathlib import Path
import re
import struct

from ..contracts import digest

PRE = re.compile(r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\nA-Za-z0-9]?[A-Za-z]+|[0-9]| ?[^\sA-Za-z0-9]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+")


def metadata(path):
    with Path(path).open('rb') as stream:
        def number(fmt):
            return struct.unpack('<' + fmt, stream.read(struct.calcsize(fmt)))[0]
        def string():
            return stream.read(number('Q')).decode('utf-8')
        def value(kind):
            formats = {0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
            if kind in formats:
                return number(formats[kind])
            if kind == 8:
                return string()
            if kind == 9:
                element, length = number('I'), number('Q')
                return [value(element) for _ in range(length)]
            raise ValueError('Unsupported GGUF metadata type')
        if stream.read(4) != b'GGUF' or number('I') not in (2,3):
            raise ValueError('Unsupported GGUF')
        number('Q')
        result = {}
        for _ in range(number('Q')):
            key = string()
            result[key] = value(number('I'))
        return result


class FrozenTokenizer:
    def __init__(self, info, identity):
        if info.get('tokenizer.ggml.pre') != 'qwen2' or info.get('tokenizer.ggml.model') != 'gpt2':
            raise ValueError('Expected frozen Qwen2 GPT2 byte-BPE tokenizer')
        self.identity = identity
        self.tokens = set(info['tokenizer.ggml.tokens'])
        self.ranks = {tuple(m.split(' ')): i for i, m in enumerate(info['tokenizer.ggml.merges'])}
        bs = list(range(33,127)) + list(range(161,173)) + list(range(174,256))
        cs, extra = bs[:], 0
        for byte in range(256):
            if byte not in bs:
                bs.append(byte)
                cs.append(256 + extra)
                extra += 1
        self.bytes = dict(zip(bs, map(chr,cs)))
        self.cache = {}

    @classmethod
    def installed(cls, model_config, directory=None):
        directory = Path(directory or Path.home() / '.ollama/models')
        manifest = directory / 'manifests/registry.ollama.ai/library/qwen2.5-coder/1.5b'
        raw = manifest.read_bytes()
        if hashlib.sha256(raw).hexdigest() != model_config['expected_digest']:
            raise ValueError('Installed model manifest differs from M0.7 digest')
        data = json.loads(raw)
        layer = next(x for x in data['layers'] if x['mediaType'] == 'application/vnd.ollama.image.model')
        blob = directory / 'blobs' / layer['digest'].replace(':','-')
        hasher = hashlib.sha256()
        with blob.open('rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                hasher.update(block)
        if 'sha256:' + hasher.hexdigest() != layer['digest']:
            raise ValueError('GGUF model blob checksum mismatch')
        info = metadata(blob)
        subset = {k:v for k,v in info.items() if k.startswith('tokenizer.')}
        return cls(info, {'version':1, 'model_digest':model_config['expected_digest'],
                         'blob_digest':layer['digest'], 'tokenizer_hash':digest(subset),
                         'pretokenizer':'qwen2-ascii-1', 'gguf_pre':info['tokenizer.ggml.pre']})

    def count(self, text):
        if not text.isascii():
            raise ValueError('Frozen ASCII tokenizer cannot certify non-ASCII text')
        count = 0
        for match in PRE.finditer(text):
            piece = ''.join(self.bytes[b] for b in match.group().encode())
            if piece not in self.cache:
                parts = list(piece)
                while len(parts) > 1:
                    pairs = [(self.ranks.get((parts[i],parts[i+1]),float('inf')),i) for i in range(len(parts)-1)]
                    rank, index = min(pairs)
                    if rank == float('inf'):
                        break
                    parts[index:index+2] = [parts[index]+parts[index+1]]
                if any(part not in self.tokens for part in parts):
                    raise ValueError('Unrecognized byte-BPE token')
                self.cache[piece] = len(parts)
            count += self.cache[piece]
        return count

    def prompt_upper_bound(self, messages):
        # Qwen's frozen chat-template framing is bounded separately from content.
        return sum(self.count(m['content']) for m in messages) + 256
