import random
from typing import Dict, List, Tuple
import copy

def extract_state(cloud_clusters: Dict[str, List[Dict]]
) -> Tuple[Dict[str, List[Dict]], Dict[str, List[Dict]]]:
    """
    From Step 2's cloud_clusters, build:
      - tasks_by_cluster: all tasks per cluster (with orig_server for seeding)
      - servers_by_cluster: current servers with their remaining CPU, RAM, BW, throughput
    """
    tasks_by_cluster = {}
    servers_by_cluster = {}

    for cname, servers in cloud_clusters.items():
        # 1) Gather tasks (including original assignment)
        tasks = []
        for srv in servers:
            for t in srv.get("tasks", []):
                tasks.append({
                    "device_id":  t["device_id"],
                    "task":       t["task"],
                    "complexity": t["complexity"],
                    "orig_server": srv["server_id"]
                })
        tasks_by_cluster[cname] = tasks

        # 2) Snapshot server resources after Step 2
        servers_by_cluster[cname] = [
            {
                "server_id":  srv["server_id"],
                "cpu":        srv["cpu"],        # remaining CPU
                "ram":        srv["ram"],
                "bandwidth":  srv["bandwidth"],
                "throughput": srv.get("throughput", 0),
                "status":     srv.get("status", "active")  # Add status field
            }
            for srv in servers
        ]

    return tasks_by_cluster, servers_by_cluster

def check_server_health(servers: List[Dict], failure_prob: float = 0.5) -> List[Dict]:
    """
    Simulate random server failures and mark unhealthy servers
    failure_prob: Probability of any server failing (0-1)
    """
    for server in servers:
        if random.random() < failure_prob:
            server['status'] = 'failed'
            server['cpu'] = 0  # Set CPU to 0 to prevent task assignment
        else:
            server['status'] = 'active'
    return servers

def generate_chromosome(
    tasks: List[Dict],
    servers: List[Dict],
    use_orig: bool = False
) -> List[Dict]:
    """
    Build one chromosome:
      - if use_orig=True, replicate Step 2 assignment (baseline)
      - else, randomly assign each task to any server whose CPU >= task.complexity
      - Now avoids failed servers
    """
    chromosome = []
    active_servers = [s for s in servers if s.get('status', 'active') == 'active']
    
    for task in tasks:
        if use_orig:
            # Check if original server is still active
            orig_server = next((s for s in servers if s["server_id"] == task["orig_server"]), None)
            if orig_server and orig_server.get('status', 'active') == 'active':
                server_id = task["orig_server"]
            else:
                # Find alternative server
                eligible = [s for s in active_servers if task["complexity"] <= s["cpu"]]
                if not eligible:
                    eligible = active_servers  # allow infeasible if none fit
                server_id = random.choice(eligible)["server_id"] if active_servers else None
        else:
            eligible = [s for s in active_servers if task["complexity"] <= s["cpu"]]
            if not eligible:
                eligible = active_servers  # allow infeasible if none fit
            server_id = random.choice(eligible)["server_id"] if active_servers else None

        if server_id:
            chromosome.append({
                "device_id":  task["device_id"],
                "task":       task["task"],
                "complexity": task["complexity"],
                "server_id":  server_id,
            })
    return chromosome

def generate_initial_population(
    cloud_clusters: Dict[str, List[Dict]],
    population_size: int = 10
) -> Dict[str, List[List[Dict]]]:
    """
    For each cluster Ci, produce a population:
      1) First chromosome = exact Step 2 assignment (baseline)
      2) Next (population_size-1) chromosomes = random variations
    """
    tasks_map, servers_map = extract_state(cloud_clusters)
    populations: Dict[str, List[List[Dict]]] = {}

    for cname in cloud_clusters:
        tasks   = tasks_map[cname]
        servers = servers_map[cname]
        servers = check_server_health(servers)  # Check for failures

        # 1) Baseline
        pop = [generate_chromosome(tasks, servers, use_orig=True)]

        # 2) Randomized rest
        for _ in range(population_size - 1):
            pop.append(generate_chromosome(tasks, servers, use_orig=False))

        populations[cname] = pop

    return populations

def evaluate_chromosome(
    chromosome: List[Dict],
    servers: List[Dict],
    weights: Dict[str, float],
    failure_penalty: float = -1000
) -> float:
    """
    Correctly compute Fs using absolute available CPU (no normalization):
      CA = srv['cpu'] - used_cpu
    Now includes penalty for failed server assignments
    """
    # Track failed assignments
    failed_assignments = 0
    
    # group tasks by server
    tasks_by_srv = {srv["server_id"]: [] for srv in servers}
    for gene in chromosome:
        tasks_by_srv[gene["server_id"]].append(gene)
        # Check if assigned to failed server
        server = next((s for s in servers if s["server_id"] == gene["server_id"]), None)
        if server and server.get('status', 'active') == 'failed':
            failed_assignments += 1

    best_fs = -float("inf")
    for srv in copy.deepcopy(servers):  # prevent mutation bleed-over
        if srv.get('status', 'active') == 'failed':
            continue  # skip failed servers
            
        used_cpu = sum(g["complexity"] for g in tasks_by_srv[srv["server_id"]])
        CA = max(0, srv["cpu"] - used_cpu)         # absolute available CPU
        RA = srv["ram"]
        BA = srv["bandwidth"]
        TS = srv["throughput"]

        fs = (
            weights["cpu"]        * CA +
            weights["ram"]        * RA +
            weights["bandwidth"]  * BA +
            weights["throughput"] * TS
        )
        best_fs = max(best_fs, fs)

    # Apply penalty for failed assignments
    if failed_assignments > 0:
        best_fs += failed_assignments * failure_penalty
        
    return best_fs

def evaluate_population(
    populations: Dict[str, List[List[Dict]]],
    ORIGINAL_CLUSTERS: Dict[str, List[Dict]],  # <-- use original
    weights: Dict[str, float]
) -> Dict[str, List[float]]:
    fitness_map: Dict[str, List[float]] = {}
    for cname, chroms in populations.items():
        fitness_map[cname] = [
            evaluate_chromosome(chrom, ORIGINAL_CLUSTERS[cname], weights)
            for chrom in chroms
        ]
    return fitness_map

def roulette_selection(population: List[List[Dict]], fitness_scores: List[float], num_parents: int = 2) -> List[List[Dict]]:
    total_fitness = sum(fitness_scores)
    if total_fitness == 0:
        # All fitness are 0 → return random parents
        return random.sample(population, num_parents)

    selection_probs = [score / total_fitness for score in fitness_scores]
    selected = random.choices(population, weights=selection_probs, k=num_parents)
    return selected

def two_point_crossover(parent1: List[Dict], parent2: List[Dict]) -> List[Dict]:
    size = len(parent1)
    if size < 2:
        return parent1.copy()

    pt1 = random.randint(0, size - 2)
    pt2 = random.randint(pt1 + 1, size - 1)

    child = parent1[:pt1] + parent2[pt1:pt2] + parent1[pt2:]

    return child

def mutate_chromosome(chromosome: List[Dict], servers: List[Dict], mutation_rate: float = 0.20) -> List[Dict]:
    new_chrom = []
    active_servers = [s for s in servers if s.get('status', 'active') == 'active']
    
    for gene in chromosome:
        if random.random() < mutation_rate:
            # Find active servers that can handle the task
            eligible = [s for s in active_servers if gene["complexity"] <= s["cpu"]]
            if eligible:
                new_server = random.choice(eligible)
                new_gene = gene.copy()
                new_gene["server_id"] = new_server["server_id"]
                new_chrom.append(new_gene)
            else:
                new_chrom.append(gene)
        else:
            new_chrom.append(gene)
    return new_chrom

def evolve_population(
    population: List[List[Dict]],
    fitness_scores: List[float],
    servers: List[Dict],
    population_size: int
) -> List[List[Dict]]:
    import copy
    new_generation = []

    # Step 1: Elitism — Retain best chromosome
    best_idx = fitness_scores.index(max(fitness_scores))
    new_generation.append(population[best_idx])

    # Step 2: Create the rest of the new generation
    while len(new_generation) < population_size:
        # Ensure parents are distinct
        attempts = 0
        max_attempts = 10
        while True:
            parent1, parent2 = roulette_selection(population, fitness_scores, num_parents=2)
            if parent1 != parent2:
                break
            attempts += 1
            if attempts >= max_attempts:
                break

        # Step 3: Crossover
        child = two_point_crossover(parent1, parent2)

        # Step 4: Mutation
        mutated_child = mutate_chromosome(child, copy.deepcopy(servers))  # safe copy

        new_generation.append(mutated_child)

    return new_generation