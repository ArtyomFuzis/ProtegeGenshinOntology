from owlready2 import *
import csv


def formalized(some_str: str) -> str:
    return some_str.replace(" ", "_").replace("'","").replace("\"","~~").replace("'", "~").replace("`", "~~~")

# Загрузить онтологию
onto = get_ontology("http://example.org/my_ontology")
with onto:
    class Character(Thing):
        pass
    
    class Weapon(Thing):
        pass

    class Monster(Thing):
        pass
    
    class WeaponType(Thing):
        pass

    class Rarity(Thing):
        pass

    class Region(Thing):
        pass

    class Element(Thing):
        pass

    class MonsterType(Thing):
        pass

    class character_element(ObjectProperty):
        domain = [Character]
        range = [Element]
    
    class character_region(ObjectProperty):
        domain = [Character]
        range = [Region]
    
    class character_rarity(ObjectProperty):
        domain = [Character]
        range = [Rarity]
    
    class character_weapon_type(ObjectProperty):
        domain = [Character]
        range = [WeaponType]
    
    class weapon_type(ObjectProperty):
        domain = [Weapon]
        range = [WeaponType]
    
    class weapon_rarity(ObjectProperty):
        domain = [Weapon]
        range = [Rarity]
    
    class monster_type(ObjectProperty):
        domain = [Monster]
        range = [MonsterType]
    
    class monster_region(ObjectProperty):
        domain = [Monster]
        range = [Region]
     


with open('characters.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rarity = onto.Rarity(formalized(row['Rarity']))
        region = onto.Region(formalized(row['Region']))
        element = onto.Element(formalized(row['Element']))
        weapon = onto.Weapon(formalized(row['Weapon']))
       
        individual = onto.Character(formalized(row['Name']))
        individual.character_rarity = [rarity]
        individual.character_region = [region]
        individual.character_element = [element]
        individual.character_weapon_type = [weapon]

def parseWeapon(wtype, csv_file):
    with open(csv_file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rarity = onto.Rarity(formalized(row['Rarity']))
            weapon_type = onto.WeaponType(wtype)
            individual = onto.Weapon(formalized(row['Name']))
            individual.weapon_rarity = [rarity]
            individual.weapon_type = [weapon_type]

def parseBoss(mtype, csv_file):
    with open(csv_file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            monster_type = onto.MonsterType(mtype)
            individual = onto.Monster(formalized(row['Name']))
            region = onto.Region(formalized(row['Region']))
            individual.monster_type = [monster_type]
            individual.monster_region = [region]

parseWeapon("Sword","swords.csv")
parseWeapon("Polearm","polearms.csv")
parseWeapon("Claymore","claymores.csv")
parseWeapon("Bow","bows.csv")
parseWeapon("Catalyst","catalysts.csv")
parseBoss("WeeklyBoss","weekly_monsters.csv")
parseBoss("NormalBoss","normal_monsters_m.csv")
parseBoss("NormalBoss","normal_monsters_l.csv")
parseBoss("NormalBoss","normal_monsters_i.csv")
parseBoss("NormalBoss","normal_monsters_s.csv")
parseBoss("NormalBoss","normal_monsters_f.csv")
parseBoss("NormalBoss","normal_monsters_n.csv")
parseBoss("NormalBoss","normal_monsters_nc.csv")
onto.save(file="my_ontology.rdf", format="rdfxml")