import sys
import json
import random
import pandas as pd
import time

sys.path.append(r'D:\Programing\test\TextProbAnalisis\src\cpp\build')
import roll_card

rarity_list = [
    {"Name": "Common", "Probability": 0.7, "multiplier": 1},
    {"Name": "Uncommon", "Probability": 0.2, "multiplier": 100},
    {"Name": "Rare", "Probability": 0.075, "multiplier": 10000},
    {"Name": "Epic", "Probability": 0.025, "multiplier": 1000000}
]

# Medir tiempo de carga de cartas
t0 = time.perf_counter()
with open(r"D:\Programing\test\TextProbAnalisis\data\cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)
t1 = time.perf_counter()
print(f"Tiempo de carga de cartas: {t1 - t0:.6f} segundos")

def buscar_por_rank(anime_list, rank):
    for personaje in anime_list:
        if personaje["rank"] == rank:
            return personaje
    return None

def seleccionar_rareza(rarity_list):
    rand_val = random.random()
    cumulative = 0.0
    for r in rarity_list:
        cumulative += float(r["Probability"])
        if rand_val < cumulative:
            return r
    return rarity_list[-1]

# Prepara la data para C++
t2 = time.perf_counter()
card_data = [{"rank": int(card["rank"]), "power_level": int(card["power_level"])} for card in cards]
t3 = time.perf_counter()
print(f"Tiempo de preparación de card_data: {t3 - t2:.6f} segundos")

# DataFrame vacío para registrar los resultados
df = pd.DataFrame(columns=["Carta", "Rareza", "Poder", "Veces"])

# Sistema de rolls
rolls = 100000
t4 = time.perf_counter()
for i in range(rolls):
    t_roll_start = time.perf_counter()
    selected_rank = roll_card.roll_card(card_data)
    t_roll_end = time.perf_counter()
    if selected_rank != -1:
        card = buscar_por_rank(cards, selected_rank)
        if card is not None:
            t_rareza_start = time.perf_counter()
            rareza = seleccionar_rareza(rarity_list)
            t_rareza_end = time.perf_counter()
            poder_final = int(card["power_level"]) * rareza["multiplier"]
            nombre = card["name"]
            # Si la carta ya está en el DataFrame, actualiza
            if nombre in df["Carta"].values:
                df.loc[df["Carta"] == nombre, "Veces"] += 1
                df.loc[df["Carta"] == nombre, "Rareza"] = rareza["Name"]
                df.loc[df["Carta"] == nombre, "Poder"] = poder_final
            else:
                # Si no está, agrega una nueva fila
                df = pd.concat([df, pd.DataFrame([{
                    "Carta": nombre,
                    "Rareza": rareza["Name"],
                    "Poder": poder_final,
                    "Veces": 1
                }])], ignore_index=True)
        else:
            print("Error: No se encontró la carta con el rank retornado.")
    else:
        print("No salió ninguna carta en este roll.")
t5 = time.perf_counter()
print(f"Tiempo total de {rolls} rolls: {t5 - t4:.6f} segundos")

print(df)