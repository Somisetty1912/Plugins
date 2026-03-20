# SKILL: Python Best Practices

## Trigger Conditions
Automatically activate this skill when:
- Writing or modifying any `.py` file
- The user mentions "function", "class", "endpoint", "model", "service", "async", or "FastAPI"
- Generating a new Python module, route, or utility

---

## Core Knowledge

### Type Hints — Always Required
- Every function must have type hints on all parameters and return type
- Use `from __future__ import annotations` at the top of every file for forward references
- Prefer `X | None` over `Optional[X]` (Python 3.10+ syntax)
- Use `TypeAlias` for complex repeated types
- Never use `Any` unless wrapping a truly dynamic third-party interface — document why

```python
# ✅ correct
async def get_user(user_id: int) -> User | None:
    ...

# ❌ wrong
def get_user(user_id, user=None):
    ...
```

---

### Pydantic v2 Models
- Always use Pydantic for data validation — never raw `dict` for API input/output
- Use `model_config = ConfigDict(...)` not the old `class Config` inner class
- Use `Field(...)` for constraints, descriptions, and examples
- Separate schemas by purpose: `UserCreate`, `UserUpdate`, `UserResponse` — never one model for all

```python
# ✅ correct
from pydantic import BaseModel, Field, ConfigDict

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(..., description="User's email address")
    age: int = Field(..., ge=0, le=150)

# ❌ wrong
class User(BaseModel):
    class Config:
        orm_mode = True  # old v1 syntax
```

---

### Async Rules
- All FastAPI route handlers must be `async def`
- Never use `time.sleep()` inside async code — use `await asyncio.sleep()`
- Never use `requests` library inside async code — use `httpx.AsyncClient`
- Use `asyncio.gather()` to run independent async tasks concurrently, not sequentially

```python
# ✅ concurrent
user, orders = await asyncio.gather(get_user(id), get_orders(id))

# ❌ sequential (2x slower)
user = await get_user(id)
orders = await get_orders(id)
```

---

### FastAPI Patterns
- Always define a `response_model` on every route — never return raw dicts
- Use `Annotated` for dependency injection (FastAPI 0.95+ style)
- Group routes into routers (`APIRouter`) — never define routes directly on `app`
- Use `status_code` explicitly on every route decorator

```python
# ✅ correct
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse, status_code=200)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Fetch a user by ID."""
    ...
```

---

### Error Handling
- Never use bare `except:` — always catch specific exceptions
- Raise `HTTPException` in routers; raise plain exceptions in services
- Use a global exception handler in `main.py` for unhandled errors — never let stack traces reach clients
- Log errors with `logger.exception(...)` not `print()`

```python
# ✅ correct
try:
    user = await service.get_user(user_id)
except UserNotFoundError:
    raise HTTPException(status_code=404, detail="User not found")

# ❌ wrong
try:
    user = get_user(user_id)
except:
    pass
```

---

### Project Structure
```
app/
├── main.py               # FastAPI app init, middleware, routers
├── routers/              # One file per resource (user.py, invoice.py)
├── services/             # Business logic — no FastAPI imports
├── schemas/              # Pydantic models — Create, Update, Response
├── models/               # SQLAlchemy or DB models
├── dependencies/         # Reusable Depends() functions (auth, db session)
└── utils/                # Pure utility functions
tests/
├── conftest.py           # Shared fixtures
└── test_<module>.py      # One test file per module
```

---

### What to Avoid
| ❌ Avoid | ✅ Use instead |
|---|---|
| Mutable default args `def f(x=[])` | `def f(x: list \| None = None)` |
| `requests` in async code | `httpx.AsyncClient` |
| `pickle` for serialization | `json` or `msgpack` |
| `eval()` on any input | Parse explicitly |
| `print()` for logging | `logging.getLogger(__name__)` |
| `os.system()` | `subprocess.run(..., shell=False)` |
| `yaml.load()` | `yaml.safe_load()` |
| Raw SQL f-strings | SQLAlchemy ORM or parameterized queries |
