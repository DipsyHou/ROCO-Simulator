
def update_after_turn(battle):
    for spirit in [battle.player1_spirit_onfield, battle.player2_spirit_onfield]:

        # 异常标记结算
        if "abnormal_immune" in spirit.imprints and spirit.imprints["abnormal_immune"]:
            spirit.imprint["abnormality_immunity"] -= 1

        # 宠物特殊标记结算
        if "shelly_of_light_damage_limit" in spirit.imprints and spirit.imprints["shelly_of_light_damage_limit"]:
            spirit.imprint["shelly_of_light_damage_limit"] -= 1