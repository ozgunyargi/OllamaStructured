from tenacity.retry import retry_if_exception_type
from os import stat
import os, json
from pathlib import Path
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from copy import deepcopy

from typing import Self, Annotated
from ollama import Client, ChatResponse
from pydantic import BaseModel, ValidationError
from json.decoder import JSONDecodeError

from .prompts import BASE_INSTRUCTION, STRUCTURED_OUTPUT_INSTRUCTION, RECOVER_OUTPUT_INSTRUCTION
from .exceptions import OllamaLLMStructuredOutputException

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
        self.__last_response = None
        self.__recover_exceptions = {
            JSONDecodeError: "Unable to create a valid python dictionary from the response since 'json.loads()' has been failed due 'JSONDecodeError' exception.",
            ValidationError: "Unable to validate response dict due 'pydantic.ValidationError' exception."
        }

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

    @staticmethod
    def __prepare_user_message(prompt: str, img: Annotated[str, 'Path of the image'] | bytes | None = None) -> dict:
        _message = {
                'role': 'user',
                'content': prompt
            }
        if img:
            _message['images'] = [img]
        return _message

    @retry(
        stop = stop_after_attempt(3),
        reraise=True,
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry = retry_if_exception_type((
            JSONDecodeError,
            ValidationError
        )),
        retry_error_cls=OllamaLLMStructuredOutputException
    )
    def __structured_output_recover(self, prompt: str, schema: BaseModel, exception_message: str, img: Annotated[str, 'Path of the image'] | bytes | None = None, **chat_kwargs) -> BaseModel:
        print('Retrying...')
        messages = deepcopy(self.__messages)
        messages += [
            self.__prepare_user_message(prompt, img),
            {
                'role': 'assistant',
                'content': self.__last_response
            },
            {
                'role': 'user',
                'content': RECOVER_OUTPUT_INSTRUCTION.replace("<PYDANTIC_SCHEMA>", json.dumps(schema.model_json_schema()))\
                                                     .replace("<EXCEPTION>", exception_message)
            }
        ]
        self.__last_response = self.client.chat(
            model=self.model,
            messages=self.__messages,
            **chat_kwargs
        ).message.content
        resp = json.loads(self.__last_response)
        return schema(**resp)
        

    def _ask(self, prompt: str, img: Annotated[str, 'Path of the image'] | bytes | None = None, **chat_kwargs) -> ChatResponse:
        _message = self.__prepare_user_message(prompt, img)
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

    def ask_w_structured_output(self, prompt: str, schema: BaseModel, img: Annotated[str, 'Path of the image']| bytes | None = None, **chat_kwargs) -> BaseModel:
        structured_output_instruction = self.__instruction + "\n" + STRUCTURED_OUTPUT_INSTRUCTION.replace("<PYDANTIC_SCHEMA>", json.dumps(schema.model_json_schema()))
        self.__messages[0]['content'] = structured_output_instruction
        self.__last_response = self._ask(prompt, img, **chat_kwargs).message.content
        try:
            resp = json.loads(self.__last_response)
            return schema(**resp)
        except (JSONDecodeError, ValidationError) as e:
            return self.__structured_output_recover(prompt, schema, self.__recover_exceptions[type(e)], img, **chat_kwargs)
