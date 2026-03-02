# StructUI Testing Specifications & Architecture

## Overview
This specification mandates the testing philosophy and architectural patterns for the StructUI test suite. All contributions must adhere to these standards to ensure the stability and reliability of the application.

## Core Requirements

- **Framework:** Use `pytest` as the primary testing framework.
- **Coverage Goal:** A minimum of **85% line coverage** is strictly enforced via `pytest-cov`. Commits dropping coverage below this threshold will fail the CI pipeline.

## Testing Strategies

### 1. Data Parsing & I/O Isolation
- **Mocking:** Use `pytest-mock` to isolate file I/O operations from parser logic.
- Unit tests for the parser and state manager must not rely on the physical filesystem unless explicitly testing file I/O edge cases.

### 2. Headless UI Testing
- **Approach:** Specify and utilize headless UI testing techniques (e.g., using native framework hooks or libraries like `selenium` or NiceGUI's internal test client) to simulate user inputs, button clicks, and validation triggers without rendering a physical window.
- The goal is to mathematically prove that UI interactions correctly mutate the internal `AppState` according to the schema.

### 3. Schema Fixtures
- All test environments must use standard fixtures located in `tests/fixtures/`.
- **Requirements:** You must create and maintain a standard set of complex schema fixtures testing deeply nested containers, strict type validations, and edge-case data scenarios.
