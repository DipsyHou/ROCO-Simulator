from spirit import Spirit
from skills import Skill

import random
import json

def load_skills(file_path):
    with open(file_path, 'r') as file:
        skills_data = json.load(file)
        return [Skill(**skill_data) for skill_data in skills_data]

def load_spirits(file_path, all_skills):
    with open(file_path, 'r') as file:
        spirits_data = json.load(file)
        spirits = []
        for spirit_data in spirits_data:
            spirit_data['skills'] = [skill for skill in all_skills if skill.id in spirit_data['skills']]
            spirits.append(Spirit(**spirit_data))
        return spirits
