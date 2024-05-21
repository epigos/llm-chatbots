# LLM ChatBots

![Backend CI](https://github.com/epigos/llm-chatbots/actions/workflows/backend-ci.yaml/badge.svg)

[![codecov](https://codecov.io/gh/epigos/llm-chatbots/graph/badge.svg?token=3KU23PETYZ)](https://codecov.io/gh/epigos/llm-chatbots)

Welcome to LMM ChatBots, this is just another LMM chatbots to allows you to create chatbots and interact with LLM
models.

# 🚀Features

- Create bots using prompt engineering.
- Interacts with the demo bots by using the UI.
- Integrate your data by uploading documents and chat with your documents.

# ⚡️Quick start

## Local Run

### Clone repository

```bash
git clone ...
```

### Build docker

```bash
make build
```

### Start server

```bash
make start
```

View the UI at http://localhost:3000

Access the API at http://localhost:8000

## Contributing

If you want to extend our Python library or if you find a bug, please open a PR!

Also be sure to test your code with the `make` command at the root level directory.

Run tests:

```bash
make test
```

### Commit message guidelines

It’s important to write sensible commit messages to help the team move faster.

Please follow the [commit guidelines](https://www.conventionalcommits.org/en/v1.0.0/)

## License

This library is released under the [MIT License](LICENSE).
