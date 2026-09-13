# Project Initializer

Automate the cumbersome process of creating a new project with a proper structure, licensing, and CI/CD setup.

<https://gitlab.com/brlin/project-initializer>  
[![The GitLab CI pipeline status badge of the project's `main` branch](https://gitlab.com/brlin/project-initializer/badges/main/pipeline.svg?ignore_skipped=true "Click here to check out the comprehensive status of the GitLab CI pipelines")](https://gitlab.com/brlin/project-initializer/-/pipelines) [![GitHub Actions workflow status badge](https://github.com/brlin-tw/project-initializer/actions/workflows/check-potential-problems.yml/badge.svg "GitHub Actions workflow status")](https://github.com/brlin-tw/project-initializer/actions/workflows/check-potential-problems.yml) [![pre-commit enabled badge](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white "This project uses pre-commit to check potential problems")](https://pre-commit.com/) [![REUSE Specification compliance badge](https://api.reuse.software/badge/gitlab.com/brlin/project-initializer "This project complies to the REUSE specification to decrease software licensing costs")](https://api.reuse.software/info/gitlab.com/brlin/project-initializer)

## Prerequisites

Before using the utility, ensure that you have the following:

* A POSIX-compatible operating system with Python 3.10 or later, the Python
  `venv` module, and `pip`.
* Network access to the configured GitLab and GitHub API endpoints.  When
  Telegram integration is enabled, the GitLab instance must also be able to
  reach the Telegram Bot API.
* A GitLab.com account, or an account on a GitLab 18.10 or later Self-Managed
  or Dedicated instance.  The account must be allowed to create public
  projects.
* A GitLab fine-grained personal access token with the permissions documented
  in the [GitLab permissions section](#gitlab).
* A GitHub account that is allowed to create public repositories, plus two
  fine-grained personal access tokens belonging to that same account:
    + One token for repository creation and management.
    + One token for repository mirroring.

  Both tokens must have the repository access and permissions documented in
  the [GitHub permissions section](#github).
* To optionally enable Telegram integration, a Telegram bot API token and the
  identifier of the target channel or group.  Add the bot to the target chat
  before running the utility.  For a channel, make the bot an administrator and
  grant it permission to post messages.
* A project identifier that is available in both the GitLab and GitHub
  accounts.  The utility creates new repositories and does not reuse existing
  ones.

## Installation

The following installation options are available:

### Snap package

Install the application on snap-enabled systems by running the following command in a text terminal:

```bash
sudo snap install project-initializer
```

If your projects are under the `/mnt`, `/media`, and `/run/media` directories,
run the following command to enable access to these directories from the snap:

```bash
sudo snap connect project-initializer:removable-media
```

### Source installation

Refer to the following instructions to install the utility from a source
tree (or from a Git checkout):

1. Download the release archive from the [product releases page](https://gitlab.com/brlin/project-initializer/-/releases) and extract it to a directory of your choice.
1. Launch a text terminal.
1. In the text terminal, run the following command to change the working directory to the extracted directory:

    ```bash
    cd /path/to/extracted/directory
    ```

   Replace the `/path/to/extracted/directory` placeholder text with the actual path to the extracted directory.
1. Run the following command to initialize the Python virtual environment:

    ```bash
    python3 -m venv .venv
    ```

   If you're using [uv](https://docs.astral.sh/uv/), run the following command instead:

    ```bash
    uv venv
    ```

1. Activate the Python virtual environment:

    ```bash
    source /path/to/extracted/directory/.venv/bin/activate
    ```

   Replace the `/path/to/extracted/directory` placeholder text with the actual path to the extracted directory.

   **NOTE:** This command assumes you are using a Born Again Shell (bash) or a compatible shell.  If you are using a different shell, use another environment activation script in the /path/to/extracted/directory/.venv/bin directory or refer to the documentation of your shell for the appropriate command to activate the virtual environment.
1. Install the utility in a Python virtual environment:

    ```bash
    pip install --editable /path/to/extracted/directory
    ```

   If you're using [uv](https://docs.astral.sh/uv/), run the following command instead:

    ```bash
    uv pip install -e /path/to/extracted/directory
    ```

   Replace the `/path/to/extracted/directory` placeholder text with the actual path to the extracted directory.

## Usage

Refer to the following instructions to use the utility to create a new project on GitLab and GitHub, doing various configurations and mirroring the GitLab repository to GitHub:

1. (If you're using a source installation) Activate the Python virtual environment by running the following command:

    ```bash
    source /path/to/extracted/directory/.venv/bin/activate
    ```

   Replace the `/path/to/extracted/directory` placeholder text with the actual path to the extracted directory.
1. Create a `.project-initializer.toml` configuration file from [the project-initializer.example.toml sample file](project-initializer.example.toml) in your project folder(or any accessible directory of your choice).  If you lack any fields, the utility will prompt you for them interactively.

   Refer to [the Required permissions](#required-permissions) section for the necessary GitLab and GitHub token permissions to set-up.
1. Launch a text terminal.
1. Run the following command to switch the working directory to the location of the `.project-initializer.toml` configuration file:

    ```bash
    cd /path/to/directory/containing/.project-initializer.toml
    ```

   Replace the `/path/to/directory/containing/.project-initializer.toml` placeholder text with the actual path to the directory containing the `.project-initializer.toml` configuration file.
1. Run the following command to validate the configuration and access tokens, then print the planned operations without mutating remote resources:

    ```bash
    project-initializer --dry-run
    ```

1. Run the following command to execute the remote automation:

    ```bash
    project-initializer
    ```

   The utility creates public GitLab and GitHub repositories under the
   authenticated token owners, optionally configures Telegram notifications
   and stores their values in GitHub Actions secrets/variables, and configures
   GitLab to push-mirror to GitHub.

## Required permissions

The section documents the required permissions and their rationale when applying for the GitLab and GitHub tokens to use with the utility.

### GitLab

The following fine-grained permissions are required for the GitLab personal access token:

* User
    + Groups
        - Namespace
            * Read: To retrieve the namespace ID for project creation
    + System Access
        - Personal Access Token
            * Read: To verify that the GitLab token is active
        - User
            * Read: To identify the authenticated user's namespace
    + Projects
        - Project
            * Create: To create a new project
* Group and project
    + Integrations
        - Integration:
            * Update: To create a new Telegram integration when configured
    + Project features
        - Remote Mirror
            * Create: To create a new remote mirror
    + Projects
        - Project
            * Read: To retrieve the newly created project before configuring it

The token's group and project access must include projects created after the
token was issued so that it can configure the new project's integration and
remote mirror.

Before creating either repository, the utility verifies that the GitLab token
is active, that both GitHub tokens authenticate successfully, that both GitHub
tokens belong to the same account, and that the Telegram bot token is valid
when Telegram integration is configured.  It also verifies that the project
identifier does not already exist in either account's namespace.  GitLab and
GitHub do not provide PAT self-inspection APIs that expose all fine-grained
permission grants, so the remaining permissions cannot be verified without
performing the operations that require them.

### GitHub

You need two [GitHub personal access tokens (PATs)](https://github.com/settings/personal-access-tokens/new) for the utility, one for repository creation and management, and another for repository mirroring.

The fine-grained personal access token for repository creation and management
must have access to all repositories so that it can configure repositories
created after the token was issued.  The following repository permissions are
required:

* Administration: Read and write: To create the mirror repository, update its details, and replace its topics
* Variables: Read and write: To create or update the GitHub Actions repository variable when Telegram integration is configured
* Secrets: Read and write: To create or update the GitHub Actions repository secret when Telegram integration is configured

The fine-grained personal access token for repository mirroring must also have
access to all repositories so that it can push to repositories created after
the token was issued.  The following repository permissions are required:

* Contents: Read and write: To push non-workflow content to the repository
* Workflows: Read and write: To push workflow content to the repository

## Licensing

Unless otherwise noted([comment headers](https://reuse.software/spec-3.3/#comment-headers)/[REUSE.toml](https://reuse.software/spec-3.3/#reusetoml)), this product is licensed under [the 3.0 version of the GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.html), or any of its more recent versions of your preference.

This work complies to [the REUSE Specification](https://reuse.software/spec/), refer to the [REUSE - Make licensing easy for everyone](https://reuse.software/) website for info regarding the licensing of this product.
