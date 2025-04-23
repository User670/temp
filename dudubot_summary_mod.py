'''
Original file: https://github.com/1475505/nonebot_plugins_of_dudubot/blob/main/plugins/summary_message/__init__.py
This modification adds a few commands towards the end of the file, all of them are modified copies of "zdict".
Note that I am unable to test the code due to lack of relevant environment and API keys.

Commands added:
/词典 : provide dictionary-like explanation to up to 3 words or phrases, with pronunciation, etymology, and definition.
/百科 : provide encyclopedia-like explanation to up to 3 concepts.
/网络梗 : provide explanation to up to 3 internet memes.
/解析 : parse a hard-to-understand chat message and rewrite in easier-to-understand terms.
'''
import traceback

import nonebot
from nonebot.adapters import Bot, Event
from nonebot.exception import AdapterException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot import on_command


from nonebot_plugin_alconna import Alconna, Args, on_alconna

from .config import Config
from nonebot.adapters import MessageSegment
from nonebot.adapters.onebot.v11 import GroupMessageEvent,Message

__plugin_meta__ = PluginMetadata(
    name="对引用的信息进行总结",
    description="11",
    usage="122",
    config=Config,

)

from openai import AsyncOpenAI

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

client = AsyncOpenAI(
    api_key=plugin_config.chat_oneapi_key, base_url=plugin_config.chat_oneapi_url
)

conclude = on_command("概括", priority=13, block=True)

async def callModel(model: str, content: str):
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message

@conclude.handle()
async def handle_reply(event: GroupMessageEvent):
    # 检查是否包含回复信息
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
        #if replied_message.reply:
        #    replied_content = replied_message.reply.message.extract_plain_text()
        # 对内容进行总结
        prompt = """你现在是一位专业的教授. 请使用1-2句话简单概括接下来的文本讲述的内容、论证逻辑和观点。如果文本中存在难以理解的内容/网络流行梗,使用通俗化的语言讲述.然后，以客观的角度分析，提供看法。输出格式：
        [总结]...
        [AI看法]...
        [相关知识]...
        （严格按照此格式，不要输出其他内容）
        你需要处理的文本是：
        """ + replied_content
        response = await callModel("Pro/deepseek-ai/DeepSeek-R1", prompt)
        await conclude.finish(response.content, at_sender=True)

from nonebot.params import CommandArg
zdict = on_command("扫盲", priority=13, block=True)
@zdict.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 检查是否包含回复信息
    replied_content = "嘟嘟可"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    # 对内容进行总结
    prompt = """你现在是一位喜欢二次元的程序员，面向高三竞赛生,讲解接下来基于的文字/词语/短句/网络流行词中,对应的读音(拼音/该语言对应的音标),中文含义和历史渊源,即词典功能.输出最好能激发学习兴趣,格式：
        [词典]...
        [相关故事]...
        （严格按照此格式，不要输出其他内容）
        你需要处理的文本是：
    """ + replied_content
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await zdict.finish("\n" + response.content, at_sender=True)

quest = on_command("质疑", priority=13, block=True)
@quest.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
      # 检查是否包含回复信息
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
        #if replied_message.reply:
        #    replied_content = replied_message.reply.message.extract_plain_text()
        # 对内容进行总结
        prompt = """你现在是一位高考状元/开源贡献者/C++高手/北大小男娘/梗指南大师. 接下来我将给出一段文本，文本的内容、论证逻辑和观点可能存在错误。请以批判性质疑的角度，对其进行深入的分析，给出文本中观点的合理之处、错误之处，提出适当的质疑，并通俗地补充相关知识。输出格式：
        [判断]...
        [质疑]...
        [相关知识]...
        （严格按照此格式，不要输出其他内容）
        你需要处理的文本是：
        """ + replied_content
        response = await callModel("Pro/deepseek-ai/DeepSeek-R1", prompt)
        await quest.finish(response.content, at_sender=True)
    
    

commonai = on_command("安慰", aliases={"夸夸"}, priority=13, block=True)
@commonai.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 检查是否包含回复信息
    replied_content = "嘟嘟可"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    command = event.get_plaintext().strip().split()[0][1:]
    # 对内容进行总结
    prompt = f"""你现在是一位喜欢二次元的程序员. 接下来我将给出一段文本, 请对该文本进行简单的{command}, 需要具有同理心. 输出格式：
        [{command}]...
        [相关建议]...
        （严格按照此格式，不要输出其他内容）
        你需要处理的文本是：
    """ + replied_content
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await zdict.finish("\n" + response.content, at_sender=True)

import random

mc = on_command("鸣式", priority=13, block=True)
@mc.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
      # 检查是否包含回复信息
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
        #if replied_message.reply:
        #    replied_content = replied_message.reply.message.extract_plain_text(a
        # 对内容进行总结
        p = random.random()
        prompt1 = f"""请将文本{replied_content}改写成下面的格式, 基于文本, 允许少量自由发挥，可增加适量的讽刺色彩（A和B为名词，C为一种动作，意为A只有在主体为B的条件下才能做动作C. 严格按照此格式，不要输出其他内容）:
        请谅解
        A
        只有 B
        可以 C
        
        示例：
        请谅解
        今天
        只有 中国人
        可以 玩原神
        """ 
        prompt2 = f"""请将文本{replied_content}改写成下面的格式, 基于文本, 允许少量自由发挥（A/B 改写为相关 4 个字以内的对立概念, C改为相关的短句. 严格按照此格式，不要输出其他内容）:
        A是这样的。B只需要负责C就可以了，而A要考虑的事情就多了.

        示例：后方是这样的。前线的将士只要全身心投入到战场中，听命行事，奋力杀敌就可以，可是后方人员要考虑的事情就很多了。
        """
        prompt3 = f"""请将文本{replied_content}改写成下面的格式, 基于文本, 允许少量自由发挥，可增加适量的讽刺色彩（A和B为名词，C为一种动作，意为A只有在主体为B的条件下才能做动作C. D可以为一个第三方旁观者名词. 严格按照此格式，不要输出其他内容）:
        请谅解
        A
        只有 B
        可以 C
        D 要考虑的事情就多了.
        """
        prompt = prompt1
        if p > 0.5:
            prompt = prompt2
        if p > 0.9:
            prompt = prompt3
        #response = await callModel("Pro/deepseek-ai/DeepSeek-R1", prompt)
        response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
        await mc.finish("\n"+response.content, at_sender=True)


htx = on_command("何式", priority=13, block=True)
@htx.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
      # 检查是否包含回复信息
    replied_content = "我玩原神从不抽卡"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    #if replied_message.reply:
    #    replied_content = replied_message.reply.message.extract_plain_text(a
    p = random.random()
    prompt1 = f"""任务：接下来，我将给你一段基准文本，然后，你需要将输入的文本改写成基准文本类似的语言和文本格式, 需要保证段落结构的一致性和通顺性。请严格进行改写。
    基准文本：以前打网约车，司机师傅跟我说打个好评，我都会说好好好，但是下车后也没想起来打。其实这样挺不好的。现在司机师傅跟我说打个好评，除非服务真的很好到我想打好评的程度，否则我就会直接说，抱歉我不想打，然后下车。作为一个有讨好倾向的人，这是我锻炼真诚和勇气的方式。

    示例：
    输入文本：我看B站视频不喜欢一键三连。
    输出文本：以前看何同学的视频，他总说记得一键三连，我都会说好好好，但退出后也没想起来按。其实这样挺不礼貌的。 现在何同学再提一键三连，除非视频真的有趣到让我想掏硬币，否则我就直接说：「抱歉，您的视频暂时无法三连」，然后退出全屏。作为一个有原则的观众，这是我锻炼自我和解与节能环保的方式。

    接下来，请对下面的输入文本进行改写，只输出对应改写后的输出文本，不要输出其他内容,不要输出其他内容,不要输出其他内容。
    输入文本：{replied_content}
    """
    prompt = prompt1
    #response = await callModel("Pro/deepseek-ai/DeepSeek-R1", prompt)
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await htx.finish("\n"+response.content, at_sender=True)

from . import xf_ocr
ocr = on_command("ocr", priority=13, block=True)
@ocr.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
      # 检查是否包含回复信息
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        for seg in replied_message:
            if seg.type == "image":
                img_url = seg.data["url"]
                txt = xf_ocr.ocr(img_url)
                if len(txt) < 30:
                    await ocr.finish(txt)
                else:
                    # 将长文本分段
                    segments = [txt[i:i+1000] for i in range(0, len(txt), 1000)]
                    messages = []
                    
                    # 创建转发消息节点
                    for index, segment in enumerate(segments, 1):
                        messages.append({
                            "type": "node",
                            "data": {
                                "name": "OCR结果",
                                "uin": event.self_id,
                                "content": f"第{index}部分：\n{segment}"
                            }
                        })
                    
                    # 发送合并转发消息
                    await bot.call_api(
                        "send_group_forward_msg",
                        group_id=event.group_id,
                        messages=messages
                    )

'''
Mods by User670
'''
user670_summary_dictionary = on_command("词典", priority=255, block=True)
@user670_summary_dictionary.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 检查是否包含回复信息
    replied_content = "嘟嘟可"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    # 对内容进行总结
    prompt = """用户对一个或多个单字、词语或短语不理解，需要类似词典的解释。对用户给出的每个关键字、词或词组，按照如下的格式提供解释。如果用户提供的内容过长，例如包含整个句子或段落，则提取最多3个最可能需要解释的字、词或词组进行解释。请用纯文本输出，不要使用markdown语法。

格式：
<词条>
[读音]...
[词源]...
[释义]...

对于读音，如果词条语言为中文，则给出汉语拼音。如果词条语言是日文，则给出黑本式罗马字。如果词条语言是拉丁字母拼写的其他语言，则给出IPA。如果词条语言是其他书写系统拼写的其他语言，则给出IPA和拉丁化转写。
对于词源(etymology)，请给出该词条的公认的词源，例如词根词缀，构词法，相应的典故（对于俗语和成语）等。如果没有可靠的词源信息，则跳过该部分。
对于释义，请按照类似词典的格式列举该词条的释义。

用户提供的文本是：
""" + replied_content
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await user670_summary_dictionary.finish("\n" + response.content, at_sender=True)


user670_summary_encyclopedia = on_command("百科", priority=255, block=True)
@user670_summary_encyclopedia.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 检查是否包含回复信息
    replied_content = "嘟嘟可"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    # 对内容进行总结
    prompt = """用户对一个或多个概念希望获取类似百科全书的解释。对用户给出的每个关键概念给出解释。如果用户提供的内容过长，例如包含整个句子或段落，则提取最多3个最可能需要解释的概念进行解释。解释应言简意赅，对关键点进行概括，格式应类似维基百科词条的首段，不要超过200字。请用纯文本输出，不要使用markdown语法。

格式：
<词条>
<解释>

用户提供的文本是：
""" + replied_content
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await user670_summary_encyclopedia.finish("\n" + response.content, at_sender=True)


user670_summary_meme = on_command("网络梗", priority=255, block=True)
@user670_summary_meme.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 检查是否包含回复信息
    replied_content = "嘟嘟可"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    # 对内容进行总结
    prompt = """用户对一个或多个网络迷因、次文化梗等不理解。在用户提供的消息中，提取不超过3个最需要解释的迷因，并对每个迷因按照如下格式解释。请用纯文本输出，不要使用markdown语法。

格式：
<词条>
[词源]...
[解释]...

用户提供的文本是：
""" + replied_content
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await user670_summary_meme.finish("\n" + response.content, at_sender=True)


user670_summary_parse = on_command("解析", priority=255, block=True)
@user670_summary_parse.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 检查是否包含回复信息
    replied_content = "嘟嘟可"
    if event.reply:
        # 获取被引用消息的内容
        replied_message = event.reply.message
        replied_content = replied_message.extract_plain_text()  # 提取纯文本内容
    else:
        replied_content = msg.extract_plain_text()
    # 对内容进行总结
    prompt = """用户对网络群聊中的一条消息不理解。请对提供的消息进行解析并改写为清晰易懂的语言。原文中可能包含网络迷因/次文化梗、缩写/简写/代指、谐音替换/双关语、专业术语等。请用纯文本输出，不要使用markdown语法。

格式：
您提供的消息改写结果如下：
<改写后的文本>

用户提供的文本是：
""" + replied_content
    response = await callModel("Pro/deepseek-ai/DeepSeek-V3", prompt)
    await user670_summary_parse.finish("\n" + response.content, at_sender=True)

'''
End of mods by User670
'''
