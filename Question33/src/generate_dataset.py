"""
Synthetic Dataset Generator for Smart Agriculture Challenge (DS_Day01_33)
Generates 2,160 records across 12 farms over 90 days with 2 daily readings.
Reflects realistic pre-irrigation soil moisture readings, weather, fixed irrigation schedules,
water stress occurrences, and crop outcomes.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_agricultural_dataset(output_path="data/DS_Day01_33_Smart_Agriculture_Synthetic_Dataset.xlsx", random_seed=42):
    np.random.seed(random_seed)
    
    num_farms = 12
    num_days = 90
    start_date = datetime(2024, 5, 1)
    farm_ids = [f"Farm_{i:02d}" for i in range(1, num_farms + 1)]
    
    # Regional baseline temperature across 90 days (summer progression)
    base_temps = 26.5 + 5.5 * np.sin(np.linspace(0, np.pi, num_days))
    # Heatwave during peak flowering (days 35-52)
    base_temps[35:53] += np.random.uniform(2.5, 4.8, 18)
    
    # Regional rain events (11 distinct rain systems over 90 days)
    rain_days_indices = [5, 12, 19, 27, 33, 58, 64, 71, 77, 82, 87]
    rain_amounts = np.zeros(num_days)
    for rd in rain_days_indices:
        rain_amounts[rd] = np.random.uniform(14.0, 36.0)
    # Minor showers
    for si in [9, 23, 61, 79]:
        rain_amounts[si] = np.random.uniform(3.0, 7.5)

    records = []
    
    for farm_idx, farm_id in enumerate(farm_ids):
        # Initial pre-season soil moisture (%)
        current_moisture = float(np.random.uniform(28.0, 32.0))
        
        # Farm fixed schedule interval: Farm 1-4: 3 days, Farm 5-8: 2 days, Farm 9-12: 4 days
        if farm_idx < 4:
            fixed_interval = 3
        elif farm_idx < 8:
            fixed_interval = 2
        else:
            fixed_interval = 4
            
        preferred_slot = "Morning" if (farm_idx % 2 == 0) else "Evening"
        
        for day in range(num_days):
            current_day_date = start_date + timedelta(days=day)
            
            # Crop Stage progression
            if day < 30:
                crop_stage = "Vegetative"
                stress_threshold = 19.0
                optimal_low, optimal_high = 23.0, 35.0
                crop_et_multiplier = 1.0
            elif day < 65:
                crop_stage = "Flowering"
                stress_threshold = 24.0  # Flowering is sensitive to moisture deficit
                optimal_low, optimal_high = 27.0, 38.0
                crop_et_multiplier = 1.35
            else:
                crop_stage = "Maturity"
                stress_threshold = 16.5
                optimal_low, optimal_high = 20.0, 33.0
                crop_et_multiplier = 0.90
                
            day_rain = rain_amounts[day]
            farm_rain = max(0.0, np.round(day_rain + np.random.normal(0, 0.7) if day_rain > 0 else 0.0, 1))
            
            for hour, slot_name in [(8, "Morning"), (17, "Evening")]:
                timestamp = current_day_date.replace(hour=hour, minute=0, second=0)
                
                # Temperature & Humidity for slot
                if slot_name == "Morning":
                    temp = base_temps[day] - 4.2 + np.random.normal(0, 0.8)
                    humidity = np.clip(76 - (temp - 20) * 1.5 + np.random.normal(0, 2.5), 45.0, 92.0)
                    slot_rain = farm_rain * 0.45 if farm_rain > 0 else 0.0
                else:
                    temp = base_temps[day] + 4.5 + np.random.normal(0, 1.0)
                    humidity = np.clip(54 - (temp - 24) * 1.9 + np.random.normal(0, 2.8), 24.0, 72.0)
                    slot_rain = farm_rain * 0.55 if farm_rain > 0 else 0.0
                    
                temp = float(np.round(np.clip(temp, 16.5, 42.5), 1))
                humidity = float(np.round(humidity, 1))
                slot_rain = float(np.round(slot_rain, 1))
                
                # Current observed soil moisture AT DECISION TIME
                obs_moisture = float(np.round(current_moisture, 1))
                
                # Farmer Fixed Schedule decision (calendar-based)
                is_schedule_slot = (day % fixed_interval == 0) and (slot_name == preferred_slot)
                if is_schedule_slot:
                    irrigate = 1 if np.random.random() < 0.92 else 0
                else:
                    irrigate = 1 if np.random.random() < 0.04 else 0
                    
                irrigation_status = "Irrigated" if irrigate == 1 else "Not Irrigated"
                
                # Crop outcome observed at current conditions
                if obs_moisture < stress_threshold:
                    crop_outcome = "Stressed"
                elif obs_moisture >= optimal_low and obs_moisture <= optimal_high:
                    if temp >= 39.0 and humidity <= 27.0:
                        crop_outcome = "Moderate"
                    else:
                        crop_outcome = "Optimal"
                else:
                    crop_outcome = "Moderate"
                    
                # Append observation record
                records.append({
                    "Timestamp": timestamp,
                    "Farm_ID": farm_id,
                    "Soil_Moisture": obs_moisture,
                    "Temperature": temp,
                    "Humidity": humidity,
                    "Rainfall": slot_rain,
                    "Crop_Stage": crop_stage,
                    "Irrigation_Status": irrigation_status,
                    "Crop_Outcome": crop_outcome
                })
                
                # Physical transition to next time slot:
                # Recharge from slot rain and irrigation
                rain_recharge = slot_rain * 0.45
                irr_recharge = 7.5 if irrigate == 1 else 0.0
                # Evapotranspiration depletion
                et_depletion = (0.045 * temp - 0.015 * humidity + 0.60) * crop_et_multiplier
                et_depletion = max(0.4, et_depletion) + np.random.normal(0, 0.08)
                
                current_moisture = current_moisture + rain_recharge + irr_recharge - et_depletion
                current_moisture = np.clip(current_moisture, 11.5, 45.0)

    df = pd.DataFrame(records)
    print(f"Generated Dataset Shape: {df.shape}")
    print(f"Farms: {df['Farm_ID'].nunique()}, Days: {df['Timestamp'].dt.date.nunique()}")
    print("\n--- Summary Statistics of Features ---")
    print(df[['Soil_Moisture', 'Temperature', 'Humidity', 'Rainfall']].describe().round(2))
    print("\n--- Irrigation Status Counts ---")
    print(df['Irrigation_Status'].value_counts())
    print("\n--- Crop Outcome Counts ---")
    print(df['Crop_Outcome'].value_counts())
    print("\n--- Crop Stage Counts ---")
    print(df['Crop_Stage'].value_counts())
    
    # Save to Excel
    df.to_excel(output_path, index=False)
    print(f"\nSuccessfully saved dataset to {output_path}")
    return df

if __name__ == "__main__":
    generate_agricultural_dataset()
