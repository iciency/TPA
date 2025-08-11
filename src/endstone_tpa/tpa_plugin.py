import json
import os
import time
from typing import Dict, Tuple
from uuid import UUID

from endstone import Player
from endstone.command import Command, CommandSender
from endstone.form import MessageForm
from endstone.plugin import Plugin


class TpaPlugin(Plugin):
    prefix = "TpaPlugin"
    api_version = "0.6"
    load = "POSTWORLD"
    # target_uuid -> (requester_uuid, timestamp, type)
    tpa_requests: Dict[UUID, Tuple[UUID, float, str]] = {}
    translations: Dict[str, Dict[str, str]] = {}

    def _(self, sender: CommandSender, message: str, *args, return_string: bool = False) -> str | None:
        if isinstance(sender, Player):
            locale = sender.locale
        else:
            locale = self.server.language.locale

        translation = self.translations.get(message, {}).get(
            locale, self.translations.get(message, {}).get("en_US")
        )
        text_to_translate = translation if translation else message

        if args:
            formatted_message = text_to_translate.format(*args)
        else:
            formatted_message = text_to_translate

        if return_string:
            return formatted_message
        else:
            sender.send_message(formatted_message)
            return None

    commands = {
        "tpa": {
            "description": "Request to teleport to another player.",
            "usages": ["/tpa <player: player>"],
            "permissions": ["tpa.command.tpa"],
        },
        "tpaccept": {
            "description": "Accept a teleport request.",
            "usages": ["/tpaccept [player: player]"],
            "permissions": ["tpa.command.tpaccept"],
        },
        "tpdeny": {
            "description": "Deny a teleport request.",
            "usages": ["/tpdeny [player: player]"],
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
        "tpa.command.*": {"description": "Allows users to use all TPA commands.", "default": True},
        "tpa.command.tpa": {"description": "Allows users to use the /tpa command.", "default": True},
        "tpa.command.tpaccept": {"description": "Allows users to use the /tpaccept command.", "default": True},
        "tpa.command.tpdeny": {"description": "Allows users to use the /tpdeny command.", "default": True},
        "tpa.command.tpacancel": {"description": "Allows users to use the /tpacancel command.", "default": True},
        "tpa.command.tpthere": {"description": "Allows users to use the /tpthere command.", "default": True},
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
            case "tpa" | "tpthere":
                if len(args) != 1:
                    usage_key = "tpa.command.usage" if command.name == "tpa" else "tpthere.command.usage"
                    self._(sender, usage_key)
                    return False

                target_name = args[0]
                target = self.server.get_player(target_name)

                if target is None:
                    self._(sender, "tpa.player_not_found", target_name)
                    return True

                if player == target:
                    self._(player, "tpa.cannot_request_self")
                    return True

                self.tpa_requests[target.unique_id] = (player.unique_id, time.time(), command.name)
                self._(player, "tpa.request_sent", target.name)

                def on_form_submit(target_player: Player, data: int):
                    # Wrap player name in quotes to handle names with spaces
                    if data == 0:  # Accept
                        self.server.dispatch_command(target_player, f'tpaccept "{player.name}"')
                    else:  # Deny
                        self.server.dispatch_command(target_player, f'tpdeny "{player.name}"')

                content_key = "tpa.form.content.tpa" if command.name == "tpa" else "tpa.form.content.tpthere"
                form = MessageForm(
                    title=self._(target, "tpa.form.title", return_string=True),
                    content=self._(target, content_key, player.name, return_string=True),
                    button1=self._(target, "tpa.form.accept", return_string=True),
                    button2=self._(target, "tpa.form.deny", return_string=True),
                )
                # Send a chat message as a fallback first
                fallback_content_key = "tpa.request_received" if command.name == "tpa" else "tpthere.request_received"
                self._(target, fallback_content_key, player.name)
                self._(target, "tpa.request_helper")
                
                form.on_submit = on_form_submit
                target.send_form(form)
                return True

            case "tpaccept":
                # This command can be called with a player name (from form) or without (manual)
                # We need to find the correct request to accept.
                
                # For now, we only support one incoming request at a time.
                # A more complex system would be needed to handle multiple requests by name.
                if player.unique_id not in self.tpa_requests:
                    self._(player, "tpa.no_pending_request")
                    return True

                requester_uuid, timestamp, tpa_type = self.tpa_requests.pop(player.unique_id)
                requester = self.server.get_player(requester_uuid)

                if time.time() - timestamp > 60:
                    self._(player, "tpa.request_expired")
                    if requester:
                        self._(requester, "tpa.requester_expired", player.name)
                    return True

                if not requester:
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
                # Similar to tpaccept, we only handle the single most recent request.
                if player.unique_id not in self.tpa_requests:
                    self._(player, "tpa.no_pending_request")
                    return True

                requester_uuid, _, _ = self.tpa_requests.pop(player.unique_id)
                requester = self.server.get_player(requester_uuid)

                self._(player, "tpa.denied")
                if requester:
                    self._(requester, "tpa.denied_by_target", player.name)
                return True

            case "tpacancel":
                target_uuid = None
                for t_uuid, (r_uuid, _, _) in self.tpa_requests.items():
                    if r_uuid == player.unique_id:
                        target_uuid = t_uuid
                        break

                if target_uuid is None:
                    # To be consistent, we should probably say "no pending request"
                    # but the original logic said this. Keeping for now.
                    self._(player, "tpa.no_pending_request")
                    return True

                self.tpa_requests.pop(target_uuid)
                target = self.server.get_player(target_uuid)

                self._(player, "tpa.request_cancelled")
                if target:
                    self._(target, "tpa.cancelled_by_requester", player.name)
                return True

        return False
