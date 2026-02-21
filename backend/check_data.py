import yaml
from pymilvus import MilvusClient


def main():
    try:
        with open("config.yaml", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        host = config["milvus"]["host"]
        port = config["milvus"]["port"]
        collection = config["milvus"]["collection"]

        client = MilvusClient(uri=f"http://{host}:{port}")

        if client.has_collection(collection):
            stats = client.get_collection_stats(collection)
            print(f"COLLECTION: {collection}")
            print(f"ROW_COUNT: {stats.get('row_count', 0)}")
        else:
            print(f"COLLECTION {collection} NOT FOUND")

    except Exception as e:
        print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    main()
