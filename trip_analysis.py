import pandas as pd
import gdown
from itertools import combinations
from collections import Counter

# Download CSV files from Google Drive
transaction_url = 'https://drive.google.com/uc?id=1XLEAD8d3llXuWCfNWOVk-eMAq8VCahOT'
user_url = 'https://drive.google.com/uc?id=12AKPVGVN8QGdMQWt103JQlw4IXItW28c'

gdown.download(transaction_url, 'transaction.csv', quiet=False)
gdown.download(user_url, 'user.csv', quiet=False)

users = pd.read_csv('user.csv')
transactions = pd.read_csv('transaction.csv')

# Merge and sort data
merged = pd.merge(transactions, users, on='user_id', how='left')
merged = merged.sort_values(by=['user_id', 'date', 'hour'])

# Function to identify trips
def find_trips(user_data):
    trips = []
    current_trip = []
    hometown = user_data['hometown'].iloc[0]
    
    for index, row in user_data.iterrows():
        if row['province'] == hometown:
            if current_trip:
                trip_info = {
                    'trip_id': len(trips) + 1,
                    'user_id': row['user_id'],
                    'start_date': current_trip[0]['date'],
                    'end_date': current_trip[-1]['date'],
                    'province_list': ' '.join(sorted(set([x['province'] for x in current_trip if x['province'] != hometown])))
                }
                trips.append(trip_info)
                current_trip = []
        else:
            current_trip.append(row)
    
    if current_trip:
        trip_info = {
            'trip_id': len(trips) + 1,
            'user_id': row['user_id'],
            'start_date': current_trip[0]['date'],
            'end_date': current_trip[-1]['date'],
            'province_list': ' '.join(sorted(set([x['province'] for x in current_trip if x['province'] != hometown])))
        }
        trips.append(trip_info)
    
    return trips

# Apply trip identification function to each user
trip_list = []
for user_id, user_data in merged.groupby('user_id'):
    trip_list.extend(find_trips(user_data))

# Convert trip list to DataFrame and save as CSV
trips_df = pd.DataFrame(trip_list)
trips_df.to_csv('trips.csv', index=False)

#1 What is the total number of trips?
print(f"Total number of trips: {len(trips_df)}")

#2 How many provinces are there in the trip with the most number of provinces?
trips_df['num_provinces'] = trips_df['province_list'].apply(lambda x: len(x.split()))
max_provinces = trips_df['num_provinces'].max()
print(f"Maximum number of provinces in a single trip: {max_provinces}")

#3 What are the most common province pairs that people travel to in the same trip?
def find_province_pairs(province_list):
    pairs = list(combinations(sorted(province_list.split()), 2))
    return pairs

pair_list = trips_df['province_list'].apply(find_province_pairs).explode().value_counts()
most_common_pairs = pair_list.head(5)
print("Most common province pairs:")
print(most_common_pairs)

print("Trips have been successfully saved to 'trips.csv'.")
