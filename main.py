# This is a sample Python scrip

import pandas as pd
from matplotlib import pyplot as plt
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    xls = pd.ExcelFile("GPS_ERT.xlsx")
    for sheet in xls.sheet_names[0:1]:

        df = pd.read_excel(xls,sheet)
        # df = pd.read_csv("A-1m_topo.csv")
        df["Elektrode nr "] = df["Elektrode nr "] - 1
        df.index = df["Elektrode nr "]
        df.plot(x="Elektrode nr ",y="Z")
        outstring = ""
        outstring+="topo\n2\n%i\n" % len(df)
        outstring+= df["Z"].to_string(header=False)
        outstring +="\ntopo\n0\n0\n0\n0\n"
        print(outstring)
        plt.show
        #df.plot.scatter(x = "X", y = "Y", c = "Z" ,colormap='viridis',title = sheet)
        #plt.savefig("./pictures/"+sheet + ".png")
        #df = df.reindex(range(1, df.index.max() + 1)).interpolate(method='linear')
        #df[["X", "Y", "Z"]].to_csv("./topofiles/topo" + sheet + ".csv")

    xls.close()
