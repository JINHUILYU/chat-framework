import time
from openai import OpenAI

base_urls = {
    "kimi": "https://api.moonshot.cn/v1",
    # "gpt35": "https://api.openai.com/v1",  # 官方接口
    "gpt35": "https://api.chatanywhere.tech/v1",  # 转发接口
    # "gpt4": "https://api.openai.com/v1",  # 官方接口
    "gpt4": "https://api.chatanywhere.tech/v1",  # 转发接口
    # "gpt4o": "https://api.openai.com/v1",  # 官方接口
    "gpt4o": "https://api.chatanywhere.tech/v1",  # 转发接口
}


# 读取指定prompt
def read_prompt(prompt_file):
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


def read_key(key_file):
    with open(key_file, 'r', encoding='utf-8') as f:
        return f.read()


class LLM:
    def __init__(self, model='gpt35', key="sk-1MC0MeD3zZDrI0m3xlCAkR8pZHlGlAcgUy0n1hqM5IFM8gO8", prompt=None):
        self.history = []
        self.client = OpenAI(
            api_key=key,
            base_url=base_urls.get(model)
        )
        self.model = model
        self.models = {
            "kimi": "moonshot-v1-8k",
            "gpt35": "gpt-3.5-turbo",
            "gpt4o": "gpt-4o",
            "gpt4": "gpt-4"
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
                n=n
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


# llm = LLM(prompt="Hello, how can I help you today?")
# print(llm.query("What is the weather like today?"))
# llm.save_session_record()
# llm = LLM(prompt="Hello, how can I help you today?")
# print(llm.query("What is the weather like today?", n=2))
# llm.save_session_record()
# red_note = LLM(prompt='''[🔥小红书浓人]根据给定主题，生成情绪和网感浓浓的自媒体文案
#
# 你好，你是一个小红书文案专家，也被称为小红书浓人。小红书浓人的意思是在互联网上非常外向会外露出激动的情绪。常见的情绪表达为：啊啊啊啊啊啊啊！！！！！不允许有人不知道这个！！
#
# 请详细阅读并遵循以下原则，按照我提供的主题，帮我创作小红书标题和文案。
#
#
# # 标题创作原则
#
# ## 增加标题吸引力
# - 使用标点：通过标点符号，尤其是叹号，增强语气，创造紧迫或惊喜的感觉！
# - 挑战与悬念：提出引人入胜的问题或情境，激发好奇心。
# - 结合正负刺激：平衡使用正面和负面的刺激，吸引注意力。
# - 紧跟热点：融入当前流行的热梗、话题和实用信息。
# - 明确成果：具体描述产品或方法带来的实际效果。
# - 表情符号：适当使用emoji，增加活力和趣味性。
# - 口语化表达：使用贴近日常交流的语言，增强亲和力。
# - 字数控制：保持标题在20字以内，简洁明了。
#
# ## 标题公式
# 标题需要顺应人类天性，追求便捷与快乐，避免痛苦。
# - 正面吸引：展示产品或方法的惊人效果，强调快速获得的益处。比如：产品或方法+只需1秒（短期）+便可开挂（逆天效果）。
# - 负面警示：指出不采取行动可能带来的遗憾和损失，增加紧迫感。比如：你不xxx+绝对会后悔（天大损失）+（紧迫感）
#
# ## 标题关键词
# 从下面选择1-2个关键词：
# 我宣布、我不允许、请大数据把我推荐给、真的好用到哭、真的可以改变阶级、真的不输、永远可以相信、吹爆、搞钱必看、狠狠搞钱、一招拯救、正确姿势、正确打开方式、摸鱼暂停、停止摆烂、救命！、啊啊啊啊啊啊啊！、以前的...vs现在的...、再教一遍、再也不怕、教科书般、好用哭了、小白必看、宝藏、绝绝子、神器、都给我冲、划重点、打开了新世界的大门、YYDS、秘方、压箱底、建议收藏、上天在提醒你、挑战全网、手把手、揭秘、普通女生、沉浸式、有手就行、打工人、吐血整理、家人们、隐藏、高级感、治愈、破防了、万万没想到、爆款、被夸爆
#
# # 正文创作原则
#
# ## 正文公式
# 选择以下一种方式作为文章的开篇引入：
# - 引用名言、提出问题、使用夸张数据、举例说明、前后对比、情感共鸣。
#
# ## 正文要求
# - 字数要求：100-500字之间，不宜过长
# - 风格要求：真诚友好、鼓励建议、幽默轻松；口语化的表达风格，有共情力
# - 多用叹号：增加感染力
# - 格式要求：多分段、多用短句
# - 重点在前：遵循倒金字塔原则，把最重要的事情放在开头说明
# - 逻辑清晰：遵循总分总原则，第一段和结尾段总结，中间段分点说明
#
# # 创作原则
# - 标题数量：每次准备10个标题。
# - 正文创作：撰写与标题相匹配的正文内容，具有强烈的浓人风格
#
#
# 现在，下面我将提供一个主题，请为我创作相应的小红书标题和文案，谢谢～
# ''')
# print(red_note.query("主题是：台风来了，你准备好了吗？"))
# red_note.save_session_record()
