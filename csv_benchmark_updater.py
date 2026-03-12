import csv
import json
import os

csv_path = r"f:\sem 4\edi 2 v2\groundwater_ai\data\groundwater_dataset.csv"
benchmarks_path = r"f:\sem 4\edi 2 v2\groundwater_ai\data\benchmarks.json"

district_data = {}

try:
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row['district'].upper()
            if d not in district_data:
                district_data[d] = {
                    'rain_sum': 0.0, 'rech_sum': 0.0, 'extr_sum': 0.0, 
                    'egw_sum': 0.0, 'agri_sum': 0.0, 'count': 0
                }
            
            try:
                # Accumulate sums for district-wide calculation (weighted average by count/volume)
                district_data[d]['rain_sum'] += float(row['rainfall'])
                district_data[d]['rech_sum'] += float(row['total_recharge'])
                district_data[d]['extr_sum'] += float(row['groundwater_extraction_total'])
                district_data[d]['egw_sum'] += float(row['extractable_groundwater'])
                district_data[d]['agri_sum'] += float(row['agriculture_extraction'])
                district_data[d]['count'] += 1
            except (ValueError, TypeError):
                continue

    final_districts = {}
    for d, sums in district_data.items():
        if sums['count'] == 0: continue
        
        # Means for the district
        avg_rain = sums['rain_sum'] / sums['count']
        avg_rech = sums['rech_sum'] / sums['count']
        avg_extr = sums['extr_sum'] / sums['count']
        avg_egw = sums['egw_sum'] / sums['count']
        avg_agri = sums['agri_sum'] / sums['count']
        
        # Benchmarks
        stress = round((avg_extr / avg_egw * 100), 1) if avg_egw else 0
        sust = round(avg_rech / avg_extr, 1) if avg_extr else 0
        # Efficiency calculation matched to India logic: (Total Recharge / Rainfall) * scale
        # India: 448.51 / 1055.21 = 0.425 -> 425.0. 
        # So it's (Recharge / Rainfall) * 1000
        eff = round((avg_rech / avg_rain * 1000), 1) if avg_rain else 0
        agri_dep = round((avg_agri / avg_extr * 100), 1) if avg_extr else 0
        
        final_districts[d] = {
            "name": f"{d} AVG",
            "stress_index": stress,
            "sustainability_ratio": sust,
            "recharge_efficiency": eff,
            "agri_dependency": agri_dep
        }

    # Load and update
    with open(benchmarks_path, 'r') as f:
        data = json.load(f)
    
    data["districts"] = final_districts
    
    with open(benchmarks_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully processed {len(final_districts)} districts from CSV.")

except Exception as e:
    print(f"Error: {e}")
