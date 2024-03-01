import requests
import json
import sseclient

def get_api_key(service):
    with open('.quickprompt.json') as f:
        settings = json.load(f)
        return settings['api_keys'][service]

def call_model(message):
    # TODO: Config for model in ui
    client = OpenAIClient()
    for result in client.ask(message):
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
        self.messages.append(message)
        headers = {
            'Authorization': f'Bearer {self.api_key}', 
            'Accept': 'text/event-stream',
            'Content-Type': 'application/json',
        }
        response = requests.post(self.endpoint,json={
                'model': self.model,
                'stream': True,
                'messages': self.messages,
            }, 
            headers=headers, stream=True)

        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data == '[DONE]':
                break
            try:
                data = json.loads(event.data)
                chunk = data['choices'][0]['delta']['content']
                yield chunk
            except:
                print(f'Failed to decode: {event.data}')
        
    def print(self, question):
        for chunk in self.ask(question):
            print(chunk, end='')
        

class MistralClient(BaseChatClient):
    def __init__(self, model='mistral-tiny'):
        key = get_api_key('mistral')
        super().__init__('https://api.mistral.ai/v1/chat/completions', model, key)


class OpenAIClient(BaseChatClient):
    def __init__(self, model='gpt-3.5-turbo'):
        key = get_api_key('openai')
        super().__init__('https://api.openai.com/v1/chat/completions', model, key)
