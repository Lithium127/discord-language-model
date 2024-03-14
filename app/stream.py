from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from discord import Message

import unicodedata as ud
import re


class WordStream(object):
    _index: int
    
    _content: list[str]
    _raw: str
    
    _wordcount: int
    
    
    def __init__(self, content: str) -> None:
        self._raw = content
        self._raw = re.sub(r'[^\x00-\x7f]', r'', self._raw)
        self._raw = ud.normalize('NFC', self._raw)
        
        self._content = self._raw.split()
        self._wordcount = len(self._content)
        self._index = -1
    
    @classmethod
    def from_file(cls: WordStream, fp: str) -> WordStream:
        with open(fp, "r") as f:
            content = f.read()
            
        return cls(content)
        
    def next(self) -> str | None:
        if self.end:
            return None
        
        self._index += 1
        return self.content[self._index].lower()
    
    def peek(self, dist: int = 1) -> str | None:
        pos = self._index + dist
        
        if pos >= self._wordcount:
            return None
        
        return self.content[pos].lower()
    
    def prev(self, dist: int = 1) -> str | None:
        pos = self._index - dist
        
        if pos < 0:
            return None
        
        return self.content[pos].lower()
    
    
    
    @property
    def content(self) -> list[str]:
        return self._content
    
    @property
    def end(self) -> bool:
        return self._index >= self._wordcount - 1

    @property
    def word_count(self) -> int:
        return self._wordcount



class Singleton(type):
    """Allows for any class that uses this class as a metaclass to reference the same instace
    from multiple locations
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MessageStream(metaclass = Singleton):
    
    mesages: list[Message] = []
    
    def __init__(self):
        pass
    
    def add_message(self, msg: Message):
        self.mesages.append(msg)
    
    def next_message(self) -> WordStream:
        return WordStream(self.mesages.pop(0).content)

    
    
    
    
