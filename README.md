# fast-simple-crud

FastAPI demo: REST CRUD, SSE, WebSocket

## 📦 Installation

```bash
# From GitHub
pip install git+https://github.com/yourname/fast-simple-crud.git

# For development
git clone https://github.com/yourname/fast-simple-crud.git
cd fast-simple-crud
pip install -e ".[dev]"
pre-commit install
```

## 🚀 Usage

```python
from fast_simple_crud import Client

async with Client() as client:
    result = await client.request()
```

## 🛠️ Development

```bash
ruff check .      # Linting
ruff format .     # Formatting
mypy src          # Type checking
pytest            # Tests
```

## 📋 Standards

- ✅ Strict typing (mypy strict)
- ✅ 80%+ test coverage
- ✅ Auto-formatting (ruff)
- ✅ Secret detection
