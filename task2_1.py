import copy

def is_valid(assignment, var, val, anti_affinity):
    """Verifica si asignar var=val respeta las restricciones dadas las asignaciones actuales."""
    # Revisión de capacidad (Global): Ningún servidor puede alojar más de 3
    counts = {'S1': 0, 'S2': 0, 'S3': 0}
    for v, s in assignment.items():
        counts[s] += 1
    counts[val] += 1
    if counts[val] > 3:
        return False
        
    # Revisión de Anti-Afinidad (Binarias): variables en conflicto no pueden estar en el mismo servidor
    for neighbor in anti_affinity.get(var, []):
        if neighbor in assignment and assignment[neighbor] == val:
            return False
            
    return True

def forward_checking(var, val, assignment, domains, anti_affinity, variables):
    """
    Aplica Lookahead (Forward Checking).
    Filtra los dominios de las variables no asignadas basándose en la nueva asignación var=val.
    Retorna los nuevos dominios si ningún dominio queda vacío, de lo contrario retorna False.
    """
    # Usamos deepcopy para no alterar el dominio de los padres en el árbol de recursión
    new_domains = copy.deepcopy(domains)
    
    # Contar cuántos microservicios hay en cada servidor incluyendo la nueva asignación predictiva
    counts = {'S1': 0, 'S2': 0, 'S3': 0}
    for assigned_var, assigned_val in assignment.items():
        counts[assigned_val] += 1
    counts[val] += 1
    
    unassigned = [v for v in variables if v not in assignment and v != var]
    
    for u in unassigned:
        # 1. Aplicar restricción de Anti-Afinidad
        if u in anti_affinity.get(var, []):
            if val in new_domains[u]:
                new_domains[u].remove(val)
                
        # 2. Aplicar restricción de Capacidad
        # Si un servidor llegó a su máxima capacidad (3), no puede ser asignado a otras variables
        for s, count in counts.items():
            if count == 3:
                if s in new_domains[u]:
                    new_domains[u].remove(s)
                    
        # Poda temprana: Si alguna variable se queda sin valores posibles en su dominio,
        # detenemos esta rama de búsqueda tempranamente.
        if len(new_domains[u]) == 0:
            return False
            
    return new_domains

def backtrack(assignment, domains, variables, anti_affinity):
    """Algoritmo recursivo de Backtracking Search con Forward Checking."""
    # Caso base: Si todas las variables están asignadas, retorna la asignación (Weight = 1)
    if len(assignment) == len(variables):
        return assignment
        
    # Seleccionar variable no asignada (usa el orden de la lista original)
    unassigned_vars = [v for v in variables if v not in assignment]
    var = unassigned_vars[0]
    
    # Intentar asignar posibles valores dentro del dominio activo de 'var'
    for val in domains[var]:
        if is_valid(assignment, var, val, anti_affinity):
            # Aplicar técnica Lookahead (Forward Checking)
            new_domains = forward_checking(var, val, assignment, domains, anti_affinity, variables)
            
            # Si el Forward Checking NO detecta un dominio vacío (rama inválida)
            if new_domains is not False: 
                assignment[var] = val
                
                # Búsqueda en profundidad
                result = backtrack(assignment, new_domains, variables, anti_affinity)
                if result is not False:
                    return result
                    
                # Backtracking: Deshacer asignación si no se llegó al final
                del assignment[var]
                
    # Si ningún valor funciona para la variable actual, retornar False para aplicar backtrack
    return False

def main():
    # Definición de variables del M1 al M8 y el domino de servidores S1 a S3
    variables = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
    servers = ['S1', 'S2', 'S3']
    domains = {v: list(servers) for v in variables}
    
    # Restricciones de Anti-Afinidad (Bidireccionales para mapeo rápido)
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
    
    print("Iniciando búsqueda con Backtracking & Forward Checking...")
    assignment = {}
    solution = backtrack(assignment, domains, variables, anti_affinity)
    
    if solution:
        print("\n¡Solución Encontrada! Asignación válida (Weight = 1):")
        for v in variables:
            print(f"  {v} -> {solution[v]}")
            
        print("\nVerificando restricciones estricta e internamente...")
        counts = {'S1': 0, 'S2': 0, 'S3': 0}
        for v in variables:
            counts[solution[v]] += 1
            
        print(f"1. Capacidad (máx 3): S1={counts['S1']}, S2={counts['S2']}, S3={counts['S3']} -> {'OK' if all(c <= 3 for c in counts.values()) else 'ERROR'}")
        
        # Validar parejas separadas
        pairs = [('M1', 'M2'), ('M3', 'M4'), ('M5', 'M6'), ('M1', 'M5')]
        all_pairs_ok = True
        for p1, p2 in pairs:
            s1, s2 = solution[p1], solution[p2]
            status = 'OK' if s1 != s2 else 'ERROR'
            print(f"2. Anti-Afinidad {p1} y {p2} separados: {p1} en {s1}, {p2} en {s2} -> {status}")
            if s1 == s2:
                all_pairs_ok = False
                
        if all_pairs_ok:
            print("Todas las restricciones de Anti-Afinidad OK.")
    else:
        print("\nNo se encontró ninguna asignación válida.")

if __name__ == "__main__":
    main()
