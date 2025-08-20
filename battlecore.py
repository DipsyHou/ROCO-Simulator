from utils.utils_load_data import load_spirits, load_skills
from utils.utils_battle import compareSpeed, elementalAdvantage, attack, action
from utils.utils_update_states import update_after_turn

import copy
import os

class BattleCore:
    def __init__(self, player1_spirits, player2_spirits):
        self.player1_spirits = player1_spirits
        self.player2_spirits = player2_spirits
        self.player1_spirit_onfield = player1_spirits[0]
        self.player2_spirit_onfield = player2_spirits[0]
        self.weather_or_environment = {
            # 0 for "no weather or environment"
            # WEATHERS: 1 for "sunny", 2 for "windy", 3 for "rainy"
            # ENVIRONMENTS: -1 for "Fragrant"，-2 for "maze"
            "type": 0,
            "locked": 0,
            "last_turn": 0
        }


    # 战斗回合
    def battle(self, player1_action, player2_action):
        # 清空终端
        os.system('cls' if os.name == 'nt' else 'clear')

        # 更新天气环境
        if self.weather_or_environment["locked"] == 0:
            if self.weather_or_environment["type"] != 0:
                self.weather_or_environment["last_turn"] -= 1
                if self.weather_or_environment["last_turn"] == 0:
                    self.weather_or_environment["type"] = 0
        else:
            self.weather_or_environment["locked"] -= 1


        if self.player1_spirit_onfield.hp > 0 and self.player2_spirit_onfield.hp > 0:

            # Determine the first mover
            if compareSpeed(self.player1_spirit_onfield, self.player2_spirit_onfield):
                first_mover = self.player1_spirit_onfield
                second_mover = self.player2_spirit_onfield
                first_action = player1_action
                second_action = player2_action
                print("Player 1 moves first")
            else:
                first_mover = self.player2_spirit_onfield
                second_mover = self.player1_spirit_onfield
                first_action = player2_action
                second_action = player1_action
                print("Player 2 moves first")

            print( "Player" + str(1 if first_mover == self.player1_spirit_onfield else 2) + " actions:")
            action(self, 1 if first_mover == self.player1_spirit_onfield else 2, first_action, True)

            if second_mover.hp <= 0:
                pass # todo
            
            print( "Player" + str(2 if first_mover == self.player1_spirit_onfield else 1) + " actions:")
            action(self, 2 if first_mover == self.player1_spirit_onfield else 1, second_action, False)

            if first_mover.hp <= 0:
                pass # todo

            update_after_turn(self)


    # 打印战局
    def print(self):
        print("=" * 50)
        print("                 Battle Summary                 ")
        print("=" * 50)

        print(f"Weather or Environment: Type {self.weather_or_environment['type']}, "
              f"Last Turn {self.weather_or_environment['last_turn']}, "
              f"Locked {self.weather_or_environment['locked']}")
        print("-" * 50)

        print(f"{'Player 1 Spirit':<25}{'Player 2 Spirit':>25}")
        print(f"{'HP: ' + str(self.player1_spirits[0].hp) + '/' + str(self.player1_spirits[0].maxhp):<25}"
              f"{'HP: ' + str(self.player2_spirits[0].hp) + '/' + str(self.player2_spirits[0].maxhp):>25}")
        print("-" * 50)

        print(f"{'Player 1 Skills':<25}{'Player 2 Skills':>25}")
        for i in range(max(len(self.player1_spirits[0].equipped_skills), len(self.player2_spirits[0].equipped_skills))):
            skill1 = self.player1_spirits[0].equipped_skills[i] if i < len(self.player1_spirits[0].equipped_skills) else None
            skill2 = self.player2_spirits[0].equipped_skills[i] if i < len(self.player2_spirits[0].equipped_skills) else None
            skill1_info = f"Skill ID {skill1.id}: PP {skill1.pp}/{skill1.maxpp}" if skill1 else ""
            skill2_info = f"Skill ID {skill2.id}: PP {skill2.pp}/{skill2.maxpp}" if skill2 else ""
            print(f"{skill1_info:<25}{skill2_info:>25}")
        print("-" * 50)

        print(f"{'Player 1 Imprints':<25}{'Player 2 Imprints':>25}")
        player1_imprints = self.player1_spirits[0].imprints
        player2_imprints = self.player2_spirits[0].imprints
        all_imprint_keys = set(player1_imprints.keys()).union(player2_imprints.keys())
        for key in all_imprint_keys:
            imprint1 = player1_imprints.get(key, 0)
            imprint2 = player2_imprints.get(key, 0)
            print(f"{key + ': ' + str(imprint1):<25}{key + ': ' + str(imprint2):>25}")
        print("-" * 50)

        print(f"{'Player 1 Abilities Boosts':<25}{'Player 2 Abilities Boosts':>25}")
        player1_abilities_boosts = self.player1_spirit_onfield.ability_boosts
        player2_abilities_boosts = self.player2_spirit_onfield.ability_boosts
        all_boost_keys = set(player1_abilities_boosts.keys()).union(player2_abilities_boosts.keys())
        for key in all_boost_keys:
            boost1 = player1_abilities_boosts.get(key, 0)
            boost2 = player2_abilities_boosts.get(key, 0)
            print(f"{key + ': ' + str(boost1):<25}{key + ': ' + str(boost2):>25}")
        print("=" * 50)

if __name__ == "__main__":
    all_skills = load_skills('res/skills.json')
    spirits = load_spirits('res/spirits.json', all_skills)

    spirit1 = copy.deepcopy(spirits[0])
    spirit1.equip_skills([1, 2, 3, 4])
    spirit2 = copy.deepcopy(spirits[0])
    spirit2.equip_skills([1, 3, 2, 4])
    player1_spirits = [spirit1]
    player2_spirits = [spirit2]
    battle = BattleCore(player1_spirits, player2_spirits)

    while True:
        battle.print()
        player1_action = int(input("Player 1, choose your action (skill ID): "))
        player2_action = int(input("Player 2, choose your action (skill ID): "))
        
        battle.battle(player1_action, player2_action)

        if spirit1.hp <= 0 or spirit2.hp <= 0:
            print("Battle Over!")
            break