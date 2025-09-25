EMISSION_FACTORS = {
    'car_per_km': 0.192,
    'bus_per_km': 0.089,
    'train_per_km': 0.041,
    'flight_per_hour': 90.0,
    'electricity_per_kwh': 0.82,
    'meat_meal': 5.5,
    'veg_meal': 2.0,
    'one_tree_absorb_per_year_kg': 22
}
def compute_co2(inputs: dict) -> dict:
    car = inputs.get('daily_car_km', 0) * EMISSION_FACTORS['car_per_km'] * 365
    bus = inputs.get('daily_bus_km', 0) * EMISSION_FACTORS['bus_per_km'] * 365
    train = inputs.get('daily_train_km', 0) * EMISSION_FACTORS['train_per_km'] * 365
    flights = inputs.get('weekly_flight_hours', 0) * EMISSION_FACTORS['flight_per_hour'] * 52
    electricity = inputs.get('monthly_electricity_kwh', 0) * EMISSION_FACTORS['electricity_per_kwh'] * 12
    meals_per_day = inputs.get('meals_per_day', 3)
    meat_ratio = inputs.get('meat_meal_ratio', 0.5)
    meat_meals = meals_per_day * 365 * meat_ratio
    veg_meals = meals_per_day * 365 * (1 - meat_ratio)
    diet = meat_meals * EMISSION_FACTORS['meat_meal'] + veg_meals * EMISSION_FACTORS['veg_meal']
    trees = inputs.get('trees_planted', 0) * EMISSION_FACTORS['one_tree_absorb_per_year_kg']
    total = car + bus + train + flights + electricity + diet - trees
    if total < 0:
        total = 0
    if total < 2000:
        cat = 'Good Footprint'
    elif total < 6000:
        cat = 'Moderate Footprint'
    else:
        cat = 'Dirty Footprint'
    breakdown = {
        'Car': round(car,2), 'Bus': round(bus,2), 'Train': round(train,2),
        'Flights': round(flights,2), 'Electricity': round(electricity,2), 'Diet': round(diet,2),
        'TreesRemoved': round(trees,2)
    }
    return {'total_kg_co2_per_year': round(total,2), 'category': cat, 'breakdown': breakdown}
