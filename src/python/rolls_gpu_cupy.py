import cupy as cp
import numpy as np
import time

def roll_card(cartas, M):
    power_levels = cp.array([int(carta["power_level"]) for carta in cartas], dtype=cp.int64)
    ranks = np.array([int(carta["rank"]) for carta in cartas], dtype=np.int32)
    N = len(cartas)
    start = time.perf_counter()
    selected_indices = cp.full(M, -1, dtype=cp.int32)
    pendientes = cp.arange(M)
    while pendientes.size > 0:
        rand_matrix = cp.empty((pendientes.size, N), dtype=cp.int64)
        for j in range(N):
            rand_matrix[:, j] = cp.random.randint(1, power_levels[j] + 1, size=pendientes.size, dtype=cp.int64)
        candidatas = (rand_matrix == 1)
        any_candidatas = cp.any(candidatas, axis=1)
        nuevos_idx = cp.where(any_candidatas, cp.argmax(candidatas, axis=1), -1)
        # Asignar solo a los que estaban pendientes
        for i in range(pendientes.size):
            if nuevos_idx[i] != -1:
                selected_indices[pendientes[i]] = nuevos_idx[i]
        # Actualizar pendientes
        pendientes = pendientes[selected_indices[pendientes] == -1]
    selected_indices_np = cp.asnumpy(selected_indices)
    selected_ranks = [int(ranks[idx]) for idx in selected_indices_np]
    end = time.perf_counter()
    print(f"Simulación de {M} rolls en GPU (CuPy) tomó {end - start:.6f} segundos")
    return selected_ranks