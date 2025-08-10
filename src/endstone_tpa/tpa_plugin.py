import time
from typing import Dict, Tuple
from uuid import UUID

from endstone import Player
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender


class TpaPlugin(Plugin):
    prefix = "TpaPlugin"
    api_version = "0.6"
    load = "POSTWORLD"
    tpa_requests: Dict[UUID, Tuple[UUID, float]] = {}  # target_uuid -> (requester_uuid, timestamp)
    
    commands = {
        "tpa": {
            "description": "Request to teleport to another player.",
            "usages": ["/tpa <player: player>"],
            "permissions": ["tpa.command.tpa"],
        },
        "tpaccept": {
            "description": "Accept a teleport request.",
            "usages": ["/tpaccept"],
            "permissions": ["tpa.command.tpaccept"],
        },
        "tpdeny": {
            "description": "Deny a teleport request.",
            "usages": ["/tpdeny"],
            "permissions": ["tpa.command.tpdeny"],
        },
        "tpacancel": {
            "description": "Cancel a teleport request.",
            "usages": ["/tpacancel"],
            "permissions": ["tpa.command.tpacancel"],
        },
    }
    
    permissions = {
        "tpa.command.*": {
            "description": "Allows users to use all TPA commands.",
            "default": True,
        },
        "tpa.command.tpa": {
            "description": "Allows users to use the /tpa command.",
            "default": True,
        },
        "tpa.command.tpaccept": {
            "description": "Allows users to use the /tpaccept command.",
            "default": True,
        },
        "tpa.command.tpdeny": {
            "description": "Allows users to use the /tpdeny command.",
            "default": True,
        },
        "tpa.command.tpacancel": {
            "description": "Allows users to use the /tpacancel command.",
            "default": True,
        },
    }

    def on_load(self) -> None:
        self.logger.info("TPA plugin loaded.")

    def on_enable(self) -> None:
        self.logger.info("TPA plugin enabled.")
        self.register_events(self)

    def on_disable(self) -> None:
        self.logger.info("TPA plugin disabled.")

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if not isinstance(sender, Player):
            sender.send_message("This command can only be used by a player.")
            return True
        
        player = sender

        match command.name:
            case "tpa":
                if len(args) != 1:
                    sender.send_message(f"Usage: {self.commands[command.name]['usages'][0]}")
                    return False

                target_name = args[0]
                target = self.server.get_player(target_name)

                if target is None:
                    sender.send_message(f"Player '{target_name}' not found.")
                    return True

                if player == target:
                    player.send_message("You cannot send a teleport request to yourself.")
                    return True

                self.tpa_requests[target.unique_id] = (player.unique_id, time.time())
                player.send_message(f"Teleport request sent to {target.name}.")
                target.send_message(f"{player.name} has requested to teleport to you.")
                target.send_message("Type /tpaccept to accept or /tpdeny to deny. The request will expire in 60 seconds.")
                return True

            case "tpaccept":
                if player.unique_id not in self.tpa_requests:
                    player.send_message("You have no pending teleport requests.")
                    return True

                requester_uuid, timestamp = self.tpa_requests.pop(player.unique_id)

                if time.time() - timestamp > 60:
                    player.send_message("This teleport request has expired.")
                    requester = self.server.get_player(requester_uuid)
                    if requester is not None:
                        requester.send_message(f"Your teleport request to {player.name} has expired.")
                    return True
                requester = self.server.get_player(requester_uuid)

                if requester is None:
                    player.send_message("The player who sent the request is no longer online.")
                    return True
                
                requester.teleport(player.location)
                requester.send_message(f"Teleport request to {player.name} accepted. Teleporting...")
                player.send_message(f"You have accepted the teleport request from {requester.name}.")
                return True

            case "tpdeny":
                if player.unique_id not in self.tpa_requests:
                    player.send_message("You have no pending teleport requests.")
                    return True

                requester_uuid, _ = self.tpa_requests.pop(player.unique_id)
                requester = self.server.get_player(requester_uuid)

                player.send_message("You have denied the teleport request.")
                if requester is not None:
                    requester.send_message(f"{player.name} has denied your teleport request.")
                return True

            case "tpacancel":
                # Find the request sent by the current player
                target_uuid = None
                for t_uuid, (r_uuid, _) in self.tpa_requests.items():
                    if r_uuid == player.unique_id:
                        target_uuid = t_uuid
                        break

                if target_uuid is None:
                    player.send_message("You have not sent any teleport requests.")
                    return True

                # Remove the request
                self.tpa_requests.pop(target_uuid)

                target = self.server.get_player(target_uuid)

                player.send_message("You have canceled your teleport request.")
                if target is not None:
                    target.send_message(f"{player.name} has canceled their teleport request.")
                return True

        return False
