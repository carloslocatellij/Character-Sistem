---
name: copilot-instructions
description: "Workspace instructions for the Character-Sistem Python RPG online simulator project. Use when editing game domain logic, CLI flows, tests, persistence models, or documentation."
applyTo:
  - "**/*.py" ,
  - "**/*.md"
---

## Project Overview

SisCharlesRpg is a RPG Online Online Creator focused on RPG game creation, battle simulation, and persistence using SQLAlchemy. The project currently exposes a CLI entrypoint in `rpg_api/main_cli.py` and implements core game mechanics in `rpg_api/app/core/`.

- The goal in this project is to be a system which the user can make your own game by create your cenarios in form off a maps tree inherity. Each map contains a set off events that can interate with the plasye's personage and allow a game logic. 
- In the future, we will be can connect online users and allow them chat, share your scenarios ech other and play the same game in a team.
- The project is primarily a Python backend/domain project, with the CLI as the active interface.

## Key Areas

- `rpg_api/main_cli.py`
  - primary CLI entrypoint and database session lifecycle
  - maps SQLAlchemy `PersonagemDB` records into pure domain `Personagem` objects
  - should remain the place for user interaction logic, not battle formulas

- `rpg_api/app/core/personagens.py`
  - domain model for `Raca`, `ClasseRPG`, and `Personagem`
  - implements attribute totals, hp/mp formulas, attack/damage mechanics, and effect handling
  - preserves separation between core rules and CLI persistence

- `rpg_api/app/core/` other modules
  - `equipamentos.py`: weapons, armor, shields, and item abstractions
  - `habilidades_magias.py`: spells, abilities, and effect objects

- `rpg_api/app/views/`
  - `map_manager_screen.py`: map editor and game events management
  - `game_play_screen.py`: view screen to play the game   
  - `simulador.py`: combat simulation orchestrator

- `rpg_api/app/models/` and `rpg_api/app/db/`
  - SQLAlchemy models and database initialization
  - keep DB-specific schema and relationships separate from domain class logic

## Test and Development Commands

- Install dependencies:
  - `pip install -r requirements.txt`

- Run tests from the repo root:
  - `python -m pytest`

- Launch the CLI for manual testing:
  - `python -m rpg_api.main_cli`

## Conventions

- Keep business logic in `app/core/` and persistence logic in `app/models/`.
- Do not add direct CLI input/output inside domain classes.
- Use `MANUAL.md` as the source of truth for formulas and game balance comments.
- `pytest.ini` already sets `pythonpath = ./rpg_api`, so tests should run from the repository root.

## Current Implementation Notes


- Todo:
- `rpg_api/app/main.py` exists but is currently empty.
- `rpg_api/app/routers/__init__.py` is present but no FastAPI routes are implemented yet.

## When to Use These Instructions

- editing or extending combat formulas, character attributes, or magic systems
- changing CLI behavior, command flows, or database mapping
- adding new tests, refactoring existing tests, or updating project documentation
- evaluating whether a change belongs in the domain layer versus the CLI layer

## Documentation References

- `Readme.md` — project summary and purpose
- `MANUAL.md` — design notes and game mechanics formulas
