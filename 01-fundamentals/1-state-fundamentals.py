from enum import Enum

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph

# 1. State


class MyGraphState(MessagesState):
    step_count: int


# 2. Nodes


class NodeEnum(Enum):
    UserNode = "user_node"
    AINode = "ai_node"
    StepCountNode = "step_count_node"


def user_node(state: MyGraphState):
    print("Executing user node...")

    return {"messages": HumanMessage(content="What is the weather like today?")}


def ai_node(state: MyGraphState):
    print("Executing AI node...")

    last_message = state["messages"][-1].content
    print(f"Human Prompt: {last_message}")

    response_content = f'I have received your last message "{last_message}", however I am a mocked AI, I cannot use this at all'

    return {"messages": response_content}


def step_count_node(state: MyGraphState):
    updated_step_count = state["step_count"] + 1

    return {"step_count": updated_step_count}


# 3. Edges

graph = StateGraph(MyGraphState)

graph.add_node(user_node)
graph.add_node(ai_node)
graph.add_node(step_count_node)

graph.add_edge(START, NodeEnum.UserNode.value)
graph.add_edge(NodeEnum.UserNode.value, NodeEnum.AINode.value)
graph.add_edge(NodeEnum.AINode.value, NodeEnum.StepCountNode.value)
graph.add_edge(NodeEnum.StepCountNode.value, END)

# 4. Compile and build graph

agent = graph.compile()

initial_state = {"step_count": 0}
initial_state = MyGraphState(messages=[], step_count=0)

final_state = agent.invoke(initial_state)

print("--- Final State ---")
print(final_state)

