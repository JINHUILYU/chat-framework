import time
from openai import OpenAI

base_urls = {
    "Kimi": "https://api.moonshot.cn/v1",
    "GPT-3.5": "https://api.openai.com/v1",
    "GPT-4": "https://api.openai.com/v1",
    "GPT-4o": "https://api.openai.com/v1",
    "Default": "https://api.chatanywhere.tech/v1",  # 转发接口
}


# 读取指定prompt
def read_prompt(prompt_file):
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


def read_key(key_file):
    with open(key_file, 'r', encoding='utf-8') as f:
        return f.read()


class LLM:
    def __init__(self, model='Default', key=None, prompt=None):
        self.history = []
        self.client = OpenAI(
            api_key="sk-1MC0MeD3zZDrI0m3xlCAkR8pZHlGlAcgUy0n1hqM5IFM8gO8" if model == "Default" else key,
            base_url=base_urls.get(model)
        )
        self.model = model
        self.models = {
            "Kimi": "moonshot-v1-8k",
            "GPT-3.5": "gpt-3.5-turbo",
            "GPT-4o": "gpt-4o",
            "GPT-4": "gpt-4",
            "Default": "gpt-3.5-turbo"
        }
        self.prompt = prompt
        self.history.append({"role": "system", "content": self.prompt})

    # query interface
    def query(self, sentence, context=True, n=1, temperature=0.3):
        self.history.append({"role": "user", "content": sentence})
        try:
            completion = self.client.chat.completions.create(
                model=self.models.get(self.model),
                messages=self.history,
                temperature=temperature,
                timeout=15,
                n=n,
                stream=False
            )
        except Exception as ex:
            return f"Error processing data: {ex}"
        # 获取处理后的数据
        if n == 1:
            processed_data = completion.choices[0].message.content.strip()
        else:
            processed_data = []
            for choice in completion.choices:
                processed_data.append(choice.message.content.strip())
        # 上下文处理
        if context:
            self.history.append({"role": "assistant", "content": processed_data})
        else:
            self.history.pop()
        return processed_data

    def save_session_record(self):
        with open(f"logs/{time.strftime(f'%Y-%m-%d-%H-%M-%S', time.localtime())}-session.txt", "a", encoding='utf-8') as f:
            for item in self.history:
                f.write(str(item) + "\n")


class pipeline:
    def __init__(self, model='Default', key=None, prompt_1=None, prompt_2=None, prompt_3=None):
        self.llm_1 = LLM(model=model, key=key, prompt=prompt_1)
        self.llm_2 = LLM(model=model, key=key, prompt=prompt_2)
        self.llm_3 = LLM(model=model, key=key, prompt=prompt_3)

    def query(self, question):
        answer_1 = self.llm_1.query(question)
        answer_2 = self.llm_2.query(answer_1)
        answer_3 = self.llm_3.query(answer_2)
        return answer_3


class arbitration:
    def __init__(self, model='Default', key=None, prompt_1=None, prompt_2=None, prompt_3=None, prompt_4=None):
        self.llm_1 = LLM(model=model, key=key, prompt=prompt_1)
        self.llm_2 = LLM(model=model, key=key, prompt=prompt_2)
        self.llm_3 = LLM(model=model, key=key, prompt=prompt_3)
        self.llm_4 = LLM(model=model, key=key, prompt=prompt_4)

    def query(self, question):
        answer_1 = self.llm_1.query(question)
        answer_2 = self.llm_2.query(question)
        answer_3 = self.llm_3.query(question)
        answers = f"The question is {question}, the answers are answer_1: '{answer_1}', answer_2: '{answer_2}', answer_3: '{answer_3}', you need to choose the correct one and explain why."
        answer_4 = self.llm_4.query(answers)
        return answer_4
