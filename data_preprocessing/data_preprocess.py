import os
import networkx as nx
import osmnx as ox
import pandas as pd
from tqdm import tqdm
from map_preprocessing.preprocess import find_hexagon

tqdm.pandas()

def load_csv_and_drop_duplication(file_path):
    df = pd.read_csv(file_path, header=None)
    df.columns = ["order_id", "order_start_time", "order_end_time", "order_lng", "order_lat", "dest_lng", "dest_lat"]
    df = df.drop_duplicates()
    base_file_path, file_name = os.path.split(file_path)
    new_file_path = os.path.join(base_file_path, f"{file_name.split('.')[0]}_final.csv")

    drop_indices = df.sample(frac=0.9).index
    df = df.drop(drop_indices)

    df['origin_idx'] = df.progress_apply(lambda row: find_hexagon(row['order_lat'], row['order_lng'], 10), axis=1)
    df['dest_idx'] = df.progress_apply(lambda row: find_hexagon(row['dest_lat'], row['dest_lng'], 10), axis=1)

    G = ox.load_graphml("../data/maps/chengdu.graphml")

    def calculate_itinerary(row):
        start_lat, start_lng = row['order_lat'], row['order_lng']
        end_lat, end_lng = row['dest_lat'], row['dest_lng']
        try:
            start_node = ox.distance.nearest_nodes(G, start_lng, start_lat)
            end_node = ox.distance.nearest_nodes(G, end_lng, end_lat)

            route = nx.shortest_path(G, start_node, end_node, weight="length")
            route_gdf = ox.routing.route_to_gdf(G, route)
            edges = list(route_gdf['length'])
            return pd.Series([route, edges])
        except (nx.NetworkXNoPath, nx.NodeNotFound, Exception) as e:
            print(f"Error processing row {row['order_id']}: {e}")
            return pd.Series([None, None])

    # 计算每一行的数据并更新进度条
    df[['itinerary_node_list', 'itinerary_segment_dis_list']] = df.progress_apply(
        lambda row: calculate_itinerary(row), axis=1
    )

    # 删除包含错误计算结果的行
    df = df.dropna(subset=['itinerary_node_list', 'itinerary_segment_dis_list'])

    # 保存结果到新的 CSV 文件
    df.to_csv(new_file_path, index=False)
    print(f"数据已保存到 {new_file_path}")

if __name__ == '__main__':
    path1 = "../data/data20161101/order_20161101_final.csv"
    if not os.path.exists(path1):
        load_csv_and_drop_duplication("../data/data20161101/order_20161101.csv")
    path2 = "../data/data20161102/order_20161102_final.csv"
    if not os.path.exists(path2):
        load_csv_and_drop_duplication("../data/data20161102/order_20161102.csv")
