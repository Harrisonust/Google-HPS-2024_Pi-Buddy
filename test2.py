import pyttsx3

# 初始化
engine = pyttsx3.init()

voices = engine.getProperty('voices')
# 語速控制
rate = engine.getProperty('rate')
print(rate)
engine.setProperty('rate', rate-20)

# 音量控制
volume = engine.getProperty('volume')
print(volume)
engine.setProperty('volume', volume-0.25)

engine.say('hello world')
engine.say('你好，世界')
# 朗讀一次
engine.runAndWait()

engine.say('語音合成開始')
engine.say('我會說中文了，開森，開森')
engine.runAndWait()

engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()