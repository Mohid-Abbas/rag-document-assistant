from typing import TypedDict, Annotated, Sequence, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, FunctionMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from app.services.vector_store import VectorStoreService
from app.core.config import get_settings

settings = get_settings()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: List[str]

class AgentService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0
        )
        self.vector_store = VectorStoreService()
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    async def retrieve_node(self, state: AgentState):
        query = state["messages"][-1].content
        results = self.vector_store.similarity_search(query, k=5)
        context = [doc.page_content for doc, _ in results]
        return {"context": context}

    async def generate_node(self, state: AgentState):
        query = state["messages"][-1].content
        context_str = "\n\n".join(state["context"])
        
        system_prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.
        If the answer is not in the context, say you don't know.
        
        Context:
        {context_str}
        """
        
        messages = [
            HumanMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = await self.llm.ainvoke(messages)
        return {"messages": [response]}

    async def process_query(self, query: str):
        inputs = {"messages": [HumanMessage(content=query)], "context": []}
        result = await self.workflow.ainvoke(inputs)
        return result["messages"][-1].content
