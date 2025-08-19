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


# 结算增减限伤
def calculate_buffs(acting_spirit, target_spirit, is_first_mover, weather_or_environment, skill):
    # 攻击宠物增伤区
    # 天气环境
    if weather_or_environment["type"] == 1 and skill.element == "fire":  # 暴晒
        acting_spirit.physical_damage_boost_rate *= 1.5
        acting_spirit.magical_damage_boost_rate *= 1.5
    # 印记专属

    # 宠物专属
    
    #-------------------------------------------
    # 受击宠物减伤限伤区
    # 天气环境
    
    # 印记专属

    # 宠物专属
    if(target_spirit.id == 1):
        target_spirit.physical_damage_limit = min(220 - target_spirit.imprints["Zhuque_Tianhuo_self"] * 20, target_spirit.physical_damage_limit)
        target_spirit.magical_damage_limit = min(220 - target_spirit.imprints["Zhuque_Tianhuo_self"] * 20, target_spirit.magical_damage_limit)
        target_spirit.real_damage_limit = min(220 - target_spirit.imprints["Zhuque_Tianhuo_self"] * 20, target_spirit.real_damage_limit)

             
# 伤害计算
# type: 0--真伤, 1--物理伤害, 2--魔法伤害
def attack(acting_spirit, target_spirit, weather_or_environment, type, power, elemental_advantage, skill):
    calculate_buffs(acting_spirit, target_spirit, True, weather_or_environment, skill)
    calculate_buffs(target_spirit, acting_spirit, False, weather_or_environment, skill)
    
    if type == 0:
        damage = (power * acting_spirit.real_damage_boost_rate + acting_spirit.real_damage_boost - target_spirit.real_damage_reduction) * target_spirit.real_damage_reduction_rate * elemental_advantage
        damage = min(damage, target_spirit.real_damage_limit)
        target_spirit.hp -= max(damage, 1)
        print(f"{acting_spirit.id} dealt {max(damage, 1)} true damage to {target_spirit.id}.")

    elif type == 1:
        actual_atk = (acting_spirit.atk * (acting_spirit.ability_boosts["atk"] + 2.0) / 2.0) if acting_spirit.ability_boosts["atk"] >= 0 else (acting_spirit.atk * 2.0 / (2.0 - acting_spirit.ability_boosts["atk"]))
        actual_defence = (target_spirit.defence * (target_spirit.ability_boosts["defence"] + 2.0) / 2.0) if target_spirit.ability_boosts["defence"] >= 0 else (target_spirit.defence * 2.0 / (2.0 - target_spirit.ability_boosts["defence"]))
        actual_power = power * actual_atk / actual_defence
        damage = (actual_power * acting_spirit.physical_damage_boost_rate + acting_spirit.physical_damage_boost - target_spirit.physical_damage_reduction) * target_spirit.physical_damage_reduction_rate * elemental_advantage
        damage = min(damage, target_spirit.physical_damage_limit)
        target_spirit.hp -= max(damage, 0)
        print(f"{acting_spirit.id} dealt {max(damage, 1)} physical damage to {target_spirit.id}.")

    elif type == 2:
        actual_mp = (acting_spirit.mp * (acting_spirit.ability_boosts["mp"] + 2.0) / 2.0) if acting_spirit.ability_boosts["mp"] >= 0 else (acting_spirit.mp * 2.0 / (2.0 - acting_spirit.ability_boosts["mp"]))
        actual_resistance = (target_spirit.resistance * (target_spirit.ability_boosts["resistance"] + 2.0) / 2.0) if target_spirit.ability_boosts["resistance"] >= 0 else (target_spirit.resistance * 2.0 / (2.0 - target_spirit.ability_boosts["resistance"]))
        actual_power = power * actual_mp / actual_resistance
        damage = (actual_power * acting_spirit.magical_damage_boost_rate + acting_spirit.magical_damage_boost - target_spirit.magical_damage_reduction) * target_spirit.magical_damage_reduction_rate * elemental_advantage
        damage = min(damage, target_spirit.magical_damage_limit)
        target_spirit.hp -= max(damage, 0)
        print(f"{acting_spirit.id} dealt {max(damage, 1)} magical damage to {target_spirit.id}.")


# 使用技能
def action(acting_spirit, skill_id, target_spirit, is_first_mover, weather_or_environment):
    skill = next((skill for skill in acting_spirit.equipped_skills if skill.id == skill_id), None)
    if not skill:
        print(f"Skill {skill_id} is not equipped!")
        return

    # 南陆祺光
    if skill.id == 1:
        skill.pp -= 1

        # 回复血量
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
        if weather_or_environment["type"] >= 0 and weather_or_environment["locked"] == 0:
            weather_or_environment["type"] = 2
            weather_or_environment["last_turn"] = 3

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
        if weather_or_environment["type"] >= 0 and weather_or_environment["locked"] == 0:
            weather_or_environment["type"] = 1
            weather_or_environment["last_turn"] = 3
        
        # 威力伤害
        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints or target_spirit.imprints["Zhuque_Tianhuo_enemy"] < 5:
            attack(acting_spirit, target_spirit, weather_or_environment, 2, 90, 2, skill)
        # 强化威力技能-必定克制
        else:
            attack(acting_spirit, target_spirit, weather_or_environment, 2, 90, elementalAdvantage(skill, target_spirit), skill)

        # 依据对手被天火灼烧次数造成固伤
        if "Zhuque_Tianhuo_enemy" not in target_spirit.imprints:
            pass
        else:
            attack(acting_spirit, target_spirit, weather_or_environment, 0, 20 * target_spirit.imprints["Zhuque_Tianhuo_enemy"], 1, skill)

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
            attack(acting_spirit, target_spirit, weather_or_environment, 2, 100, elementalAdvantage(skill, target_spirit), skill)
        # 强化威力技能-必定克制    
        else:
            attack(acting_spirit, target_spirit, weather_or_environment, 2, 100, 2, skill)
        
        # 领获天火
        if acting_spirit.imprints["Zhuque_Tianhuo_self"] < 5:
            acting_spirit.imprints["Zhuque_Tianhuo_self"] += 1
            acting_spirit.hp = min(acting_spirit.hp + 80, acting_spirit.maxhp)
            print(f"{acting_spirit.id} restored {80} HP.")
        
