from gymnasium.envs.registration import register
import gymnasium as gym
from biped.my_bipedal_walker import MyBipedalWalker

register(
    id="MyBipedalWalker-v0",
    entry_point="biped.my_bipedal_walker:MyBipedalWalker",
    max_episode_steps=1000,
)

def run(actions, render=False):
    env = gym.make("MyBipedalWalker-v0")

    obs, info = env.reset(seed=42)
    done = False
    reward = -1
    while not done:
        obs, reward, terminated, truncated, info = env.step(actions)

        if render:
            env.render()

        done = terminated or truncated

    env.reset()
    return reward