# Analyze the data and calculate the transition probability matrix for the Markov-Chain
# Implement a Markov-Chain based data generator

import pandas as pd
import matplotlib.pyplot as plt
import pygraphviz as pgv
import numpy as np
import time

def probs_out_of_counts(array_counts):
    """
    function that takes an array-like object (e.g. a list) with counts and calculates
    the corresponding probabilities
    """

    sum_count = array_counts.sum()
    factor = 100/sum_count
    array_probs = []
    for i in array_counts:
        array_probs.append(i*factor)
    return array_probs


days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
data_days = {}

for i, j in enumerate(days):
    data_days[days[i]] = pd.read_csv(f"supermarket_data/{j}.csv", sep=";", index_col="timestamp")
    # change customer_no to format monday_1, etc.
    new_list = []
    for z in data_days[days[i]]["customer_no"].values:
        new_list.append(str(z) + "_" + j)
    data_days[days[i]]["customer_no"] = new_list

# turn indexes into datetime
for data in data_days.values():
    data.index = pd.to_datetime(data.index)


data_week = pd.concat(data_days)
data_week = data_week.reset_index(0, drop=True) # drops one part of the multi_index (weekdays)
data_week

# 0) how many customer are there on each day, counting them in a unique manner?
sum = 0
for i in days:
    sum = sum + len(data_days[i]["customer_no"].unique())
    print(i, len(data_days[i]["customer_no"].unique()))

# and total:
print(sum)
print(len(data_week["customer_no"].unique()))




# 1) total number of customers in each section
# --> there are customers that are counted but did not go to checkout

for i in days:
    print(i, data_days[i].groupby("location").count())
    print()

# 2) Calculate the total number of customers in each section over time

# customers in the market per minute (NOT included the fact, that customers stay longer in one section than 1 minute!):
customers_per_minute = data_days["monday"].groupby(data_days["monday"].index).count()["location"]
customers_per_minute.head(15)
customers_per_minute.plot()

# customers in the market per hour:
data_days["monday"].groupby(data_days["monday"].index.hour).count()["location"]

# route of x specific customers:
for i in range(1, 2):
    print(data_days["monday"][data_days["monday"]["customer_no"]== f"{i}_monday"])
    time.sleep(1)


# how many customers are in which section at what time? (given a day)

data_days["monday"].groupby([data_days["monday"].index.hour, data_days["monday"].index.minute, data_days["monday"].location]).count().head(40)

# Display the number of customers at checkout over time
#per day + hour
data_week[data_week["location"]=="checkout"].groupby([data_week[data_week["location"]=="checkout"]\
            .index.weekday, data_week[data_week["location"]=="checkout"].index.hour]).count()["location"]

# per day + hour + minute
amount_at_checkout = data_week[data_week["location"]=="checkout"].groupby(data_week[data_week["location"]=="checkout"].index).count()["location"]
amount_at_checkout


# Calculate the time each customer spent in the market

unique_customers = data_week["customer_no"].unique()
unique_customers

#dic_time_in_supermarket = {}

# takes long! see file...
# for i, customer in enumerate(unique_customers):
#     first_appear = data_week[data_week["customer_no"]==unique_customers[i]].iloc[0].name
#     customer_checkout = data_week[data_week["customer_no"]==unique_customers[i]][data_week[data_week["customer_no"]==unique_customers[i]]["location"]=="checkout"].index[0]
#     time_in_supermarket = customer_checkout - first_appear
#     dic_time_in_supermarket[customer] = time_in_supermarket
#
# for i in range(len(unique_customers)):
#     print(i, data_week[data_week["customer_no"]==unique_customers[i]][data_week[data_week["customer_no"]==unique_customers[i]]["location"]=="checkout"].index)



# CUSTOMERS WITHOUT CHECKOUT: 7428, 7430, 7434, 7437
unique_customers[7428]
unique_customers[7430]

data_week[data_week["customer_no"]== "1496_friday"]


#dic_time_in_supermarket["1_monday"][0]

# series_dic = pd.Series(dic_time_in_supermarket)
# series_dic
# series_dic.to_csv("dic_time_in_supermarket.csv")



# Calculate the total number of customers present in the supermarket over time.

data_week.groupby(data_week.index).count()["location"]

# Our business managers think that the first section customers visit follows a different pattern than the following ones.
# Plot the distribution of customers of their first visited section versus following sections
# (treat all sections visited after the first as “following”).


data_week["first_visit_in_section"] = ~data_week.duplicated(subset=["location", "customer_no"])
data_week.head(15)

# transition propabilities:

data_week["next_location_customer"] = data_week.groupby("customer_no")["location"].shift(-1)

P2 = pd.crosstab(data_week['location'], data_week['next_location_customer'], normalize=0)
P2

states = ["checkout", "dairy", "drinks", "fruit", "spices"]

new_df = pd.DataFrame({"checkout":[1, 0, 0, 0, 0]}, index=states)
new_df.T


P2 = P2.append(new_df.T)

P2.to_csv("probabilities.csv")
states
G = pgv.AGraph(directed=True)
for state_from in states:
    for state_to in states:
        G.add_edge(state_from, state_to, label=np.round(P2.loc[state_from, state_to],2))

G.draw('transition.png', prog='dot')

# How long is a business day?

data_days["monday"].index[0]

duration_business_day = data_days["monday"].index[-1] - data_days["monday"].index[0]

duration_business_day

# Which section do customers visit first after entering the supermarket?

data_week["just_entered"] = ~data_week.duplicated(subset=["customer_no"])

count_entry = data_week.groupby("just_entered").get_group(True)["location"].value_counts()

count_entry
count_entry.sum()
100/7445
1143 * 100/7445



probs_entry = probs_out_of_counts(count_entry)
probs_entry.append(0.0)
probs_entry
probs_entry_points = ["fruit", "dairy", "spices", "drinks", "checkout"]
probs_entry = pd.DataFrame(probs_entry, index=probs_entry_points, columns=["probabilities"])
probs_entry.to_csv("probabilities_entry.csv")


# REAL: 900 minuten, 1500 customers --> alle 35 Sekunden betritt ein Customer den Laden
