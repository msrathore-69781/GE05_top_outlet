import pandas as pd

jan = pd.read_excel("first_month.xlsx")
feb = pd.read_excel("second_month.xlsx")
mar = pd.read_excel("third_month.xlsx")

def process(df):
    # Filter where Sales Qty CMLY (index 9) != 0
    df_filtered = df[df.iloc[:, 9].notna()]


    # Group by Retailer Code (index 4)
    result = df_filtered.groupby(df_filtered.iloc[:, 4]).agg(
        sku_count=(df_filtered.columns[6], 'nunique'),   # unique SKU (Material Code)
        total_to=(df_filtered.columns[11], 'sum'),       # sum of TO
        wd_code=(df_filtered.columns[2], 'first'),
        wd=(df_filtered.columns[3], 'first'),
        ret_name=(df_filtered.columns[5], 'first'),
        ffr=(df_filtered.columns[1], 'first')
    ).reset_index()

    # Rename Retailer Code column
    result = result.rename(columns={result.columns[0]: 'Retailer Code'})

    return result

# Process each month
jan_res = process(jan)
feb_res = process(feb)
mar_res = process(mar)

# Rename columns
jan_res = jan_res.rename(columns={'sku_count': 'sku_jan', 'total_to': 'to_jan'})
feb_res = feb_res.rename(columns={'sku_count': 'sku_feb', 'total_to': 'to_feb'})
mar_res = mar_res.rename(columns={'sku_count': 'sku_mar', 'total_to': 'to_mar'})

# Merge all months
merged = jan_res.merge(
    feb_res[['Retailer Code', 'sku_feb', 'to_feb']],
    on='Retailer Code', how='outer'
)

merged = merged.merge(
    mar_res[['Retailer Code', 'sku_mar', 'to_mar']],
    on='Retailer Code', how='outer'
)

# Fill missing values
merged[['sku_jan','sku_feb','sku_mar','to_jan','to_feb','to_mar']] = \
    merged[['sku_jan','sku_feb','sku_mar','to_jan','to_feb','to_mar']].fillna(0)

# Calculate averages
merged['Average SKU Count'] = (
    merged['sku_jan'] + merged['sku_feb'] + merged['sku_mar']
) / 3

merged['Average TO'] = (
    merged['to_jan'] + merged['to_feb'] + merged['to_mar']
) / 3

# Final output
final = merged[[
    'wd_code', 'wd', 'Retailer Code', 'ret_name',
    'ffr', 'Average SKU Count', 'Average TO'
]]

# Save file
final.to_excel("Retailer_Summary.xlsx", index=False)

print("✅ Done! File saved as Retailer_Summary.xlsx")