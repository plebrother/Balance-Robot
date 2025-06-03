import speech_recognition as sr
from gtts import gTTS
import os
from openai import OpenAI

# 初始化语音识别器
recognizer = sr.Recognizer()

# 捕获音频输入
with sr.Microphone() as source:
    print("请说话...")
    audio = recognizer.record(source,duration=10)

# 使用Google Web Speech API进行语音识别
try:
    text = recognizer.recognize_google(audio,language='zh-CN')
    print(f"你说: {text}")
except sr.UnknownValueError:
    print("无法识别语音")
except sr.RequestError as e:
    print(f"请求错误 {e}")

# 语音输出



client = OpenAI(
  api_key=""
) #DO NOT STEAL MY API KEY!!!


completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": text},
    {"role": "system", "content": "你的输出应该只包含纯文本，不以markdown或其他非纯文本的方式输出，因为你的输出将会被语音播报，所以你的输出应该遵循接近人类自然语气和口语语法"}
  ]
)

output_text = completion.choices[0].message.content


#output_text = "你刚才说的是：" + text
tts = gTTS(output_text, lang='zh-CN')
tts.save("output.mp3")
os.system("start output.mp3")
input()