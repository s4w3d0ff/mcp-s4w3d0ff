import os
import asyncio
import logging
from poolguy.twitchapi import TwitchApi
from pydantic import Field
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "PoolGuy (Twitch API) Server", 
    dependencies=["poolguy"]
)

config = {
    "client_id": os.environ.get('TWITCH_CLIENT_ID', None),
    "client_secret": os.environ.get('TWITCH_CLIENT_SECRET', None),
    "redirect_uri": os.environ.get('TWITCH_REDIRECT_URI', "http://localhost:5050/callback"),
    "scopes": os.environ.get('TWITCH_SCOPES', []),
    "storage": os.environ.get('TWITCH_STORAGE', "json"),
    "browser": os.environ.get('TWITCH_OATH_BROWSER', {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        })
}

twitch_api = TwitchApi(**config)

@mcp.tool()
async def get_twitch_user_info(username: str = Field(description="The Twitch username you want to fetch information for")) -> dict:
    """Fetch Twitch user info from the Twitch API"""
    users = await twitch_api.getUsers(logins=[username])
    if not users:
       return {"error": "User not found on Twitch"}
    return users[0]

@mcp.tool()
async def get_twitch_channel_info(broadcaster_id: str = Field(description="The Twitch broadcaster ID you want to fetch information for")) -> dict:
    """Fetch channel info from the Twitch API"""
    channel_info = await twitch_api.getChannelInfo(broadcaster_id=broadcaster_id)
    return channel_info

@mcp.tool()
async def get_twitch_chat_settings(broadcaster_id: str = Field(description="The Twitch broadcaster ID you want to fetch information for")) -> dict:
    """Fetch chat settings from the Twitch API"""
    chat_settings = await twitch_api.getChatSettings(broadcaster_id=broadcaster_id)
    return chat_settings

@mcp.tool()
async def get_twitch_clips(
    broadcaster_id: str = Field(
        description="An ID that identifies the broadcaster whose video clips you want to get. Use this parameter to get clips that were captured from the broadcaster's streams.", 
        default=None), 
    game_id: str = Field(
        description="An ID that identifies the game whose clips you want to get. Use this parameter to get clips that were captured from streams that were playing this game.", 
        default=None), 
    clip_id: str = Field(
        description="An ID that identifies the clip to get. To specify more than one ID, include this parameter for each clip you want to get. For example, id=foo&id=bar. You may specify a maximum of 100 IDs.", 
        default=None),
    first: int = Field(description="Optional number of clips to get.", default=20)
    ) -> list:
    """Gets one or more video clips that were captured from streams. The clip_id, game_id, and broadcaster_id parameters are mutually exclusive."""
    clips = await twitch_api.getClips(broadcaster_id=broadcaster_id, game_id=game_id, clip_id=clip_id, first=first)
    return clips

@mcp.tool()
async def get_twitch_top_games(
    first: int = Field(description="Optional number of top games to get.", default=20)
    ) -> list:
    """Gets the top games that are being played on Twitch."""
    games = await twitch_api.getTopGames(first=first)
    return games

@mcp.tool()
async def search_twitch_categories(
    query: str = Field(description="The search query."), 
    first: int = Field(description="Optional number of categories to get.", default=20)
    ) -> list:
    """Searches for games or categories that match the specified query."""
    categories = await twitch_api.searchCategories(query=query, first=first)
    return categories

@mcp.tool()
async def search_twitch_channels(
    query: str = Field(description="The search query."), 
    first: int = Field(description="Optional number of channels to get.", default=20), 
    live_only: bool = Field(description="Whether to only include live channels in the results.", default=False)
    ) -> list:
    """Searches for channels that match the specified query."""
    channels = await twitch_api.searchChannels(query=query, first=first, live_only=live_only)
    return channels

async def main():
    await twitch_api.login()

if __name__ == "__main__":
    asyncio.run(main())
    mcp.run(transport='stdio')