# Warzone AI

# Play against the built in AI
```
import wzai
env = wzai.gym.BotGame()
bot = wzai.agents.Random(1)
env.play(bot, options={
    "mapid": wzai.api.MapID.SMALL_EARTH
})
```

# Or against a human
```
import wzai
env = wzai.gym.PlayerGame()
bot = wzai.agents.Random(wzai.api.BOT_ID)
env.play(bot, options={
    "player": <players-email-here>,
    "mapid": wzai.api.MapID.SMALL_EARTH
})
```
