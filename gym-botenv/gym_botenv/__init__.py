from gym.envs.registration import register

register(
    id='botenv-v0',
    entry_point='gym_botenv.envs:BotEnv',
)

register(
    id='botenv-extrahard-v0',
    entry_point='gym_botenv.envs:BotenvExtraHardEnv',
)

