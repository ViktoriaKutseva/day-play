# Day Play

A personal project for gamified task management and learning FastAPI.

## Description

This project combines task management with gamification elements while serving as a hands-on study of the FastAPI library. It implements a RESTful API for managing daily tasks with CRUD operations, built with modern Python tools and best practices.

## Features

- **Task Management**: Create, read, update, and delete tasks
- **SQLite Database**: Persistent storage using SQLModel
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Type Safety**: Full type hints with Pydantic models
- **Database Integration**: SQLModel for database operations with automatic table creation
- **RESTful API**: Clean API endpoints following REST conventions

## Tech Stack

- **FastAPI**: Web framework for building APIs
- **SQLModel**: SQL database interaction with Python type hints
- **SQLite**: Lightweight database for data persistence
- **Uvicorn**: ASGI server for running the application

## API Endpoints

- `GET /` - Welcome message
- `GET /tasks` - Retrieve all tasks
- `GET /tasks/{task_id}` - Retrieve a specific task
- `POST /tasks` - Create a new task
- `PUT /tasks/{task_id}` - Update an existing task
- `DELETE /tasks/{task_id}` - Delete a task

## Getting Started

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Visit `http://localhost:8000/docs` for interactive API documentation

## Learning Goals

- Understanding FastAPI framework and its features
- Working with modern Python async/await patterns
- Database integration with SQLModel
- Building RESTful APIs with proper HTTP status codes
- Type safety and validation with Pydantic models

## Project Status

This is a personal learning project and is actively being developed as I explore FastAPI capabilities and best practices.