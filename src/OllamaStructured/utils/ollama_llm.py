import os, json
from pathlib import Path
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from typing import Self, Annotated
from ollama import Client, ChatResponse
from pydantic import BaseModel
from json.decoder import JSONDecodeError
from .prompts import BASE_INSTRUCTION, STRUCTURED_OUTPUT_INSTRUCTION, RECOVER_OUTPUT_INSTRUCTION

class OllamaLLM:

    def __init__(self, client: Client, model: str = 'gpt-oss:20b-cloud', instruction: str = BASE_INSTRUCTION, track_chat_history: bool = False) -> None:
        self.__client = client
        self.model = model
        self.__instruction = instruction
        self.__messages = [
            {
                'role': 'system',
                'content': self.__instruction
            }
        ]
        self.__track_chat_history = track_chat_history

    @property
    def client(self) -> Client:
        return self.__client

    @classmethod
    def connect_to_ollama_cloud(cls, ollama_api_key: str | None = None, model: str = 'gpt-oss:20b-cloud', instruction: str = BASE_INSTRUCTION, track_chat_history: bool = False) -> Self:
        key_to_use = ollama_api_key or os.getenv("OLLAMA_API_KEY")
        if not key_to_use:
            raise ValueError("'OLLAMA_API_KEY' environment variable not found")
        client = Client(
            host='https://ollama.com',
            headers={'Authorization': 'Bearer '+key_to_use})
        return cls(client, model, instruction, track_chat_history)

    @classmethod
    def connect_to_local_ollama(cls, host: str, model: str, instruction: str = BASE_INSTRUCTION, track_chat_history: bool = False) -> Self:
        client = Client(host=host)
        return cls(client, model, instruction, track_chat_history)

    def structured_output_recover(self, prompt: str, schema: BaseModel, **chat_kwargs) -> BaseModel:
        messages = [
            {
                'role': 'system',
                'content': RECOVER_OUTPUT_INSTRUCTION.replace("<PYDANTIC_SCHEMA>", json.dumps(schema.model_json_schema()))
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        response = self.client.chat(
            model=self.model,
            messages=messages,
            **chat_kwargs
        )
        content = response.message.content
        content = json.loads(content)
        return schema(**content)
        

    def _ask(self, prompt: str, img: Annotated[str, 'Path of the image'] | bytes | None = None, **chat_kwargs) -> ChatResponse:
        _message = {
                'role': 'user',
                'content': prompt
            }
        if img:
            _message['images'] = [img]
        self.__messages.append(
            _message
        )
        response = self.client.chat(
            model=self.model,
            messages=self.__messages,
            **chat_kwargs
        )
        if self.__track_chat_history:
            self.__messages.append(
                {
                    'role': 'assistant',
                    'content': response.message.content
                }
        )
        else:
            self.__messages.pop()
        return response

    def ask(self, prompt: str, img: Annotated[str, 'Path of the image'] | bytes | None = None, **chat_kwargs) -> str:
        return self._ask(prompt, img, **chat_kwargs).message.content

    @retry(
        sleep=1,
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(JSONDecodeError),
        before_sleep= lambda x: self.structured_output_recover(prompt, schema, **chat_kwargs)
    )
    def ask_w_structured_output(self, prompt: str, schema: BaseModel, img: Annotated[str, 'Path of the image']| bytes | None = None, **chat_kwargs) -> BaseModel:
        structured_output_instruction = self.__instruction + "\n" + STRUCTURED_OUTPUT_INSTRUCTION.replace("<PYDANTIC_SCHEMA>", json.dumps(schema.model_json_schema()))
        self.__messages[0]['content'] = structured_output_instruction
        resp = self._ask(prompt, img, **chat_kwargs).message.content
        resp = json.loads(resp)
        return schema(**resp)
