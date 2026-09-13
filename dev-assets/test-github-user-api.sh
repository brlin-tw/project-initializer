#!/usr/bin/env bash
# Test the GitHub /user API endpoint with an authentication token
#
# Copyright 2026 林博仁(Buo-ren Lin) <buo.ren.lin@gmail.com>
# SPDX-License-Identifier: CC-BY-SA-4.0

init(){
    local token=""
    local api_url="https://api.github.com"

    if test "${#script_args[@]}" -gt 0; then
        token="${script_args[0]}"
    elif test -v GITHUB_TOKEN; then
        token="${GITHUB_TOKEN}"
    else
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

    printf \
        'Info: Testing GitHub /user API endpoint at "%s"...\n' \
        "${api_url}"

    if ! test_github_user_endpoint "${api_url}" "${token}"; then
        printf \
            'Error: GitHub /user API test failed.\n' \
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
    realpath
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
if test "${flag_required_command_check_failed}" == true; then
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

test_github_user_endpoint(){
    local api_url="${1}"; shift
    local token="${1}"; shift

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

    local response
    if ! response="$(
        curl \
            --silent \
            --show-error \
            --write-out '\n%{http_code}' \
            --header "Accept: application/vnd.github+json" \
            --header "Authorization: Bearer ${token}" \
            --header "X-GitHub-Api-Version: 2026-03-10" \
            "${api_url%/}/user"
        )"; then
        printf \
            'Error: curl request to GitHub API failed to execute.\n' \
            1>&2
        return 1
    fi

    local http_code="${response##*$'\n'}"
    local response_body="${response%$'\n'*}"

    if test "${http_code}" -ne 200; then
        printf \
            'Error: GitHub API returned unexpected HTTP status %s.\n' \
            "${http_code}" \
            1>&2
        printf \
            'Response payload:\n%s\n' \
            "${response_body}" \
            1>&2
        return 1
    else
        printf \
            'Info: Successfully authenticated with GitHub API (HTTP 200).\n'
        printf \
            'Response payload:\n%s\n' \
            "${response_body}"
    fi

    return 0
}

init
