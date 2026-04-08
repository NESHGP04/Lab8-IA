"""
Task 2.4 - Benchmarking
======================

Cree una celda final donde ejecute los 3 algoritmos para el mismo problema. Debe imprimir y comparar: 
1. ¿Los tres encontraron una solución válida? Si Beam o Local Search fallaron (se atascaron), repórtelo. 
2. Utilice la librería time para medir cuánto tardó cada uno. 
3. Redacte un breve párrafo analizando los resultados empíricos observados. ¿Se cumplió lo teórico 
respecto a la velocidad y la exactitud? 

"""

import time
from task2_1 import backtrack
from task2_2 import beam_search
from task2_3 import icm

VARIABLES = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
SERVERS = ['S1', 'S2', 'S3']

def run_benchmark():
    print("\n" + "="*60)
    print("BENCHMARK DE ALGORITMOS")
    print("="*60)

    #BACKTRACKING
    variables = VARIABLES
    domains = {v: SERVERS[:] for v in VARIABLES}

    anti_affinity = {
        'M1': ['M2', 'M5'],
        'M2': ['M1'],
        'M3': ['M4'],
        'M4': ['M3'],
        'M5': ['M1', 'M6'],
        'M6': ['M5'],
        'M7': [],
        'M8': []
    }

    start = time.time()
    bt_solution = backtrack({}, domains, variables, anti_affinity)
    bt_time = time.time() - start

    #BEAM SEARCH
    start = time.time()
    beam_solution = beam_search(k=3, verbose=False)
    beam_time = time.time() - start

    #ICM
    start = time.time()
    icm_solution = icm(max_iters=1000)
    icm_time = time.time() - start

    #RESULTADOS
    print("\nResultados:\n")

    print(f"Backtracking: {'✔' if bt_solution else '✘'} | Tiempo: {bt_time:.5f}s")
    print(f"Beam Search:  {'✔' if beam_solution else '✘'} | Tiempo: {beam_time:.5f}s")
    print(f"ICM:          {'✔' if icm_solution else '✘'} | Tiempo: {icm_time:.5f}s")

    print(f"{'Algoritmo':<15}{'Estado':<25}{'Tiempo (s)':<15}")
    print("-"*55)

    # Backtracking
    bt_status = "Solución válida" if bt_solution else "Falló"
    print(f"{'Backtracking':<15}{bt_status:<25}{bt_time:<15.6f}")

    # Beam
    if beam_solution:
        beam_status = "Solución válida"
    else:
        beam_status = "Falló (atascado o K insuficiente)"

    print(f"{'Beam Search':<15}{beam_status:<25}{beam_time:<15.6f}")

    # ICM
    if icm_solution:
        icm_status = "Solución válida"
    else:
        icm_status = "Falló (óptimo local)"

    print(f"{'ICM':<15}{icm_status:<25}{icm_time:<15.6f}")


run_benchmark()