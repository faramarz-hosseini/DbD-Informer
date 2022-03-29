import os
import inspect
from datetime import datetime
from typing import Union, Dict

import requests
from discord import (
    Client, Message
)

from const import (
    DBD_STATS_MAP, SPACE_NEEDED_FIELDS, STEAM_STATS, MsgField,
    SHRINE_MSG, RANK_RESET_MSG,
)
from utils import convert_pips_to_rank


class InformerClient(Client):
    STEAM_KEY = os.environ.get('steam-key')
    DBD_APPID = 381210
    PROFILE_TO_ID_API = ("http://api.steampowered.com/ISteamUser/"
                         "ResolveVanityURL/v0001/?key={key}&vanityurl={profile}")
    STATS_API = ("https://api.steampowered.com/ISteamUserStats/"
                 "GetUserStatsForGame/v0002/?appid=381210&key={key}&steamid={steamid}")
    TIMEPLAY_API = ("https://api.steampowered.com/IPlayerService/"
                    "GetOwnedGames/v0001/?key={key}&steamid={steamid}")
    SHRINE_API = "https://dbd.onteh.net.au/api/shrine"
    RANK_RESET_API = "https://dbd.onteh.net.au/api/rankreset"

    def __init__(self, token):
        super().__init__()
        self.token = token
        self.non_command_methods = {"on_ready", "on_message"}
        self.commands = self._get_command_methods()

    async def on_ready(self):
        print('We have logged in as {0}'.format(self.user))

    async def on_message(self, message: Message):
        if message.content.startswith("!"):
            cmd_parts = message.content[1:].strip().split()
            cmd, args = cmd_parts[0], cmd_parts[1:]
            handler = self.commands.get(cmd, None)
            if handler:
                await handler(self, message, *args)

    async def stats(self, message: Message, *args):
        for url in args:
            stats, steamid = self._get_dbd_stats(profile_url=url)
            if stats[0].get("Error"):
                await message.reply(stats[0].get("Error"))
                continue

            parsed_stats = self._parse_stats(stats=stats, steamid=steamid)
            msg_txt = "\n".join(
                field + ": " + value
                for field, value in parsed_stats.items()
            )
            await message.reply("**" + url + "**" + ":\n" + msg_txt)

    async def shrine(self, message: Message, *args):
        shrine_info = requests.get(self.SHRINE_API).json()
        current_shrine_end = float(shrine_info["end"])
        perks = [perk_dic['id'] for perk_dic in shrine_info['perks']]
        seconds_until_end = current_shrine_end - datetime.now().timestamp()
        days = seconds_until_end // 3600 // 24
        hours = (seconds_until_end // 3600) % 24

        await message.reply(
            SHRINE_MSG.format(
                *perks, int(days), int(hours)
            )
        )

    async def rank_reset(self, message: Message, *args):
        reset_time = requests.get(self.RANK_RESET_API).json()['rankreset']
        seconds_until_reset = reset_time - datetime.now().timestamp()
        days = seconds_until_reset // 3600 // 24
        hours = (seconds_until_reset // 3600) % 24
        await message.reply(
            RANK_RESET_MSG.format(
                int(days), int(hours)
            )
        )

    def _parse_stats(self, stats: Dict, steamid: str) -> Dict:
        parsed_stats = {}
        for stat in stats:
            if stat['name'] in DBD_STATS_MAP:
                field_name = DBD_STATS_MAP[stat['name']]
                parsed_stats[field_name] = stat['value']

        k_rank = self._convert_role_pips_to_rank(
            pips=parsed_stats.get(MsgField.K_RANK)
        )
        parsed_stats[MsgField.K_RANK] = k_rank if k_rank is not None else "No rank yet"

        s_rank = self._convert_role_pips_to_rank(
            pips=parsed_stats.get(MsgField.S_RANK)
        )
        parsed_stats[MsgField.S_RANK] = s_rank if s_rank is not None else "No rank yet"

        time_played = self._get_time_play_stat(steamid)
        parsed_stats[MsgField.PLAY_TIME] = time_played

        return self._sort_stats(parsed_stats)

    @staticmethod
    def _sort_stats(stats: Dict):
        sorted_stats = {}

        for field_name in STEAM_STATS:
            val = stats[field_name]
            if isinstance(val, int) or isinstance(val, float):
                val = f'{round(val):,}'
            sorted_stats[field_name] = val \
                if field_name not in SPACE_NEEDED_FIELDS else val+"\n"

        for field_name in DBD_STATS_MAP.values():
            val = stats[field_name]
            if isinstance(val, int) or isinstance(val, float):
                val = f'{round(val):,}'
            sorted_stats[field_name] = val \
                if field_name not in SPACE_NEEDED_FIELDS else val+"\n"

        return sorted_stats

    @staticmethod
    def _convert_role_pips_to_rank(
            pips: Union[None, int]
    ) -> str:
        if pips is not None:
            return convert_pips_to_rank(pips)

    def _get_dbd_stats(self, profile_url):
        steamid = self._get_steam_id(profile_url)
        stats_req = requests.get(
            self.STATS_API.format(key=self.STEAM_KEY, steamid=steamid)
        )
        if stats_req.status_code == 500 or stats_req.status_code == 403:
            return [{"Error": "Could not get stats. Private profile maybe?"}], None

        stats = stats_req.json().get('playerstats', {'stats': None}).get('stats')
        if stats is None or not stats:
            raise ValueError("could not fetch data. unexpected keys returned by api or bad input")

        return stats, steamid

    def _get_time_play_stat(self, steam_id):
        data = requests.get(
            self.TIMEPLAY_API.format(key=self.STEAM_KEY, steamid=steam_id)
        ).json()
        data = data.get('response').get('games')

        time_played = None
        for game in data:
            if game['appid'] == self.DBD_APPID and game['playtime_forever']:
                time_played = game['playtime_forever']

        if time_played:
            return str(time_played // 60)+" Hrs"
        return "Private"

    def _get_steam_id(self, profile_url: str) -> Union[str, None]:
        if profile_url.endswith("/"):
            profile_url = profile_url[:-1]
        profile_name = profile_url.split('/')[-1]
        if "profiles" in profile_url:
            return profile_name
        data = requests.get(
            self.PROFILE_TO_ID_API.format(key=self.STEAM_KEY, profile=profile_name)
        ).json().get('response', {'steamid': None}).get('steamid')

        if data is not None:
            return data
        return None

    def _get_command_methods(self):
        all_methods = inspect.getmembers(InformerClient, predicate=inspect.isfunction)
        return {
            func_name: func for func_name, func in all_methods
            if not func_name.startswith("_")
            and func_name not in dir(Client)
            and func_name not in self.non_command_methods
        }
