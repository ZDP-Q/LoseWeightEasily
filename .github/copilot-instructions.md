# GitHub Copilot Instructions for LossWeightEasily

This document provides context and instructions for AI agents working on the `LossWeightEasily` codebase.

## 🏗️ Architecture & Core Concepts

This project is a food nutrition search engine using **FAISS** for vector similarity search and **SQLite** for detailed data storage.

### Key Components
- **`src/loss_weight/search.py`**: The core search engine. It combines:
  - **`sentence-transformers`**: Generates embeddings for queries (supports multilingual: en/zh).
  - **`faiss`**: Stores vectors for fast retrieval.
  - **Metadata**: A companion `pickle` file (`food_metadata.pkl`) maps FAISS IDs back to food IDs/names.
- **`src/loss_weight/database.py`**: Manages the SQLite database (`food_data.db`).
  - Handles import from the raw USDA JSON dump (`data/FoodData_...json`).
  - Stores relational data: Foods, Nutrients, Portions.
- **`src/loss_weight/config.py`**: Centralized configuration using `os.getenv` with `LOSS_` prefix.

### Data Flow
1. **Raw Data**: `data/*.json` (USDA FoodData Central).
2. **Import**: `init` command parses JSON -> SQLite.
3. **Indexing**: `init` (or dynamic build) fetches text from SQLite -> Embeddings -> FAISS Index.
4. **Query**: User Input -> Embedding -> FAISS Search -> SQLite Lookup (for details).

## 🚀 Workflows & Commands

**Package Manager**: This project uses `uv` for dependency management.

### Common Tasks
- **Install/Sync**: `uv sync`
- **Run CLI**: `uv run loss-weight [command]` or `uv run python -m loss_weight`
- **Tests**: `uv run pytest`
- **Initialize Data**: `uv run loss-weight init` (Crucial first step!)
- **Rebuild Index**: `uv run loss-weight build-index --force`

### Debugging Notes
- The embedding model (`paraphrase-multilingual-MiniLM-L12-v2`) is downloaded on the **first run**. This may cause a delay or timeout.
- Ensure `food_index.faiss` and `food_metadata.pkl` are always in sync. If in doubt, rebuild the index.

## 📝 Coding Standards & Conventions

- **Language**: Core logic and comments in **Python**. Docstrings and user-facing output in **Chinese** (Simplified).
- **Type Hinting**: Use strict type hints (`typing` module) for all function signatures.
- **Path Handling**: Always use `pathlib.Path`, never string concatenation for paths.
- **Async**: The current architecture is **synchronous**. Do not introduce `async/await` unless refactoring the entire CLI/API boundary.

### Specific Patterns
- **Lazy Loading**: The `FoodSearchEngine` loads the heavy ML model lazily in the `model` property to allow quick CLI startup for non-search commands.
- **Configuration**: Access settings via `from .config import config`. Do not hardcode paths or constants.

## 🧪 Testing Strategies

- **Unit Tests**: Located in `tests/`.
- **Mocking**: Mock `faiss` and `sentence_transformers` in unit tests to avoid loading heavy models or requiring the large dataset.
- **Integration**: Real data tests should check `config.database_exists()` before running.
