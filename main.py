from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import os
import json
from datetime import datetime, timedelta
import requests

nowtime = datetime.utcnow() + timedelta(hours=8)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")


def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}

    # 获取当前时间的年、月、日部分，并格式化为"yyyy-mm-dd"的字符串形式
    current_date_str = nowtime.strftime("%Y-%m-%d")

    # 根据当前时间的星期几（通过nowtime.strftime('%A')获取英文星期名称），从字典中获取对应的中文星期表述
    a = dictDate[nowtime.strftime('%A')]

    return current_date_str + " " + a


def get_words():
    words = requests.get("https://www.mxnzp.com/api/daily_word/recommend?app_secret={}&app_id={}".format(Word_app_secret,Word_app_id)).json()
    print(words)
    if words['code'] != 200:
        return get_words()
    return words['data'][0]['content']

def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    # print(url)
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather

def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days


if __name__ == '__main__':
    app_id = os.getenv("APP_ID")
    app_secret = os.getenv("APP_SECRET")
    template_id = os.getenv("TEMPLATE_ID")
    weather_key = os.getenv("WEATHER_API_KEY")

    # 文新一言api
    Word_app_id = os.getenv('WORD_APP_ID')
    Word_app_secret = os.getenv('WORD_APP_SECRET')

    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    f = open("users_info.json", encoding="utf-8")
    js_text = json.load(f)
    f.close()
    data = js_text['data']

    num = 0
    words=get_words()
    out_time=get_time()
    print(out_time.encode('utf-8'))

    for user_info in data:
        born_date = user_info['born_date']
        birthday = born_date[5:]
        city = user_info['city']
        user_id = user_info['user_id']
        name = user_info['user_name'].upper()


        wea_city,weather = get_weather(city,weather_key)
        data = dict()
        data['time'] = {'value': out_time}
        data['words'] = {'value': words}
        data['weather'] = {'value': weather['text_day']}
        data['city'] = {'value': wea_city}
        data['tem_high'] = {'value': weather['high']}
        data['tem_low'] = {'value': weather['low']}
        data['born_days'] = {'value': get_count(born_date)}
        data['birthday_left'] = {'value': get_birthday(birthday)}
        data['wind'] = {'value': weather['wind_direction']}
        data['name'] = {'value': name}
        print(data)

        res = wm.send_template(user_id, template_id, data)
        print(res)
        num += 1
    print(f"成功发送{num}条信息")


