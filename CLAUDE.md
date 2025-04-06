# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run PDF parsing: `python pdf_parser.py`
- Run RAG CLI: `python rag_cli.py --query "your question"` (utilise ./db/knowledge_graph.graphml par défaut)
- Convert PDFs: `python rag_cli.py --convert-only --graph ./cours_psychologie --db-dir ./db`
- List models: `python rag_cli.py --list-models`
- Use markdown: `python rag_cli.py --md --graph ./cours_psychologie --query "your question"`
- Specify db dir: `python rag_cli.py --db-dir ./custom_db --query "your question"`

## Directory Structure
- `./cours_psychologie/` - Contient les fichiers PDF et leurs conversions en markdown
- `./db/` - Répertoire par défaut pour stocker le graphe de connaissances

## Style Guidelines
- Language: Python 3.x with French docstrings and comments
- Imports: Group standard lib, then third-party, then local imports
- Error handling: Use try/except blocks with specific error messages
- String formatting: Use f-strings for readability
- Documentation: Use docstrings for all functions
- Types: Include type hints in function signatures
- Naming: Use snake_case for variables and functions
- File processing: Always use proper encoding (utf-8) for file operations