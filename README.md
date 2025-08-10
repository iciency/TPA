# Endstone TPA Plugin

A simple Teleport Request plugin for Endstone Minecraft Bedrock servers.

## Features

-   Request to teleport to another player.
-   Accept or deny teleport requests.

## Commands

-   `/tpa <player>`: Sends a teleport request to the specified player.
-   `/tpaccept`: Accepts a pending teleport request.
-   `/tpdeny`: Denies a pending teleport request.

## Permissions

-   `tpa.command.tpa`: Allows usage of the `/tpa` command. (Default: true)
-   `tpa.command.tpaccept`: Allows usage of the `/tpaccept` command. (Default: true)
-   `tpa.command.tpdeny`: Allows usage of the `/tpdeny` command. (Default: true)

## Installation

1.  Download the latest release from the [releases page](https://github.com/iciency/TPA/releases).
2.  Place the `.whl` file into your server's `plugins` directory.
3.  Restart the server.
