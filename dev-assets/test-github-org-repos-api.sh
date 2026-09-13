#!/usr/bin/env bash
# Test the GitHub /orgs/{org}/repos API endpoint with an authentication token
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: CC-BY-SA-4.0

init(){
    local token=""
    local org_name=""
    local repo_name=""
    local api_url="https://api.github.com"

    if test -v GITHUB_API_URL; then
        api_url="${GITHUB_API_URL}"
    fi

    if test "${#script_args[@]}" -ge 3; then
        token="${script_args[0]}"
        org_name="${script_args[1]}"
        repo_name="${script_args[2]}"
    elif test "${#script_args[@]}" -eq 2; then
        local regex_pat='^(ghp_|github_pat_)'
        if [[ "${script_args[0]}" =~ ${regex_pat} ]]; then
            token="${script_args[0]}"
            org_name="${script_args[1]}"
        elif test -v GITHUB_TOKEN; then
            token="${GITHUB_TOKEN}"
            org_name="${script_args[0]}"
            repo_name="${script_args[1]}"
        else
            token="${script_args[0]}"
            org_name="${script_args[1]}"
        fi
    elif test "${#script_args[@]}" -eq 1; then
        local regex_pat='^(ghp_|github_pat_)'
        if [[ "${script_args[0]}" =~ ${regex_pat} ]]; then
            token="${script_args[0]}"
        elif test -v GITHUB_TOKEN; then
            token="${GITHUB_TOKEN}"
            org_name="${script_args[0]}"
        else
            token="${script_args[0]}"
        fi
    elif test -v GITHUB_TOKEN; then
        token="${GITHUB_TOKEN}"
    fi

    if test -z "${org_name}"; then
        if test -v GITHUB_ORG; then
            org_name="${GITHUB_ORG}"
        elif test -v GITHUB_ORGANIZATION; then
            org_name="${GITHUB_ORGANIZATION}"
        fi
    fi

    if test -z "${token}"; then
        printf \
            'Info: No token passed as argument or GITHUB_TOKEN environment variable.\n'
        printf \
            'Please enter the GitHub personal access token to test: '
        if ! read -r -s token; then
            printf \
                '\nError: Unable to read authentication token from standard input.\n' \
                1>&2
            exit 1
        fi
        printf '\n'
    fi

    if test -z "${token}"; then
        printf \
            'Error: GitHub token cannot be empty.\n' \
            1>&2
        exit 1
    fi

    if test -z "${org_name}"; then
        printf \
            'Please enter the GitHub organization name to test: '
        if ! read -r org_name; then
            printf \
                '\nError: Unable to read organization name from standard input.\n' \
                1>&2
            exit 1
        fi
    fi

    if test -z "${org_name}"; then
        printf \
            'Error: GitHub organization name cannot be empty.\n' \
            1>&2
        exit 1
    fi

    if test -z "${repo_name}"; then
        local timestamp
        if ! timestamp="$(date +%s)"; then
            printf \
                'Error: Unable to determine current timestamp for default repository name.\n' \
                1>&2
            exit 1
        fi
        repo_name="test-repo-${timestamp}"
        printf \
            'Info: No repository name specified, defaulting to "%s".\n' \
            "${repo_name}"
    fi

    printf \
        'Info: Testing GitHub /orgs/%s/repos API endpoint at "%s" for repository "%s"...\n' \
        "${org_name}" \
        "${api_url}" \
        "${repo_name}"

    if ! test_github_org_repos_endpoint "${api_url}" "${token}" "${org_name}" "${repo_name}"; then
        printf \
            'Error: GitHub /orgs/%s/repos API test failed.\n' \
            "${org_name}" \
            1>&2
        exit 1
    fi

    printf \
        'Info: Operation completed without errors.\n'
    exit 0
}

printf \
    'Info: Configuring the defensive interpreter behaviors...\n'
set_opts=(
    # Terminate script execution when an unhandled error occurs
    -o errexit
    -o errtrace

    # Terminate script execution when an unset parameter variable is
    # referenced
    -o nounset
)
if ! set "${set_opts[@]}"; then
    printf \
        'Error: Unable to configure the defensive interpreter behaviors.\n' \
        1>&2
    exit 1
fi

printf \
    'Info: Checking the existence of the required commands...\n'
required_commands=(
    curl
    date
    grep
    mktemp
    realpath
    rm
    tr
)
flag_required_command_check_failed=false
for command in "${required_commands[@]}"; do
    if ! command -v "${command}" >/dev/null; then
        flag_required_command_check_failed=true
        printf \
            'Error: This program requires the "%s" command to be available in your command search PATHs.\n' \
            "${command}" \
            1>&2
    fi
done
if test "${flag_required_command_check_failed}" = true; then
    printf \
        'Error: Required command check failed, please check your installation.\n' \
        1>&2
    exit 1
fi

printf \
    'Info: Configuring the convenience variables...\n'
if test -v BASH_SOURCE; then
    # Convenience variables may not need to be referenced
    # shellcheck disable=SC2034
    {
        printf \
            'Info: Determining the absolute path of the program...\n'
        if ! script="$(
            realpath \
                --strip \
                "${BASH_SOURCE[0]}"
            )"; then
            printf \
                'Error: Unable to determine the absolute path of the program.\n' \
                1>&2
            exit 1
        fi
        script_dir="${script%/*}"
        script_filename="${script##*/}"
        script_name="${script_filename%%.*}"
    }
fi
# Convenience variables may not need to be referenced
# shellcheck disable=SC2034
{
    script_basecommand="${0}"
    script_args=("${@}")
}

printf \
    'Info: Setting the ERR trap...\n'
# Trap functions are invoked when the corresponding signal is received.
# shellcheck disable=SC2329
trap_err(){
    printf \
        'Error: The program has encountered an unhandled error and is prematurely aborted.\n' \
        1>&2
}
if ! trap trap_err ERR; then
    printf \
        'Error: Unable to set the ERR trap.\n' \
        1>&2
    exit 1
fi

test_github_org_repos_endpoint(){
    local api_url="${1}"; shift
    local token="${1}"; shift
    local org_name="${1}"; shift
    local repo_name="${1}"; shift

    if test -z "${api_url}"; then
        printf \
            'Error: API URL parameter cannot be empty.\n' \
            1>&2
        return 1
    fi
    if test -z "${token}"; then
        printf \
            'Error: Token parameter cannot be empty.\n' \
            1>&2
        return 1
    fi
    if test -z "${org_name}"; then
        printf \
            'Error: Organization name parameter cannot be empty.\n' \
            1>&2
        return 1
    fi
    if test -z "${repo_name}"; then
        printf \
            'Error: Repository name parameter cannot be empty.\n' \
            1>&2
        return 1
    fi

    local regex_identifier='^[a-zA-Z0-9._-]+$'
    if ! [[ "${org_name}" =~ ${regex_identifier} ]]; then
        printf \
            'Error: Invalid organization name "%s". GitHub organization names may only contain alphanumeric characters, hyphens, periods, and underscores.\n' \
            "${org_name}" \
            1>&2
        return 1
    fi
    if ! [[ "${repo_name}" =~ ${regex_identifier} ]]; then
        printf \
            'Error: Invalid repository name "%s". GitHub repository names may only contain alphanumeric characters, hyphens, periods, and underscores.\n' \
            "${repo_name}" \
            1>&2
        return 1
    fi

    local json_payload
    if ! json_payload="$(
        printf \
            '{"name":"%s","description":"Test repository created by test-github-org-repos-api.sh","private":false,"has_issues":false,"has_projects":false,"has_wiki":false,"has_pull_requests":false,"auto_init":false,"has_downloads":true}' \
            "${repo_name}"
    )"; then
        printf \
            'Error: Unable to generate JSON payload.\n' \
            1>&2
        return 1
    fi

    local headers_file
    if ! headers_file="$(mktemp)"; then
        printf \
            'Error: Unable to create temporary file for response headers.\n' \
            1>&2
        return 1
    fi

    local response
    if ! response="$(
        curl \
            --silent \
            --show-error \
            --dump-header "${headers_file}" \
            --write-out '\n%{http_code}' \
            --header "Accept: application/vnd.github+json" \
            --header "Authorization: Bearer ${token}" \
            --header "X-GitHub-Api-Version: 2026-03-10" \
            --header "Content-Type: application/json" \
            --data "${json_payload}" \
            "${api_url%/}/orgs/${org_name}/repos"
        )"; then
        printf \
            'Error: curl request to GitHub API failed to execute.\n' \
            1>&2
        rm -f "${headers_file}"
        return 1
    fi

    local oauth_scopes=""
    local accepted_oauth_scopes=""
    if test -f "${headers_file}"; then
        if grep -i '^x-oauth-scopes:' "${headers_file}" >/dev/null 2>&1; then
            oauth_scopes="$(grep -i '^x-oauth-scopes:' "${headers_file}" | tr -d '\r')"
        fi
        if grep -i '^x-accepted-oauth-scopes:' "${headers_file}" >/dev/null 2>&1; then
            accepted_oauth_scopes="$(grep -i '^x-accepted-oauth-scopes:' "${headers_file}" | tr -d '\r')"
        fi
        rm -f "${headers_file}"
    fi

    local http_code="${response##*$'\n'}"
    local response_body="${response%$'\n'*}"

    if test "${http_code}" -ne 201; then
        printf \
            'Error: GitHub API returned unexpected HTTP status %s.\n' \
            "${http_code}" \
            1>&2
        printf \
            'Response payload:\n%s\n' \
            "${response_body}" \
            1>&2
        if test -n "${accepted_oauth_scopes}"; then
            printf \
                '%s\n' \
                "${accepted_oauth_scopes}" \
                1>&2
        fi
        if test -n "${oauth_scopes}"; then
            printf \
                '%s\n' \
                "${oauth_scopes}" \
                1>&2
        fi

        local regex_fine_grained_pat='^github_pat_'
        local regex_classic_pat='^ghp_'
        if [[ "${token}" =~ ${regex_fine_grained_pat} ]]; then
            printf \
                '\nDiagnostic analysis:\n' \
                1>&2
            printf \
                '* The token appears to be a fine-grained personal access token (starts with "github_pat_").\n' \
                1>&2
            printf \
                '* Verify that the fine-grained personal access token was created with the resource owner set to organization "%s".\n' \
                "${org_name}" \
                1>&2
            printf \
                '* Verify that the token has the "Administration: Read and write" repository permission or organization repository creation permission.\n' \
                1>&2
            printf \
                '* If organization policy requires approval for fine-grained personal access tokens, verify that an organization administrator has approved the token.\n' \
                1>&2
        elif [[ "${token}" =~ ${regex_classic_pat} ]]; then
            printf \
                '\nDiagnostic analysis:\n' \
                1>&2
            printf \
                '* The token appears to be a classic personal access token (starts with "ghp_").\n' \
                1>&2
            printf \
                '* Ensure the token has the "repo" (or "public_repo") scope enabled.\n' \
                1>&2
            printf \
                '* Ensure the authenticated user is an active member of organization "%s" with permission to create repositories.\n' \
                "${org_name}" \
                1>&2
        fi

        return 1
    else
        printf \
            'Info: Successfully created GitHub repository "%s/%s" (HTTP 201).\n' \
            "${org_name}" \
            "${repo_name}"
        printf \
            'Response payload:\n%s\n' \
            "${response_body}"
        printf \
            'Note: If this was a test repository, remember to delete it from GitHub if no longer needed.\n'
    fi

    return 0
}

init
