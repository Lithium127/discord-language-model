import json
import typing as t
from random import choice

from .stream import WordStream, MessageStream

from discord import Message


class BaseModel(object):
    
    _models_folder = ".models"
    
    _recursion: int
    _save_path: str
    
    stream: WordStream
    data: t.Optional[dict[str, t.Any]] = None
    
    
    def __init__(self, save_path: str) -> None:
        self._recursion = 3
        self._save_path = save_path
        
        
        if self.data is None:
            self._init_data()
    
    
    
    def _init_data(self) -> None:
        self.data = {}
        self.data = {
            "meta":{
                "recursion":self._recursion
            },
            "reference":{}
        }
    

    def _train(self, stream: WordStream | None = None) -> None:
        
        while not stream.end:
            
            word = stream.next()
            
            try:
                target = self.reference[word]
            except:
                self.reference[word] = {
                    "fallback" : [],
                    "words" : {}
                }
                target = self.reference[word]
            
            target["fallback"].append(stream.peek())
            
            t = self._recursive_add(
                next_word = stream.peek(),
                ref_dict = target["words"],
                stream=stream
            )
            
            if t is not None:
                target["words"] |= t
        
        with open(f"{self._models_folder}/{self._save_path}", "w") as f:
            json.dump(self.data, f, indent=4)
    
    @t.overload
    def train(self, ws: WordStream) -> None:
        self._train(ws)
    
    def train(self, fp: str) -> None:
        ws = WordStream(fp)
        self._train(ws)  
    
    def _recursive_add(self, next_word: str, ref_dict: list | dict, *, current_index: int = 1, stream: WordStream | None = None):
        prev_word = stream.prev(current_index)
        ref_dict |= {prev_word: {}}
        
        if current_index >= self._recursion:
            try:
                ref_dict.append(next_word)
            except:
                ref_dict[prev_word] = []
                ref_dict[prev_word].append(next_word)
            
        else:
            self._recursive_add(
                next_word     = next_word,
                ref_dict      = ref_dict[prev_word],
                current_index = current_index + 1,
                stream        = stream
            )


    
    def generate(self, count: int) -> str:
        data: list = [choice(list(self.reference.keys()))]
        
        selection: str | None
        next_word: str | None = None
        
        for index in range(count):
            target = self.reference[data[index]]
            try:
                for i in range(self._recursion):
                    target = target[data[index-i-1]]
                selection = target
            except KeyError:
                selection = target["fallback"]
            except IndexError:
                selection = target["fallback"]
            
            for _ in range(0,10):
                # try 10 times to select a word
                next_word = choice(selection)
                if next_word is not None:
                    break
            else:
                # choose random word from full dict
                next_word = choice(list(self.reference.keys()))
            data.append(next_word)
        
        return " ".join(data)
    
    def extend(self, data: str, count: int) -> str:
        
        # add context to reference
        self._train(WordStream(data))
        
        
        data = data.split()
        
        selection: str | None
        next_word: str | None = None
        
        for index in range(count):
            target = self.reference[data[index]]
            try:
                for i in range(self._recursion):
                    target = target[data[index-i-1]]
                selection = target
            except KeyError:
                selection = target["fallback"]
            except IndexError:
                selection = target["fallback"]
            
            for _ in range(0,10):
                # try 10 times to select a word
                next_word = choice(selection)
                if next_word is not None:
                    break
            else:
                # choose random word from full dict
                next_word = choice(list(self.reference.keys()))
            data.append(next_word)
        
        return " ".join(data)
    
    
    @property
    def meta(self) -> dict:
        return self.data["meta"]
    
    
    
    @property
    def reference(self) -> dict:
        return self.data["reference"]
    

class DiscordModel(BaseModel):
    
    def __init__(self) -> None:
        super().__init__("lang_bot.json")
    
    def base_training(self, fps: list[str]) -> None:
        for fp in fps:
            try:
                with open(f".training/{fp}", mode="r", encoding="utf8") as f:
                    self._train(WordStream(f.read()))
            except FileNotFoundError:
                pass
    
    def update(self, msg: Message) -> None:
        self._train(WordStream(msg.content))
