import numpy as np
from openai import OpenAI
from mistralai import Mistral
from google import genai
from google.genai import types
import ollama
from tqdm import tqdm
import time
import re


class Player():
    def __int__(self):
        raise NotImplementedError
    
    def reset_player(self, _):
        raise NotImplementedError
    
    def convert_conversation(self, _):
        raise NotImplementedError
    
    def chat(self, _):
        raise NotImplementedError
    
    def get_letter(self, _):
        raise NotImplementedError
    
    def make_guess(self, _):
        raise NotImplementedError



class GPTPlayer(Player):

    def __init__(self, args):
        self.args = args

        self.client = OpenAI(
            organization='<your-organization-id>',
            project="<your-project-id>",
            api_key="<your-api-key>",
        )


    def reset_player(self, _):
        pass

    def convert_conversation(self, conversation):
        return [{"role": role, "content": content} for role, content in conversation]
    


    def chat(self, conversation):
        completion = self.client.chat.completions.create(
            model=self.args['player']['name'],
            messages=self.convert_conversation(conversation),
            seed=self.args['seed'],
        )

        return completion.choices[0].message.content

        
    def get_letter(self, conversation):
        llm_guess = self.chat(conversation)
        
        return llm_guess, llm_guess.strip()[-1]
    

    def make_guess(self, conversation):
        llm_guess = self.chat(conversation)

        return llm_guess, llm_guess.strip()
    
class GeminiPlayer(Player):

    def __init__(self, args):
        self.args = args
        self.client = genai.Client(api_key="<your-api-key>")
        self.model_name = args['player']['name']

        self.generation_config = types.GenerateContentConfig(
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "block_none"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "block_none"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "block_none"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "block_none"},
            ],
        )

    def reset_player(self, system_prompt):
        pass

    def convert_conversation(self, conversation):

        ROLE_MAP = {
            "system": "user",      # Gemini does not support 'system', map to 'user'
            "assistant": "model",
            "user": "user"
        }
        return [
            {"role": ROLE_MAP.get(role, "user"), "parts": [{"text": content}]}
            for role, content in conversation
        ]
    

    def chat(self, conversation):
        try:
            time.sleep(10)
            completition = self.client.models.generate_content(model=self.model_name,
                                                               contents=self.convert_conversation(conversation),
                                                               config=self.generation_config)
        except Exception as e:
            if self.args['verbose']: tqdm.write(f"Watining 60s\n - Error: {e}") 

            time.sleep(60)
            completition = self.client.models.generate_content(model=self.model_name,
                                                               contents=self.convert_conversation(conversation),
                                                               config=self.generation_config)
        return completition.text
    

    def get_letter(self, conversation):
        llm_guess = self.chat(conversation)
        if llm_guess.strip()[-1] == ".":
            return llm_guess, llm_guess.strip()[-2]
        return llm_guess, llm_guess.strip()[-1]
    

    def make_guess(self, conversation):
        llm_guess = self.chat(conversation)

        return llm_guess, llm_guess.strip()
    

class MistralPlayer(Player):

    def __init__(self, args):
        self.args = args
        self.client = Mistral(api_key="<your-api-key>")


    def reset_player(self, _):
        pass

    def convert_conversation(self, conversation):
        return [{"role": role, "content": content} for role, content in conversation]
    


    def chat(self, conversation):
        try:
            completion = self.client.chat.complete(
                model=self.args['player']['name'],
                temperature=self.args['player']['temperature'],
                messages=self.convert_conversation(conversation),
                random_seed=self.args['seed'],
            )
        except Exception as e:

            time.sleep(20)
            completion = self.client.chat.complete(
                model=self.args['player']['name'],
                messages=self.convert_conversation(conversation),
                random_seed=self.args['seed'],
            )
        return completion.choices[0].message.content
    

    def get_letter(self, conversation):
        llm_guess = self.chat(conversation)

        return llm_guess, llm_guess.strip()[-1].upper()
    

    def make_guess(self, conversation):
        llm_guess = self.chat(conversation)

        if "pass" in llm_guess.lower():
            return llm_guess, llm_guess.strip()

        else:
            return llm_guess, llm_guess.strip().upper()
        



class OllamaPlayer(Player):
    
    def __init__(self, args):
        self.args = args
        self.model_name = args['player']['name']

        try:
            ollama.chat(self.model_name)
        except ollama.ResponseError as e:
            print('Downloading', self.model_name)
            if e.status_code == 404:
                ollama.pull(self.model_name)


    def reset_player(self, system_prompt):
        pass

    def convert_conversation(self, conversation):
        return [{"role": role, "content": content} for role, content in conversation]


    def chat(self, conversation):
        response = ollama.chat(model=self.model_name, messages=self.convert_conversation(conversation))
        response['message']['content'] = re.sub(r"<think>.*?</think>", "", response['message']['content'], flags=re.DOTALL)
        return (response['message']['content'])


    def get_letter(self, conversation):
        llm_guess = self.chat(conversation)
        if '[' in llm_guess:
            llm_guess = llm_guess.replace("[", "")
        if ']' in llm_guess:
            llm_guess = llm_guess.replace("]", "")

        return llm_guess, llm_guess.strip()[-1]
    

    def make_guess(self, conversation):
        llm_guess = self.chat(conversation)

        return llm_guess, llm_guess.strip()
    

    def clear_model(self):
        print("Clearing model: ",self.model_name)
        ollama.delete(self.model_name)
    
