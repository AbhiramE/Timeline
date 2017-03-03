import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn.cluster import DBSCAN
from datetime import date, datetime, timedelta
import requests


# Get centroids of cluster
def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def get_geo_address(top_10):
    top_10_addresses = []
    for latlong in top_10:
        payload = {'latlng': str(latlong[0]) + ',' + str(latlong[1])}
        r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload)
        result = r.json()
        top_10_addresses.append(result['results'][0]['formatted_address'])

    return top_10_addresses


def plot_graph(new_df):
    # Plot all cluster points
    fig, ax = plt.subplots(figsize=[10, 6])
    df_scatter = ax.scatter(new_df['Longitude'], new_df['Latitude'], c='k', alpha=0.9, s=3)
    ax.set_title('Clusters')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.savefig('Data.png')


def cluster(df, file_name):
    # Cluster the data
    coords = df.as_matrix()
    kms_per_radian = 6371.0088
    epsilon = 1 / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    print('Number of clusters: {:,}'.format(num_clusters))

    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    centermost_points = clusters.map(get_centermost_point)

    # Get latitude and longitudes of clusters
    lats, lons = zip(*centermost_points)
    new_df = pd.DataFrame({'Longitude': lons, 'Latitude': lats})
    new_df.to_csv(file_name)

    # Retrieve actual values from df and drop duplicates
    new_df.drop_duplicates()
    return new_df


def first_day_of_month(d):
    return date(d.year, d.month, 1)


def first_day_of_last_month(d):
    if d.month == 1:
        return date(d.year - 1, 12, 1)
    else:
        return date(d.year, d.month - 1, 1)


def temp_days(d, days):
    return datetime(d.year, d.month, 1) - timedelta(days)


# Get the list of top 10 places from last month
df = pd.read_csv('location_history.csv')
df = df.loc[df['Time'].astype('datetime64[ns]') > temp_days(date.today(), 150)]
df.drop(df.columns[0], axis=1, inplace=True)
file_name = 'old_clusters.csv'
new_df = cluster(df, file_name)
top_10 = new_df.as_matrix()[range(1, 11)]
top_10_addresses_old = get_geo_address(top_10)

# Get the list of top 10 places from last month
df = pd.read_csv('location_history.csv')
df = df.loc[df['Time'].astype('datetime64[ns]') > temp_days(date.today(), 80)]
df.drop(df.columns[0], axis=1, inplace=True)
file_name = 'new_clusters.csv'
new_df = cluster(df, file_name)
top_10 = new_df.as_matrix()[range(1, 11)]
top_10_addresses_new = get_geo_address(top_10)

# Find all new places
new_places = set(top_10_addresses_new) - set(top_10_addresses_old)

print(top_10_addresses_new)
print(top_10_addresses_old)
print("\n")

# Conclusions
print("Good you visited {} new places", new_places)

if len(new_places) < 5:
    print(" You can visit these places")
