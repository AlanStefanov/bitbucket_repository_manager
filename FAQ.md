# FAQ — Bitbucket Manager

## How do I create a Bitbucket API token?
Go to https://id.atlassian.com/manage-profile/security/api-tokens and create a token. Required scopes: `repository:read`, `repository:admin`, `pullrequest:read`, `pullrequest:write`, `workspace:membership:read`.

## Where does the config get saved?
`~/.config/bitbucket-manager/env`. If it doesn't exist, the app shows an interactive config screen.

## Can I use `.env` files?
Yes. The app also reads from `.env` in the project root and `~/.bbm/.env` (legacy).

## Why `bitbucket-manager` and not `bbm` or `brm`?
`brm` was taken on PyPI (Bicycle Repair Man, 2022). `bbm` was also taken (Buzzni Batch Monitor, 2024). `bitbucket-manager` was available and better describes the scope.

## Does it work on Windows?
The app is optimized for Linux and macOS. Windows may work with WSL2 but is not officially supported.

## How do I clone a repo?
Open the Repos screen from the home menu, select a repo, and press Enter.

## How do I remove a member from a group?
Open Groups → select the group → enter the member's nickname and click "Remover".

## I found a bug, where do I report it?
https://github.com/AlanStefanov/bitbucket-manager/issues
