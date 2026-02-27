from langchain_classic.memory import ConversationBufferMemory

def create_memory():
    """创建上下文记忆"""
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        input_key="input",
        output_key="output"
    )
    return memory