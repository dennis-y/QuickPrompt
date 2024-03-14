import requests
import json
import sseclient
from settings import settings
import logging

logger = logging.getLogger(__name__)

OPENAI_CLIENT = None
MISTRAL_CLIENT = None

def call_model(message):
    global OPENAI_CLIENT
    # TODO: Config for model in ui
    if OPENAI_CLIENT is None:
        OPENAI_CLIENT = OpenAIClient()
    for result in OPENAI_CLIENT.ask(message):
        yield result

class BaseChatClient:
    def __init__(self, endpoint, model, api_key):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.messages = []

    def ask(self, question, role="user"):
        message = {
            "role": role,
            "content": question,
        }
        # TODO: Keep track of all messages? Could be a lot of tokens
        # TODO: What happens when we hit the token limit?
        self.messages.append(message)
        headers = {
            'Authorization': f'Bearer {self.api_key}', 
            'Accept': 'text/event-stream',
            'Content-Type': 'application/json',
        }
        logger.info(f'Sending messages: {self.messages}')
        response = requests.post(self.endpoint,json={
                'model': self.model,
                'stream': True,
                'messages': self.messages,
            }, 
            headers=headers, stream=True)

        client = sseclient.SSEClient(response)
        model_message = []
        for event in client.events():
            if event.data == '[DONE]':
                break
            try:
                data = json.loads(event.data)
                chunk = data['choices'][0]['delta']['content']
                model_message.append(chunk)
                yield chunk
            except:
                logger.warn(f'Failed to decode: {event.data}')
        full_message = ''.join(model_message)
        logger.info(f'Got response: {full_message}')
        self.messages.append({
            "role": "assistant", 
            "content": full_message,
        })
        
    def print(self, question):
        for chunk in self.ask(question):
            print(chunk, end='')
        

class MistralClient(BaseChatClient):
    def __init__(self, model='mistral-tiny'):
        key = settings.get_api_key('mistral')
        super().__init__('https://api.mistral.ai/v1/chat/completions', model, key)


class OpenAIClient(BaseChatClient):
    def __init__(self, model='gpt-3.5-turbo'):
        key = settings.get_api_key('openai')
        super().__init__('https://api.openai.com/v1/chat/completions', model, key)

