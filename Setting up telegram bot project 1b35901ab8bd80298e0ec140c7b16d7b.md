# Setting up telegram bot project

- [ ]  Git hub
    - [ ]  gitignore python
    - [ ]  license mit
- [ ]  clone to vs code
- [ ]  create structure

📂 app/                # Main application code
│   │-- 📂 models/         # Database models (OOP structured)
│   │-- 📂 services/       # Business logic (SOLID principles)
│   │-- 📂 handlers/       # Telegram bot handlers (divided for clarity)
│   │-- 📂 database/       # Database setup
│   │-- 📂 utils/          # Helper functions (DRY)
│   │-- main[.py](http://bot.py/)             # Main bot file (entry point)
│-- 📂 config/             # Configuration files
│   │-- [config.py](http://config.py/)          # Stores API keys & settings
│-- 📂 tests/

- [ ]  create **init**.py
- [ ]  fix launch.json

debug, create launch json file

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "inputs": [
        {
            "id": "pytest_keywords",
            "type": "promptString",
            "description": "Enter pytest keywords",
            "default": ""
        }
    ],
    "configurations": [
        {
            "name": "Run specific tests",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "console": "integratedTerminal",
            "args": [
                "--rootdir=tests",
                "--log-cli-level=INFO",
                "-k", "${input:pytest_keywords}"
            ],
            "env": {
                "PYTHONPATH": "${workspaceFolder}/app"
            },
        },
        {
            "name": "Run bot",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/app/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/app",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/app",
            },
        },
        {
            "name": "Launch current file",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/app"
            },
        }
    ]
}
```

- [ ]  create virtual env and select interpreter
- [ ]  create and install requirements.txt

```
aiogram
pydantic
sqlalchemy
python-dotenv
fastapi
uvicorn
```

- [ ]  create .env

```
DB_URL=sqlite:///bot.db
TELEGRAM_BOT_TOKEN=dsfffds
```

- [ ]  Connect env in config file

```jsx
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure the token exists
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing from .env file")
```

- [ ]  Initialize a Git Repository & Push to GitHub

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main

- [ ]  create models

- [ ]