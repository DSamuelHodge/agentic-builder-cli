
from datetime import timedelta
from typing import List, Literal, Optional
from pydantic import BaseModel
from restack_ai.agent import agent, condition, import_functions

# Import generated functions lazily (recommended by docs)
with import_functions():
    # Example: from src.functions.llm_chat import llm_chat
    
    pass
    

class MyAgentInput(BaseModel):
    messages: List[dict] = []
    end_on_first_reply: bool = True

@agent.defn()
class MyAgent:
    def __init__(self) -> None:
        self._end: bool = False
        self._messages: List[dict] = []

    @agent.event
    async def messages(self, messages: List[dict]):
        self._messages.extend(messages)
        return {"received": len(messages)}

    @agent.event
    async def end(self):
        self._end = True
        return {"ended": True}

    @agent.run
    async def run(self, agent_input: MyAgentInput):
        # initial state from input
        self._messages = list(agent_input.messages)

        
        reply = {"text": "Hello from MyAgent!"}
        

        # optionally end immediately
        if agent_input.end_on_first_reply:
            self._end = True

        # wait for either 'end' event or continue-as-new trigger
        await condition(lambda: self._end or agent.should_continue_as_new())

        if agent.should_continue_as_new():
            await agent.agent_continue_as_new()

        return {"reply": reply}