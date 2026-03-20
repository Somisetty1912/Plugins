# /generate-endpoint

Scaffold a fully typed FastAPI endpoint with Pydantic models, dependency injection, error handling, and a matching pytest test.

## What this command does

Given a resource name and HTTP method, generate:
1. **FastAPI router** — with Pydantic request/response models, dependency injection, and HTTPException handling
2. **Pydantic schemas** — `Create`, `Update`, and `Response` schemas for the resource
3. **Service layer** — a plain Python class with business logic, separate from the router
4. **pytest test** — using `TestClient` with at least a happy path and one error case

## Usage

```
/generate-endpoint <resource> <method> <purpose>
```

### Rules:
- **purpose**: is the how the endpoint will be used

### Examples
```
/generate-endpoint user GET         → GET /users/{user_id}
/generate-endpoint invoice POST     → POST /invoices
/generate-endpoint product DELETE   → DELETE /products/{product_id}
```

## Output Format

Generate 4 files:

### 1. `app/routers/<resource>.py`
```python
from fastapi import APIRouter, Depends, HTTPException
# ... full implementation
```

### 2. `app/schemas/<resource>.py`
```python
from pydantic import BaseModel, Field
# Create, Update, Response schemas
```

### 3. `app/services/<resource>_service.py`
```python
class <Resource>Service:
    # business logic, no FastAPI imports here
```

### 4. `tests/test_<resource>.py`
```python
from fastapi.testclient import TestClient
# happy path + error case
```

## Rules
- Always use `async def` for route handlers
- Always use Pydantic v2 syntax (`model_config`, `Field`, not `class Config`)
- Return types must always be annotated with the Response schema
- Use `Annotated[..., Depends(...)]` for dependency injection (FastAPI v0.95+ style)
- Service layer must have zero FastAPI imports — pure Python only
- Add docstrings to all route handlers (they become OpenAPI descriptions)
