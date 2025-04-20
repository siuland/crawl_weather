import os
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

# 数据库配置从环境变量读取
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'user': os.getenv('DB_USER', 'weather_user'),
    'password': os.getenv('DB_PASSWORD', 'Weather@123'),
    'database': os.getenv('DB_NAME', 'weather_db'),
    'auth_plugin': 'mysql_native_password'
}

# 中国热门城市及对应城市代码
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

def save_to_mysql(weather_data):
    """保存数据到MySQL数据库"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for city_data in weather_data:
            if city_data is None:
                continue
            for day_data in city_data['data']:
                insert_sql = """
                INSERT INTO weather_data 
                (city, date, weather, temp, high_temp, low_temp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                # 处理温度数据类型转换
                try:
                    high_temp = int(day_data['high_temp'])
                    low_temp = int(day_data['low_temp'])
                except ValueError:
                    high_temp = None
                    low_temp = None

                cursor.execute(insert_sql, (
                    city_data['city'],
                    day_data['date'],
                    day_data['weather'],
                    day_data['temp'],
                    high_temp,
                    low_temp
                ))
        conn.commit()
        print(f"数据已保存到MySQL数据库")

    except mysql.connector.Error as e:
        print(f"数据库操作失败: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def main():
    all_weather_data = []
    print("开始爬取热门城市天气预报...")
    for city_name, city_code in CITY_CODES.items():
        print(f"正在爬取{city_name}的天气数据...")
        weather_data = get_weather_from_weathercn(city_code)
        all_weather_data.append(weather_data)

        # 添加延时，避免请求过于频繁（3-5秒比较安全）
        time.sleep(4)

    save_to_mysql(all_weather_data)


if __name__ == '__main__':
    main()