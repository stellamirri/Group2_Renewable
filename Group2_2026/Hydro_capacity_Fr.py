import requests
import pandas as pd
import matplotlib.pyplot as plt

dfPH = pd.read_csv("Evol_Capacity_Hydro_Pumped_Storage.csv")
dfHror = pd.read_csv("Evol_capacity_Hydro_run_of_river_and_poundage.csv")
dfWR = pd.read_csv("Evol_Capacity_hydro_reservoir.csv")
#dfTot = pd.read_csv("Evol_parc_installe_elec_FR.csv", sep = ";")


Pumped_hydro_storage = dfPH[(dfPH["Year"] >= 2016)&(dfPH["Year"] <= 2025)]
year = Pumped_hydro_storage["Year"]
Pumped_hydro_storage = Pumped_hydro_storage["Installed Production Capacity (MW)"]/1000
Run_of_river_and_poundage = dfHror[(dfHror["Year"] >= 2016)&(dfHror["Year"] <= 2025)]
Run_of_river_and_poundage = Run_of_river_and_poundage["Installed Production Capacity (MW)"]/1000
Water_reservoir = dfWR[(dfWR["Year"] >= 2016)&(dfWR["Year"] <= 2025)]
Water_reservoir = Water_reservoir["Installed Production Capacity (MW)"]/1000

# df_tot_hydraulique = dfTot[dfTot["Filière"] == "Hydraulique"]
# df_tot_hydraulique = df_tot_hydraulique[(dfTot["Date"] >= 2016)&(dfTot["Date"] <= 2025)]
# Total_capacity = df_tot_hydraulique["Valeur (GW)"]*1000




bar_width = 0.35
x = range(len(year))

plt.figure(figsize=(9, 5))
plt.bar([i for i in x], Pumped_hydro_storage, width=bar_width, label = "Pumped Hydro Storage", color = "blue")
plt.title("France - evolution of the installed capacity of pumped storage hydro")
plt.xlabel("Year")
plt.ylabel("Capacity (GW)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, year)
plt.ylim(60, 64)
plt.legend(loc="upper left")
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "The pumped hydro storage installed capacity has increase during the past few years.\n "
    "Source : RTE",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  # Fond gris clair avec transparence
)



plt.figure(figsize=(9, 5))
plt.bar([i for i in x], Water_reservoir, width=bar_width, label = "Water reservoir", color = "red")
plt.title("France - evolution of the installed capacity of water reservoir")
plt.xlabel("Year")
plt.ylabel("Capacity (GW)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, year)
plt.ylim(8.5, 9)
plt.legend(loc="upper left")
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "The water reservoir installed capacity has stayed stable during the past few years. \n"
    "Source : RTE",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  # Fond gris clair avec transparence
)

plt.figure(figsize=(9, 5))
plt.bar([i for i in x], Run_of_river_and_poundage, width=bar_width, label = "Run of river and poundage", color = "yellow")
plt.title("France - evolution of the installed capacity of run of river and poundage hydro")
plt.xlabel("Year")
plt.ylabel("Capacity (GW)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, year)
plt.ylim(10.75, 11.75)
plt.legend(loc="upper left")
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "The run of river and poundage installed capacity has increase during the past few years. \n"
    "Source : RTE",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  # Fond gris clair avec transparence
)

plt.show() 