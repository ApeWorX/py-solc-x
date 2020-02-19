# Development

To start development for py-solc-x you should begin by cloning the repo.

```bash
$ git clone https://github.com/iamdefinitelyahuman/py-solc-x.git
```

Next, ensure all dev dependencies have been installed:

```bash
pip install -r requirements-dev.txt
```

## Pull Requests

Pull requests are welcomed! Please adhere to the following:

- Ensure your pull request passes our linting checks (`tox -e lint`)
- Include test cases for any new functionality
- Include any relevant [documentation updates](README.md)

It's a good idea to make pull requests early on. A pull request represents the start of a discussion, and doesn't necessarily need to be the final, finished submission.

If you are opening a work-in-progress pull request to verify that it passes CI tests, please consider [marking it as a draft](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests#draft-pull-requests).
