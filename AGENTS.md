# Agent instructions

## Language

- Write all project text in English, including UI text, messages, comments,
  docstrings, and documentation. Chat replies may use the user's language.

## Approach

- Consider the project as a whole when answering questions or making changes.
  The open file and selected text are context, not the entire task scope.
- Think through the goal, existing code, and consequences before making changes.
- Challenge proposals that are incorrect or unnecessarily complicated. Explain
  the concrete issue and suggest a better approach when one is available.
- Keep changes small and appropriate for this project. Prefer clear,
  straightforward code and avoid abstractions without a current need.

## Formatting

- Keep source code and Markdown lines at most 88 characters long.

## Documentation

- Write documentation in English, primarily for AI coding agents.
- Keep documentation minimal, concrete, and consistent with the current code.
- Split documentation into focused files by topic.

## Tests

- Keep tests minimal and focused on meaningful behavior and failure cases.
- Avoid redundant tests and tests that merely repeat the implementation.

## Database migrations

- Create migrations only when the user explicitly requests them. Adding or
  changing models does not authorize creating migrations.

## Running the project

- When asked to run the project, follow `docs/launch.md`.
- If the launch instructions are empty or incomplete, explain what is missing
  before proceeding.
