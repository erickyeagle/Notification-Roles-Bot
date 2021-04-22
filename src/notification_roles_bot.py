#!/usr/bin/env python

"""
Notification Roles Bot is a Discord bot that simplifies the use of no permission, mentionable roles
that a user wants to subscribe to.
"""

import os
import sys
from typing import List, Optional

from discord import Embed, Guild, Member, Permissions, Role
from discord.ext.commands import (Bot, CommandError, CommandInvokeError,
                                  CommandNotFound, Context,
                                  MissingRequiredArgument, NoPrivateMessage,
                                  RoleConverter, TooManyArguments,
                                  bot_has_guild_permissions, guild_only)

GUILD_CONTEXT_REQUIRED_ERROR   = 'Uh-oh...this command is only valid in a guild context!'
ROLE_ADD_TO_GUILD_ERROR        = 'Uh-oh...the role "{0}" could not be added to your guild!'
ROLE_ADD_TO_MEMBER_ERROR       = 'Uh-oh...the role {0.mention} could not be added to you!'
ROLE_ADDED_TO_GUILD            = 'The role {0.mention} has been added to your guild!'
ROLE_ADDED_TO_MEMBER           = 'The role {0.mention} has been added to you!'
ROLE_FOUND_IN_GUILD_ERROR      = 'Uh-oh...your guild already has the role {0.mention}!'
ROLE_FOUND_IN_MEMBER_ERROR     = 'Uh-oh...you already have the role {0.mention}!'
ROLE_NOT_COMPATIBLE_ERROR      = 'Uh-oh...the role {0.mention} is not a notification role!'
ROLE_NOT_FOUND_IN_GUILD_ERROR  = 'Uh-oh...your guild does not have the role "{0}"!'
ROLE_NOT_FOUND_IN_MEMBER_ERROR = 'Uh-oh...you don\'t have the role {0.mention}!'
ROLE_REMOVED_FROM_MEMBER       = 'The role {0.mention} has been removed from you!'
SYNTAX                         = 'Syntax: !nr {list | {add | sub[scribe] | unsub[scribe]} <role>}'
TOKEN_NOT_SET_ERROR            = 'The environment variable "NOTIFICATION_ROLES_BOT_TOKEN" is not '\
                                 'set!'
UNHANDLED_EXCEPTION            = 'It looks like you found a bug in Notification Roles Bot. If you '\
                                 'would like to help us out, please file an issue on [GitHub]'\
                                 '(https://github.com/erickyeagle/notification-roles-bot/issues). '\
                                 'Thank you!'

bot: Bot = Bot(case_insensitive = True, command_prefix = '!', help_command = None)

async def convert_str_to_role(context: Context, role_str: str) -> Optional[Role]:
    """ Converts a role name or mention string into a Role object. """
    try:
        role: Optional[Role] = await RoleConverter().convert(context, role_str)
        return role
    except: # pylint: disable=bare-except
        return None

def is_notification_role(guild: Guild, role: Role) -> bool:
    """
    Returns whether the role is a notification role. A role is a notification role if:
        1) it is mentionable
        2) it has no permissions
        3) the role is in the bot's roles list
    """
    return role.mentionable                       and \
           role.permissions == Permissions.none() and \
           role in guild.me.roles

def run() -> None:
    """ Loads the Discord bot token from the environment and starts the bot. """
    notification_roles_bot_token: Optional[str] = os.environ.get('NOTIFICATION_ROLES_BOT_TOKEN')
    if not notification_roles_bot_token:
        print(TOKEN_NOT_SET_ERROR, file = sys.stderr)
        return
    bot.run(notification_roles_bot_token)

@bot.group(name = 'nr', case_insensitive = True)
@bot_has_guild_permissions(manage_roles = True, read_messages = True, send_messages = True)
@guild_only()
async def _nr(context: Context) -> None:
    """ Bot command group entry point. """
    if context.invoked_subcommand is None:
        raise CommandInvokeError

@_nr.command(name = 'add', ignore_extra = False)
@bot_has_guild_permissions(manage_roles = True, read_messages = True, send_messages = True)
@guild_only()
async def _add(context: Context, role_str: str) -> None:
    """ Adds a notification role to the guild. """
    role: Optional[Role] = await convert_str_to_role(context, role_str)
    if role is not None:
        embed: Embed = Embed(description = ROLE_FOUND_IN_GUILD_ERROR.format(role))
        await context.reply(embed = embed)
        return
    guild: Optional[Guild] = context.guild
    if guild is None:
        raise NoPrivateMessage
    permissions: Permissions = Permissions().none()
    role = await guild.create_role(mentionable = True, name = role_str, permissions = permissions)
    if role is None:
        embed: Embed = Embed(description = ROLE_ADD_TO_GUILD_ERROR.format(role_str))
        await context.reply(embed = embed)
        return
    await guild.me.add_roles(role)
    embed: Embed = Embed(description = ROLE_ADDED_TO_GUILD.format(role))
    await context.reply(embed = embed)

@_nr.command(name = 'list', ignore_extra = False)
@bot_has_guild_permissions(manage_roles = True, read_messages = True, send_messages = True)
@guild_only()
async def _list(context: Context) -> None:
    """ Lists all notification roles for the current guild. """
    guild: Optional[Guild] = context.guild
    if guild is None:
        raise NoPrivateMessage
    roles: List[Role] = [role for role in guild.roles if is_notification_role(guild, role)]
    if roles is not None and len(roles) > 0:
        embed: Embed = Embed(description = ", ".join(map(lambda role: role.mention, roles)))
        await context.reply(embed = embed)

@_nr.command(name = 'subscribe', aliases = ['sub'], ignore_extra = False)
@bot_has_guild_permissions(manage_roles = True, read_messages = True, send_messages = True)
@guild_only()
async def _subscribe(context: Context, role_str: str) -> None:
    """ Subscribes a user to a notification role. """
    role: Optional[Role] = await convert_str_to_role(context, role_str)
    if role is None:
        embed: Embed = Embed(description = ROLE_NOT_FOUND_IN_GUILD_ERROR.format(role_str))
        await context.reply(embed = embed)
        return
    guild: Optional[Guild] = context.guild
    if not is_notification_role(guild, role):
        embed: Embed = Embed(description = ROLE_NOT_COMPATIBLE_ERROR.format(role))
        await context.reply(embed = embed)
        return
    member: Member = context.author
    if role in member.roles:
        embed: Embed = Embed(description = ROLE_FOUND_IN_MEMBER_ERROR.format(role))
        await context.reply(embed = embed)
        return
    await member.add_roles(role)
    embed: Embed = Embed(description = ROLE_ADDED_TO_MEMBER.format(role))
    await context.reply(embed = embed)

@_nr.command(name = 'unsubscribe', aliases = ['unsub'], ignore_extra = False)
@bot_has_guild_permissions(manage_roles = True, read_messages = True, send_messages = True)
@guild_only()
async def _unsubscribe(context: Context, role_str: str) -> None:
    """ Unsubscribes a user from a notification role. """
    role: Optional[Role] = await convert_str_to_role(context, role_str)
    if role is None:
        embed: Embed = Embed(description = ROLE_NOT_FOUND_IN_GUILD_ERROR.format(role_str))
        await context.reply(embed = embed)
        return
    guild: Optional[Guild] = context.guild
    if guild is None:
        raise NoPrivateMessage
    if not is_notification_role(guild, role):
        embed: Embed = Embed(description = ROLE_NOT_COMPATIBLE_ERROR.format(role))
        await context.reply(embed = embed)
        return
    member: Member = context.author
    if not role in member.roles:
        embed: Embed = Embed(description = ROLE_NOT_FOUND_IN_MEMBER_ERROR.format(role))
        await context.reply(embed = embed)
        return
    await member.remove_roles(role)
    embed: Embed = Embed(description = ROLE_REMOVED_FROM_MEMBER.format(role))
    await context.reply(embed = embed)
    if len(role.members) == 1 and guild.me in role.members:
        await role.delete()

@bot.event
async def on_command_error(context: Context, error: CommandError) -> None:
    """ The default command error handler provided by the bot. """
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, (CommandInvokeError, MissingRequiredArgument, TooManyArguments)):
        embed: Embed = Embed(description = SYNTAX)
        await context.reply(embed = embed)
        return
    if isinstance(error, NoPrivateMessage):
        embed: Embed = Embed(description = GUILD_CONTEXT_REQUIRED_ERROR)
        await context.reply(embed = embed)
        return
    embed: Embed = Embed()
    embed.add_field(name = error, value = UNHANDLED_EXCEPTION)
    await context.reply(embed=embed)

@bot.event
async def on_ready() -> None:
    """ Called when the client is done preparing the data received from Discord. """
    print('\n{0.user} is online!'.format(bot))

if __name__ == '__main__':
    run()
