import time
import threading
import random


class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.alive = True
        self.target = None
        self.saved_by_bodyguard = False
        self.visited_by_harlot = False
        self.elder_protection = (
            True if role == "Elder" else False
        )  # Elder initial protection


class Game:
    def __init__(self, player_names, player_roles, time_limits):
        if len(player_names) - len(player_roles) != 0:
            raise ValueError("Number of players must match the number of roles.")
            print(f"Number of players: {len(player_names)}")
            print(f"Number of roles: {len(player_roles)}")
        random.shuffle(player_names)
        self.players = [
            Player(name, role) for name, role in zip(player_names, player_roles)
        ]
        self.time_limits = time_limits
        self.current_time_limit = self.time_limits[0]
        self.night_phase = True
        self.hunter_target = None
        self.witch_revive_used = False
        self.witch_kill_used = False
        self.bodyguard_last_target = None
        self.game_targets = []  # List to store targets for the entire game
        self.hanged_players = []
        self.day_count = 0  # add day_count for day phase time limit

    def start_game(self):
        print("Welcome to Werewolf!")
        print("Assigning roles...")
        self.print_living_players_and_roles()
        print(f"\nNumder of players: {len(self.players)}")
        print(
            f"Number of Werewolf: {sum(1 for player in self.players if player.role == 'Werewolf')}"
        )
        print(
            f"Number of Villagers: {sum(1 for player in self.players if player.role != 'Werewolf')}"
        )

        while True:
            if self.night_phase:
                self.night()
            else:
                self.day()
            if self.check_game_over():
                break

    def night(self):
        print("\n--- Night Phase ---")
        self.werewolf_target = None
        self.targets = {}
        self.witch_revive_target = None
        self.witch_kill_target = None
        self.harlot_target = None
        self.bb_wolf_target = None

        living_players = self.get_alive_players()
        print(
            f"Living Players: {', '.join([player.name for player in living_players])} ({len(living_players)})\n"
        )

        for player in self.players:
            if player.alive:
                if player.role == "Werewolf" and self.werewolf_target is None:
                    print(f"{player.name} (Werewolf) is choosing a victim.")
                    self.werewolf_target = self.get_player_input(
                        player.name, "Choose a victim: ", living_players
                    )
                    self.targets["Werewolf"] = (
                        self.werewolf_target.name if self.werewolf_target else None
                    )

                elif player.role == "BB Wolf" and self.bb_wolf_target is None:
                    print(f"\n{player.name} (BB Wolf) is choosing a victim.")
                    self.bb_wolf_target = self.get_player_input(
                        player.name, "Choose a victim: ", living_players
                    )
                    self.targets["BB Wolf"] = (
                        self.bb_wolf_target.name if self.bb_wolf_target else None
                    )

                elif player.role == "Harlot":
                    print(f"\n{player.name} (Harlot) is choosing someone to visit.")
                    self.harlot_target = self.get_player_input(
                        player.name,
                        "Choose a player to visit (or ENTER to stay home): ",
                        living_players,
                    )
                    if self.harlot_target and (
                        self.harlot_target.role in ["Werewolf", "BB Wolf"]
                        or self.harlot_target
                        in [self.werewolf_target, self.bb_wolf_target]
                    ):
                        # Determine which wolf to retarget:
                        if self.harlot_target == self.werewolf_target:
                            self.werewolf_target = (
                                player  # Change werewolf_target to Harlot
                            )
                            print(
                                f"{player.name} (Harlot) visited a Werewolf and will be the Werewolf's target."
                            )
                        elif self.harlot_target == self.bb_wolf_target:
                            self.bb_wolf_target = (
                                player  # Change bb_wolf_target to Harlot
                            )
                            print(
                                f"{player.name} (Harlot) visited a BB Wolf and will be the BB Wolf's target."
                            )
                        else:  # Case where Harlot visits a Werewolf/BB Wolf directly
                            if self.harlot_target.role == "Werewolf":
                                self.werewolf_target = (
                                    player  # Change werewolf_target to Harlot
                                )
                            elif self.harlot_target.role == "BB Wolf":
                                self.bb_wolf_target = (
                                    player  # Change bb_wolf_target to Harlot
                                )
                            print(
                                f"{player.name} (Harlot) visited a Werewolf/BB Wolf and will be their target."
                            )

                        self.harlot_target.visited_by_harlot = True
                    elif self.harlot_target:
                        self.harlot_target.visited_by_harlot = True
                        print(
                            f"{player.name} (Harlot) will visit {self.harlot_target.name}."
                        )
                    else:
                        self.harlot_target = player
                        print(f"{player.name} (Harlot) will stay home.")
                    self.targets["Harlot"] = (
                        self.harlot_target
                        if isinstance(self.harlot_target, str)
                        else self.harlot_target.name
                    )

                elif player.role == "Seer" and not player.visited_by_harlot:
                    print(f"\n{player.name} (Seer) is checking another player's role.")
                    player.target = self.get_player_input(
                        player.name, "Choose a player to check: ", living_players
                    )
                    self.targets["Seer"] = player.target.name if player.target else None
                    if player.target:
                        print(
                            f"Seer, {player.target.name} is a {'Werewolf' if player.target.role in ['Werewolf', 'BB Wolf'] else 'Villager'}"
                        )
                elif player.role == "Bodyguard" and not player.visited_by_harlot:
                    print(
                        f"\n{player.name} (Bodyguard) is choosing a player to protect."
                    )
                    player.target = self.get_player_input(
                        player.name,
                        "Choose a player to protect: ",
                        living_players,
                        exclude_previous=self.bodyguard_last_target,
                    )
                    self.targets["Bodyguard"] = (
                        player.target.name if player.target else None
                    )
                    self.bodyguard_last_target = player.target
                elif player.role == "Hunter" and not player.visited_by_harlot:
                    print(f"\n{player.name} (Hunter) is choosing a target to mark.")
                    player.target = self.get_player_input(
                        player.name,
                        "Choose a player to mark: ",
                        living_players,
                        exclude_self=True,
                    )
                    self.hunter_target = player.target
                    self.targets["Hunter"] = (
                        player.target.name if player.target else None
                    )
                # Witch Actions
                elif player.role == "Witch" and not player.visited_by_harlot:
                    if (
                        self.werewolf_target or self.bb_wolf_target
                    ) and not self.witch_revive_used:
                        targets = [self.werewolf_target, self.bb_wolf_target]
                        valid_targets = [t for t in targets if t is not None]
                        target_names = [t.name for t in valid_targets]

                        if valid_targets:
                            print(
                                f"\nWitch, the Werewolves' targets are {', '.join(target_names)}."
                            )
                            while True:
                                revive_input = input(
                                    f"Enter the name of the player you want to save (or press Enter to not save anyone): "
                                ).lower()
                                if revive_input == "":
                                    break
                                elif revive_input in [
                                    name.lower() for name in target_names
                                ]:
                                    self.witch_revive_target = next(
                                        t
                                        for t in valid_targets
                                        if t.name.lower() == revive_input
                                    )
                                    if self.witch_revive_target == self.werewolf_target:
                                        self.werewolf_target = None
                                    else:
                                        self.bb_wolf_target = None
                                    self.witch_revive_used = True
                                    break
                                else:
                                    print(
                                        "Invalid input. Please enter a valid player name or press Enter."
                                    )
                        else:
                            print("\nNo one was targeted by the Werewolves.")

                    if not self.witch_kill_used:
                        while True:
                            kill_input = input(
                                "Witch, choose a player to kill (Press Enter for No/Enter player name to kill): "
                            ).lower()
                            print()
                            if kill_input == "":
                                break
                            elif kill_input in [
                                player.name.lower()
                                for player in self.players
                                if player.alive
                            ]:
                                self.witch_kill_target = next(
                                    (
                                        p
                                        for p in self.players
                                        if p.name.lower() == kill_input
                                    ),
                                    None,
                                )
                                break
                            else:
                                print("Invalid input.")
                    print()
                    self.targets["Witch_Revive"] = (
                        self.witch_revive_target.name
                        if self.witch_revive_target
                        else None
                    )
                    if self.witch_revive_target:
                        print(
                            f"{self.witch_revive_target.name} was saved by the Witch."
                        )
                    print()
                    self.targets["Witch_Kill"] = (
                        self.witch_kill_target.name if self.witch_kill_target else None
                    )
                    if self.witch_kill_target:
                        self.witch_kill_target.alive = False
                        print(f"{self.witch_kill_target.name} was killed by the Witch.")
                        self.witch_kill_used = True

                player.visited_by_harlot = False
        # Bodyguard protection
        if self.werewolf_target or self.bb_wolf_target:
            bodyguard_target = None
            for player in self.players:
                if player.role == "Bodyguard" and player.alive:
                    bodyguard_target = player.target
                    break
            if (
                bodyguard_target
                and bodyguard_target in [self.werewolf_target, self.bb_wolf_target]
                and not bodyguard_target.saved_by_bodyguard
            ):
                print(f"\n{bodyguard_target.name} was saved by the Bodyguard.")
                bodyguard_target.saved_by_bodyguard = True
            # else:
            #     self.werewolf_target.saved_by_bodyguard = False
        print()
        # Werewolf and BB Wolf kill
        for target in [self.werewolf_target, self.bb_wolf_target]:
            if target and not target.saved_by_bodyguard:

                if (
                    target.role == "Harlot"
                    and self.harlot_target.role not in ["Harlot", "Werewolf", "BB Wolf"]
                    and self.harlot_target.name
                    not in [self.targets["Werewolf"], self.targets["BB Wolf"]]
                ):
                    print(
                        f"{target.name} (Harlot) was visiting someone else and avoided the Werewolf."
                    )
                elif target.role == "Cursed":  # Check for Cursed role
                    target.role = "Werewolf"  # Promote to Werewolf
                    print(f"{target.name} (Cursed) has become a Werewolf!")
                elif (
                    target.role == "Elder" and target.elder_protection
                ):  # Handle Elder's first attack
                    target.elder_protection = False
                    print(
                        f"{target.name} (Elder) survived the Werewolf's attack! (0 attack remaining)"
                    )
                else:
                    target.alive = False
                    print(f"{target.name} was killed by the Werewolf.")

        # Hunter's revenge (Night Kill)
        for player in self.players:
            # print(player.role == 'Hunter' and not player.alive)
            if (
                player.role == "Hunter"
                and not player.alive
                and self.hunter_target is not None
            ):
                for p in self.players:
                    if p.name == self.hunter_target.name:
                        p.alive = False
                        print(f"{p.name} died due to Hunter's revenge.")
                        self.hunter_target = None
                        break
            player.saved_by_bodyguard = False

        self.game_targets.append(
            self.targets.copy()
        )  # Append the copy of target to keep the history

        # Game Process Log
        print("\nGame Process:")
        for night_num, night_targets in enumerate(self.game_targets):
            print(f"Night {night_num + 1}:")
            for i, (role, target) in enumerate(night_targets.items()):
                # Skip printing if the Witch action has already been logged
                if role == "Witch_Revive" and self.witch_revive_used and target is None:
                    continue
                if role == "Witch_Kill" and self.witch_kill_used and target is None:
                    continue
                print(f" {i + 1}. - {role}: {target}")  # Add {i + 1}. for numbering
            print()
        self.night_phase = False

    def day(self):
        print("\n--- Day Phase ---")
        print("Villagers discuss and vote...")
        print(
            f"Living Players: {', '.join([player.name for player in self.get_alive_players()])} ({len(self.get_alive_players())})"
        )

        # Get the time limit for the current day
        if self.day_count < len(self.time_limits):
            current_time_limit = self.time_limits[self.day_count]
        else:
            current_time_limit = self.time_limits[
                -1
            ]  # use the last time limit if day count exceed the list

        interrupted = self.start_timer(current_time_limit)
        if interrupted:
            print("The discussion was interrupted.")
        self.day_count += 1  # Increment day count

        lynched_player = self.get_player_input(
            None, "\nChoose a player to lynch: ", self.get_alive_players()
        )

        if lynched_player:
            print(f"{lynched_player.name} was lynched by the villagers.")
            self.hanged_players.append(
                lynched_player.name
            )  # Append the name to the list
            lynched_player.alive = False
            if lynched_player.role == "Hunter":
                print(
                    f"{lynched_player.name} (Hunter) will take revenge on {self.hunter_target.name} at the end of the next night."
                )
            if lynched_player.role == "Fool":
                print("\nFool wins!")
        else:
            print("No one was lynched today.")

        print("\nHanged Players: ", ", ".join(self.hanged_players))
        self.print_living_players_and_roles()
        self.night_phase = True

    def get_player_input(
        self, chooser, message, alive_players, exclude_previous=None, exclude_self=False
    ):  # add exclude_self=False
        while True:
            player_input = input(f"{message} ").lower()
            if player_input == "":
                return None
            valid_choices = [
                player.name.lower()
                for player in alive_players
                if (player != exclude_previous or not exclude_previous)
                and (player.name != chooser or not exclude_self)
            ]  # use exclude_self

            if player_input in valid_choices:
                for player in self.players:
                    if player.name.lower() == player_input:
                        return player
            else:
                print("Invalid input. Please enter a valid player name from the list.")

    def get_alive_players(self):
        return [player for player in self.players if player.alive]

    def print_living_players_and_roles(self):
        print("Living Players:")
        for i, player in enumerate(self.get_alive_players()):
            print(f"{i + 1}. {player.name} ({player.role})")

    def check_game_over(self):
        werewolf_count = sum(
            1
            for player in self.players
            if player.role in ["Werewolf", "BB Wolf"] and player.alive
        )
        villager_count = sum(
            1
            for player in self.players
            if player.role not in ["Werewolf", "BB Wolf"] and player.alive
        )
        fool_alive = sum(
            1 for player in self.players if player.role == "Fool" and player.alive
        )

        # Check if the Fool was lynched using a list comprehension
        fool_lynched = any(
            player.role == "Fool" and player.name in self.hanged_players
            for player in self.players
        )

        if fool_lynched:
            if werewolf_count >= villager_count:
                print("\nWerewolves and The Fool win!")
                return True
            elif werewolf_count == 0:
                print("\nVillagers and The Fool win !")
                return True
            else:
                return False

        if werewolf_count >= villager_count:
            print("\nWerewolves win!")
            return True
        elif werewolf_count == 0:
            print("\nVillagers win!")
            return True
        else:
            return False

    def start_timer(self, seconds):  # add self
        def timer_function():
            try:
                time.sleep(seconds)
                print("\nTime's up!")  # Print on a new line
                raise TimeoutException("Time's up!")
            except TimeoutException:  # catch the exception to prevent traceback
                pass

        timer_thread = threading.Thread(target=timer_function)
        timer_thread.daemon = True
        timer_thread.start()

        start_time = time.time()
        try:
            while time.time() - start_time < seconds:
                remaining_time = int(seconds - (time.time() - start_time))
                print(f"Time remaining: {remaining_time} seconds", end="\r")
                time.sleep(1)
            return False  # Timer finished normally
        except TimeoutException:
            return True  # Timer timed out
        except KeyboardInterrupt:
            print("\nTimer stopped by the moderator.")  # Print on a new line
            return True

    # @staticmethod
    # def start_timer(seconds):
    #     signal.signal(signal.SIGABRT, timeout_handler)
    #     signal.alarm(seconds)
    #     try:
    #         for i in range(seconds, 0, -1):
    #             print(f"Time remaining: {i} seconds", end="\r")
    #             time.sleep(1)
    #         print("Time's up!                     ")
    #         signal.alarm(0)
    #         return False
    #     except (TimeoutException, KeyboardInterrupt) as e:
    #         print(f"\r{e}                 ")
    #         return True
    #     finally:
    #         signal.alarm(0)


class TimeoutException(Exception):
    pass


# def timeout_handler(signum, frame):
#     raise TimeoutException("Time's up!")
