# /review-module

Review the specified Python module for quality, correctness, and best practices.

## What this command does

1. Reads the target `.py` file
2. Checks for the following issues:
   - Mutable default arguments (e.g., `def foo(items=[])`)
   - Bare `except:` clauses that swallow all errors silently
   - Missing type hints on function signatures
   - Functions longer than 40 lines (suggest splitting)
   - Missing docstrings on public functions and classes
   - Hardcoded credentials or config values (URLs, passwords, tokens)
   - Synchronous blocking calls inside `async def` functions (e.g., `time.sleep`, `requests.get`)
   - Missing `__all__` in modules intended as public APIs
3. Checks Pydantic model definitions for missing validators
4. Flags any direct use of `dict` where a Pydantic model would be safer
5. Outputs a structured review

## Usage

```
/review-module
/review-module app/services/user_service.py
```

## Output Format

```
## Module Review: <filename>

### ✅ Passed
- <item>

### ⚠️ Warnings
- <item> — <reason and suggested fix>

### ❌ Issues
- <item> — <reason and suggested fix>

### 📋 Summary
<one paragraph summary with priority action>
```
