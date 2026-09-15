# 🤖 AI Website Generator
AI Website Generator is a high-performance, asynchronous web application powered by FastAPI that transforms natural
language prompts into fully functional websites. By bridging the gap between generative AI and modern web technologies,
this service allows users to generate clean HTML, CSS, and JavaScript code instantly from a simple text description.


## 📌 Table of Contents
- [⚙️ Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🛠️ Installation and Setup](#-installation-and-setup)
- [🚀 Quick Start Guide](#-quick-start-guide)
  - [Development Server Launch](#development-server-launch)


## ⚙️ Tech Stack
- **Operating System:** Linux, macOS, or Windows
- **Language:** `Python 3.13+`
- **Python Package Manager:** `uv`
- **Validation & Configuration:** `pydantic` & `pydantic-settings`
- **Asynchronous Framework:** `FastAPI`


## 📁 Project Structure
```text
.
├── src/                       # Main application source code folder
│   └── main.py                # Main application entry point
├── .editorconfig              # Consistent coding styles across different IDEs
├── .pre-commit-config.yaml    # Automates Git hooks to check code before commits
├── Makefile                   # Short commands for installation, testing, and running
├── pyproject.toml             # Main configuration file for project metadata and tools
├── ruff.toml                  # Custom rules for the Ruff linter and formatter
└── uv.lock                    # Lockfile ensuring deterministic and reproducible dependencies
```


## 🛠️ Installation and Setup
### Prerequisites:
- [Git SCM](https://git-scm.com/)
- [GNU Make](https://www.gnu.org/software/make/)
- [uv](https://docs.astral.sh/uv/)

### Platform-Specific Setup
#### Linux / macOS:
To run the application, you will need the command-line versions of `Git` and `Make`.
Consult the official websites above for installation instructions.

You can check whether these programs are installed using the following commands:
```bash
git --version
make --version
```

#### Windows:
For Windows users, it is also necessary to install the `Git` command-line tools.
Additionally, you need to install `make` within `Git Bash`:
- Go to the [ezwinports](https://sourceforge.net/projects/ezwinports/files/) website.
- Find and download `make-4.4.1-without-guile-w32-bin.zip`.
- Extract the archive.
- Copy the contents of the archive to `C:\ProgramFiles\Git\mingw64\` or to the location where `Git` was installed,
**WITHOUT** overwriting or replacing any nested files.

**Run all subsequent commands from `Git Bash`.**

### Backend Setup
#### 1. Clone the repository:
```bash
git clone https://github.com/...
cd project-directory
```

#### 2. Set up a virtual environment:
[uv](https://docs.astral.sh/uv/) is used as the package manager for the project.

[Install uv](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/Uv-package-manager#1-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-uv) and in the root of the repository run the command:
```bash
uv sync
```

After that, activate the virtual environment in the current terminal session:
```bash
source .venv/bin/activate  # on Linux / macOS / Windows (via Git Bash)
.venv\Scripts\activate  # on Windows
```

### Frontend Setup
You can find instructions on how to set up the frontend in the [CONTRIBUTING.md](./CONTRIBUTING.md#frontend-setup) file, under the "Frontend Setup" section.


## 🚀 Quick Start Guide
### Development Server Launch
From the project's root directory, you can launch the project with the following command:
```bash
fastapi dev src/main.py
# or
make run-dev
```

Instructions and reference information regarding application development are collected in the [CONTRIBUTING.md](./CONTRIBUTING.md) file.
