import pandas as pd
import mysql.connector
import numpy as np

# === Configuration ===
csv_path = r"C:\Users\madhugula padmavathi\Downloads\combined_bird_monitoring_data.csv"

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Padmavathi@09",  
    database="bird_monitoring_db"
)
cursor = db.cursor()

# === Drop the table if it exists ===
cursor.execute("DROP TABLE IF EXISTS bird_table")
print("✅ Dropped existing bird_table if it existed.")

# === Create table with appropriate column types ===
create_query = """
CREATE TABLE bird_table (
    Admin_Unit_Code VARCHAR(100),
    Plot_Name VARCHAR(100),
    Location_Type VARCHAR(100),
    Year INT,
    Date DATE,
    Start_Time VARCHAR(20),
    End_Time VARCHAR(20),
    Observer VARCHAR(100),
    Visit VARCHAR(50),
    Interval_Length VARCHAR(50),
    ID_Method VARCHAR(50),
    Distance VARCHAR(50),
    Flyover_Observed VARCHAR(10),
    Sex VARCHAR(20),
    Common_Name VARCHAR(100),
    Scientific_Name VARCHAR(100),
    AcceptedTSN VARCHAR(50),
    TaxonCode VARCHAR(50),
    AOU_Code VARCHAR(50),
    PIF_Watchlist_Status VARCHAR(50),
    Regional_Stewardship_Status VARCHAR(50),
    Temperature FLOAT,
    Humidity FLOAT,
    Sky VARCHAR(50),
    Wind VARCHAR(50),
    Disturbance VARCHAR(255),
    Previously_Obs VARCHAR(50),
    Initial_Three_Min_Cnt VARCHAR(50),
    Source_File VARCHAR(255),
    Sheet_Name VARCHAR(100),
    Site_Name VARCHAR(100),
    NPSTaxonCode VARCHAR(50),
    Sub_Unit_Code VARCHAR(50)
);
"""
cursor.execute(create_query)
print("✅ Recreated bird_table with correct schema.")

# === Load CSV ===
df = pd.read_csv(csv_path, dtype=str, low_memory=False)
print(f"📊 Loaded CSV with {len(df)} rows.")

# === Clean Data ===
# Fix Date column to be proper datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Convert numeric columns to proper types
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
df['Humidity'] = pd.to_numeric(df['Humidity'], errors='coerce')

# Replace NaN/NA with None
df = df.where(pd.notnull(df), None)

# === Insert Data ===
insert_query = """
INSERT INTO bird_table (
    Admin_Unit_Code, Plot_Name, Location_Type, Year, Date, Start_Time, End_Time, Observer,
    Visit, Interval_Length, ID_Method, Distance, Flyover_Observed, Sex, Common_Name,
    Scientific_Name, AcceptedTSN, TaxonCode, AOU_Code, PIF_Watchlist_Status,
    Regional_Stewardship_Status, Temperature, Humidity, Sky, Wind, Disturbance,
    Previously_Obs, Initial_Three_Min_Cnt, Source_File, Sheet_Name, Site_Name,
    NPSTaxonCode, Sub_Unit_Code
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

count = 0
for _, row in df.iterrows():
    cleaned_row = [None if pd.isna(val) else val for val in row]
    cursor.execute(insert_query, tuple(cleaned_row))
    count += 1
    if count % 1000 == 0:
        db.commit()
        print(f"✅ Inserted {count} rows...")

db.commit()
print(f"🎉 All {count} rows inserted into bird_table.")

# === Close connection ===
cursor.close()
db.close()
print("🔒 MySQL connection closed.")
