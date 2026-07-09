# Prompt

Implement a Python utility that prompt the following details:

* The new project's:
    + Identifier
    + Display name
    + Topic tags(only lowercase english and dashes)
* GitLab authentication token
* GitHub authentication token
* Telegram channel/group identifier
* Telegram bot token
* GitHub personal access token(PAT) for repository mirroring

and do the following automation:

1. Create a new GitLab project with correct:
    + Identifier
    + Display name
    + Topic tags
1. Create a new GitHub project with correct:

    + Identifier
    + Topic tags

   without default Git content
1. For the GitHub project, disable the following features:
    + Wikis
    + Issues
    + Projects
    + Pull requests
1. For the GitHub project, add the following Repository secrets:
    + TELEGRAM_BOT_API_TOKEN_CI: With the Telegram bot token as the value
1. For the GitHub project, add the following Repository variables:
    + TELEGRAM_CHAT_ID_CI: Telegram channel/group identifier
1. For the GitLab project, set the Telegram integration with the following parameters:
    + New token: With the Telegram bot token as the value
    + Enable all triggers
    + Channel identifer: With the Telgram channel/group identifier as the value
    + Notify on all pipeline statuses, not just broken ones
    + Notify status on all branches, not just the default branch
1. For the GitLab project, set the following push mirror settings:
    + Git repository URL: Set the GitHub repository's push URL
    + Authentication method: Username and Password
    + Username: Username of the account of the GitHub authentication token
    + Password: GitHub personal access token(PAT) for repository mirroring
1. For the GitHub project's repository details, set the following items:
    + Website: Set the GitLab project's web URL
    + Include in the home page: Only "Releases"
