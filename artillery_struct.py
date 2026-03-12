import json

from enum import Enum


class ArtilleryType(Enum):
    ROCKET = "ROCKET"
    MORTAR = "MORTAR"
    TUBE = "ARTI"


class Artillery:
    gun_name = ""
    example_gun = ""
    ammo_name = ""
    calibre = 0
    aim_time = 0
    reload_time = 0
    damage = 0
    damage_radius = 0
    suppression = 0
    suppression_radius = 0
    min_range = 0
    max_range = 0
    min_range_dispersion = 0
    max_range_dispersion = 0
    projectiles_salvo = 0
    ammo_count = 0
    weapon_cost = 0
    supply_cost = 0
    corrected_shot_aim_time_multiplier = 1.0
    corrected_shot_dispersion_multiplier = 1.0
    artillery_type = ArtilleryType.TUBE

    def __init__(self, gun_name, example_gun, ammo_name, calibre, aim_time, reload_time, damage, damage_radius,
                 suppression, suppression_radius, min_range, max_range, min_range_dispersion, max_range_dispersion,
                 projectiles_salvo, ammo_count, weapon_cost, supply_cost, corrected_shot_dispersion_multiplier,
                 corrected_shot_aim_time_multiplier, artillery_type):
        self.gun_name = gun_name
        self.example_gun = example_gun
        self.ammo_name = ammo_name
        self.calibre = calibre
        self.aim_time = aim_time
        self.reload_time = reload_time
        self.damage = damage
        self.damage_radius = damage_radius
        self.suppression = suppression
        self.suppression_radius = suppression_radius
        self.min_range = min_range
        self.max_range = max_range
        self.min_range_dispersion = min_range_dispersion
        self.max_range_dispersion = max_range_dispersion
        self.projectiles_salvo = projectiles_salvo
        self.ammo_count = ammo_count
        self.weapon_cost = weapon_cost
        self.supply_cost = supply_cost
        self.corrected_shot_aim_time_multiplier = corrected_shot_dispersion_multiplier
        self.corrected_shot_dispersion_multiplier = corrected_shot_aim_time_multiplier
        self.artillery_type = artillery_type

    def dispersion(self, distance):
        if distance < self.min_range or distance > self.max_range:
            return None
        ratio = (distance - self.min_range) / (self.max_range - self.min_range)
        return self.min_range_dispersion + ratio * (self.max_range_dispersion - self.min_range_dispersion)

    def to_json(self):
        data = self.__dict__.copy()
        data["artillery_type"] = self.artillery_type.value  # convert enum to string
        return json.dumps(data, indent=4)

    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        data["artillery_type"] = ArtilleryType(data["artillery_type"])  # convert string back to enum
        return Artillery(**data)
