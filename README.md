# Project Initializer

Automate the cumbersome process of creating a new project with a proper structure, licensing, and CI/CD setup.

<https://gitlab.com/brlin/project-initializer>  
[![The GitLab CI pipeline status badge of the project's `main` branch](https://gitlab.com/brlin/project-initializer/badges/main/pipeline.svg?ignore_skipped=true "Click here to check out the comprehensive status of the GitLab CI pipelines")](https://gitlab.com/brlin/project-initializer/-/pipelines) [![GitHub Actions workflow status badge](https://github.com/brlin-tw/project-initializer/actions/workflows/check-potential-problems.yml/badge.svg "GitHub Actions workflow status")](https://github.com/brlin-tw/project-initializer/actions/workflows/check-potential-problems.yml) [![pre-commit enabled badge](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white "This project uses pre-commit to check potential problems")](https://pre-commit.com/) [![REUSE Specification compliance badge](https://api.reuse.software/badge/gitlab.com/brlin/project-initializer "This project complies to the REUSE specification to decrease software licensing costs")](https://api.reuse.software/info/gitlab.com/brlin/project-initializer)

## Prerequisites

Before using the utility, ensure that you have the following:

* A POSIX-compatible operating system with Python 3.10 or later, the Python
  `venv` module, and `pip`.
* Network access to the configured GitLab and GitHub API endpoints.  The GitLab
  instance must also be able to reach the Telegram Bot API.
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
* A Telegram bot API token and the identifier of the target channel or group.
  Add the bot to the target chat before running the utility.  For a channel,
  make the bot an administrator and grant it permission to post messages.
* A project identifier that is available in both the GitLab and GitHub
  accounts.  The utility creates new repositories and does not reuse existing
  ones.

## Usage

Refer to the following instructions to use the utility to create a new project on GitLab and GitHub, doing various configurations and mirroring the GitLab repository to GitHub.

Note that this applies to the source installation, adapt the flow accordingly if you are using a package manager installation.

1. Download the release archive from the [product releases page](https://gitlab.com/brlin/project-initializer/-/releases) and extract it to a directory of your choice.
1. Create a local configuration from `project-initializer.example.toml` named `.project-initializer.toml` in the extracted directory.  If you lack any fields, the utility will prompt you for them interactively.
1. Launch a text terminal.
1. In the text terminal, run the following command to change the working directory to the extracted directory:

    ```bash
    cd /path/to/extracted/directory
    ```

   Replace the `/path/to/extracted/directory` placeholder text with the actual path to the extracted directory.
1. Run the following command to initialize the Python virtual environment:

    ```bash
    python3 -m venv venv
    ```

1. Activate the Python virtual environment:

    ```bash
    source venv/bin/activate
    ```

   **NOTE:** This command assumes you are using a Born Again Shell (bash) or a compatible shell.  If you are using a different shell, use another environment activation script in the venv/bin directory or refer to the documentation of your shell for the appropriate command to activate the virtual environment.
1. Install the utility in a Python virtual environment:

    ```bash
    pip install --editable .
    ```

1. Validate the configuration and access tokens, then print the planned operations without mutating remote resources:

    ```bash
    project-initializer --dry-run
    ```

1. Run the remote automation:

    ```bash
    project-initializer
    ```

   The utility creates public GitLab and GitHub repositories under the
   authenticated token owners, configures Telegram notifications, stores the
   Telegram values in GitHub Actions secrets/variables, and configures GitLab to
   push-mirror to GitHub.

## Required permissions

The section documents the required permissions and their rationale when applying for the GitLab and GitHub tokens to use with the utility.

### GitLab

The following fine-grained permissions are required for the GitLab personal access token:

* User
    + System Access
        - Personal Access Token
            * Read: To verify that the GitLab token is active
    + Projects
        - Project
            * Create: To create a new project
* Group and project
    + Integrations
        - Integration:
            * Update: To create a new Telegram integration
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
is active, that both GitHub tokens authenticate successfully, and that both
GitHub tokens belong to the same account.  GitLab and GitHub do not provide
PAT self-inspection APIs that expose all fine-grained permission grants, so the
remaining permissions cannot be verified without performing the operations
that require them.

### GitHub

You need two [GitHub personal access tokens (PATs)](https://github.com/settings/personal-access-tokens/new) for the utility, one for repository creation and management, and another for repository mirroring.

The fine-grained personal access token for repository creation and management
must have access to all repositories so that it can configure repositories
created after the token was issued.  The following repository permissions are
required:

* Administration: Read and write: To create the mirror repository, update its details, and replace its topics
* Variables: Read and write: To create or update the GitHub Actions repository variable
* Secrets: Read and write: To create or update the GitHub Actions repository secret

The fine-grained personal access token for repository mirroring must also have
access to all repositories so that it can push to repositories created after
the token was issued.  The following repository permissions are required:

* Contents: Read and write: To push non-workflow content to the repository
* Workflows: Read and write: To push workflow content to the repository

## Licensing

Unless otherwise noted([comment headers](https://reuse.software/spec-3.3/#comment-headers)/[REUSE.toml](https://reuse.software/spec-3.3/#reusetoml)), this product is licensed under [the 3.0 version of the GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.html), or any of its more recent versions of your preference.

This work complies to [the REUSE Specification](https://reuse.software/spec/), refer to the [REUSE - Make licensing easy for everyone](https://reuse.software/) website for info regarding the licensing of this product.
