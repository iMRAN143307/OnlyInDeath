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

    def load_and_scale(filename, size=None, transparency=None):
        if transparency is not None:
            unscaled = pygame.image.load(resource_path(f"{filename}.png")).convert_alpha()
        else:
            unscaled = pygame.image.load(resource_path(f"{filename}.png")).convert()
        if size is not None:
            return pygame.transform.scale(unscaled, size)
        else:
            return unscaled

    def drawbattle(playerhp, enemies):
        pass

    font = pygame.font.SysFont(None, 48)

    attack = load_and_scale("attack")
    forfeit = load_and_scale("forfeit")
    item = load_and_scale("item")
    skill = load_and_scale("skill")
    bg = load_and_scale("bg", (1280, 720))
    slime = load_and_scale("slime", None, True)
    player = load_and_scale("player", (75, 200), True)

    running = True

    round = 0

    keydelay = 60

    playerstats = {"STR": 0, "DEX": 0, "INT": 0, "CON": 0}

    playeritems = []

    playerweapons = [
    "stick",
    ]

    playerskills = []

    playercurrency = 0 #name currency; DO NOT MAKE IT GOLD

    playerhp = 10

    playermagicresource = 0 #name magic resource; DO NOT MAKE IT MANA

    currentenemies = [["slime", 2, slime], ["slime", 2, slime]] #(enemy0, health, sprite)

    enemies = { #(STR, DEX, INT, CON), (basedmg, %ofSTR, %ofDEX, %ofINT), "attribute"
    "slime": ((1, 1, 1, 2), (1, 0.5, 0, 0), ""),
    "skeleton": ((2, 2, 1, 1), (1, 0, 1, 0), ""),
    "ghoul": ((1, 3, 2, 1), (2, 0, 0, 0.5), "tough")
    }

    attributes = [
    "tough", #enemy attacks with -1 STR
    ]

    mode = "playerturn"

    modes = ["playerturn", "enemyturn", "levelup", "shop", "mainmenu", "attackoptions", "skilloptions", "itemoptions"]

    battleoptions = ["attack", "skill", "item", "forfeit"] #maybe add some bonus when you forfeit to encourage players to forfeit and then bounce back

    battleoption = 0

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


    clock = pygame.time.Clock()

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

        if mode == "enemyturn":
            for enemy in currentenemies:
                enemydmgs = enemies[enemy[0]][1]
                enemystats = enemies[enemy[0]][0]
                playerhp -= (enemydmgs[0] + enemydmgs[1] * enemystats[0] + enemystats[1] * enemydmgs[2] + enemydmgs[3] * enemystats[2])
            mode = "playerturn"

        elif mode == "attackoptions":
            for i, weapon in enumerate(playerweapons):
                if i == battleoption:
                    colour = (255, 255, 0)
                else:
                    colour = (255, 255, 255)
                text_surface = font.render(weapon, True, colour)
                text_rect = text_surface.get_rect(center=(150 + (270 * i), 490))
                screen.blit(text_surface, text_rect)

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and keydelay == 0:
                battleoption = (battleoption - 1) % len(playerweapons)
                keydelay = 60
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and keydelay == 0:
                battleoption = (battleoption + 1) % len(playerweapons)
                keydelay = 60
            elif keys[pygame.K_SPACE] and keydelay == 0:
                enemyselected = random.choice(range(len(currentenemies))) #check for off by one
                weaponstats = weapons[playerweapons[battleoption]]
                currentenemies[enemyselected][1] -= (weaponstats[0] + weaponstats[1]*playerstats["STR"] + weaponstats[2]*playerstats["DEX"] + weaponstats[3]*playerstats["INT"])
                if currentenemies[enemyselected][1] <= 0:
                    currentenemies.remove(currentenemies[enemyselected])
                keydelay = 60

                if currentenemies == []:
                    mode = "levelup"
                else:
                    mode = "enemyturn"


        elif mode == "playerturn":

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and keydelay == 0:
                battleoption = (battleoption - 1) % 4
                keydelay = 60
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and keydelay == 0:
                battleoption = (battleoption + 1) % 4
                keydelay = 60
            elif keys[pygame.K_SPACE] and keydelay == 0:
                if battleoptions[battleoption] == "attack" and playerweapons != []:
                    mode = "attackoptions"
                elif battleoptions[battleoption] == "skill" and playerskills != []:
                    mode = "skilloptions"
                elif battleoptions[battleoption] == "item" and playeritems != []:
                    mode = "itemoptions"
                elif battleoptions[battleoption] == "forfeit":
                    pass
                keydelay = 60

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
