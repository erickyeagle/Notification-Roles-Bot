# Notification Roles Bot
Notification Roles Bot is a Discord bot that simplifies the use of what we coined as "notification roles". A notification role is a standard, mentionable Discord role that lacks all permissions. These roles can be made for things such as games, etc. Any user that wants to be subscribed to a role ping can have the role added to themselves.

## Installation
This is a self-hosted Discord bot. You will need to provide your own hosting. The host environment needs to the following software packages:

* [Latest Notification Roles Bot source code](https://github.com/erickyeagle/notification-roles-bot/releases)
* [Python 3.5.3+](https://www.python.org/downloads)
* [Poetry](https://python-poetry.org)

## Usage
In order to run this Discord bot, you will need to create a bot application from the Discord developer's portal. The bot's token will be used in step 2 below.

After deploying the source code to your host:

1. Install Poetry dependencies.

    ```
    poetry install --no-dev
    ```

2. Export the ```DISCORD_BOT_TOKEN``` environment variable. The method of exporting of this environment variable may depend on the host environment. Refer to the documentation for your host environment for the correct approach to use. You can export the environment variable via the command line.

    ```
    export DISCORD_BOT_TOKEN=<token>
    ```

3. Run Notification Roles Bot.

    ```
    python notification_roles_bot.py
    ```

**Note:** If you are running the bot on [Replit](https://replit.com) with a free account, you will need to keep the bot alive using something like [replit-keep-alive](https://github.com/erickyeagle/replit-keep-alive).

## Contributing
If you would like to contribute to this project, you can [file an issue](https://github.com/erickyeagle/notification-roles-bot/issues/new) or [submit a pull request](https://github.com/erickyeagle/notification-roles-bot/compare) from a forked repository. If you would like to contribute, but don't have any coding experience, you can ask questions or propose changes over at our [discussions page](https://github.com/erickyeagle/notification-roles-bot/discussions).