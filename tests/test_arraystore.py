# test_arraystore.py

import os
import sys
import sqlite3
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from jsonstore.arraystore.table import (
    create_array_table,
    insert_array,
    insert_array_auto_hash,
    insert_arrays_auto_hash,
    retrieve_array,
    retrieve_all_arrays,
)
from jsonstore import canonical_json
import hashlib


def test_method1_storage():
    """Test storing and retrieving array via Method 1."""
    test_array = [42, 3.14, None, True, False, "hello", "true", "false", "null", "", 0, -0, 1, -1, "0", "1"]
    canonical_json_sha1 = "testhash"
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    insert_array(conn, canonical_json_sha1, test_array, table_name="arraystore")
    result = retrieve_array(conn, canonical_json_sha1, table_name="arraystore")

    assert result == test_array, (
        f"Restored array does not match original.\n"
        f"Original: {test_array}\nRestored: {result}"
    )
    assert json.dumps(result) == json.dumps(test_array), (
        f"JSON representation does not match.\n"
        f"Original: {json.dumps(test_array)}\nRestored: {json.dumps(result)}"
    )

    print("All tests passed. Array restored with exact type and value match.")
    conn.close()


def test_method1_nested_array():
    """Test storing and retrieving nested arrays via Method 1."""
    nested_array = [[1, 2], ["a", True], [], [None, [3.14]]]
    canonical_json_sha1 = "nested_test"
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    insert_array(conn, canonical_json_sha1, nested_array, table_name="arraystore")
    result = retrieve_array(conn, canonical_json_sha1, table_name="arraystore")

    assert result == nested_array, (
        f"Restored nested array does not match original.\n"
        f"Original: {nested_array}\nRestored: {result}"
    )
    assert json.dumps(result) == json.dumps(nested_array), (
        f"JSON representation of nested array does not match.\n"
        f"Original: {json.dumps(nested_array)}\nRestored: {json.dumps(result)}"
    )

    print("Nested array test passed. Structure and types preserved.")
    conn.close()


def test_method1_object_array():
    """Test storing and retrieving array with object elements via Method 1."""
    object_array = [
        {"a": 1, "b": [2, False]},
        {"nested": {"x": True, "y": None}}
    ]
    canonical_json_sha1 = "object_test"
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    insert_array(conn, canonical_json_sha1, object_array, table_name="arraystore")
    result = retrieve_array(conn, canonical_json_sha1, table_name="arraystore")

    assert result == object_array, (
        f"Restored object array does not match original.\n"
        f"Original: {object_array}\nRestored: {result}"
    )
    assert json.dumps(result) == json.dumps(object_array), (
        f"JSON representation of object array does not match.\n"
        f"Original: {json.dumps(object_array)}\nRestored: {json.dumps(result)}"
    )

    print("Object array test passed. Objects and nested structures preserved.")
    conn.close()


def test_custom_table_name():
    """Test using a custom table name for storage and retrieval."""
    custom_table = "custom_elements"
    test_array = [1, 2, 3]
    canonical_json_sha1 = "custom_table_test"

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name=custom_table)
    insert_array(conn, canonical_json_sha1, test_array, table_name=custom_table)
    result = retrieve_array(conn, canonical_json_sha1, table_name=custom_table)

    assert result == test_array
    conn.close()


def test_insert_array_auto_hash():
    """Ensure insert_array_auto_hash computes SHA1 and stores array."""
    arr = [1, {"b": True}, [2, 3]]
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    computed_hash = insert_array_auto_hash(conn, arr, table_name="arraystore")
    result = retrieve_array(conn, computed_hash, table_name="arraystore")

    expected_hash = hashlib.sha1(canonical_json(arr).encode("utf-8")).hexdigest()

    assert computed_hash == expected_hash
    assert result == arr
    conn.close()


def test_element_json_canonical():
    """Ensure each element is stored using canonical JSON."""
    data = [0, 1.0, -0.0, {"b": [2, False]}, [1, 2], None]
    cid = "canon_test"
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    insert_array(conn, cid, data, table_name="arraystore")

    cur = conn.cursor()
    cur.execute(
        "SELECT element_index, element_json, element_json_sha1 FROM arraystore WHERE canonical_json_sha1 = ? ORDER BY element_index",
        (cid,),
    )
    rows = cur.fetchall()

    for idx, json_val, sha1_val in rows:
        canon = canonical_json(data[idx])
        expected_sha1 = hashlib.sha1(canon.encode("utf-8")).hexdigest()
        assert json_val == canon
        assert sha1_val == expected_sha1
    conn.close()


def test_insert_arrays_auto_hash():
    """Insert multiple arrays in a single call."""
    arrays = [[1, 2], [True, False, None]]
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    hashes = insert_arrays_auto_hash(conn, arrays, table_name="arraystore")

    assert len(hashes) == len(arrays)
    for arr, cid in zip(arrays, hashes):
        restored = retrieve_array(conn, cid, table_name="arraystore")
        expected = hashlib.sha1(canonical_json(arr).encode("utf-8")).hexdigest()
        assert cid == expected
        assert restored == arr
    conn.close()


def test_retrieve_all_arrays():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    create_array_table(conn, table_name="arraystore")
    arrays = [[i] for i in range(3)]
    for arr in arrays:
        insert_array_auto_hash(conn, arr, table_name="arraystore")

    records = retrieve_all_arrays(conn, table_name="arraystore")
    records_sorted = sorted(records, key=lambda x: x[0])

    assert records_sorted == arrays
    conn.close()


if __name__ == "__main__":
    test_method1_storage()
    test_method1_nested_array()
    test_method1_object_array()
