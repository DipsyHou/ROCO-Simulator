import random

# if spirit1 is first return 1, else return 0
def compareSpeed(spirit1, spirit2):
    if spirit1.speed > spirit2.speed:
        return 1
    elif spirit1.speed < spirit2.speed:
        return 0
    else:
        return random.randint(0, 1)


def elementalAdvantage(skill, target_spirit):
    advantage_map = {
        "fire": {"plant": 1, "ice": 1, "metal": 1, "water": -1, "rock": -1, "earth": -1},
        "water": {"fire": 1, "rock": 1, "ground": 1, "plant": -1, "water": -1, "dragon": -1}
    }
    
    cnt = 0
    if skill.element in advantage_map:
        for element, value in advantage_map[skill.element].items():
            if element in target_spirit.element:
                cnt += value
    return (1 + cnt) if cnt >= 0 else (1.0 / (1 - cnt))


# 更改天气环境
def changeWeatherOrEnvironment(battle, which_player, skill, is_first_mover, new_weather_or_environment):
    acting_spirit = battle.player1_spirit_onfield if which_player == 1 else battle.player2_spirit_onfield
    target_spirit = battle.player2_spirit_onfield if which_player == 1 else battle.player1_spirit_onfield

    if battle.weather_or_environment["locked"] == 0 and battle.weather_or_environment["type"] * new_weather_or_environment["type"] >= 0:
        battle.weather_or_environment["type"] = new_weather_or_environment["type"]
        battle.weather_or_environment["last_turn"] = new_weather_or_environment["last_turn"]
        battle.weather_or_environment["locked"] = new_weather_or_environment["locked"]
        print(f"{acting_spirit.id} changed the weather/environment to {new_weather_or_environment['type']} for {new_weather_or_environment['last_turn']} turns.")


# 结算增减限伤
def calculate_buffs(battle, which_player, skill, is_first_mover):
    acting_spirit = battle.player1_spirit_onfield if which_player == 1 else battle.player2_spirit_onfield
    target_spirit = battle.player2_spirit_onfield if which_player == 1 else battle.player1_spirit_onfield

    # 初始化
    acting_spirit.physical_damage_boost_rate = 1.0
    acting_spirit.magical_damage_boost_rate = 1.0
    acting_spirit.real_damage_boost_rate = 1.0
    acting_spirit.physical_damage_boost = 0
    acting_spirit.magical_damage_boost = 0
    acting_spirit.real_damage_boost = 0
    target_spirit.physical_damage_reduction_rate = 1.0
    target_spirit.magical_damage_reduction_rate = 1.0
    target_spirit.real_damage_reduction_rate = 1.0
    target_spirit.physical_damage_reduction = 0
    target_spirit.magical_damage_reduction = 0
    target_spirit.real_damage_reduction = 0
    target_spirit.physical_damage_limit = 999
    target_spirit.magical_damage_limit = 999
    target_spirit.real_damage_limit = 999

    # 攻击宠物增伤区
    # 天气环境
    if battle.weather_or_environment["type"] == 1 and skill.element == "fire":  # 暴晒
        acting_spirit.physical_damage_boost_rate *= 1.5
        acting_spirit.magical_damage_boost_rate *= 1.5

    # 印记专属

    # 宠物专属
    
    #-------------------------------------------
    # 受击宠物减伤限伤区
    # 天气环境
    
    # 印记专属

    # 宠物专属
    if target_spirit.id == 1:
        target_spirit.physical_damage_limit = min(220 - target_spirit.imprints.get("Zhuque_Tianhuo_self", 0) * 20, target_spirit.physical_damage_limit)
        target_spirit.magical_damage_limit = min(220 - target_spirit.imprints.get("Zhuque_Tianhuo_self", 0) * 20, target_spirit.magical_damage_limit)
        target_spirit.real_damage_limit = min(220 - target_spirit.imprints.get("Zhuque_Tianhuo_self", 0) * 20, target_spirit.real_damage_limit)

             
# 伤害计算
# type: 0--真伤, 1--物理伤害, 2--魔法伤害
# preset_elemental_advantage 若为 None 则使用默认的元素克制关系
def attack(battle, which_player, skill, is_first_mover, type, power, preset_elemental_advantage):

    acting_spirit = battle.player1_spirit_onfield if which_player == 1 else battle.player2_spirit_onfield
    target_spirit = battle.player2_spirit_onfield if which_player == 1 else battle.player1_spirit_onfield

    elemental_advantage = preset_elemental_advantage if preset_elemental_advantage is not None else elementalAdvantage(skill, target_spirit)

    calculate_buffs(battle, which_player, skill, is_first_mover)

    if type == 0:
        damage = (power * acting_spirit.real_damage_boost_rate + acting_spirit.real_damage_boost - target_spirit.real_damage_reduction) * target_spirit.real_damage_reduction_rate * elemental_advantage
        damage = min(damage, target_spirit.real_damage_limit)
        damage = int(damage)
        target_spirit.hp -= max(damage, 1)
        print(f"{acting_spirit.id} dealt {max(damage, 1)} true damage to {target_spirit.id}.")

    elif type == 1:
        actual_atk = (acting_spirit.atk * (acting_spirit.ability_boosts["atk"] + 2.0) / 2.0) if acting_spirit.ability_boosts["atk"] >= 0 else (acting_spirit.atk * 2.0 / (2.0 - acting_spirit.ability_boosts["atk"]))
        actual_defence = (target_spirit.defence * (target_spirit.ability_boosts["defence"] + 2.0) / 2.0) if target_spirit.ability_boosts["defence"] >= 0 else (target_spirit.defence * 2.0 / (2.0 - target_spirit.ability_boosts["defence"]))
        actual_power = power * actual_atk / actual_defence
        damage = (actual_power * acting_spirit.physical_damage_boost_rate + acting_spirit.physical_damage_boost - target_spirit.physical_damage_reduction) * target_spirit.physical_damage_reduction_rate * elemental_advantage
        damage = min(damage, target_spirit.physical_damage_limit)
        damage = int(damage)
        target_spirit.hp -= max(damage, 1)
        print(f"{acting_spirit.id} dealt {max(damage, 1)} physical damage to {target_spirit.id}.")

    elif type == 2:
        actual_mp = (acting_spirit.mp * (acting_spirit.ability_boosts["mp"] + 2.0) / 2.0) if acting_spirit.ability_boosts["mp"] >= 0 else (acting_spirit.mp * 2.0 / (2.0 - acting_spirit.ability_boosts["mp"]))
        actual_resistance = (target_spirit.resistance * (target_spirit.ability_boosts["resistance"] + 2.0) / 2.0) if target_spirit.ability_boosts["resistance"] >= 0 else (target_spirit.resistance * 2.0 / (2.0 - target_spirit.ability_boosts["resistance"]))
        actual_power = power * actual_mp / actual_resistance
        damage = (actual_power * acting_spirit.magical_damage_boost_rate + acting_spirit.magical_damage_boost - target_spirit.magical_damage_reduction) * target_spirit.magical_damage_reduction_rate * elemental_advantage
        damage = min(damage, target_spirit.magical_damage_limit)
        damage = int(damage)
        target_spirit.hp -= max(damage, 1)
        print(f"{acting_spirit.id} dealt {max(damage, 1)} magical damage to {target_spirit.id}.")


# 使用技能
def action(battle, which_player, skill_id, is_first_mover):
    
    acting_spirit = battle.player1_spirit_onfield if which_player == 1 else battle.player2_spirit_onfield
    skill = next((skill for skill in acting_spirit.equipped_skills if skill.id == skill_id), None)
    if not skill:
        print(f"Skill {skill_id} is not equipped!")
        return
    
    if acting_spirit.id == 1:
        Zhuque(battle, which_player, skill, is_first_mover)
    elif acting_spirit.id == 2:
        Shelly_of_light(battle, which_player, skill, is_first_mover)

def Zhuque(battle, which_player, skill, is_first_mover):

    acting_spirit = battle.player1_spirit_onfield if which_player == 1 else battle.player2_spirit_onfield
    target_spirit = battle.player2_spirit_onfield if which_player == 1 else battle.player1_spirit_onfield

    # 南陆祺光
    if skill.id == 1:
        skill.pp -= 1

        # 回复血量
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] > 0:
            acting_spirit.hp = min(acting_spirit.hp + 80 * acting_spirit.imprints["Zhuque_Tianhuo_self"], acting_spirit.maxhp)
            print(f"{acting_spirit.id} restored {80 * acting_spirit.imprints['Zhuque_Tianhuo_self']} HP.")

        # 赐予天火
        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints:
            target_spirit.imprints["Zhuque_Tianhuo_enemy"] = 0
        target_spirit.imprints["Zhuque_Tianhuo_enemy"] += acting_spirit.imprints["Zhuque_Tianhuo_self"]
        if target_spirit.imprints["Zhuque_Tianhuo_enemy"] > 5:
            target_spirit.imprints["Zhuque_Tianhuo_enemy"] = 5
        acting_spirit.imprints["Zhuque_Tianhuo_self"] = 0

        # 强化变化技能-回复其他技能1pp
        if target_spirit.imprints["Zhuque_Tianhuo_enemy"] == 5:
            for skill in acting_spirit.skills:
                if skill.id != 1:
                    skill.pp = min(skill.pp + 1, skill.maxpp)

        # 领获天火
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] < 5:
            acting_spirit.imprints["Zhuque_Tianhuo_self"] += 1
            acting_spirit.hp = min(acting_spirit.hp + 80, acting_spirit.maxhp)
            print(f"{acting_spirit.id} restored {80} HP.")

    # 珠星垂影
    elif skill.id == 2:
        skill.pp -= 1

        # 恐惧对手
        # todo

        # 召唤疾风天气
        changeWeatherOrEnvironment(battle, which_player, skill, is_first_mover, {"type": 2, "last_turn": 3, "locked": 0})

        # 删除对方群1
        for skill in target_spirit.equipped_skills:
            skill.pp = max(skill.pp - 1, 0)
        
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] < 5:
            acting_spirit.imprints["Zhuque_Tianhuo_self"] += 1
            
        # 强化变化技能-回复其他技能1pp
        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints or target_spirit.imprints["Zhuque_Tianhuo_enemy"] < 5:
            pass
        else:
            for skill in acting_spirit.skills:
                if skill.id != 1:
                    skill.pp = min(skill.pp + 1, skill.maxpp)

        # 领获天火
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] < 5:
            acting_spirit.imprints["Zhuque_Tianhuo_self"] += 1
            acting_spirit.hp = min(acting_spirit.hp + 80, acting_spirit.maxhp)
            print(f"{acting_spirit.id} restored {80} HP.")

    # 鹑火伏辰
    elif skill.id == 3:
        skill.pp -= 1

        # 召唤暴晒天气
        changeWeatherOrEnvironment(battle, which_player, skill, is_first_mover, {"type": 1, "last_turn": 3, "locked": 0})
        
        # 威力伤害
        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints or target_spirit.imprints["Zhuque_Tianhuo_enemy"] < 5:
            attack(battle, which_player, skill, is_first_mover, 2, 90, None)
        # 强化威力技能-必定克制
        else:
            attack(battle, which_player, skill, is_first_mover, 2, 90, 2)

        # 依据对手被天火灼烧次数造成固伤
        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints or target_spirit.imprints["Zhuque_Tianhuo_enemy"] == 0 :
            pass
        else:
            attack(battle, which_player, skill, is_first_mover, 0, 20 * target_spirit.imprints["Zhuque_Tianhuo_enemy"], 1)

        # 领获天火
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] < 5:
            acting_spirit.imprints["Zhuque_Tianhuo_self"] += 1
            acting_spirit.hp = min(acting_spirit.hp + 80, acting_spirit.maxhp)
            print(f"{acting_spirit.id} restored {80} HP.")

    
    # 驱邪咒缚
    elif skill.id == 4:
        skill.pp -= 1

        # 删群1
        for skill in target_spirit.equipped_skills:
            skill.pp = max(skill.pp - 1, 0)

        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints or target_spirit.imprints["Zhuque_Tianhuo_enemy"] < 5:

            # 未造成克制伤害强化1级魔攻
            if elementalAdvantage(skill, target_spirit) <= 0:
                acting_spirit.ability_boosts["mp"] = (acting_spirit.ability_boosts["mp"] + 1) if acting_spirit.ability_boosts["mp"] < 1 else acting_spirit.ability_boosts["mp"]

            # 造成抵抗伤害额外删群1
            if elementalAdvantage(skill, target_spirit) < 0:
                for skill in target_spirit.equipped_skills:
                    skill.pp = max(skill.pp - 1, 0)
        # 威力伤害
            attack(battle, which_player, skill, is_first_mover, 2, 100, None)
        # 强化威力技能-必定克制    
        else:
            attack(battle, which_player, skill, is_first_mover, 2, 100, 2)
        
        # 领获天火
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] < 5:
            acting_spirit.imprints["Zhuque_Tianhuo_self"] += 1
            acting_spirit.hp = min(acting_spirit.hp + 80, acting_spirit.maxhp)
            print(f"{acting_spirit.id} restored {80} HP.")

        
def Shelly_of_light(acting_spirit, skill, target_spirit, is_first_mover, weather_or_environment):
    
    # 柔如彩虹
    if skill.id == 5:
        skill.pp -= 1

        # 回复血量
        healing_amount = int(acting_spirit.maxhp * 0.5)
        acting_spirit.hp = min(acting_spirit.hp, acting_spirit.maxhp)
        print(f"{acting_spirit.id} restored {healing_amount} HP.")

        # 获得4回合异常免疫与限伤
        acting_spirit.imprints["abnormality_immunity"] = 4
        acting_spirit.imprints["shelly_of_light_damage_limit"] = 4

    # 永恒思念

    # 圣光祝福
    elif skill.id == 7:
        skill.pp -= 1

        # 永久提升队友威力伤害
        acting_spirit.physical_damage_boost_rate *= 1.2
        acting_spirit.magical_damage_boost_rate *= 1.2


        # 生命值低时效果提升

    # 至神约束
    elif skill.id == 8:
        skill.pp -= 1

        # 重置并锁定全场强化

        # 生命值低时效果提升
