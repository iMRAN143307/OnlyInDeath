import pygame
import sys
import os
import asyncio
import random

pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
screen = pygame.display.set_mode((1280, 720))

def resource_path(relative_path):
    try:
        base_path = sys.MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

async def main():

    pygame.mixer.music.load(os.path.join("music.ogg"))
    pygame.mixer.music.play(loops=-1, start=0.0)

    def load_and_scale(filename, size=None, transparency=None):
        if transparency is not None:
            unscaled = pygame.image.load(resource_path(f"{filename}.png")).convert_alpha()
        else:
            unscaled = pygame.image.load(resource_path(f"{filename}.png")).convert()
        if size is not None:
            return pygame.transform.scale(unscaled, size)
        else:
            return unscaled

    font = pygame.font.SysFont(None, 48)

    attack = load_and_scale("attack")
    forfeit = load_and_scale("forfeit")
    item = load_and_scale("item")
    skill = load_and_scale("skill")
    bg = load_and_scale("bg", (1280, 720))
    slime = load_and_scale("slime", None, True)
    player = load_and_scale("player", (75, 200), True)
    skeleton = load_and_scale("skeleton", (40, 60), True)
    ghoul = load_and_scale("ghoul", None, True)

    running = True

    round = 0

    keydelay = 30

    playerstats = {"STR": 0, "DEX": 0, "INT": 0, "CON": 0}

    playeritems = []

    playerweapons = [
    "stick",
    ]

    playerskills = []

    playercurrency = 0 #name currency; DO NOT MAKE IT GOLD

    playerhp = 10

    playermagicresource = 0 #name magic resource; DO NOT MAKE IT MANA

    currentenemies = [["slime", 2, slime]] #(enemy0, health, sprite)

    enemies = { #(STR, DEX, INT, CON), (basedmg, %ofSTR, %ofDEX, %ofINT), "attribute"
    "slime": ((1, 1, 1, 2), (1, 0.5, 0, 0), ""),
    "skeleton": ((2, 2, 1, 1), (1, 0, 1, 0), ""),
    "ghoul": ((1, 2, 2, 2), (2, 0, 0, 0.5), "tough")
    }

    attributes = [
    "tough", #enemy attacks with -1 STR
    ]

    mode = "playerturn"

    modes = ["playerturn", "enemyturn", "levelup", "shop", "mainmenu", "attackoptions", "skilloptions", "itemoptions"]

    battleoptions = ["attack", "skill", "item", "forfeit"] #maybe add some bonus when you forfeit to encourage players to forfeit and then bounce back

    battleoption = 0

    weaponoption = 0

    weapons = { #weapon: (basedmg, %ofSTR, %ofDEX, %ofINT, (skillsgiven))
        "stick": (1, 0, 0, 0, ()),
        "shortsword": (2, 0.5, 0.25, 0),
        "longsword": (4, 1, 0.25, 0),
        "shortbow": (2, 0.1, 0.5, 0.1),
        "longbow": (3, 0.25, 1, 0.25),
        "wand": (3, 0, 0, 0.5),
        "staff": (4, 0, 0, 1.25)
    }

    skills = { #skill: (resourcecost)

    }

    lupoption = 0
    shoption = -1

    clock = pygame.time.Clock()

    def generate(round):
        le = []
        if round < 5:
            var = random.choice([["slime", 0, slime], ["slime", 0, slime], ["skeleton", 0, skeleton]])
            le.append(var)
        elif round < 10:
            var = random.choice([["slime", 0, slime], ["slime", 0, slime], ["skeleton", 0, skeleton]])
            le.append(var)
            var = random.choice([["slime", 0, slime], ["skeleton", 0, skeleton], ["ghoul", 0, ghoul]])
            le.append(var)
        else:
            var = random.choice([["slime", 0, slime], ["slime", 0, slime], ["skeleton", 0, skeleton], ["ghoul", 0, ghoul]])
            le.append(var)
            var = random.choice([["slime", 0, slime], ["slime", 0, slime], ["skeleton", 0, skeleton], ["ghoul", 0, ghoul]])
            le.append(var)
            var = random.choice([["slime", 0, slime], ["skeleton", 0, skeleton], ["ghoul", 0, ghoul]])
            le.append(var)

        for enemy in le:
            enemy[1] = max(enemies[enemy[0]][0][3] * (round//3), 1)

        return le

    while running:

        screen.blit(bg, (0, 0))

        for i, enemy in enumerate(currentenemies):
            screen.blit(enemy[2], (700 + (100*i), 200))
            text_surface = font.render(str(enemy[1]), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(725 + (100 * i), 300))
            screen.blit(text_surface, text_rect)

        screen.blit(player, (158, 80))
        text_surface = font.render(str(playerhp), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(200, 300))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if mode == "shop":
            if shoption == -1:
                shoption = 0
                shopitem = random.choice(["stick", "stick", "stick", "shortsword", "shortsword", "shortbow", "shortbow", "wand", "wand", "staff", "longbow", "longsword"])
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and keydelay == 0:
                shoption = (shoption - 1) % 4
                keydelay = 30
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and keydelay == 0:
                shoption = (shoption + 1) % 4
                keydelay = 30
            elif keys[pygame.K_SPACE] and keydelay == 0:
                keydelay = 30
                if len(playerweapons) <= 4 and shoption == 0:
                    playerweapons.append(shopitem)
                shoption = -1
                currentenemies = generate(round)
                mode = "playerturn"

            if shoption == 0:
                text_surface = font.render("Yes", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(200, 600))
                screen.blit(text_surface, text_rect)
            elif shoption == 1:
                text_surface = font.render("No", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(1000, 600))
                screen.blit(text_surface, text_rect)

            text_surface = font.render(shopitem, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(600, 600))
            screen.blit(text_surface, text_rect)


        elif mode == "levelup":

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and keydelay == 0:
                lupoption = (lupoption - 1) % 4
                keydelay = 30
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and keydelay == 0:
                lupoption = (lupoption + 1) % 4
                keydelay = 30
            elif keys[pygame.K_SPACE] and keydelay == 0:
                keydelay = 30
                round += 1
                if lupoption == 0:
                    playerstats["STR"] += 1
                elif lupoption == 1:
                    playerstats["DEX"] += 1
                elif lupoption == 2:
                    playerstats["INT"] += 1
                elif lupoption == 3:
                    playerstats["CON"] += 1
                playerhp += playerstats["CON"]
                mode = "shop"

            text_surface = font.render("Level Up!", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(630, 500))
            screen.blit(text_surface, text_rect)

            if lupoption == 0:
                colour = (255, 255, 0)
            else:
                colour = (255, 255, 255)

            text_surface = font.render(f"STR: {playerstats["STR"]}", True, colour)
            text_rect = text_surface.get_rect(center=(300, 600))
            screen.blit(text_surface, text_rect)

            if lupoption == 1:
                colour = (255, 255, 0)
            else:
                colour = (255, 255, 255)

            text_surface = font.render(f"DEX: {playerstats["DEX"]}", True, colour)
            text_rect = text_surface.get_rect(center=(500, 600))
            screen.blit(text_surface, text_rect)

            if lupoption == 2:
                colour = (255, 255, 0)
            else:
                colour = (255, 255, 255)

            text_surface = font.render(f"INT: {playerstats["INT"]}", True, colour)
            text_rect = text_surface.get_rect(center=(700, 600))
            screen.blit(text_surface, text_rect)

            if lupoption == 3:
                colour = (255, 255, 0)
            else:
                colour = (255, 255, 255)

            text_surface = font.render(f"CON: {playerstats["CON"]}", True, colour)
            text_rect = text_surface.get_rect(center=(900, 600))
            screen.blit(text_surface, text_rect)

        elif mode == "enemyturn":
            for enemy in currentenemies:
                enemydmgs = enemies[enemy[0]][1]
                enemystats = enemies[enemy[0]][0]
                playerhp -= (enemydmgs[0] + enemydmgs[1] * enemystats[0] + enemystats[1] * enemydmgs[2] + enemydmgs[3] * enemystats[2])
            if playerhp <= 0:
                text_surface = font.render("You Are Dead", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(640, 360))
                screen.blit(text_surface, text_rect)
                running = False
            mode = "playerturn"

        elif mode == "attackoptions":
            for i, weapon in enumerate(playerweapons):
                if i == weaponoption:
                    colour = (255, 255, 0)
                else:
                    colour = (255, 255, 255)
                text_surface = font.render(weapon, True, colour)
                text_rect = text_surface.get_rect(center=(150 + (270 * i), 490))
                screen.blit(text_surface, text_rect)

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and keydelay == 0:
                weaponoption = (weaponoption - 1) % len(playerweapons)
                keydelay = 30
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and keydelay == 0:
                weaponoption = (weaponoption + 1) % len(playerweapons)
                keydelay = 30
            elif keys[pygame.K_SPACE] and keydelay == 0:
                enemyselected = random.choice(range(len(currentenemies))) #check for off by one
                weaponstats = weapons[playerweapons[weaponoption]]
                currentenemies[enemyselected][1] -= (weaponstats[0] + weaponstats[1]*playerstats["STR"] + weaponstats[2]*playerstats["DEX"] + weaponstats[3]*playerstats["INT"])
                if currentenemies[enemyselected][1] <= 0:
                    currentenemies.remove(currentenemies[enemyselected])
                keydelay = 30

                if currentenemies == []:
                    mode = "levelup"
                else:
                    mode = "enemyturn"


        elif mode == "playerturn":

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and keydelay == 0:
                battleoption = (battleoption - 1) % 4
                keydelay = 30
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and keydelay == 0:
                battleoption = (battleoption + 1) % 4
                keydelay = 30
            elif keys[pygame.K_SPACE] and keydelay == 0:
                if battleoptions[battleoption] == "attack" and playerweapons != []:
                    mode = "attackoptions"
                elif battleoptions[battleoption] == "skill" and playerskills != []:
                    mode = "skilloptions"
                elif battleoptions[battleoption] == "item" and playeritems != []:
                    mode = "itemoptions"
                elif battleoptions[battleoption] == "forfeit":
                    pass
                keydelay = 30

            screen.blit(attack, (230, 540))
            screen.blit(skill, (455, 540))
            screen.blit(item, (680, 540))
            screen.blit(forfeit, (920, 540))
            if battleoption == 0:
                screen.blit(attack, (230, 490))
            if battleoption == 1:
                screen.blit(skill, (455, 490))
            if battleoption == 2:
                screen.blit(item, (680, 490))
            if battleoption == 3:
                screen.blit(forfeit, (920, 490))

        if keydelay > 0:
            keydelay -= 3

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.mixer.music.stop()
    pygame.quit()

asyncio.run(main())
