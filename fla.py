import pandas as pd

# Read CSV
df = pd.read_csv("raw_fla_data.csv")

# Check column names
print("Columns:")
for i, col in enumerate(df.columns):
    print(i, repr(col))

# Store each lamp setting's data
data = {}

for i in range(0, len(df.columns), 2):

    time_col = df.columns[i]
    current_col = df.columns[i + 1]

    # Extract lamp setting
    lamp = int(time_col.split()[2])

    # Convert to numeric
    time = pd.to_numeric(df[time_col], errors="coerce")
    current = pd.to_numeric(df[current_col], errors="coerce")

    # Create dataframe
    lamp_data = pd.DataFrame({
        "Relative Time (s)": time,
        "Current (A)": current
    })

    # Remove missing values
    lamp_data = lamp_data.dropna()

    # Normalize time so that the first time value is 0
    lamp_data["Time (s)"] = (
        lamp_data["Relative Time (s)"]
        - lamp_data["Relative Time (s)"].iloc[0]
    )

    # Calculate resistance: R = V/I, where V = 0.5 V
    lamp_data["Resistance (Ω)"] = (
        0.5 / lamp_data["Current (A)"].replace(0, pd.NA)
    )

    # Store data
    data[lamp] = lamp_data

    