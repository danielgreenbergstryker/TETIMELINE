import csv
import random
from itertools import product, combinations

project_types = ['New system', 'Line extension']
business_units = ['Foot & Ankle', 'Trauma', 'Upper Extremities']
business_impacts = ['Revenue generator', 'Strategic importance', 'Innovation', 'Fill The Bag']
divisions = ['Trauma & Extremities', 'Other']
components = ['Implants', 'Instruments', 'Software', 'Electronics', 'Cases & Trays', 'Biologics', 'Combination Devices', 'OEM']
sku_ranges = {'1-5': (1, 5), '6-25': (6, 25), '26-50': (26, 50), '50-100': (50, 100), '100-200': (100, 200), '200-500': (200, 500)}
sterility = ['Yes', 'No']
target_markets = ['United States']
regulatory_pathways = ['510(k)', 'Letter to File']
complexity_matrices = {
    'Line extension': {'CC1': 10, 'CC2': 10.5, 'CC3': 14, 'CC4': 17.5, 'CC5': 23, 'CC6': 31},
    'New system': {'CC1': 14, 'CC2': 18, 'CC3': 20, 'CC4': 26, 'CC5': 32, 'CC6': 38}
}
variations = {'CC1': 0.05, 'CC2': 0.075, 'CC3': 0.09, 'CC4': 0.13, 'CC5': 0.175, 'CC6': 0.20}
reg_pathways_durations = {'510(k)': 126 / 30.44, 'Letter to File': 0}
sku_duration_addition = {'1-5': 0, '6-25': 1, '26-50': 3, '50-100': 6, '100-200': 10, '200-500': 14}

def get_random_sku(sku_key):
    sku_min, sku_max = sku_ranges[sku_key]
    return random.randint(sku_min, sku_max)

def format_for_excel(scenarios):
    header = ["Project Type", "Business Units", "Business Impact", "Division Included", "Components", "Target Market", 
              "Regulatory Path", "Design Complexity", "Manufacturing Complexity", "Overall Complexity Score", 
              "SKU Count", "Sterility", "Actual Duration Range (months)"]
    formatted_scenarios = [header]
    for scenario in scenarios:
        formatted_scenarios.append([
            scenario[0],
            ', '.join(scenario[1]),
            ', '.join(scenario[2]),
            scenario[3],
            ', '.join(scenario[4]),
            scenario[5][0], 
            ', '.join(scenario[6]),
            scenario[7],
            scenario[8], 
            scenario[9],
            scenario[10],
            scenario[11],
            scenario[12] 
        ])
    return formatted_scenarios

def calculate_duration_range(base_duration, complexity, division, business_units, components, sku_count, sterility, regulatory_path):
    variability = variations[complexity]
    lower_bound_base = base_duration * (1 - variability)
    upper_bound_base = base_duration * (1 + variability)

    total_duration = base_duration

    if division == 'Trauma & Extremities, Other':
        total_duration += 6

    if len(business_units) > 1:
        total_duration += 2

    if 'Software' in components or 'Electronics' in components:
        total_duration += 6

    sku_range_key = next(key for key, value in sku_ranges.items() if value[0] <= sku_count <= value[1])
    total_duration += sku_duration_addition[sku_range_key]

    if sterility == 'Yes':
        total_duration += 4

    if '510(k)' in regulatory_path:
        total_duration += 4.14

    lower_bound = lower_bound_base + total_duration - base_duration
    upper_bound = upper_bound_base + total_duration - base_duration
    return f"{lower_bound:.2f}-{upper_bound:.2f}"

def validate_components(components):
    components = list(components)
    invalid_combinations = [
        ('Software', 'Biologics'),
        ('Software', 'Cases & Trays'),
        ('Biologics', "Cases & Trays"),
        ('Software', 'Combination Devices'),
        ('Software', 'OEM'),
        ('Biologics', 'Implants'),
        ('Biologics', 'Electronics'),
        ('Electronics', 'Combination Devices'),
        ('Combination Devices', 'Implants'),
        ('Cases & Trays', 'Software')
    ]
    for combo in invalid_combinations:
        if set(combo).issubset(set(components)):
            components = ['Implants', 'Instruments', 'Cases & Trays']
    if len(components) > 2 and 'Software' in components and 'Biologics' in components:
        components.remove('Biologics')
    return components

def process_and_save_scenarios(num_samples=3000):
    bu_combinations = [list(combo) for i in range(1, len(business_units) + 1) for combo in combinations(business_units, i)]
    bi_combinations = [list(combo) for i in range(1, len(business_impacts) + 1) for combo in combinations(business_impacts, i)]
    c_combinations = [list(combo) for i in range(1, len(components) + 1) for combo in combinations(components, i) if validate_components(combo)]
    rp_combinations = [list(combo) for i in range(1, len(regulatory_pathways) + 1) for combo in combinations(regulatory_pathways, i)]
    
    specific_combination = ['Implants', 'Instruments', 'Cases & Trays']
    num_specific_combinations = int(0.70 * num_samples)
    specific_combinations = [specific_combination] * num_specific_combinations

    valid_c_combinations = [combo for combo in c_combinations if combo != specific_combination]
    remaining_combinations = []
    while len(remaining_combinations) < (num_samples - num_specific_combinations):
        remaining_combinations.extend(valid_c_combinations)

    remaining_combinations = random.sample(remaining_combinations, num_samples - num_specific_combinations)
    c_combinations = specific_combinations + remaining_combinations
    random.shuffle(c_combinations)

    batch_size = 1000
    header_written = False

    for start in range(0, num_samples, batch_size):
        end = min(start + batch_size, num_samples)
        batch_scenarios = []

        for _ in range(start, end):
            project_type = random.choice(project_types)
            bus = random.choice(bu_combinations)
            bis = random.choice(bi_combinations)
            di = 'Trauma & Extremities' if random.random() < 0.95 else 'Trauma & Extremities, Other'
            cs = random.choice(c_combinations)
            rps = random.choice(rp_combinations)
            dc = random.randint(1, 3)
            mc = random.randint(1, 3)
            
            if dc == 1 and mc == 1:
                complexity_category = 'CC1'
            elif (dc == 1 and mc == 2) or (dc == 2 and mc == 1):
                complexity_category = 'CC2'
            elif (dc == 1 and mc == 3) or (dc == 3 and mc == 1):
                complexity_category = 'CC3'
            elif dc == 2 and mc == 2:
                complexity_category = 'CC4'
            elif (dc == 2 and mc == 3) or (dc == 3 and mc == 2):
                complexity_category = 'CC5'
            elif dc == 3 and mc == 3:
                complexity_category = 'CC6'

            if complexity_category in ['CC3', 'CC4', 'CC5', 'CC6'] and '510(k)' not in rps:
                rps.append('510(k)')

            cs = validate_components(cs)
            sku_range_key = random.choice(list(sku_ranges.keys()))
            sku_count = get_random_sku(sku_range_key)

            sterility_option = random.choice(sterility)

            base_duration = complexity_matrices[project_type][complexity_category]
            duration_range = calculate_duration_range(base_duration, complexity_category, di, bus, cs, sku_count, sterility_option, rps)

            batch_scenarios.append((project_type, bus, bis, di, cs, ['United States'], rps, dc, mc, complexity_category, sku_count, sterility_option, duration_range))

        formatted_scenarios = format_for_excel(batch_scenarios)

        with open("project_scenarios.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            if not header_written:
                writer.writerow(formatted_scenarios[0])
                header_written = True
            writer.writerows(formatted_scenarios[1:])
        print(f"Processed batch {start // batch_size + 1} of {num_samples // batch_size + 1}")

process_and_save_scenarios()

#note