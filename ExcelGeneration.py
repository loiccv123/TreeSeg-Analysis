import os
import pandas as pd
import numpy as np


base_path = '/Users/loiccv/Documents/UQAM/RStudio_1st_project/Markdown/Completed/reports 2025/processed jul 1 2026'
output_excel = os.path.join(base_path, "New_growth.xlsx")


### ADDD RMSEEEEE
wanted_cols = [
    "Bloc_Nb",
    "Tree_ID",
    "Tree_Type",
    "Treatment",
    "Height_m",
    "Crown_Diam_m",

    # "Nb_Voxel_in_cone_6m_2_5cm",
    "Nb_Voxel_in_cone_6m_5cm",
    # "Nb_Voxel_in_cone_6m_10cm",
    # "total_voxels_2_5cm",
    "total_voxels_5cm",
    # "total_voxels_10cm",

    "Total_pixel",

    # "Cone_Count_0.5",
    # "Cone_Count_0.75",
    # "Cone_Count_1",
    # "Cone_Count_1.5",
    # "Cone_Count_2",
    # "Cone_Count_2.5",
    # "Cone_Count_3",
    # "Cone_Count_4",
    # "Cone_Count_5",
    # "Cone_Count_7.5",
    # "Cone_Count_10",
    # "Cone_Count_15",
    # "Cone_Count_20",

    # "Total_Count_0.5",
    # "Total_Count_0.75",
    # "Total_Count_1",
    # "Total_Count_1.5",
    # "Total_Count_2",
    # "Total_Count_2.5",
    # "Total_Count_3",
    # "Total_Count_4",
    # "Total_Count_5",
    # "Total_Count_7.5",
    # "Total_Count_10",
    # "Total_Count_15",
    # "Total_Count_20",

    # "Alignement_RSME",

    # "Growth_Voxel_5cm_res_5cm_dist",
    # "Growth_Voxel_5cm_res_10cm_dist",
    "Growth_Voxel_5cm_res_15cm_dist",
    # "Growth_Voxel_10cm_res_5cm_dist",
    # "Growth_Voxel_10cm_res_10cm_dist",
    # "Growth_Voxel_10cm_res_15cm_dist",

    # "Growth_Pct_5cm_res_5cm_dist",
    # "Growth_Pct_5cm_res_10cm_dist",
    "Growth_Pct_5cm_res_15cm_dist",
    # "Growth_Pct_10cm_res_5cm_dist",
    # "Growth_Pct_10cm_res_10cm_dist",
    # "Growth_Pct_10cm_res_15cm_dist",
]

def find_all_csvs(folder):
    csv_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return sorted(csv_files)

all_csvs = find_all_csvs(base_path)
combined = []

for csv_path in all_csvs:
    try:
        df = pd.read_csv(csv_path)

        keep = [c for c in wanted_cols if c in df.columns]
        df = df[keep].copy()

        for c in wanted_cols:
            if c not in df.columns:
                df[c] = np.nan

        df = df[wanted_cols]

        combined.append(df)
        print(f"Loaded: {csv_path}")

    except Exception as e:
        print(f"Skipped: {csv_path} -> {e}")

if not combined:
    raise RuntimeError("No CSV files were loaded.")

final_df = pd.concat(combined, ignore_index=True)

final_df = final_df.drop_duplicates().reset_index(drop=True)

final_df.to_excel(output_excel, index=False)

print(f"\nSaved Excel file:\n{output_excel}")
print(f"Rows exported: {len(final_df)}")