from enum import Enum
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime


class GraphState(TypedDict):
    input: str
    results: str


class ContextSchema(TypedDict):
    user_id: int


class NodeEnum(Enum):
    Plain = "plain_node"
    WithConfig = "node_with_config"
    WithRuntime = "node_with_runtime"


def plain_node(state: GraphState):
    print("Executing plain node...")

    return {"results": f"Hello, {state['input']}"}


def node_with_config(state: GraphState, config: RunnableConfig):
    print("Execunting node with config...")

    thread_id = config.get("configurable", {}).get("thread_id")

    print(f"--- Accessed thread id from config: {thread_id}")

    return {"results": "Config successful accessed"}


def node_with_runtime(state: GraphState, runtime: Runtime[ContextSchema]):
    print("Executing node with runtime...")

    user_id = runtime.context["user_id"]

    print(f"--- Accessed user_id from runtime: {user_id}")

    return {"results": f"Runtime context accessed: user_id={user_id}"}


builder = StateGraph(GraphState)

builder.add_node(NodeEnum.Plain.name, plain_node)
builder.add_node(NodeEnum.WithConfig.name, node_with_config)
builder.add_node(NodeEnum.WithRuntime.name, node_with_runtime)  # type: ignore[arg-type]

builder.add_edge(START, NodeEnum.Plain.name)
builder.add_edge(NodeEnum.Plain.name, NodeEnum.WithConfig.name)
builder.add_edge(NodeEnum.WithConfig.name, NodeEnum.WithRuntime.name)
builder.add_edge(NodeEnum.WithRuntime.name, END)

graph_context: ContextSchema = {"user_id": 12345}

graph = builder.compile()

initial_state: GraphState = {"input": "Juan Oliu", "results": ""}

run_config: RunnableConfig = {"configurable": {"thread_id": "ABC1234"}}

final_state = graph.invoke(
    initial_state,
    config=run_config,
    context=graph_context,  # type: ignore[arg-type]
)

print("--- Final state")
print(final_state)
