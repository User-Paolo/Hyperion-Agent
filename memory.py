from collections import OrderedDict
from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# History limits
MAX_HISTORY_CHARS = 6000
MAX_SESSIONS = 500
MAX_TOUCHED = 5


@dataclass
class Session:
    history: list[BaseMessage] = field(default_factory=list)
    pending: list[dict] = field(default_factory=list)
    touched: list[str] = field(default_factory=list)


class SessionMemory:
    def __init__(self, max_chars: int = MAX_HISTORY_CHARS, max_sessions: int = MAX_SESSIONS):
        self.max_chars = max_chars
        self.max_sessions = max_sessions
        self._sessions: OrderedDict[str, Session] = OrderedDict()

    def history(self, user_id: str) -> list[BaseMessage]:
        session = self._sessions.get(user_id)
        return list(session.history) if session else []

    def add_turn(self, user_id: str, user_text: str, reply: str) -> None:
        session = self._session(user_id)
        session.history = self._trim(session.history + [HumanMessage(user_text), AIMessage(reply)])

    def clear(self, user_id: str) -> None:
        self._sessions.pop(user_id, None)

    def set_pending(self, user_id: str, items: list[dict]) -> None:
        self._session(user_id).pending = list(items)

    def pop_pending(self, user_id: str) -> list[dict]:
        session = self._sessions.get(user_id)
        if not session:
            return []
        items, session.pending = session.pending, []
        return items

    def touch(self, user_id: str, path: str) -> None:
        session = self._session(user_id)
        session.touched = [p for p in session.touched if p != path][-(MAX_TOUCHED - 1):] + [path]

    def touched(self, user_id: str) -> list[str]:
        session = self._sessions.get(user_id)
        return list(session.touched) if session else []

    def _session(self, user_id: str) -> Session:
        session = self._sessions.pop(user_id, None) or Session()
        self._sessions[user_id] = session

        # Evict oldest session
        while len(self._sessions) > self.max_sessions:
            self._sessions.popitem(last=False)
        return session

    def _trim(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        # Drop oldest turns
        while len(messages) > 2 and sum(len(m.content) for m in messages) > self.max_chars:
            messages = messages[2:]
        return messages
