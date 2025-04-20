import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime

# 中国热门城市及对应城市代码（来自中国天气网）
CITY_CODES = {
    '北京': '101010100',
    '上海': '101020100',
    '广州': '101280101',
    '深圳': '101280601',
    '成都': '101270101',
    '重庆': '101040100',
    '武汉': '101200101',
    '杭州': '101210101',
    '南京': '101190101',
    '西安': '101110101'
}


def get_weather_from_weathercn(city_code='101010100'):
    url = f"http://www.weather.com.cn/weather/{city_code}.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析城市名称
        city = soup.find('div', class_='crumbs fl').text.strip().split('\n')[-1]

        # 解析7天天气预报
        weather_data = []
        items = soup.select('ul.t.clearfix > li')

        for item in items[:3]:  # 只取最近3天
            date = item.h1.text
            weather = item.p.text
            temp = item.select('p.tem')[0].text.replace('\n', '').strip()

            weather_data.append({
                'date': date,
                'weather': weather,
                'temp': temp,
                'high_temp': temp.split('/')[0].replace('℃', ''),
                'low_temp': temp.split('/')[1].replace('℃', '')
            })

        return {
            'city': city,
            'data': weather_data
        }

    except Exception as e:
        print(f"爬取{city_code}失败: {e}")
        return None


def save_to_csv(weather_data, filename='weather_forecast.csv'):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['city', 'date', 'weather', 'temp', 'high_temp', 'low_temp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for city_data in weather_data:
            if city_data is None:
                continue
            for day_data in city_data['data']:
                writer.writerow({
                    'city': city_data['city'],
                    'date': day_data['date'],
                    'weather': day_data['weather'],
                    'temp': day_data['temp'],
                    'high_temp': day_data['high_temp'],
                    'low_temp': day_data['low_temp']
                })


def main():
    all_weather_data = []

    print("开始爬取热门城市天气预报...")
    for city_name, city_code in CITY_CODES.items():
        print(f"正在爬取{city_name}的天气数据...")
        weather_data = get_weather_from_weathercn(city_code)
        all_weather_data.append(weather_data)

        # 添加延时，避免请求过于频繁（3-5秒比较安全）
        time.sleep(4)

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'china_cities_weather_{timestamp}.csv'

    save_to_csv(all_weather_data, filename)
    print(f"数据已保存到 {filename}")


if __name__ == '__main__':
    main()