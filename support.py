import numpy as np
from collections import Counter

def chooseCard(hand,matches):
  # this is just hand!/matches!
  if hand < matches: return 0
  total = 1
  for x in range(matches+1,hand+1):
    total *= x
  return total

def chooseCardFixedOrder(hand,matches):
  # this is hand!/matches!/(hand-matches)! or hand choose matches
  if hand< matches:
    return 0
  return chooseCard(hand,matches)/chooseCard(hand-matches,0)

def master(allCards, hand, cards1, matches1, cards2=0, matches2=0, cards3=0, matches3=0, cards4=0, matches4=0, turn1=0, turn2=0):
  if turn2 > turn1: return "N/A"
  elif cards1 < matches1: return 0
  elif cards2 < matches2: return 0
  elif cards3 < matches3: return 0
  elif cards4 < matches4: return 0
  elif matches1 == -1: return (master(allCards, hand, 0, 0, cards2, matches2, cards3, matches3, cards4, matches4, turn1, turn2) - master(allCards, hand, cards1, 0, cards2, matches2, cards3, matches3, cards4, matches4, turn1, turn2))
  elif matches2 == -1: return (master(allCards, hand, cards1, matches1, 0, 0, cards3, matches3, cards4, matches4, turn1, turn2) - master(allCards, hand, cards1, matches1, cards2, 0, cards3, matches3, cards4, matches4, turn1, turn2))
  elif matches3 == -1: return (master(allCards, hand, cards1, matches1, cards2, matches2, 0, 0, cards4, matches4, turn1, turn2) - master(allCards, hand, cards1, matches1, cards2, matches2, cards3, 0, cards4, matches4, turn1, turn2))
  elif matches4 == -1: return (master(allCards, hand, cards1, matches1, cards2, matches2, cards3, matches3, 0, 0, turn1, turn2) - master(allCards, hand, cards1, matches1, cards2, matches2, cards3, matches3, cards4, 0, turn1, turn2))
  elif matches1 < -1: return (master(allCards, hand, cards1, matches1 + 1, cards2, matches2, cards3, matches3, cards4, matches4, turn1, turn2) - master(allCards, hand, cards1, -(matches1 + 1), cards2, matches2, cards3, matches3, cards4, matches4, turn1, turn2))
  elif matches2 < -1: return (master(allCards, hand, cards1, matches1, cards2, matches2 + 1, cards3, matches3, cards4, matches4, turn1, turn2) - master(allCards, hand, cards1, matches1, cards2, -(matches2 + 1), cards3, matches3, cards4, matches4, turn1, turn2))
  elif matches3 < -1: return (master(allCards, hand, cards1, matches1, cards2, matches2, cards3, matches3 + 1, cards4, matches4, turn1, turn2) - master(allCards, hand, cards1, matches1, cards2, matches2, cards3, -(matches3 + 1), cards4, matches4, turn1, turn2))
  elif matches4 < -1: return (master(allCards, hand, cards1, matches1, cards2, matches2, cards3, matches3, cards4, matches4 + 1, turn1, turn2) - master(allCards, hand, cards1, matches1, cards2, matches2, cards3, matches3, cards4, -(matches4 + 1), turn1, turn2))
  elif allCards - cards1 - cards2 - cards3 - cards4 - hand + matches1 + matches2 + matches3 + matches4 < 0: return 0
  # this is hand!/matches!/(hand-matches)!*(cards)!/(cards-matches)!*(allCards-cards)!/(allCards-cards-hand+matches)!/((allCards)!/(allCards-hand)!)
  else: total = chooseCardFixedOrder(hand - turn1, matches1) * (chooseCard(cards1, cards1 - matches1)) * (chooseCardFixedOrder(hand - matches1 - turn2, matches2)) * (chooseCard(cards2, cards2 - matches2)) * (chooseCardFixedOrder(hand - matches1 - matches2, matches3)) * (chooseCard(cards3, cards3 - matches3)) * (chooseCardFixedOrder(hand - matches1 - matches2 - matches3, matches4)) * (chooseCard(cards4, cards4 - matches4)) * (chooseCard(allCards - cards1 - cards2 - cards3 - cards4, allCards - cards1 - cards2 - cards3 - cards4 - hand + matches1 + matches2 + matches3 + matches4)) / (chooseCard(allCards, allCards - hand))
  x=1 #if we want turn1>1 later, change x=2?
  if turn1 > 1: return "N/A"
  elif turn2 > 1: return "N/A"
  elif (turn1 == 1) and (turn2 == 0): total += chooseCard(hand - x, hand - matches1 - x) / (chooseCard(hand - turn1 + x, hand - turn1 - matches1)) * (chooseCard(matches1 + x, matches1)) * (master(allCards, hand, cards1, matches1 + x, cards2, matches2, cards3, matches3, cards4, matches4, turn1 - x, turn2))
  elif (turn1 == 1) and (turn2 == 1): total += chooseCard(hand - x, hand - matches1 - x) / (chooseCard(hand - turn1 + x, hand - turn1 - matches1)) * (chooseCard(matches1 + x, matches1)) * (master(allCards, hand, cards1, matches1 + x, cards2, matches2, cards3, matches3, cards4, matches4, turn1 - x, turn2)) + chooseCard(hand - x, hand - matches2 - x) / (chooseCard(hand - turn2 + x, hand - turn2 - matches2)) * (chooseCard(matches2 + x, matches2)) * (master(allCards, hand, cards1, matches1, cards2, matches2 + x, cards3, matches3, cards4, matches4, turn1 - x, turn2 - x))
  return total

def master_burn_1(allCards,hand,cards1,matches1):
  # this does not take into account partial burn - the first 7 cards are drawn without burn
  # the difference is just the cards1*cards1!/(cards1-matches+1)! rather than cards1!/(cards1-matches)! due to burn
  return chooseCardFixedOrder(hand, matches1) * cards1*(chooseCard(cards1, cards1 - matches1+1)) * (chooseCard(allCards - cards1, allCards - cards1 - hand + matches1)) / (chooseCard(allCards, allCards - hand))

def master_burn(allCards,hand,cards1):
  # this is to get at least two copies - one to burn and one to play
  # so it's a bit higher than master(allCards,hand,cards1,-2) due to the redraw
  temp = 0
  for i in np.arange(2,cards1+2,1):
    temp += master_burn_1(allCards,hand,cards1,i) - cards1*master_burn_1(allCards,7,1,2)*master(allCards,hand-2,cards1-1,i-2) # this implements partial burn - repeated cards within the first 7 are not included
  return temp

def masterGem(allCards, hand, cards1, matches1, color1, gems1, cards2, matches2, color2, gems2, turn1, turn2):
  if color1 < cards1: return 0
  elif color2 < cards2: return 0
  else: total = 0
  for x in range(cards1 - matches1 + 1):
    for y in range(cards2-matches2+1):
      newgems1 = gems1 - x
      newgems2 = gems2 - y
      newcolor1 = color1
      newcolor2 = color2
      if newgems1 <= 0: newcolor1 = cards1
      if newgems2 <= 0: newcolor2 = cards2
      if newgems1 < 0: newgems1 = 0
      if newgems2 < 0: newgems2 = 0
      total += master(allCards, hand, cards1, matches1 + x, newcolor1 - cards1, -newgems1, cards2, matches2 + y, newcolor2 - cards2, -newgems2, turn1, turn2)
  return total

def multigem1(x,y):
  if len(list(Counter(x).keys())) == 2:
    if list(Counter(x).keys())[0] == color2[y]: return color1[list(Counter(x).keys())[1]]
    else: return color1[list(Counter(x).keys())[0]]
  elif len(list(Counter(x).keys())) == 1: return 0
  else:
    return None
def multigem2(x,y):
  if len(list(Counter(x).keys())) == 2:
    if list(Counter(x).keys())[0] == color2[y]: return list(Counter(x).values())[1]
    else: return list(Counter(x).values())[0]
  elif len(list(Counter(x).keys())) == 1: return 0
  else:
    return None

def subtract_gem(gem,color):
  if (gem is not None) and (len(gem) != 1):
    temp = ''
    for x in gem:
      if x == color:
        color = ''
      else:
        temp += x
    return temp
  else:
    return gem

# if st.sidebar.button("Add to deck"):
#     if card_choice in series.keys():
#         series[card_choice] += 1
#     else:
#         series[card_choice] =  1

# keys = list(series.keys())
#
# new_keys = st.sidebar.multiselect('All cards',keys,keys)
#
# for key in keys:
#     if key not in new_keys:
#         series.drop(labels=key,inplace=True)
