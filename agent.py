import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents import create_weather_agent, create_search_agent

# 加载环境变量
load_dotenv()

class WeatherAgent:
    def __init__(self):
        # 直接硬编码API密钥，移除方括号
        api_key = "sk-trvbFS2hVqfzE9qiF8Da656d31C54206A5300f8bC80d1a4e"
        
        self.llm = ChatOpenAI(
            model="glm-4.7-flash-free",
            base_url="https://aihubmix.com/v1",
            api_key=api_key,
            temperature=0.1
        )
        self.weather_agent = create_weather_agent(self.llm)
        self.search_agent = create_search_agent(self.llm)
    
    def route_query(self, query):
        """路由查询到合适的智能体"""
        # 简单的路由逻辑
        weather_keywords = ["天气", "温度", "下雨", "晴天", "预报", "气候"]
        if any(keyword in query for keyword in weather_keywords):
            return "weather"
        else:
            return "search"
    
    def process_query(self, query, chat_history=None):
        """处理用户查询"""
        agent_type = self.route_query(query)
        
        if agent_type == "weather":
            result = self.weather_agent.invoke({
                "input": query,
                "chat_history": chat_history or []
            })
        else:
            result = self.search_agent.invoke({
                "input": query,
                "chat_history": chat_history or []
            })
        
        return result["output"]