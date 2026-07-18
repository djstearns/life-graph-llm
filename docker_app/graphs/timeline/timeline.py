import streamlit as st
import pandas as pd
import numpy as np 
import os
import json
import matplotlib.pyplot as plt

def my_function(dates):
    main_function(dates)
    st.write("Function executed!")

def main_function(dates):
    json_data = json.loads(dates)
    dates = []
    phones = []
    for item in json_data['data']:
        if 'date' in item:
            dates.append(item['date'])
            if 'comment' in item:
                phones.append(item['comment'])
    # dates = ["2007-6-29", "2008-7-11", "2009-6-29", "2010-9-21", "2011-10-14", "2012-9-21", "2013-9-20",
    #         "2014-9-19", "2015-9-25", "2016-3-31", "2016-9-16", "2017-9-22", "2017-11-3", "2018-9-21",
    #         "2018-10-26", "2019-9-20", "2020-11-13", "2021-9-24", "2022-9-16"
    #         ]
    # phones = ["iPhone", "iPhone-3G", "iPhone-3GS", "iPhone 4", "iPhone 4S", "iPhone 5", "iPhone 5C/5S",
    #         "iPhone 6/6 Plus", "iPhone 6S/6s Plus", "iPhone SE", "iPhone 7/7 Plus", "iPhone 8/8 Plus",
    #         "iPhone X", "iPhone Xs/Max", "iPhone XR", "iPhone 11/Pro/Max", "iPhone 12 Pro", "iPhone 13 Pro",
    #         "iPhone 14 Plus/Pro Max"
    #         ]

    iphone_df = pd.DataFrame(data={"Date": dates, "Product": phones})
    iphone_df["Date"] = pd.to_datetime(iphone_df["Date"])
    iphone_df["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(len(iphone_df))]

    iphone_df
    with plt.style.context("fivethirtyeight"):
        fig, ax = plt.subplots(figsize=(9,18))

    ax.plot([0,]* len(iphone_df), iphone_df.Date.values, "-o", color="black", markerfacecolor="white");

    ax.set_yticks(pd.date_range("2007-1-1", "2023-1-1", freq="ys"), range(2007, 2024));
    ax.set_xlim(-7,7);
    
    for idx in range(len(iphone_df)):
        dt, product, level = iphone_df["Date"][idx], iphone_df["Product"][idx], iphone_df["Level"][idx]
        dt_str = dt.strftime("%b-%Y")
        ax.annotate(dt_str + "\n" + product, xy=(0.1 if level>0 else -0.1, dt),
                    xytext=(level, dt),
                    arrowprops=dict(arrowstyle="-",color="red", linewidth=0.8),
                    va="center"
                   );
   
    # ax.spines[["left", "top", "right", "bottom"]].set_visible(False);
    
    # ax.spines[["left"]].set_position(("axes", 0.5));
    # ax.xaxis.set_visible(False);
    # ax.set_title("Lifegraph", pad=10, loc="left", fontsize=25, fontweight="bold");
    # ax.grid(False)
    
    figs = plt.savefig("Matplotlib_lifegraph.pdf", format="pdf", bbox_inches="tight")
    
    return figs
