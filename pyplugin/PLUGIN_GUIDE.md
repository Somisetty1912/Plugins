# Claude Plugin Architecture Guide

Complete reference for understanding **Skills**, **Commands**, **Agents**, and **Hooks** in your pyplugin system.

---

## 📁 Quick Directory Overview

```
pyplugin/
├── skills/              # Contextual knowledge & best practices
├── commands/            # User-invoked slash commands (/command-name)
├── agents/              # Autonomous specialized subagents
├── hooks/               # Automatic event-triggered actions
└── .claude-plugin/      # Plugin metadata
```

---

## 1️⃣ SKILLS FOLDER (`/pyplugin/skills/`)

### What It Is
**Skills** are **contextual knowledge bases** that automatically activate when you work on specific file types or mention certain keywords. They inject best practices and conventions into my thinking without requiring explicit invocation.

### How It Works
- **Trigger**: Automatically when you edit `.py` files or mention relevant keywords
- **Scope**: Applies to the entire conversation session
- **Behavior**: I proactively follow the rules defined in the skill

### Files in Your Skills Folder
```
skills/
└── SKILL.md
    ├── Trigger Conditions
    ├── Type Hints Requirements
    ├── Pydantic v2 Models
    ├── Async Rules
    ├── FastAPI Patterns
    ├── Error Handling
    └── Project Structure
```

### Example: Python Best Practices Skill

**When it activates:**
```
- Writing/modifying any `.py` file
- Mentioning: "function", "class", "endpoint", "model", "service", "async", "FastAPI"
- Generating new Python modules, routes, utilities
```

**What it enforces:**
- ✅ Type hints on ALL functions (no `Any` except for valid reasons)
- ✅ Use `X | None` instead of `Optional[X]`
- ✅ Pydantic v2 with `model_config = ConfigDict(...)`
- ✅ Async functions in FastAPI with `async def`
- ✅ Never use `requests` in async code → use `httpx.AsyncClient`
- ✅ Never use bare `except:` → catch specific exceptions
- ✅ Explicit `status_code` on every route
- ✅ Use `APIRouter` not direct routes on `app`

**Example enforcement:**

```python
# ❌ Without skill: I might write
def get_user(user_id):
    user = db.query(User).get(user_id)
    return user

# ✅ With skill: I write
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Fetch a user by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### How to Use Skills
You don't invoke skills—they **automatically apply**. But you can reference them:
- "Follow the Python Best Practices skill"
- "Apply the SKILL.md rules"
- Just mention the task (write Python, FastAPI endpoint) and I apply the skill

### Adding New Skills
Create a file: `skills/SKILL-NAME.md` with:
```markdown
# SKILL: [Name]

## Trigger Conditions
- When...
- When...

## Core Knowledge
- Rule 1
- Rule 2
```

---

## 2️⃣ COMMANDS FOLDER (`/pyplugin/commands/`)

### What It Is
**Commands** are **explicit slash commands** that you invoke to trigger specific tasks. They're like shortcuts that perform structured operations with clear input/output formats.

### How It Works
- **Invocation**: You type `/command-name [arguments]`
- **Behavior**: I execute the command logic with defined parameters
- **Output**: Structured results in a specific format

### Files in Your Commands Folder

#### Command 1: `/generate-test`
**Purpose**: Generate comprehensive pytest test files
```
/generate-test <filepath>
```

**What it does:**
1. Reads your Python module
2. Identifies all public functions, classes, methods
3. Generates pytest tests covering:
   - Happy path for every function
   - Edge cases: empty input, None, zero, empty list/dict
   - Error cases: invalid types, missing fields, out-of-range values
   - Async functions with `@pytest.mark.asyncio`
   - FastAPI routes with `TestClient`
   - Mocks for all external dependencies

**Example Usage:**
```bash
/generate-test app/services/user_service.py
/generate-test app/routers/invoice.py
/generate-test app/utils/email.py
```

**Output:**
- Single file: `tests/test_<module_name>.py`
- Uses pytest fixtures (no repeated setup)
- Uses `pytest.mark.parametrize` for multiple input variations
- Test naming: `test_<function>_<scenario>`

**Example test names:**
```python
test_create_user_returns_created_user()
test_create_user_raises_if_email_exists()
test_get_user_with_invalid_id_returns_404()
```

---

#### Command 2: `/review-module`
**Purpose**: Review Python module for quality, correctness, best practices
```
/review-module [filepath]
```

**What it checks:**
1. Mutable default arguments: `def foo(items=[])`
2. Bare `except:` clauses
3. Missing type hints
4. Functions longer than 40 lines
5. Missing docstrings on public items
6. Hardcoded credentials/config values
7. Blocking calls in async functions (`time.sleep`, `requests.get`)
8. Pydantic validator coverage
9. Raw `dict` usage (should be Pydantic models)

**Example Usage:**
```bash
/review-module
/review-module app/services/user_service.py
```

**Output Format:**
```
## Module Review: <filename>

### ✅ Passed
- Item 1

### ⚠️ Warnings
- Item 2 — reason and suggested fix

### ❌ Issues
- Item 3 — reason and suggested fix

### 📋 Summary
One paragraph with priority action
```

---

#### Command 3: `/generate-endpoint`
**Purpose**: Scaffold a complete FastAPI endpoint with tests
```
/generate-endpoint <resource> <method> [purpose]
```

**What it generates:**
1. **Router** (`app/routers/<resource>.py`) — FastAPI endpoint with full typing
2. **Schemas** (`app/schemas/<resource>.py`) — Pydantic Create/Update/Response models
3. **Service** (`app/services/<resource>_service.py`) — Pure Python business logic
4. **Tests** (`tests/test_<resource>.py`) — Happy path + error cases

**Example Usage:**
```bash
/generate-endpoint user GET
/generate-endpoint invoice POST
/generate-endpoint product DELETE
```

**Output files created:**

1. **Router** (async, dependency injection, error handling):
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse, status_code=200)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Fetch a user by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

2. **Schemas** (Pydantic v2):
```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    email: str = Field(..., description="Email address")
    age: int = Field(..., ge=0, le=150)

class UserResponse(BaseModel):
    id: int
    email: str
    age: int
```

3. **Service** (no FastAPI imports):
```python
class UserService:
    async def get_user(self, user_id: int) -> User | None:
        # Pure Python business logic
        pass
```

4. **Tests** (TestClient):
```python
def test_get_user_returns_user():
    response = client.get("/users/1")
    assert response.status_code == 200

def test_get_user_with_invalid_id_returns_404():
    response = client.get("/users/99999")
    assert response.status_code == 404
```

---

### How to Use Commands
Simply type the command in your message:

```
User: /generate-test app/services/user_service.py

User: /review-module app/routers/invoice.py

User: /generate-endpoint product POST
```

The command executes automatically with the arguments you provide.

---

## 3️⃣ AGENTS FOLDER (`/pyplugin/agents/`)

### What It Is
**Agents** are **autonomous specialized subagents** that are invoked to handle complex, multi-step tasks independently. Unlike commands (which I execute), agents are **separate AI instances** with their own:
- Specialized system prompt (custom instruction set)
- Defined tools access (not all tools available)
- Permissions and constraints
- Model choice

### How It Works
- **Invocation**: You mention `@agent-name` in a message or I call it with specific task
- **Behavior**: The agent works independently with its own tools and constraints
- **Output**: Returns results back to the main conversation
- **When useful**: Complex analysis, security audits, parallel work

### Files in Your Agents Folder

#### Agent: `security-auditor`
**Purpose**: Autonomous security code review agent
```
@security-auditor
```

**System Prompt Expertise:**
- Application security engineer specializing in Python/FastAPI
- Audits code for vulnerabilities, leaked secrets, insecure dependencies
- Checks OWASP Top 10 issues specific to Python/FastAPI

**What it audits:**

1. **Secrets & Credentials**
   - Hardcoded API keys, tokens, passwords in source files
   - Secrets from `os.environ` without fallback checks
   - Secrets being logged via `logging` or `print`

2. **Injection Vulnerabilities**
   - Raw SQL with f-strings/% formatting (must use parameterized queries)
   - `eval()` or `exec()` with user input
   - `subprocess.shell=True` with user input (shell injection)
   - Unvalidated user input in file paths
   - SSRF: HTTP calls to user-supplied URLs without allowlist

3. **FastAPI-Specific**
   - Routes missing authentication dependencies
   - Missing rate limiting on `/login`, `/register`, `/token`
   - Overly permissive CORS: `allow_origins=["*"]`
   - Response models not set (leaking internal fields)
   - Unhandled exceptions returning 500s with stack traces

4. **Deserialization Issues**
   - `pickle.loads()` on untrusted data (RCE!)
   - `yaml.load()` without `Loader=yaml.SafeLoader`
   - `json.loads()` then `eval()`

5. **Dependencies**
   - Known vulnerable packages (from requirements.txt/pyproject.toml)
   - Weak crypto: `hashlib.md5` or `hashlib.sha1` for passwords

**Tools it can use:**
- `read_file` — inspect code
- `list_directory` — explore structure
- `bash` — run security scanners (pip-audit, bandit, grep)

**Bash permissions:**
```
✅ Allowed:
  - pip-audit
  - bandit -r
  - grep -r
  - cat requirements*.txt
  - cat pyproject.toml

❌ Denied:
  - rm
  - curl
  - wget
  - pip install
```

**How to invoke:**
```
@security-auditor please audit my FastAPI app for vulnerabilities

User: I just finished this auth endpoint, can you review it with @security-auditor?

User: @security-auditor check app/routers/ for OWASP issues
```

**Output format:**
```
## Security Audit Report

### 🔴 Critical
- Issue 1 (file:line) — explanation

### 🟠 High
- Issue 2

### 🟡 Medium
- Issue 3

### 🟢 Low / Informational
- Issue 4

### ✅ No issues found in:
- auth_service.py
```

---

## 4️⃣ HOOKS FOLDER (`/pyplugin/hooks/`)

### What It Is
**Hooks** are **automated event-triggered actions** that execute code whenever specific events happen. They're like background jobs that watch for changes and run actions automatically.

### How It Works
- **Event**: Triggers when specific conditions are met (e.g., file written, command executed)
- **Condition Matching**: Uses glob patterns and tool filters
- **Action**: Automatically runs bash commands, Python scripts, or other operations
- **No invocation needed**: Hooks are passive—you don't call them

### Files in Your Hooks Folder

#### Hook: `auto-format-on-write`
**Purpose**: Auto-format Python files after I write them

```json
{
  "id": "auto-format-on-write",
  "description": "Run ruff format on any .py file after Claude writes to it",
  "event": "PostToolUse",
  "matcher": {
    "tool": "Write",
    "filePattern": "\\.py$"
  },
  "action": {
    "type": "bash",
    "command": "ruff format \"${filePath}\" && ruff check --fix --quiet \"${filePath}\"",
    "timeoutMs": 10000,
    "onFailure": "warn",
    "displayOutput": true
  }
}
```

**How it works:**
1. **Event**: `PostToolUse` — After I use the Write tool
2. **Matcher**:
   - Tool must be `Write`
   - File must end in `.py`
3. **Action**:
   - Run `ruff format` on the file
   - Run `ruff check --fix` to apply fixes
   - Timeout after 10 seconds
   - If it fails, show a warning
   - Display the output

**What happens when I write a Python file:**
```
User: Create a FastAPI endpoint

Claude: (uses Write tool to create app/routers/user.py)

Hook triggers → auto-format-on-write activates

Result: Code is automatically formatted with ruff before you see it
```

### Hook Structure

Every hook needs:
```json
{
  "id": "unique-hook-identifier",
  "description": "Human-readable description",
  "event": "PostToolUse|PreToolUse|OnToolFailure|OnCompletion",
  "matcher": {
    "tool": "ToolName",
    "filePattern": "regex pattern",
    "command": "optional regex"
  },
  "action": {
    "type": "bash|notification|custom",
    "command": "the command to run",
    "timeoutMs": 10000,
    "onFailure": "warn|error|ignore",
    "displayOutput": true
  }
}
```

### Hook Events

| Event | When | Example |
|-------|------|---------|
| `PostToolUse` | After a tool succeeds | After I write a file, run formatter |
| `PreToolUse` | Before a tool executes | Before I delete a file, confirm |
| `OnToolFailure` | When a tool fails | When bash command errors, notify |
| `OnCompletion` | When task is fully complete | When I finish implementation, commit |

### Adding New Hooks

To auto-run tests after I write test files:
```json
{
  "id": "auto-test-on-write",
  "description": "Run pytest when test files are written",
  "event": "PostToolUse",
  "matcher": {
    "tool": "Write",
    "filePattern": "^tests/test_.*\\.py$"
  },
  "action": {
    "type": "bash",
    "command": "pytest ${filePath} -v",
    "timeoutMs": 30000,
    "onFailure": "warn",
    "displayOutput": true
  }
}
```

---

## 🎯 SIDE-BY-SIDE COMPARISON

### Skills vs Commands vs Agents vs Hooks

| Aspect | **Skills** | **Commands** | **Agents** | **Hooks** |
|--------|-----------|----------|----------|----------|
| **Invocation** | Automatic | `/command-name` | `@agent-name` | Automatic |
| **Scope** | Passive guidance | Single execution | Independent task | Event-triggered |
| **Purpose** | Best practices | Structured tasks | Complex analysis | Automation |
| **Tools available** | None (I use my tools) | My tools | Subset of tools | Bash only (usually) |
| **Runs independently** | No | No | Yes | Yes |
| **Example** | "Always use type hints" | `/generate-test` | `@security-auditor` | "Auto-format on write" |
| **Who invokes** | Me (automatic) | You (explicit) | You (mention name) | System (automatic) |
| **Output** | Applied to my responses | Structured output | Report/findings | Side effects |
| **Parallel execution** | N/A | Sequential | Can run in parallel | Concurrent |

### Decision Tree: Which One Should I Use?

```
Need best practices applied automatically?
  → SKILL ✓

Need a one-off structured task?
  → COMMAND (/generate-test, /review-module)

Need autonomous security/analysis on a complex task?
  → AGENT (@security-auditor)

Need something to auto-run when events happen?
  → HOOK (auto-format, auto-test)

Want me to do something step-by-step?
  → Just ask me directly (no plugin needed)
```

---

## 🚀 HOW TO ACCESS & USE AGENTS

### Method 1: Mention the Agent Name
```
User: @security-auditor audit my new auth endpoint for vulnerabilities
```

I will:
1. Invoke the `security-auditor` agent
2. Pass your request as the task
3. Agent works independently
4. Agent returns results
5. I summarize findings in the chat

### Method 2: Request Agent Involvement
```
User: I need a security review of my FastAPI app
```

I can respond:
```
I'll invoke the @security-auditor agent to do a comprehensive security audit.
[Agent runs independently]
Agent found 3 issues:
- 🔴 Critical: Hardcoded API key in config.py:12
- 🟡 Medium: Missing rate limiting on /login
- 🟢 Low: Loose CORS settings
```

### Method 3: Multiple Agents in Parallel
```
User: Review my entire project for security and best practices

I can invoke:
- @security-auditor for security issues
- @code-reviewer (if available) for style/quality
Both run in parallel and return findings
```

### Available Agents in Your System
Currently defined:
- **@security-auditor** — Python/FastAPI security audits
  - Checks: secrets, injection, OWASP issues, dependencies
  - Tools: read_file, list_directory, bash (pip-audit, bandit)
  - Invoke: `@security-auditor audit my code`

### Adding New Agents

Create a file: `agents/your-agent.yaml`

```yaml
name: your-agent-name
description: What this agent does

model: claude-sonnet-4-20250514  # or claude-opus-4-6

system_prompt: |
  You are an expert in [domain].
  Your job is to [task].
  Always check for [things].

  Output format:
  ```
  ## Report Title
  ### Section 1
  ### Section 2
  ```

tools:
  - read_file
  - list_directory
  - bash

tool_permissions:
  bash:
    allow:
      - "command1"
      - "command2"
    deny:
      - "dangerous-command"

invoke_with: "@agent-name"
```

---

## 📊 WORKFLOW EXAMPLES

### Example 1: Generate & Test an Endpoint

```
User: Create a new endpoint for getting users

Me: I'll create it using /generate-endpoint and test it

/generate-endpoint user GET

Result: Creates 4 files (router, schemas, service, tests)

User: Does it follow best practices?

Me: /review-module app/routers/user.py

Result: Review report showing any issues
```

### Example 2: Security-First Development

```
User: Add a login endpoint

Me:
1. /generate-endpoint auth POST  → Creates endpoint
2. @security-auditor reviews it → Checks for auth issues
3. Fixes any security issues
4. /generate-test on the endpoint
5. Hook auto-formats the code
```

### Example 3: Code Review Workflow

```
User: Review my codebase

Me: Running multiple tools:
1. /review-module app/services/user_service.py → Quality check
2. /review-module app/routers/auth.py → Quality check
3. @security-auditor audit app/ → Security scan

Consolidated report with all findings
```

---

## ⚙️ CONFIGURATION REFERENCE

### skills/SKILL.md Structure
```markdown
# SKILL: Name

## Trigger Conditions
- When...
- When you mention...

## Core Knowledge
- Rule with ✅ correct and ❌ wrong examples
```

### commands/COMMAND.md Structure
```markdown
# /command-name

Brief description

## What this command does
1. Step 1
2. Step 2

## Usage
```
/command-name arguments
```

## Output Format
Format of results
```

### agents/agent.yaml Structure
```yaml
name: agent-name
description: What it does
model: model-name
system_prompt: |
  Expert instruction
tools:
  - tool1
tool_permissions:
  tool1:
    allow: [cmd1, cmd2]
    deny: [cmd3]
invoke_with: "@agent-name"
```

### hooks/hook.json Structure
```json
{
  "id": "hook-id",
  "event": "PostToolUse|PreToolUse|OnToolFailure|OnCompletion",
  "matcher": { "tool": "ToolName", "filePattern": "pattern" },
  "action": { "type": "bash", "command": "cmd", "timeoutMs": 10000 }
}
```

---

## 💡 BEST PRACTICES

1. **Use Skills** for automatic best-practice enforcement (don't remind me)
2. **Use Commands** for repeatable structured tasks (`/generate-test`, `/review-module`)
3. **Use Agents** for complex analysis that needs independence (security audits, code reviews)
4. **Use Hooks** for dev-loop automations (format, test, lint after write)
5. **Combine them**: Generate endpoint → Auto-format via hook → Test with command → Audit with agent

---

## 🔗 Quick Reference

| I want to... | Use this |
|---|---|
| Enforce Python best practices | SKILL (auto-active) |
| Generate tests | `/generate-test <file>` |
| Review code quality | `/review-module <file>` |
| Create FastAPI endpoint | `/generate-endpoint <resource> <method>` |
| Security audit | `@security-auditor audit <path>` |
| Auto-format on write | Hook (auto-active) |
| Run tests automatically | Hook (auto-active) |
