# /generate-test

Generate a comprehensive pytest test file for an existing Python module or service.

## What this command does

1. Reads the target module
2. Identifies all public functions, classes, and methods
3. Generates pytest tests covering:
   - Happy path for every public function
   - Edge cases: empty input, None, zero, empty list/dict
   - Error cases: invalid types, missing required fields, out-of-range values
   - For async functions: uses `pytest-asyncio` with `@pytest.mark.asyncio`
   - For FastAPI routes: uses `TestClient` or `AsyncClient` from `httpx`
   - Mocks all external dependencies (DB calls, HTTP calls, file I/O) using `pytest-mock`

## Usage

```
/generate-test <filepath>
```

### Examples
```
/generate-test app/services/user_service.py
/generate-test app/routers/invoice.py
/generate-test app/utils/email.py
```

## Output Format

Generate one file: `tests/test_<module_name>.py`

## Rules
- Use `pytest` fixtures for all shared setup — never repeat setup code
- Use `pytest.mark.parametrize` for functions with multiple input variations
- Mock at the boundary — mock the DB session, not internal functions
- Each test function name must follow: `test_<function>_<scenario>`
  - e.g., `test_create_user_returns_created_user`
  - e.g., `test_create_user_raises_if_email_exists`
- Always assert both the return value AND any side effects (DB calls, events fired)
- Include a `conftest.py` snippet if new fixtures are needed
