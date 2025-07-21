import sys
import json
import random
import pandas as pd
import time
from rolls_gpu_cupy import roll_card

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

def buscar_por_idx(cards, idx):
    if idx == -1:
        return None
    return cards[idx]

def seleccionar_rareza_batch(rarity_list, n):
    # Devuelve una lista de rarezas para n rolls, según las probabilidades
    probs = [r["Probability"] for r in rarity_list]
    nombres = [r["Name"] for r in rarity_list]
    multipliers = [r["multiplier"] for r in rarity_list]
    rarezas_idx = random.choices(range(len(rarity_list)), weights=probs, k=n)
    return [
        {"Name": nombres[i], "multiplier": multipliers[i]}
        for i in rarezas_idx
    ]

# Prepara la data para GPU rolls
t2 = time.perf_counter()
card_data = [{"rank": int(card["rank"]), "power_level": int(card["power_level"])} for card in cards]
t3 = time.perf_counter()
print(f"Tiempo de preparación de card_data: {t3 - t2:.6f} segundos")

# Sistema de rolls en GPU
rolls = 100000
t4 = time.perf_counter()
selected_indices = roll_card(card_data, M=rolls)  # Devuelve índices de cartas (o -1)
t5 = time.perf_counter()
print(f"Tiempo total de {rolls} rolls (GPU): {t5 - t4:.6f} segundos")

# Asignar rarezas a cada roll (medir tiempo)
t6 = time.perf_counter()
df_rolls = pd.DataFrame({"idx": selected_indices})
rareza_batch = seleccionar_rareza_batch(rarity_list, len(df_rolls))
df_rolls["Rareza"] = [r["Name"] for r in rareza_batch]
df_rolls["Multiplier"] = [int(r["multiplier"]) for r in rareza_batch]
t7 = time.perf_counter()
print(f"Tiempo de cálculo de rarezas: {t7 - t6:.6f} segundos")

# Completar info de carta y poder final
def get_nombre(idx):
    if idx == -1:
        return None
    return cards[idx]["name"]
def get_poder(idx, mult):
    if idx == -1:
        return None
    return int(mult*int(cards[idx]["power_level"]))
df_rolls["Carta"] = df_rolls.apply(lambda row: get_nombre(row["idx"]), axis=1)
df_rolls["Poder"] = df_rolls.apply(lambda row: get_poder(row["idx"], row["Multiplier"]), axis=1)

# Contar ocurrencias por carta y rareza
resumen = df_rolls.groupby(["Carta", "Rareza", "Poder"]).size().reset_index(drop=False, name="Veces")
resumen.to_excel(r"D:\Programing\test\TextProbAnalisis\tests\rolls.xlsx")