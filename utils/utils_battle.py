import random


# 决定先手
# spirit1先手则返回 1, 否则返回 0
def compareSpeed(spirit1, spirit2):
    if spirit1.speed > spirit2.speed:
        return 1
    elif spirit1.speed < spirit2.speed:
        return 0
    else:
        return random.randint(0, 1)


# 计算属性克制关系
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
        acting_spirit.physical_damage_boost_rate += 0.5
        acting_spirit.magical_damage_boost_rate += 0.5

    # 印记专属
    if "shelly_of_light_blessing" not in acting_spirit.imprints or acting_spirit.imprints["shelly_of_light_blessing"] == 0:
        pass
    elif acting_spirit.imprints["shelly_of_light_blessing"] == 1:
        acting_spirit.physical_damage_boost_rate += 0.15
        acting_spirit.magical_damage_boost_rate += 0.15
    elif acting_spirit.imprints["shelly_of_light_blessing"] == 2:
        acting_spirit.physical_damage_boost_rate += 0.25
        acting_spirit.magical_damage_boost_rate += 0.25

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


# 改变强化等级
# 参数说明：
# boost_or_reduction: 1代表正面, 0代表负面
# boost_level: 强化等级, 为正数
# boost_level_limit: 如果为 None 则不限制最大强化等级
def changeAbilityBoosts(battle, which_player, skill, is_first_mover, target_spirit, ability_type, boost_or_reduction, boost_level, boost_level_limit):
    # 锁强
    if "shelly_of_light_binding_self" not in target_spirit.imprints or target_spirit.imprints["shelly_of_light_binding_self"] == 0:
        pass
    elif "shelly_of_light_binding_enemy" not in target_spirit.imprints or target_spirit.imprints["shelly_of_light_binding_enemy"] == 0:
        pass
    else:
        print(f"{target_spirit.id} is bound and cannot change ability boosts.")
        return

    if boost_or_reduction == 1:
        if ability_type == "atk":
            target_spirit.ability_boosts["atk"] = min(target_spirit.ability_boosts["atk"] + boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["atk"] + boost_level
        elif ability_type == "defence":
            target_spirit.ability_boosts["defence"] = min(target_spirit.ability_boosts["defence"] + boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["defence"] + boost_level
        elif ability_type == "mp":
            target_spirit.ability_boosts["mp"] = min(target_spirit.ability_boosts["mp"] + boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["mp"] + boost_level
        elif ability_type == "resistance":
            target_spirit.ability_boosts["resistance"] = min(target_spirit.ability_boosts["resistance"] + boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["resistance"] + boost_level
        elif ability_type == "speed":
            target_spirit.ability_boosts["speed"] = min(target_spirit.ability_boosts["speed"] + boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["speed"] + boost_level
        print(f"{target_spirit.id} received a boost of {boost_level} in {ability_type}. Current level: {target_spirit.ability_boosts[ability_type]}")
    
    elif boost_or_reduction == 0:
        if ability_type == "atk":
            target_spirit.ability_boosts["atk"] = max(target_spirit.ability_boosts["atk"] - boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["atk"] - boost_level
        elif ability_type == "defence":
            target_spirit.ability_boosts["defence"] = max(target_spirit.ability_boosts["defence"] - boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["defence"] - boost_level
        elif ability_type == "mp":
            target_spirit.ability_boosts["mp"] = max(target_spirit.ability_boosts["mp"] - boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["mp"] - boost_level
        elif ability_type == "resistance":
            target_spirit.ability_boosts["resistance"] = max(target_spirit.ability_boosts["resistance"] - boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["resistance"] - boost_level
        elif ability_type == "speed":
            target_spirit.ability_boosts["speed"] = max(target_spirit.ability_boosts["speed"] - boost_level, boost_level_limit) if boost_level_limit else target_spirit.ability_boosts["speed"] - boost_level
        print(f"{target_spirit.id} received a reduction of {boost_level} in {ability_type}. Current level: {target_spirit.ability_boosts[ability_type]}")


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
            if elementalAdvantage(skill, target_spirit) <= 1:
                changeAbilityBoosts(battle, which_player, skill, is_first_mover, acting_spirit, "mp", boost_or_reduction = 1, boost_level = 1, boost_level_limit = 1)

            # 造成抵抗伤害额外删群1
            if elementalAdvantage(skill, target_spirit) < 1:
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
        
def Shelly_of_light(battle, which_player, skill, is_first_mover):

    acting_spirit = battle.player1_spirit_onfield if which_player == 1 else battle.player2_spirit_onfield
    target_spirit = battle.player2_spirit_onfield if which_player == 1 else battle.player1_spirit_onfield
    acting_spirit_team = battle.player1_spirits if which_player == 1 else battle.player2_spirits
    target_spirit_team = battle.player2_spirits if which_player == 1 else battle.player1_spirits
    
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


    # 圣光祝福
    elif skill.id == 6:
        skill.pp -= 1

        # 终止约束效果
        for spirit in acting_spirit_team:
            spirit.imprints["shelly_of_light_binding_self"] = 0

        for spirit in target_spirit_team:
            spirit.imprints["shelly_of_light_binding_enemy"] = 0

        # 永久提升队友威力伤害
        if acting_spirit.hp >= acting_spirit.maxhp * 0.25:
            for spirit in acting_spirit_team:
                spirit.imprints["shelly_of_light_blessing"] = 1

        # 生命值低时效果提升    
        else:
            for spirit in acting_spirit_team:
                spirit.imprints["shelly_of_light_blessing"] = 2
            

    # 至神约束
    elif skill.id == 7:
        skill.pp -= 1

        # 终止祝福效果
        for spirit in acting_spirit_team:
            spirit.imprints["shelly_of_light_blessing"] = 0

        # 生命值低时额外强制重置全场强化
        if acting_spirit.hp < acting_spirit.maxhp * 0.25:
            for spirit in acting_spirit_team + target_spirit_team:
                spirit.ability_boosts["atk"] = 0
                spirit.ability_boosts["mp"] = 0
                spirit.ability_boosts["defence"] = 0
                spirit.ability_boosts["resistance"] = 0
                spirit.ability_boosts["speed"] = 0

        # 锁定全场强化
        for spirit in acting_spirit_team:
            spirit.imprints["shelly_of_light_binding_self"] = 1

        for spirit in target_spirit_team:
            spirit.imprints["shelly_of_light_binding_enemy"] = 1


    # 永恒思念
    elif skill.id == 8:
        skill.pp -= 1

        # 祝福效果生效时额外效果
        if acting_spirit.imprints["shelly_of_light_blessing"] > 0:
            pass
        # 约束效果生效时额外效果
        if acting_spirit.imprints["shelly_of_light_binding_self"] > 0:
            pass
        
            
        
