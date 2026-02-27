import os
import requests
import warnings
import gzip
import json
import time
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# 过滤警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="Unverified HTTPS request")

# 禁用urllib3的InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 天气缓存
weather_cache = {}
CACHE_EXPIRY = 300  # 缓存过期时间（秒）

class WeatherQueryInput(BaseModel):
    city: str = Field(description="城市名称")

class WeatherQueryTool(BaseTool):
    name: str = "weather_query"
    description: str = "查询指定城市的天气信息"
    args_schema: type = WeatherQueryInput

    def _run(self, city: str):
        # 检查缓存
        current_time = time.time()
        if city in weather_cache:
            cached_data = weather_cache[city]
            if current_time - cached_data['timestamp'] < CACHE_EXPIRY:
                return cached_data['result']
        
        try:
            # 直接设置和风天气API密钥和host
            api_key = "5576095ee31e492aba1c8a2e5199ba69"
            api_host = "mc7fc2r7te.re.qweatherapi.com"
            
            # 城市LocationID映射
            location_ids = {
                "北京": "101010100",
                "上海": "101020100",
                "广州": "101280101",
                "深圳": "101280601",
                "杭州": "101210101",
                "惠州": "101280301"
            }
            
            # 获取城市的LocationID
            location = location_ids.get(city, "101010100")  # 默认北京
            
            # 构建API URL
            url = f"https://{api_host}/v7/weather/now?location={location}&lang=zh"
            
            # 设置请求头
            headers = {
                "X-QW-Api-Key": api_key,
                "Accept-Encoding": "gzip"
            }
            
            # 发送请求，减少超时时间
            response = requests.get(url, headers=headers, verify=False, timeout=5)
            
            # 处理Gzip压缩
            try:
                if response.headers.get('Content-Encoding') == 'gzip':
                    # 尝试gzip解压
                    try:
                        data = gzip.decompress(response.content)
                        data = json.loads(data)
                    except Exception as e:
                        # 如果不是gzip文件，直接解析
                        data = response.json()
                else:
                    data = response.json()
            except Exception as e:
                # 直接尝试解析响应内容
                try:
                    data = response.json()
                except:
                    data = {'code': '500', 'message': f'解析响应失败: {str(e)}'}
            
            if data.get("code") != "200":
                result = f"错误：{data.get('message', '城市未找到')}"
            else:
                now = data["now"]
                weather = now["text"]
                temp = now["temp"]
                humidity = now["humidity"]
                wind_speed = now["windSpeed"]
                obs_time = now["obsTime"]
                
                result = f"{city}今天的天气是{weather}，温度{temp}°C，湿度{humidity}%，风速{wind_speed}km/h"
            
            # 更新缓存
            weather_cache[city] = {
                'result': result,
                'timestamp': current_time
            }
            
            return result
        except Exception as e:
            return f"查询天气时出错：{str(e)}"

class SearchInput(BaseModel):
    query: str = Field(description="搜索查询语句")

class SearchTool(BaseTool):
    name: str = "search"
    description: str = "使用网络搜索获取信息"
    args_schema: type = SearchInput

    def _run(self, query: str):
        from serpapi import GoogleSearch
        
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：未设置 SERPAPI_API_KEY 环境变量"
        
        try:
            params = {
                "q": query,
                "api_key": api_key,
                "num": 3
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "organic_results" in results:
                snippets = []
                for result in results["organic_results"][:3]:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    snippets.append(f"{title}: {snippet}")
                return "\n".join(snippets)
            else:
                return "未找到相关信息"
        except Exception as e:
            return f"搜索时出错：{str(e)}"