from skills import Skill

import json


class Spirit:
    def __init__(
        self, id, element, level, maxhp, hp, atk, mp, defence, resistance, speed,
        ability_boosts, abnormalities, abnormality_resistances, imprints,
        skills,
    ):
        self.id = id
        self.element = element
        self.level = level
        self.maxhp = maxhp
        self.hp = hp
        self.atk = atk
        self.mp = mp
        self.defence = defence
        self.resistance = resistance
        self.speed = speed
        self.skills = skills
        self.equipped_skills = []
        self.ability_boosts = ability_boosts
        self.abnormalities = abnormalities
        self.abnormality_resistances = abnormality_resistances
        self.imprints = imprints
        self.physical_damage_boost_rate = 1.0
        self.magical_damage_boost_rate = 1.0
        self.real_damage_boost_rate = 1.0
        self.physical_damage_boost = 0
        self.magical_damage_boost = 0
        self.real_damage_boost = 0
        self.physical_damage_reduction_rate = 1.0
        self.magical_damage_reduction_rate = 1.0
        self.real_damage_reduction_rate = 1.0
        self.physical_damage_reduction = 0
        self.magical_damage_reduction = 0
        self.real_damage_reduction = 0
        self.physical_damage_limit = 999
        self.magical_damage_limit = 999
        self.real_damage_limit = 999
        self.sheild = 0


    # 装备技能    
    def equip_skills(self, skill_ids):
        self.equipped_skills = [skill for skill in self.skills if skill.id in skill_ids]
        if len(self.equipped_skills) > 4:
            self.equipped_skills = self.equipped_skills[:4]

    # 分配天赋
    def allocate_talent(self, talent):
        attributes = ["maxhp", "atk", "mp", "defence", "resistance", "speed"]
        for attr in attributes:
            setattr(self, attr, getattr(self, attr) + talent[attr])
    
        self.hp = self.maxhp

    # 选择性格
    def choose_character(self, boost, reduction):
        attributes = {
            "atk": "atk",
            "defence": "defence",
            "mp": "mp",
            "resistance": "resistance",
            "speed": "speed"
        }

        if boost in attributes:
            setattr(self, attributes[boost], getattr(self, attributes[boost]) * 1.1)
        if reduction in attributes:
            setattr(self, attributes[reduction], getattr(self, attributes[reduction]) * 0.9)