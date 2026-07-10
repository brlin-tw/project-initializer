# Project Initializer

Automate the cumbersome process of creating a new project with a proper structure, licensing, and CI/CD setup.

<https://gitlab.com/brlin/project-initializer>  
[![The GitLab CI pipeline status badge of the project's `main` branch](https://gitlab.com/brlin/project-initializer/badges/main/pipeline.svg?ignore_skipped=true "Click here to check out the comprehensive status of the GitLab CI pipelines")](https://gitlab.com/brlin/project-initializer/-/pipelines) [![GitHub Actions workflow status badge](https://github.com/brlin-tw/project-initializer/actions/workflows/check-potential-problems.yml/badge.svg "GitHub Actions workflow status")](https://github.com/brlin-tw/project-initializer/actions/workflows/check-potential-problems.yml) [![pre-commit enabled badge](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white "This project uses pre-commit to check potential problems")](https://pre-commit.com/) [![REUSE Specification compliance badge](https://api.reuse.software/badge/gitlab.com/brlin/project-initializer "This project complies to the REUSE specification to decrease software licensing costs")](https://api.reuse.software/info/gitlab.com/brlin/project-initializer)

## Usage

Install the utility in a Python virtual environment:

```console
python3 -m pip install --editable .
```

Create a local configuration from `project-initializer.example.toml`:

```console
cp project-initializer.example.toml .project-initializer.toml
```

Fill in non-secret defaults in `.project-initializer.toml`.  Missing values
will be prompted interactively, and token prompts are hidden.

Validate the planned operations without calling remote APIs:

```console
project-initializer --dry-run
```

Run the remote automation:

```console
project-initializer
```

The utility creates public GitLab and GitHub repositories under the
authenticated token owners, configures Telegram notifications, stores the
Telegram values in GitHub Actions secrets/variables, and configures GitLab to
push-mirror to GitHub.

## Licensing

Unless otherwise noted([comment headers](https://reuse.software/spec-3.3/#comment-headers)/[REUSE.toml](https://reuse.software/spec-3.3/#reusetoml)), this product is licensed under [the 3.0 version of the GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.html), or any of its more recent versions of your preference.

This work complies to [the REUSE Specification](https://reuse.software/spec/), refer to the [REUSE - Make licensing easy for everyone](https://reuse.software/) website for info regarding the licensing of this product.
