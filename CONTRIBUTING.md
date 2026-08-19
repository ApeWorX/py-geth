# Development

To start development for `py-geth` you should begin by cloning the repo.

```bash
$ git clone git@github.com:ApeWorX/py-geth.git
```

# Cute Animal Pictures

All pull requests need to have a cute animal picture. This is a very important
part of the development process.

# Pull Requests

In general, pull requests are welcome. Please try to adhere to the following.

- code should conform to PEP8 and pass ruff linting/formatting
- include tests.
- include any relevant documentation updates.
- include release notes in the GitHub release when publishing.

It's a good idea to make pull requests early on. A pull request represents the
start of a discussion, and doesn't necessarily need to be the final, finished
submission.

GitHub's documentation for working on pull requests is [available here][pull-requests].

Always run linting and tests before submitting pull requests:

```bash
uv run --group lint ruff check .
uv run --group lint ruff format --check .
uv run --group test pytest tests/core
```

Once you've made a pull request take a look at the GitHub Actions status in the
GitHub interface and make sure the tests are running as you'd expect.

[pull-requests]: https://help.github.com/articles/about-pull-requests
