import requests
import pandas as pd
import matplotlib.pyplot as plt

API_KEY = "patCytbSzwwY9ZZhgner"

url = "https://api.electricitymaps.com/v3/electricity-source/hydro/past-range"

headers = {
"auth-token": API_KEY
}

params1 = {
    "zone": "FR",
    "start": "2017-01-01T00:00:00.000Z",
    "end": "2025-01-01T00:00:00.000Z",
    "temporalGranularity": "yearly"
}

params2 = {
    "zone": "FR",
    "start": "2015-01-01T00:00:00.000Z",
    "end": "2017-01-01T00:00:00.000Z",
    "temporalGranularity": "yearly"
}
#there is a 10 years time limit to this API command and there is no data before 2015 and no data after 2024


params3 = {
    "zone": "ES",
    "start": "2015-01-01T00:00:00.000Z",
    "end": "2017-01-01T00:00:00.000Z",
    "temporalGranularity": "yearly"
}
params4 = {
    "zone": "ES",
    "start": "2017-01-01T00:00:00.000Z",
    "end": "2025-01-01T00:00:00.000Z",
    "temporalGranularity": "yearly"
}


params5 = {
    "zone": "DE",
    "start": "2015-01-01T00:00:00.000Z",
    "end": "2017-01-01T00:00:00.000Z",
    "temporalGranularity": "yearly"
}
params6 = {
    "zone": "DE",
    "start": "2017-01-01T00:00:00.000Z",
    "end": "2025-01-01T00:00:00.000Z",
    "temporalGranularity": "yearly"
}

response1 = requests.get(url, headers=headers, params=params1)
response2 = requests.get(url, headers=headers, params=params2)
response3 = requests.get(url, headers=headers, params=params3)
response4 = requests.get(url, headers=headers, params=params4)
response5 = requests.get(url, headers=headers, params=params5)
response6 = requests.get(url, headers=headers, params=params6)

data1 = response1.json()
data2 = response2.json()
data3 = response3.json()
data4 = response4.json()
data5 = response5.json()
data6 = response6.json()

rows1 = data1["data"]
rows2 = data2["data"]
df1 = pd.json_normalize(rows1)
df2 = pd.json_normalize(rows2)
rows3 = data3["data"]
rows4 = data4["data"]
df3 = pd.json_normalize(rows3)
df4 = pd.json_normalize(rows4)
rows5 = data5["data"]
rows6 = data6["data"]
df5 = pd.json_normalize(rows5)
df6 = pd.json_normalize(rows6)

df1 = df1[["datetime", "value"]]
df2 = df2[["datetime", "value"]]
df3 = df3[["datetime", "value"]]
df4 = df4[["datetime", "value"]]
df5 = df5[["datetime", "value"]]
df6 = df6[["datetime", "value"]]

df12 = pd.merge(df1, df2, how='outer')
df34 = pd.merge(df3, df4, how='outer')
df56 = pd.merge(df5, df6, how='outer')

df12["datetime"] = pd.to_datetime(df12["datetime"])
df12["year"] = df12["datetime"].dt.year
df12["value"] = df12["value"]/1000000
df34["datetime"] = pd.to_datetime(df34["datetime"])
df34["year"] = df34["datetime"].dt.year
df34["value"] = df34["value"]/1000000
df56["datetime"] = pd.to_datetime(df56["datetime"])
df56["year"] = df56["datetime"].dt.year
df56["value"] = df56["value"]/1000000

france_values = df12.groupby("year")["value"].sum().values
spain_values = df34.groupby("year")["value"].sum().values
germany_values = df56.groupby("year")["value"].sum().values

bar_width = 0.35
x = range(len(df12["year"]))

plt.figure(figsize=(7, 3))
plt.bar([i - bar_width/3 for i in x], france_values, width=bar_width/3, label = "France", color = "blue")
plt.bar([i + bar_width/3 for i in x], spain_values, width=bar_width/3, label = "Spain", color = "yellow")
plt.bar([i for i in x], germany_values, width=bar_width/3, label = "Germany", color = "red")
plt.title("Hydroelectricity generation evolution 2015-2024")
plt.xlabel("Year")
plt.ylabel("Hydroelectricity Generation (TWh/year)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, df12["year"])
plt.legend()
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "We can compare on this graph the evolution of the hydroelectric production (TWh/year) over the 2015-2024 period for Spain, France and Germany.\n The evolution of the production in Spain and France follow a smiliar trend : although their values differ, they have the same profile of evolution.\n There is a sharp increase in the German production starting on 2024, with an increasing production exceeding the Spanish production.\n"
    "Source : API Electricity Maps.",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  # Fond gris clair avec transparence
)

plt.show()
