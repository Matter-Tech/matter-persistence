import gzip
import pickle
from typing import Any


def compress_pickle_data(data: Any) -> bytes:
    pickled_data = pickle.dumps(data)  # Serialize the data into bytes using pickle
    compressed_data = gzip.compress(pickled_data)  # Compress the pickled data using gzip
    return compressed_data


def decompress_pickle_data(compressed_data: bytes) -> Any:
    decompressed_data = gzip.decompress(compressed_data)  # Decompress the compressed data using gzip
    data = pickle.loads(decompressed_data)  # Deserialize the data back into Python objects using pickle
    return data
