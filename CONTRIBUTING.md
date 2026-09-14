# Contributing to AI Website Generator


## Application workflows
- [Local backend installation](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_local_installation.drawio.png)
- [Production backend installation](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_prod_installation.drawio.png)
- [Backend subsystem decomposition](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_decomposition.drawio.png)


## How to conduct development
### Pre-commit Hooks
The repository uses [pre-commit](https://pre-commit.com/) hooks to automatically run linters and automated tests.

At the root of the repository, within an **activated virtual environment**, run the command to configure the hooks:
```bash
pre-commit install
```
Now, every time you run `git commit`, the automated checks defined in `.pre-commit-config.yaml` will run on your staged files.
If the checks fail, the commit will be aborted with an error.

If you need to make a commit without checks, you can disable them using the `--no-verify` flag:
```bash
git commit -m "message" --no-verify
```

### Launch the application
The project code is located in the `/src` folder.

From the project's root directory, you can launch the project with the following command:
```bash
fastapi dev src/main.py
# or
make run-dev
```
The application will be available at http://127.0.0.1:8000/.

### `uv` package manager
[uv](https://docs.astral.sh/uv/) is used as the package manager.

Here is an example of how to add the `beautifulsoup4` library to the dependencies.
```bash
uv add beautifulsoup4
```
The `pyproject.toml` and `uv.lock` configuration files will be updated automatically.

You can remove Python packages in a similar way:
```bash
uv remove beautifulsoup4
```

If you need to update `uv.lock` manually, use the following command:
```bash
uv lock
```

### Quick-start commands using `make`
To display a list of frequently used short commands, use the command:
```bash
make list
```
