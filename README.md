# Endstone TPA Plugin

A simple Teleport Request plugin for Endstone Minecraft Bedrock servers.

## Features

-   Request to teleport to another player (`/tpa`) or have them teleport to you (`/tpthere`).
-   Accept, deny, or cancel teleport requests.
-   Block TPA requests from specific players (`/tpablock`) or all players (`/tpaallblock`).
-   Automatically accept all TPA requests (`/tpaautoaccept`).
-   Multi-language support (English, Korean).

## Commands

-   `/tpa <player>`: Sends a teleport request to the specified player.
-   `/tpthere <player>`: Sends a request for the specified player to teleport to you.
-   `/tpaccept <player>`: Accepts a pending teleport request.
-   `/tpdeny <player>`: Denies a pending teleport request.
-   `/tpacancel <player>`: Cancels a teleport request you sent to a player.
-   `/tpablock <player>`: Toggles blocking TPA requests from a specific player.
-   `/tpaallblock`: Toggles blocking all incoming TPA requests.
-   `/tpaautoaccept`: Toggles automatically accepting all incoming TPA requests.

## Permissions

-   `tpa.command.tpa`: Allows usage of the `/tpa` command. (Default: true)
-   `tpa.command.tpthere`: Allows usage of the `/tpthere` command. (Default: true)
-   `tpa.command.tpaccept`: Allows usage of the `/tpaccept` command. (Default: true)
-   `tpa.command.tpdeny`: Allows usage of the `/tpdeny` command. (Default: true)
-   `tpa.command.tpacancel`: Allows usage of the `/tpacancel` command. (Default: true)
-   `tpa.command.tpablock`: Allows usage of the `/tpablock` command. (Default: true)
-   `tpa.command.tpaallblock`: Allows usage of the `/tpaallblock` command. (Default: true)
-   `tpa.command.tpaautoaccept`: Allows usage of the `/tpaautoaccept` command. (Default: true)

## Installation

1.  Download the latest release from the [releases page](https://github.com/iciency/TPA/releases).
2.  Place the `.whl` file into your server's `plugins` directory.
3.  Restart the server.
