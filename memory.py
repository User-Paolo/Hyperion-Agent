from collections import OrderedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# History limits
MAX_HISTORY_CHARS = 6000
MAX_SESSIONS = 500


class SessionMemory:
    def __init__(self, max_chars: int = MAX_HISTORY_CHARS, max_sessions: int = MAX_SESSIONS):
        self.max_chars = max_chars
        self.max_sessions = max_sessions
        self._sessions: OrderedDict[str, list[BaseMessage]] = OrderedDict()

    def history(self, user_id: str) -> list[BaseMessage]:
        return list(self._sessions.get(user_id, []))

    def add_turn(self, user_id: str, user_text: str, reply: str) -> None:
        messages = self._sessions.pop(user_id, [])
        messages += [HumanMessage(user_text), AIMessage(reply)]
        self._sessions[user_id] = self._trim(messages)

        # Evict oldest session
        while len(self._sessions) > self.max_sessions:
            self._sessions.popitem(last=False)

    def clear(self, user_id: str) -> None:
        self._sessions.pop(user_id, None)

    def _trim(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        # Drop oldest turns
        while len(messages) > 2 and sum(len(m.content) for m in messages) > self.max_chars:
            messages = messages[2:]
        return messages
