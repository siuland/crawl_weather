import requests
from bs4 import BeautifulSoup


def get_weather_from_weathercn(city_code='101010100'):
    url = f"http://www.weather.com.cn/weather/{city_code}.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
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
            temp = item.select('p.tem')[0].text.replace('\n', '')

            weather_data.append({
                'date': date,
                'weather': weather,
                'temp': temp
            })

        return {
            'city': city,
            'data': weather_data
        }

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


# 使用示例
result = get_weather_from_weathercn()
print(result)