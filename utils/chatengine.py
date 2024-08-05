import os
from openai import AzureOpenAI
from dotenv import load_dotenv


envpath = "/home/metard/project/meta-human/user_app_v0.1.21/.env"
load_dotenv(dotenv_path=envpath)

endpoint = "https://GPT-research-dev-US-01.openai.azure.com/"
deployment = "gpt-4o"
key = os.environ.get('AZUREOPENAIKEYGPT4OUS')

class ChatEngine():
    def __init__(self, init_conversation):
        self.init_conversation = init_conversation
        self.conversation = init_conversation
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version="2024-02-01",
        )

    def create(self, messages):
        new_conversation = self.conversation
        new_conversation.append(messages)
        response = self.client.chat.completions.create(
            model=deployment, messages=new_conversation,
            temperature=0.5,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0)
        new_conversation.append(
            {"role": "assistant", "content": response.choices[0].message.content})
        self.conversation = new_conversation
        return response.choices[0].message.content
    
    def reset(self):
        self.conversation = self.init_conversation