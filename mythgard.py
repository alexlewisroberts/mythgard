import streamlit as st
import numpy as np
import pandas as pd
import string
from collections import Counter
import matplotlib.pyplot as plt
from  matplotlib.ticker import PercentFormatter
import seaborn as sns
pd.options.display.float_format = '{:.1%}'.format

import re
from bs4 import BeautifulSoup
import requests

from support import *

### Scrape information on all cards from website

@st.cache
def load_data():
    url = "https://www.mythgardhub.com/deck-builder"
    page = requests.get(url)
    soup = BeautifulSoup(page.content)

    for script in soup.find_all('script'):
      if script.get('id')=='__NEXT_DATA__':
        text = script
    return text.get_text()[195:-4208]

json_string = load_data()

### Import into dataframe
df = pd.read_json(json_string)


df['name']=df['name'].apply(lambda row: string.capwords(row))
df.set_index('name',inplace=True)

def faction(x):
  try:
    return (str(x)[127:]).split("}",1)[0][:-1]
  except:
    return None
df["faction"] = df["cardFactions"].apply(lambda x: faction(x))

### User input

st.sidebar.header("Your deck")

st.sidebar.write("""
Enter deck in box below.
""")

deck_input = """
name: Copy of BOP
coverart: The Long Winter
path: turn of seasons
power: bolster
1 honed edge
1 draupnir band
1 false mjolnir
1 loki's veil
2 forked lightning
1 junkyard valhalla
1 magnus thorsson
1 mimir reborn
2 cataclysm
2 volcanic risi
1 lamp of wonders
2 wry trickster
2 shadhavar beast
2 jaza'eri arquebus
2 peri at the gates
1 scion of pride
2 racer in shadow
2 sniffer
3 axe man
2 juke
1 night market
1 misfortune
1 shinobi of fire
2 shinobi of wind
1 thriving shade
1 merciless koxinga
1 perfect grade
"""

deck = st.sidebar.text_area("Deck Input", deck_input, height=450)

st.sidebar.write("On average, in which round is the number of cards played divided by the number of colors you play equal one?")
add_one_gem = st.sidebar.slider('Add one gem', 2, 5, 3)

st.sidebar.write("On average, in which round is the number of cards played divided by the number of colors you play equal two?")
add_two_gems = st.sidebar.slider('Add two gems', 3, 8, 5)

st.sidebar.header("Look up cards")
faction = ['Norden','Oberos','Dreni','Aztlan','Harmony','Parsa']
selected_faction = st.sidebar.selectbox('Faction', faction)
type = ['Minion','Spell','Artifact','Enchantment']
selected_type = st.sidebar.selectbox('Type', type)

card_choices = df[
                   (df['faction']==selected_faction.lower()) &
                   (df.supertype.apply(lambda x: x == list([selected_type.upper()])))
                  ].index.values
_ = st.sidebar.selectbox('Card', card_choices)

### Manipulate the user input

temp = deck.split("\n")
temp = list(map(lambda item: string.capwords(item),temp))
intro = {}
for item in temp[1:5]:
  x,y = [l.strip() for l in item.split(':')]
  intro[x] = y
path = intro['Path']
power = intro['Power']
final_list = list(map(lambda x: x.split(" ",1), temp[5:]))
final_list = list(filter(lambda x: x != [''],final_list))
dict_temp = {}
for [x,y] in final_list:
  dict_temp[y]=int(x)
series = pd.Series(dict_temp)
series.name = "multiplicity"

### Import features from json dataframe
dataframe = series.to_frame().merge(df, how="left", left_index=True, right_index=True)
dataframe.drop(columns=['__typename','cardFactions','id'],inplace=True)

### Do the math
def add_gems(gems,mana):
  if gems is not None:
    if (mana>=add_one_gem) and (mana<add_two_gems):
      gems+=gems[-1]
    elif mana>=add_two_gems:
      gems+=gems[-1]+gems[-1]
  return gems
dataframe["gem"]=dataframe.apply(lambda row: add_gems(row.gem,row.mana),axis=1)
def burn_rate(mana):
  return min(1.0,(mana-1.0)/6.0)
dataframe["burn"] = dataframe.apply(lambda row: burn_rate(row.mana),axis=1)

G = dataframe.loc[dataframe["faction"] == "dreni","multiplicity"].sum()
Y = dataframe.loc[dataframe["faction"] == "aztlan","multiplicity"].sum()
P = dataframe.loc[dataframe["faction"] == "harmony","multiplicity"].sum()
R = dataframe.loc[dataframe["faction"] == "oberos","multiplicity"].sum()
O = dataframe.loc[dataframe["faction"] == "parsa","multiplicity"].sum()
B = dataframe.loc[dataframe["faction"] == "norden","multiplicity"].sum()
color1 = {"G":G,"Y":Y,"P":P,"R":R,"O":O,"B":B}
color2 = {"dreni":"G","aztlan":"Y","harmony":"P","oberos":"R","parsa":"O","norden":"B"}
allCards = G + Y + P + R + O + B

if path == "Turn Of Seasons": draw = [4,8,12]
elif path == "Journey Of Souls": draw = [np.inf,np.inf,np.inf]
elif path == "Disk Of Circadia": draw = [5,5,7]
elif path == "Fires Of Creation": draw = [np.inf,np.inf,np.inf]
elif path == "Coliseum Of Strife": draw = [6,8,10]
elif path == "Rainbow's End": draw = [3,5,8]
elif path == "Rebellion Safehouse": draw = [6,10,np.inf]
elif path == "Alliance Command Center": draw = [5,8,11]
else: draw = None

dataframe["inHandOnCurve_no_burn"] = dataframe.apply(lambda row: (1-(row.burn*6+0.5*row.burn*row.mana)/(6+row.mana))*master(allCards,6+row.mana+sum(list(map(lambda x: int(x<=row.mana),draw))),row.multiplicity,-1,0,0,0,0,0,0,0,0),axis=1)
dataframe["inHandOnCurve_burn"] = dataframe.apply(lambda row: (row.burn*6+0.5*row.burn*row.mana)/(6+row.mana)*master_burn(allCards,6+row.mana+sum(list(map(lambda x: int(x<=row.mana),draw))),row.multiplicity),axis=1)
dataframe["inHandOnCurve"] = dataframe.apply(lambda row: row.inHandOnCurve_no_burn + row.inHandOnCurve_burn,axis=1)
dataframe["playable_no_burn"] = dataframe.apply(lambda row: masterGem(allCards,6+row.mana+sum(list(map(lambda x: int(x<=row.mana),draw))),row.multiplicity,1,color1.get(color2.get(row.faction)),Counter(row.gem).get(color2.get(row.faction)),0,0,multigem1(row.gem,row.faction),multigem2(row.gem,row.faction),0,0)/master(allCards,6+row.mana+sum(list(map(lambda x: int(x<=row.mana),draw))),row.multiplicity,-1,0,0,0,0,0,0,0,0),axis=1)
dataframe["playable_burn"] = dataframe.apply(lambda row: master(allCards,6+row.mana-2+sum(list(map(lambda x: int(x<=row.mana),draw))),color1.get(color2.get(row.faction))-2,-Counter(row.gem).get(color2.get(row.faction))+1),axis=1)
dataframe["unplayableOnCurve"] = dataframe.apply(lambda row: 1 - (row.playable_no_burn*row.inHandOnCurve_no_burn+row.playable_burn*row.inHandOnCurve_burn)/row.inHandOnCurve,axis=1)
dataframe.sort_values(by=["inHandOnCurve"],inplace=True,ascending=False)
average_inHandOnCurve = (dataframe["inHandOnCurve"]*dataframe["multiplicity"]).sum()/allCards
dataframe["percentageOfGamesNegativelyEffected"] = dataframe["inHandOnCurve"]*dataframe["unplayableOnCurve"]
cols = dataframe.columns.to_list()
cols = cols[-3:]+cols[:-3]
dataframe = dataframe[cols]
allPlayable = (1-(dataframe["percentageOfGamesNegativelyEffected"]*dataframe["multiplicity"]).sum()/allCards)**(6+8)
oneUnplayable = (6+8)*((dataframe["percentageOfGamesNegativelyEffected"]*dataframe["multiplicity"]).sum()/allCards)*(1-(dataframe["percentageOfGamesNegativelyEffected"]*dataframe["multiplicity"]).sum()/allCards)**(6+8-1)

### Display DataFrame
st.subheader('Display DataFrame')
st.write(dataframe)

### Statistics
st.write(f'Average unplayability on curve of all cards: {(dataframe["unplayableOnCurve"]*dataframe["multiplicity"]).sum()/allCards:.1%}')
st.write(f'Percentage of games having at least one unplayable card on curve: {1-allPlayable:.1%}')
st.write(f'Percentage of games having at least two unplayable cards on curve: {1-allPlayable-oneUnplayable:.1%}')

### Plots
pieChartData = dataframe[dataframe["percentageOfGamesNegativelyEffected"]>0.025]["percentageOfGamesNegativelyEffected"].sort_values()
temp = (pieChartData/dataframe["percentageOfGamesNegativelyEffected"].sum()*oneUnplayable)
newRow1 = {"All cards playable on curve":allPlayable}
newRow2 = {"Two or more cards unplayable on curve":(1-allPlayable-oneUnplayable)}
newRow3 = {"One other card (individual rates too small)":oneUnplayable*(1-pieChartData.sum()/dataframe["percentageOfGamesNegativelyEffected"].sum())}
pieChartData = temp.append(pd.Series({**newRow1, **newRow2, **newRow3}))
fig1, ax1 = plt.subplots(figsize=(10,10))
ax1.pie(pieChartData, autopct='%1.1f%%', labels=pieChartData.keys())
ax1.yaxis.set_label_text("")
ax1.set_title('Chance that there is a card you can\'t play on curve')
st.pyplot(fig1)


barChartData = dataframe[dataframe["percentageOfGamesNegativelyEffected"]>0.02]["percentageOfGamesNegativelyEffected"]
temp = (barChartData/barChartData.sum()*oneUnplayable)
newRow1 = {"All cards playable on curve":allPlayable}
newRow2 = {"Two or more cards unplayable on curve":(1-allPlayable-oneUnplayable)}
df1 = dataframe["inHandOnCurve"].to_frame(name='percentage')
df1["legend"] = "Chance the card is in hand on curve"
df2 = dataframe["unplayableOnCurve"].to_frame(name='percentage')
df2["legend"] = "Chance the card is unplayable if in hand on curve"
newdf = pd.concat([df1,df2])
newdf.reset_index(inplace=True)

sns.set_theme()
x=sns.catplot(  y = "index",       # x variable name
              x = "percentage",       # y variable name
              hue = "legend",  # group variable name
              data = newdf,     # dataframe to plot
              kind = "bar",
              height = 9)
x.set(ylabel=None)
for ax in x.axes.flat:
    ax.set_title("Individual card chances of being in hand and unplayable")
    ax.xaxis.set_major_formatter(PercentFormatter(1))
st.pyplot(x)

fig2, ax2 = plt.subplots(figsize=(10,10))
ax2.scatter(x=dataframe["inHandOnCurve"],y=dataframe["unplayableOnCurve"],c='#000000')
ax2.set_title('Overview of the unplayability of all your cards')
ax2.xaxis.set_label_text("in hand on curve")
ax2.yaxis.set_label_text("unplayable on curve")
st.pyplot(fig2)
