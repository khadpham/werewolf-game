from werewolf_core import *

if __name__ == "__main__":
    player_names = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "m",
        "F",
        "G",
        "h",
        "i",
        "j",
        "k",
        "l",
        "n",
    ]
    player_roles = [
        "Werewolf",
        "Werewolf",
        "BB Wolf",
        "Cursed",
        "Harlot",
        "Seer",
        "Hunter",
        "Witch",
        "Bodyguard",
        "Fool",
        "Elder",
        "Villager",
        "Villager",
        "Villager",
    ]
    time_limits = [120, 180, 180, 150, 120, 120, 90, 90, 90, 90]
    # time_limits =[1]
    game = Game(player_names, player_roles, time_limits)
    game.start_game()
