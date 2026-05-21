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

response1 = requests.get(url, headers=headers, params=params1)
response2 = requests.get(url, headers=headers, params=params2)

data1 = response1.json()
data2 = response2.json()

rows1 = data1["data"]
rows2 = data2["data"]
df1 = pd.json_normalize(rows1)
df2 = pd.json_normalize(rows2)

df1 = df1[["datetime", "value"]]
df2 = df2[["datetime", "value"]]

df3 = pd.merge(df1, df2, how='outer')
print(df3)

df3["datetime"] = pd.to_datetime(df3["datetime"])
df3["year"] = df3["datetime"].dt.year
df3["value"] = df3["value"]/1000000

#plt.figure(figsize=(10, 6))
df3.plot(x="year", y="value", kind = "bar")
plt.title("France - Hydroelectricity generation evolution 2015-2024")
plt.xlabel("Year")
plt.ylabel("Hydroelectricity Generation (TWh/year)")
plt.show()