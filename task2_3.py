"""
Task 2.3 - Local Search
======================
• Implemente el algoritmo de Búsqueda Local mediante Modos Condicionales Iterados. 
• Inicie con una asignación completamente aleatoria (que probablemente viole muchas reglas) 
y modifique iterativamente un microservicio a la vez, moviéndolo al servidor que maximice el 
cumplimiento de las restricciones. 
• Implemente un límite de iteraciones por si el algoritmo se queda atascado en un óptimo local.

"""

import random

VARIABLES = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
SERVERS = ['S1', 'S2', 'S3']
MAX_CAP = 3

ANTI_AFFINITY_PAIRS = {('M1', 'M2'), ('M3', 'M4'), ('M5', 'M6'), ('M1', 'M5')}


def count_violations(assignment):
    violations = 0

    # Capacidad
    counts = {}
    for s in assignment.values():
        counts[s] = counts.get(s, 0) + 1
    for cnt in counts.values():
        if cnt > MAX_CAP:
            violations += (cnt - MAX_CAP)

    # Anti-afinidad
    vars_list = list(assignment.keys())
    for i in range(len(vars_list)):
        for j in range(i + 1, len(vars_list)):
            v1, v2 = vars_list[i], vars_list[j]
            if (v1, v2) in ANTI_AFFINITY_PAIRS or (v2, v1) in ANTI_AFFINITY_PAIRS:
                if assignment[v1] == assignment[v2]:
                    violations += 1

    return violations


def random_assignment():
    return {v: random.choice(SERVERS) for v in VARIABLES}


def icm(max_iters=1000):
    current = random_assignment()

    for _ in range(max_iters):
        improved = False

        for var in VARIABLES:
            best_server = current[var]
            best_score = count_violations(current)

            for s in SERVERS:
                temp = dict(current)
                temp[var] = s
                score = count_violations(temp)

                if score < best_score:
                    best_score = score
                    best_server = s

            if best_server != current[var]:
                current[var] = best_server
                improved = True

        #si no mejora llegamos a un óptimo local
        if not improved:
            break

        #si ya es solución perfecta
        if count_violations(current) == 0:
            return current

    return current if count_violations(current) == 0 else None