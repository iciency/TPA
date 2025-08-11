import json
import os
import time
from typing import Dict, List, Tuple
from uuid import UUID

from endstone import Player
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from endstone.lang import Translatable


class TpaPlugin(Plugin):
    prefix = "TpaPlugin"
    api_version = "0.6"
    load = "POSTWORLD"
    tpa_requests: Dict[UUID, Tuple[UUID, float, str]] = {}  # target_uuid -> (requester_uuid, timestamp, type)
    translations: Dict[str, Dict[str, str]] = {}

    def _(self, sender: CommandSender, message: str, *args) -> None:
        if isinstance(sender, Player):
            locale = sender.locale
        else:
            locale = self.server.language.locale

        # Get the translation from the nested dictionary, fallback to en_US
        translation = self.translations.get(message, {}).get(
            locale, self.translations.get(message, {}).get("en_US")
        )

        # If a translation exists, use it; otherwise, use the original message key
        text_to_translate = translation if translation else message

        # Manually format the string if arguments are provided
        if args:
            formatted_message = text_to_translate.format(*args)
        else:
            formatted_message = text_to_translate

        sender.send_message(formatted_message)

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
        "tpthere": {
            "description": "Request a player to teleport to you.",
            "usages": ["/tpthere <player: player>"],
            "permissions": ["tpa.command.tpthere"],
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
        "tpa.command.tpthere": {
            "description": "Allows users to use the /tpthere command.",
            "default": True,
        },
    }

    def on_load(self) -> None:
        self.logger.info("TpaPlugin loaded.")
        lang_dir = os.path.join(os.path.dirname(__file__), "lang")
        if not os.path.exists(lang_dir):
            self.logger.warning(f"Language directory not found at {lang_dir}")
            return

        for file_name in os.listdir(lang_dir):
            if file_name.endswith(".json"):
                locale = file_name[:-5]
                with open(os.path.join(lang_dir, file_name), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if key not in self.translations:
                            self.translations[key] = {}
                        self.translations[key][locale] = value

    def on_enable(self) -> None:
        self.logger.info("TPA plugin enabled.")
        self.register_events(self)

    def on_disable(self) -> None:
        self.logger.info("TPA plugin disabled.")

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if not isinstance(sender, Player):
            self._(sender, "tpa.not_a_player")
            return True

        player = sender

        match command.name:
            case "tpa":
                if len(args) != 1:
                    self._(sender, "tpa.command.usage")
                    return False

                target_name = args[0]
                target = self.server.get_player(target_name)

                if target is None:
                    self._(sender, "tpa.player_not_found", target_name)
                    return True

                if player == target:
                    self._(player, "tpa.cannot_request_self")
                    return True

                self.tpa_requests[target.unique_id] = (player.unique_id, time.time(), "tpa")
                self._(player, "tpa.request_sent", target.name)
                self._(target, "tpa.request_received", player.name)
                self._(target, "tpa.request_helper")
                return True

            case "tpaccept":
                if player.unique_id not in self.tpa_requests:
                    self._(player, "tpa.no_pending_request")
                    return True

                requester_uuid, timestamp, tpa_type = self.tpa_requests.pop(player.unique_id)

                if time.time() - timestamp > 60:
                    self._(player, "tpa.request_expired")
                    requester = self.server.get_player(requester_uuid)
                    if requester is not None:
                        self._(requester, "tpa.requester_expired", player.name)
                    return True

                requester = self.server.get_player(requester_uuid)

                if requester is None:
                    self._(player, "tpa.requester_not_online")
                    return True

                if tpa_type == "tpa":
                    requester.teleport(player.location)
                    self._(requester, "tpa.accepted_tpa", player.name)
                    self._(player, "tpa.accepted_by_target", requester.name)
                elif tpa_type == "tpthere":
                    player.teleport(requester.location)
                    self._(player, "tpthere.accepted_tpa", requester.name)
                    self._(requester, "tpthere.accepted_by_requester", player.name)
                return True

            case "tpdeny":
                if player.unique_id not in self.tpa_requests:
                    self._(player, "tpa.no_pending_request")
                    return True

                requester_uuid, _, _ = self.tpa_requests.pop(player.unique_id)
                requester = self.server.get_player(requester_uuid)

                self._(player, "tpa.denied")
                if requester is not None:
                    self._(requester, "tpa.denied_by_target", player.name)
                return True

            case "tpacancel":
                # Find the request sent by the current player
                target_uuid = None
                for t_uuid, (r_uuid, _, _) in self.tpa_requests.items():
                    if r_uuid == player.unique_id:
                        target_uuid = t_uuid
                        break

                if target_uuid is None:
                    self._(player, "tpa.no_pending_request")
                    return True

                # Remove the request
                self.tpa_requests.pop(target_uuid)

                target = self.server.get_player(target_uuid)

                self._(player, "tpa.request_cancelled")
                if target is not None:
                    self._(target, "tpa.cancelled_by_requester", player.name)
                return True

            case "tpthere":
                if len(args) != 1:
                    self._(sender, "tpthere.command.usage")
                    return False

                target_name = args[0]
                target = self.server.get_player(target_name)

                if target is None:
                    self._(sender, "tpa.player_not_found", target_name)
                    return True

                if player == target:
                    self._(player, "tpa.cannot_request_self")
                    return True

                self.tpa_requests[target.unique_id] = (player.unique_id, time.time(), "tpthere")
                self._(player, "tpa.request_sent", target.name)
                self._(target, "tpthere.request_received", player.name)
                self._(target, "tpa.request_helper")
                return True

        return False
