import os
import warnings
from dotenv import load_dotenv
from agent import WeatherAgent

# 过滤警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

# 加载环境变量
load_dotenv()

def main():
    print("🌤️  智能天气助手")
    print("=" * 50)
    print("请输入您的问题，输入 '退出' 结束对话")
    print("=" * 50)
    
    agent = WeatherAgent()
    chat_history = []
    
    while True:
        user_input = input("\n您的问题: ").strip()
        if user_input == "退出":
            print("再见！")
            break
        
        try:
            response = agent.process_query(user_input, chat_history)
            print(f"\n助手: {response}")
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"出错了: {str(e)}")

if __name__ == "__main__":
    main()