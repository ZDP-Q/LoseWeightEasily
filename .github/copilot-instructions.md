# GitHub Copilot Instructions for LossWeightEasily

This document provides essential context for AI agents working on the `LossWeightEasily` codebase - a health management tool with food search, weight tracking, BMR calculation, and AI meal planning.

## 🏗️ Architecture & Core Concepts

### Multi-Layer Application Structure
This is **both** a CLI tool and a PySide6 GUI application sharing the same backend:
- **CLI Entry**: `loss-weight` command → `src/loss_weight/cli.py:main()`
- **GUI Entry**: `loss-weight-ui` command → `src/loss_weight/ui/__init__.py:main()`

### Design Patterns

#### Dependency Injection Container
The project uses a centralized dependency injection container (`container.py`) for managing services:

```python
from .container import get_database, get_search_engine, get_settings

# Get services via container
db = get_database()
engine = get_search_engine()
settings = get_settings()
```

**Key Container Functions**:
- `get_container()` - Returns the singleton `ServiceContainer` instance
- `get_database()` - Returns `DatabaseManager` instance
- `get_search_engine()` - Returns `FoodSearchEngine` instance
- `get_weight_tracker()` - Returns `WeightTracker` instance
- `get_meal_planner()` - Returns `MealPlanner` instance
- `get_settings()` - Returns `Settings` instance

The container uses `@cached_property` for lazy initialization of services.

#### Pydantic Data Models
All data structures use Pydantic v2 models (`models.py`) for validation and type safety:

```python
from .models import (
    Food, Nutrient, FoodNutrient, FoodPortion,
    FoodSearchResult, FoodCompleteInfo,
    WeightRecord, WeightRecordCreate, WeightStatistics,
    BMRInput, BMRResult, TDEEResult,
    MealPlanRequest, MealPlanResponse,
    DatabaseStatistics, SearchQuery
)
```

All models include `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.

#### Lazy Imports for Fast Startup
Heavy dependencies are imported lazily using `TYPE_CHECKING`:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import faiss
    from sentence_transformers import SentenceTransformer

# Import at runtime only when needed
def _load_model(self):
    import faiss
    from sentence_transformers import SentenceTransformer
    # ...
```

### Data & Search Pipeline
**FAISS Vector Search + SQLite Storage Pattern**:
1. **Raw Data**: USDA FoodData Central JSON (`data/FoodData_Central_foundation_food_json_2025-12-18.json`)
2. **Import**: `loss-weight init` → Parses JSON → 4 SQLite tables (`foods`, `nutrients`, `food_nutrients`, `food_portions`)
3. **Indexing**: Text from SQLite → `sentence-transformers` embeddings → FAISS index (`.faiss` + `.pkl` metadata)
4. **Query**: User input → Embedding → FAISS KNN → SQLite detail lookup

**Critical Files**:
- `models.py`: Pydantic data models for all entities
- `container.py`: Dependency injection container with lazy service loading
- `config.py`: Pydantic Settings-based configuration with nested configs
- `search.py`: `FoodSearchEngine` with lazy model loading (`@property model`)
- `database.py`: `DatabaseManager` with context manager and Pydantic returns

### Backend Components
- **`bmr.py`**: Mifflin-St Jeor equation for BMR/TDEE calculation, uses `BMRInput`/`BMRResult`/`TDEEResult` models
- **`weight_tracker.py`**: SQLite-backed weight logging, uses `WeightRecord`/`WeightStatistics` models
- **`meal_planner.py`**: OpenAI API integration, uses `MealPlanRequest`/`MealPlanResponse` models
- **`query.py`**: High-level search orchestration for CLI

### UI Architecture (PySide6)
**Page-Based Navigation with Shared State**:
- `ui/main_window.py`: `MainWindow` with `QStackedWidget` for page switching, collapsible sidebar
- `ui/pages/`: Each page inherits `BasePage` and implements `refresh_data()`
  - `dashboard.py`: StatCards showing BMR/TDEE/weight stats
  - `food_search.py`: Search box → results table
  - `bmr.py`, `weight.py`, `meal_plan.py`, `settings.py`
- `ui/styles.py`: Global constants (`COLORS`, `CARD_STYLE`, `NAV_STYLE`)

**Key Pattern**: Use container functions (`get_database()`, etc.) for service access.

## 🚀 Workflows & Commands

**Package Manager**: This project uses **`uv`** (not pip/poetry).

### Essential Commands
```bash
uv sync                              # Install dependencies
uv run loss-weight init              # FIRST RUN: Import data + build index
uv run loss-weight                   # Interactive CLI
uv run loss-weight-ui                # Launch GUI
uv run loss-weight search "番茄"      # Direct search
uv run loss-weight rebuild-index     # Rebuild FAISS index
uv run pytest                        # Run tests
uv run ruff check src/               # Lint code
uv run ruff format .                 # Format code
```

### Critical First-Run Behavior
- `init` downloads the 420MB embedding model (`paraphrase-multilingual-MiniLM-L12-v2`)
- Failure modes: Timeout (slow network), missing data JSON, SQLite locked
- Always check `settings.database_exists()` before operations

### Configuration Setup (Pydantic Settings)
Configuration uses Pydantic Settings with nested configs:

```python
from .config import get_settings

settings = get_settings()
# Access nested configs
settings.database.path  # Database path
settings.embedding.model  # Embedding model name
settings.search.similarity_threshold  # Search threshold
settings.llm.api_key  # LLM API key
```

**LLM API Required for Meal Planning**:
```yaml
# config.yaml (preferred)
llm:
  api_key: "sk-..."
  base_url: "https://api.openai.com/v1"  # or DeepSeek/GLM/Qwen
  model: "gpt-3.5-turbo"
```
Or environment variables: `LOSS_LLM_API_KEY`, `LOSS_LLM_BASE_URL`, `LOSS_LLM_MODEL`

## 📝 Coding Standards & Conventions

### Language & Localization
- **Code/comments**: English
- **User-facing strings** (print, UI labels, docstrings): **中文 (Simplified Chinese)**
- Example: `print("🔥 BMR: {bmr:.0f} kcal/天")`

### Python Patterns to Follow

1. **Type Hints Required**: All signatures use `typing` module
   ```python
   def search(self, query: str | SearchQuery, limit: int = 10) -> list[FoodSearchResult]:
   ```

2. **Pydantic Models for Data**: Use models from `models.py`
   ```python
   from .models import FoodSearchResult, BMRInput
   
   result = FoodSearchResult(fdc_id=123, description="Apple", similarity=0.95)
   input_data = BMRInput(weight=70, height=175, age=25, gender="male")
   ```

3. **Dependency Injection**: Use container functions, not direct instantiation
   ```python
   from .container import get_database, get_settings
   
   db = get_database()  # ✅
   db = DatabaseManager()  # ❌ (only for custom paths)
   ```

4. **Path Handling**: Always `pathlib.Path`, never string concatenation
   ```python
   index_path = Path(settings.index.path)  # ✅
   index_path = settings.index.path + ".bak"  # ❌
   ```

5. **Lazy Imports**: Use `TYPE_CHECKING` for heavy dependencies
   ```python
   from typing import TYPE_CHECKING
   
   if TYPE_CHECKING:
       import faiss
   ```

6. **Context Manager for DB Connections**:
   ```python
   with db_manager.get_connection() as conn:
       cursor = conn.cursor()
       # ... use connection
   # Connection auto-closed
   ```

7. **No Async/Await**: Entire architecture is synchronous. Do not mix unless refactoring all I/O.

### UI-Specific Patterns
- **Page Lifecycle**: Override `refresh_data()` for updates (called on page switch)
- **Styling**: Use constants from `styles.py`, not inline colors
- **Service Access**: Use `from ..container import get_database` for services

### Logging Patterns
The project uses a global logging system with dev/release mode separation:

```python
from .container import get_logger

logger = get_logger(__name__)
logger.debug("调试信息")  # 仅开发模式显示
logger.info("操作完成")   # 始终显示
logger.warning("警告")
logger.error("错误")
```

**Log Levels**:
- `DEBUG`: Detailed debug info (dev mode only)
- `INFO`: General operation info
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

**Configuration** (via `config.yaml` or env vars):
```yaml
logging:
  mode: "dev"      # "dev" or "release"
  level: "DEBUG"   # DEBUG, INFO, WARNING, ERROR, CRITICAL
  dir: "logs"      # Log file directory
  enable_console: true
  enable_file: true
```

**Environment Variables**: `LOSS_LOGGING__MODE`, `LOSS_LOGGING__LEVEL`

## 🧪 Testing Strategies

### Test Execution
- **Unit tests skip** if database doesn't exist: `pytest.skip("数据库不存在，跳过搜索测试")`
- **Container reset**: Call `get_container().reset()` in test fixtures
- **Clear settings cache**: Call `get_settings.cache_clear()` between tests
- **Mock heavy dependencies**: `sentence_transformers`, `faiss` in unit tests

### Test Patterns
```python
@pytest.fixture(autouse=True)
def setup(self):
    """Reset state before each test"""
    from loss_weight.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
```

### Debugging Patterns
- Enable verbose model loading: Check console for "🔄 加载多语言嵌入模型"
- Index sync issues: Delete both `.faiss` and `.pkl`, rebuild with `rebuild-index`
- SQLite locks: Use context manager `with db.get_connection() as conn:`
- **Check log files**: Logs are saved in `logs/loss_weight_YYYY-MM-DD.log`

## 🔗 External Dependencies & Integration Points

### Core Dependencies
- **Pydantic v2 + pydantic-settings**: Data validation and configuration
- **FAISS (faiss-cpu)**: Vector similarity search
- **sentence-transformers**: Text embeddings
- **PySide6**: GUI framework
- **OpenAI**: LLM API client (OpenAI-compatible endpoints)

### Data Sources
- **USDA FoodData Central**: Foundation foods dataset (JSON export)
- Must match schema: `foundationFoods[].fdcId`, `.description`, `.foodNutrients[]`, `.foodPortions[]`

### Third-Party APIs
- **OpenAI-compatible LLM**: Meal planner uses `openai` library with custom `base_url`
  - Tested with: OpenAI, DeepSeek, GLM-4, Qwen
  - Fallback: Feature gracefully unavailable if no API key

### ML Models
- **Sentence Transformers**: `paraphrase-multilingual-MiniLM-L12-v2`
  - Supports: English, Chinese, 50+ languages
  - Download: Auto from HuggingFace (first run only)
- **FAISS**: CPU version (`faiss-cpu`), uses L2 distance for similarity

## 🎯 Common Tasks & Solutions

### Adding a New Data Model
1. Add Pydantic model to `src/loss_weight/models.py`
2. Include `model_config = ConfigDict(from_attributes=True)`
3. Import and use in relevant modules

### Adding a New Service
1. Create service class in appropriate module
2. Add getter to `ServiceContainer` in `container.py` using `@cached_property`
3. Add convenience function like `get_my_service()`

### Adding a New UI Page
1. Create `src/loss_weight/ui/pages/new_page.py` inheriting `BasePage`
2. Register in `main_window.py`: Add to `self.pages`, `self.nav_buttons`
3. Implement `refresh_data()` for updates
4. Follow emoji + Chinese naming: `"📈 数据分析"`
5. Use container functions for service access

### Extending Database Schema
1. Add table in `database.py:create_tables()`
2. Add corresponding Pydantic model in `models.py`
3. Include foreign keys and indices
4. Update `import_from_json()` if sourcing from USDA data
5. **Migration**: No framework - manual SQL in version-specific update script

### Modifying Search Behavior
- Adjust `search.similarity_threshold` in `config.py` (lower = more results)
- Text preprocessing: Done in `search.py:build_index()` (combines description + category)
- Re-index required after logic changes: `rebuild-index`

## 🚨 Antipatterns to Avoid
- ❌ Do NOT add async functions (breaks CLI and GUI event loops)
- ❌ Do NOT hardcode file paths (use `settings.*` properties)
- ❌ Do NOT skip type hints (enforced by Ruff)
- ❌ Do NOT use English in UI strings (use Chinese for user-facing text)
- ❌ Do NOT bypass the container for service access
- ❌ Do NOT import heavy modules at top level (use lazy imports)
- ❌ Do NOT import from `tests/` in production code (separate test fixtures)
- ❌ Do NOT use dict returns when Pydantic models exist
