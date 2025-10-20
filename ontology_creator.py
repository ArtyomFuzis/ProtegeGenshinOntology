from owlready2 import *
import csv


def formalized(some_str: str) -> str:
    return some_str.replace(" ", "_").replace("'","").replace("\"","~")

# Загрузить онтологию
onto = get_ontology("http://example.org/my_ontology")
with onto:
    class Character(Thing):
        pass
    
    class Weapon(Thing):
        pass

    class Monster(Thing):
        pass

    class PersonWeaponType(Thing):
        pass
    
    class WeaponType(Thing):
        pass

    class Rarity(Thing):
        pass

    class Region(Thing):
        pass

    class Element(Thing):
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
        range = [PersonWeaponType]
    
    class weapon_type(ObjectProperty):
        domain = [Weapon]
        range = [WeaponType]
    
    class weapon_rarity(ObjectProperty):
        domain = [Weapon]
        range = [Rarity]
    
    class SwordWeapon(Weapon):
        pass
    
    class PolearmWeapon(Weapon):
        pass
    
    class ClaymoreWeapon(Weapon):
        pass
    
    class BowWeapon(Weapon):
        pass

    class CatalystWeapon(Weapon):
        pass


with open('characters.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rarity = onto.Rarity(formalized(row['Rarity']))
        region = onto.Region(formalized(row['Region']))
        element = onto.Element(formalized(row['Element']))
        weapon = onto.PersonWeaponType(formalized(row['Weapon']))
       
        individual = onto.Character(formalized(row['Name']))
        individual.character_rarity = [rarity]
        individual.character_region = [region]
        individual.character_element = [element]
        individual.character_weapon_type = [weapon]

def parseWeapon(type, csv_file):
    with open(csv_file, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rarity = onto.Rarity(formalized(row['Rarity']))
            individual = type(formalized(row['Name']))
            individual.weapon_rarity = [rarity]
            individual.character_element = [element]
            individual.character_weapon_type = [weapon]

parseWeapon(onto.SwordWeapon,"swords.csv")
parseWeapon(onto.PolearmWeapon,"polearms.csv")
parseWeapon(onto.ClaymoreWeapon,"claymores.csv")
parseWeapon(onto.BowWeapon,"bows.csv")
parseWeapon(onto.CatalystWeapon,"catalysts.csv")
onto.save(file="my_ontology.rdf", format="rdfxml")