"""
Task 2.2 - Beam Search
======================
Problema: Asignar 8 microservicios (M1..M8) a 3 servidores (S1, S2, S3)
respetando:
  1. Capacidad Global: máx 3 microservicios por servidor.
  2. Anti-Afinidad (binarias):
       (M1,M2), (M3,M4), (M5,M6), (M1,M5)

Algoritmo: Beam Search con parámetro K configurable.
Heurística de poda (Prune): Se priorizan los K candidatos con MENOR
número de violaciones de restricciones en la asignación parcial.
"""

# ──────────────────────────────────────────────────────────────────────────────
# Configuración del problema
# ──────────────────────────────────────────────────────────────────────────────
VARIABLES  = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
SERVERS    = ['S1', 'S2', 'S3']
MAX_CAP    = 3          # Capacidad máxima por servidor

# Restricciones de Anti-Afinidad representadas como conjunto de pares (sin dirección)
ANTI_AFFINITY_PAIRS = {('M1', 'M2'), ('M3', 'M4'), ('M5', 'M6'), ('M1', 'M5')}


# ──────────────────────────────────────────────────────────────────────────────
# Función Heurística / Peso
# ──────────────────────────────────────────────────────────────────────────────
def count_violations(assignment: dict) -> int:
    """
    Calcula el número total de violaciones de restricciones en una
    asignación parcial o completa.

    Se cuentan dos tipos de violaciones:
      (a) Capacidad: cada microservicio extra por encima de MAX_CAP en un servidor.
      (b) Anti-Afinidad: par de microservicios asignados al mismo servidor.

    Un candidato con MENOR puntaje es preferido (mejor candidato).
    """
    violations = 0

    # (a) Violaciones de Capacidad
    counts = {}
    for s in assignment.values():
        counts[s] = counts.get(s, 0) + 1
    for s, cnt in counts.items():
        if cnt > MAX_CAP:
            violations += (cnt - MAX_CAP)  # Cada micro extra sobre el límite suma 1

    # (b) Violaciones de Anti-Afinidad
    assigned_vars = list(assignment.keys())
    for i in range(len(assigned_vars)):
        for j in range(i + 1, len(assigned_vars)):
            v1, v2 = assigned_vars[i], assigned_vars[j]
            pair = (v1, v2) if (v1, v2) in ANTI_AFFINITY_PAIRS else (v2, v1)
            if pair in ANTI_AFFINITY_PAIRS:
                if assignment[v1] == assignment[v2]:
                    violations += 1

    return violations


def is_complete_valid(assignment: dict) -> bool:
    """Devuelve True si la asignación es completa y tiene 0 violaciones (Weight=1)."""
    if len(assignment) != len(VARIABLES):
        return False
    return count_violations(assignment) == 0


# ──────────────────────────────────────────────────────────────────────────────
# Beam Search
# ──────────────────────────────────────────────────────────────────────────────
def beam_search(k: int = 3, verbose: bool = True):
    """
    Beam Search para el problema de asignación de microservicios.

    Parámetros
    ----------
    k : int
        Tamaño del beam (número máximo de candidatos mantenidos en cada nivel).
    verbose : bool
        Si True, imprime el estado del beam en cada paso.

    Retorna
    -------
    dict | None
        La primera asignación completa válida encontrada, o None si no hay solución.
    """
    # Estado inicial: asignación vacía
    # Beam = lista de asignaciones parciales (dicts)
    beam = [{}]

    print(f"\n{'='*60}")
    print(f"  Beam Search  |  K = {k}")
    print(f"{'='*60}")

    for depth, var in enumerate(VARIABLES):
        if verbose:
            print(f"\n[Nivel {depth+1}] Expandiendo variable: {var}  |  Beam size: {len(beam)}")

        candidates = []  # Lista de (violaciones, asignación_expandida)

        # Expansión: cada estado del beam se expande con cada valor posible de 'var'
        for partial in beam:
            for server in SERVERS:
                new_assignment = dict(partial)
                new_assignment[var] = server
                violations = count_violations(new_assignment)
                candidates.append((violations, new_assignment))

        if not candidates:
            print("  [!] Beam vacío: sin candidatos para expandir.")
            return None

        # Prune: ordenar por violaciones (ascendente) y conservar los K mejores
        candidates.sort(key=lambda x: x[0])
        beam = [assignment for _, assignment in candidates[:k]]

        if verbose:
            print(f"  Candidatos generados: {len(candidates)}  →  Retenidos (K={k}): {len(beam)}")
            for rank, (viols, asg) in enumerate(candidates[:k], start=1):
                assigned_now = {v: s for v, s in asg.items() if v in VARIABLES[:depth+1]}
                print(f"    [{rank}] Violaciones={viols}  Asignación: {assigned_now}")

        # Verificar si algún estado ya es una solución completa válida
        for assignment in beam:
            if is_complete_valid(assignment):
                return assignment

    # Revisar el beam final en busca de una solución válida
    for assignment in beam:
        if is_complete_valid(assignment):
            return assignment

    return None


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def print_solution(solution: dict):
    """Imprime la solución con verificación de restricciones."""
    print("\n✔ ¡Solución Encontrada! Asignación válida (Weight = 1):")
    for v in VARIABLES:
        print(f"   {v}  →  {solution[v]}")

    print("\n  Verificación de restricciones:")
    counts = {}
    for s in solution.values():
        counts[s] = counts.get(s, 0) + 1
    for server in SERVERS:
        cnt = counts.get(server, 0)
        status = "OK" if cnt <= MAX_CAP else "ERROR"
        print(f"   Capacidad {server}: {cnt}/3  [{status}]")

    for p1, p2 in sorted(ANTI_AFFINITY_PAIRS):
        s1, s2 = solution[p1], solution[p2]
        status = "OK" if s1 != s2 else "ERROR"
        print(f"   Anti-Afinidad ({p1},{p2}): {p1}→{s1}, {p2}→{s2}  [{status}]")


def main():
    # ── Configuración del K ──────────────────────────────────────────────────
    # Puedes cambiar este valor para experimentar con distintos tamaños de beam.
    K = 3

    solution = beam_search(k=K, verbose=True)

    print(f"\n{'='*60}")
    if solution:
        print_solution(solution)
    else:
        print("✘ No se encontró ninguna asignación válida con Beam Search.")
        print(f"  Prueba aumentar K (actual={K}) para explorar más candidatos.")

    print(f"\n{'='*60}")

    # ── Experimento adicional: comparar distintos valores de K ───────────────
    print("\n\n  Comparando resultados para distintos valores de K:")
    print(f"{'─'*40}")
    print(f"  {'K':>4}  │  {'Solución encontrada':>20}  │  {'Violaciones finales':>20}")
    print(f"{'─'*40}")
    for k_val in [1, 2, 3, 5, 8]:
        sol = beam_search(k=k_val, verbose=False)
        if sol:
            viols = count_violations(sol)
            print(f"  {k_val:>4}  │  {'Sí':>20}  │  {viols:>20}")
        else:
            print(f"  {k_val:>4}  │  {'No':>20}  │  {'N/A':>20}")
    print(f"{'─'*40}")


if __name__ == "__main__":
    main()
