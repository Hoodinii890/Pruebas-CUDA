import sys
import json
import random
import pandas as pd
import time
from rolls_gpu_cupy import roll_card

upgrapes = {
    "Luck":100,
    "Rarity":45
}

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

def ajustar_probabilidades_rarity(rarity_list, rarity_bonus):
    # Copia de los valores base
    base_probs = [r["Probability"] for r in rarity_list]
    names = [r["Name"] for r in rarity_list]
    # Paso 1: Aplica bonus proporcional a todas menos Common
    probs = base_probs.copy()
    for i, name in enumerate(names):
        if name != "Common":
            probs[i] = base_probs[i] * (1 + rarity_bonus/100)
    # Paso 2: Identifica rarezas sobrantes (superan 70%)
    sobrantes_idx = []
    no_sobrantes_idx = []
    for i, name in enumerate(names):
        if name == "Epic" and probs[i] >= 0.7:
            probs[i] = 0.7  # Epic se regula a 70%
            no_sobrantes_idx.append(i)
        elif name != "Common" and probs[i] > 0.7:
            sobrantes_idx.append(i)
        elif name != "Common":
            no_sobrantes_idx.append(i)
    # Paso 3: Suma de no sobrantes
    suma_no_sobrantes = sum([probs[i] for i in no_sobrantes_idx])
    # Paso 4: Calcula el sobrante a repartir
    sobrante = 1.0 - suma_no_sobrantes
    # Paso 5: Reparte el sobrante entre Common y las rarezas sobrantes según su probabilidad base
    reparto_idx = [i for i in sobrantes_idx]
    # Common siempre entra en el reparto
    common_idx = names.index("Common")
    reparto_idx.append(common_idx)
    total_base_reparto = sum([base_probs[i] for i in reparto_idx])
    if total_base_reparto > 0:
        for i in reparto_idx:
            probs[i] = (base_probs[i] / total_base_reparto) * max(sobrante, 0)
    # Paso 6: Normaliza si hay errores numéricos
    total = sum(probs)
    if abs(total - 1.0) > 1e-8:
        # Ajuste final proporcional
        probs = [p / total for p in probs]
    
    return dict(zip(names, probs))

def seleccionar_rareza_batch(rarity_list, n, rarity_bonus=0.0):
    # Ajusta las probabilidades según el bonus de Rarity
    probs_dict = ajustar_probabilidades_rarity(rarity_list, rarity_bonus)
    nombres = [r["Name"] for r in rarity_list]
    multipliers = [r["multiplier"] for r in rarity_list]
    probs = [probs_dict[n] for n in nombres]
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
rolls = 1000
t4 = time.perf_counter()
selected_indices = roll_card(card_data, M=rolls, luck=upgrapes["Luck"])  # Devuelve índices de cartas (o -1)
t5 = time.perf_counter()
print(f"Tiempo total de {rolls} rolls (GPU): {t5 - t4:.6f} segundos")

# Asignar rarezas a cada roll (medir tiempo)
t6 = time.perf_counter()
df_rolls = pd.DataFrame({"idx": selected_indices})
# Imprime las probabilidades ajustadas de rareza
# probs_dict = ajustar_probabilidades_rarity(rarity_list, upgrapes["Rarity"])
# print("Probabilidades ajustadas de rareza:")
# for k, v in probs_dict.items():
#     print(f"  {k}: {v*100:.2f}%")
rareza_batch = seleccionar_rareza_batch(rarity_list, len(df_rolls), rarity_bonus=upgrapes["Rarity"])
df_rolls["Rareza"] = pd.Series([r["Name"] for r in rareza_batch])
df_rolls["Multiplier"] = [int(r["multiplier"]) for r in rareza_batch]
t7 = time.perf_counter()
print(f"Tiempo de cálculo de rarezas: {t7 - t6:.6f} segundos")

# # Imprime la cantidad de veces que salió cada rareza
# distribucion_rareza = df_rolls["Rareza"].value_counts().sort_index()
# print("\nDistribución de rarezas en los rolls:")
# for rareza, count in distribucion_rareza.items():
#     print(f"  {rareza}: {count} ({count/rolls*100:.2f}%)")

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