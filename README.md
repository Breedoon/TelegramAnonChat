# Anonymous Chat in Telegram

## About The Project  

By default, there is no feature in Telegram that would allow to make an anonymous chat. Yet, it is still possible to create one relying on a completely different feature: anonymous posting in channels. So, this project is about how to create such a channel where every member is an admin who can post anonymously thus effectively creating an anonymous chat.

## Getting Started  

There are 3 general steps that need to be completed: (1) set up channel and bot on Telegram, (2) Setting up the codebase, and (3) Setting up Heroku.

### Setting up on Telegram

1. Create a bot using [@BotFather](https://telegram.me/BotFather), and receive a token from it.
2. Create a channel and invite the newly created bot to it with admin permissions.

### Setting up the Code

1. Clone the git repo:

```bash
git clone https://github.com/Breedoon/TelegramAnonChat.git
```

2. Run enter your token into `config.py`.
3. Run `bot.py` to see if the bot reacts when you send messages to it.
4. Find your user id and the channel id in bot's logs `bot.log` (marked as chat), and add them to `config.py`.
    1. Search for 'channel' in the file and copy the `id` field which should be a negative number.
    2. Do the same for your own messages to find your user id, or use a bot like [@creationdatebot](https://telegram.me/creationdatebot) which will tell you your user id.
5. Add your Telegram @username and your channel's invite link to `config.py` (to be used in replies to users).
6. In `bot.py`, remove (comment out) the line `updater.start_polling()` and uncomment the line after it (`updater.start_webhook(...)`) to prepare the bot for deployment to Heroku.

### Setting up Heroku

There are other alternative platforms where a Telegram bot can be hosted, but Heroku seems to be the only one where you can host it for free. Note that to make the bot be able to run around the clock, you will need to enter your credit card, but Heroku shouldn't charge you if you're just using one app. 

1. Sign up on [Heroku](https://www.heroku.com/) and create an app.
2. Add to `config.py` the URL of your app in format: 
```python
webhook_url = 'https://name-of-your-app.herokuapp.com/'
```
3. Deploy the code to Heroku using [their instruction](https://devcenter.heroku.com/articles/git).
4. Run the App

After that, try sending commands to the bot to see if it reacts.

## Usage  

The way the bot is supposed to be used is for people to get admin permissions to write in the channel (thus making it a chat). When somebody sends `/start` to the bot the bot will do the following:
1. Check if the user who sent the command is already in the channel/chat and, if not, will send them an invite link.
2. Check if the user is already in the chat and has writing permissions, in which case it will notify the user about that.
3. Give the user (who must already be in the channel/chat) permissions to post in the chat.
4. If an error occurs, will notify the user about the error and show them the username of the admin to message.
5. If the user has sent any other (non-command) message, it will copy that message to the channel (as if the user posted the message into the channel).

One limitation Telegram has is that there can be no more than 50 admins in a channel at a time. So, to deal with it, if the bot faces such an error when trying to give writing permissions to a user, it will take those permissions away from a random user who has them and then will try again.

Also note that the bot cannot demote people who it did not make admins, so if some people (moderators) do need to be kept in the channel as admins, their user ids should be also added to the whitelist in `config.py` in order to avoid errors. 

## Anonymity

As far as I know, it is impossible to know the author of any post in a Telegram channel unless the 'Sign messages' option is turned on when that post was made (in which case the name of the author would be displayed inside the post). So, as long as the users post directly into the channel, it should be impossible to establish the authorship of the posts even for the owner of the channel.

### Caveats

There are other ways in which users can accidentally deanonymize themselves: 
1. Every person with posting permissions has access to the tab 'Recent Actions' which shows which people joined the channel and got posting rights in the recent 48 hours. So joining the chat and sending a message right away end up deanonymizing the sender, so ideally some time should pass between gaining posting rights and writing to the chat so that it is hard to match timestamps with each other.
2. When sending a message directly to the bot, the author of that message will technically be recorded in the logs. However, in practice, Heroku does not store logs (they get erased after the app has been idle for some time), so tracing back the author would be pretty difficult if not impossible.
