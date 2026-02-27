from langchain_classic.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from tools import WeatherQueryTool, SearchTool
from memory import create_memory

def create_weather_agent(llm):
    """创建天气专家智能体"""
    tools = [WeatherQueryTool()]
    memory = create_memory()
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True
    )
    return agent

def create_search_agent(llm):
    """创建搜索专家智能体"""
    tools = [SearchTool()]
    memory = create_memory()
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True
    )
    return agent