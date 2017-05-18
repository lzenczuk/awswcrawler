import unittest
import uuid

from awswcrawler.aws.ddb import create_table_with_pk, create_table_with_pk_and_sk, delete_table


class TestDDB(unittest.TestCase):
    def test_single_pk_end_to_end(self):
        delete_table("users")
        user_table = create_table_with_pk("users", "id", "S")

        user_table.insert_item({"id": "user1", "first_name": "Mike", "last_name": "Green", "age": 23})
        user_table.insert_item({"id": "user2", "first_name": "Tom", "last_name": "Black", "age": 8})
        user_table.insert_item({"id": "user3", "first_name": "Alice", "last_name": "Brooks", "age": 45})
        user_table.insert_item({"id": "user4", "first_name": "Martha", "last_name": "Stuart", "age": 55, "phone": "085 123 1234"})

        user_table.insert_items([
            {"id": "user5", "first_name": "Michael", "last_name": "Gray", "age": 72},
            {"id": "user6", "first_name": "Bob", "last_name": "Black", "age": 11},
            {"id": "user7", "first_name": "Martin", "last_name": "Case", "age": 31},
            {"id": "user8", "first_name": "Bart", "last_name": "Simpson", "age": 10, "city": "Springfield"}
        ])

        users = user_table.fetch_items_by_pk("user6")

        self.assertSequenceEqual(users, [{"id": "user6", "first_name": "Bob", "last_name": "Black", "age": 11}])

        delete_table("users")

    def test_pk_with_sk_end_to_end(self):
        delete_table("batches")
        batches_table = create_table_with_pk_and_sk("batches", "batch_id", "S", "download_id", "N")

        batches_table.insert_items([
            {"batch_id": "batch_0", "download_id": 0, "url": "http;//url00"},
            {"batch_id": "batch_0", "download_id": 1, "url": "http;//url01"},
            {"batch_id": "batch_0", "download_id": 2, "url": "http;//url02"},
            {"batch_id": "batch_0", "download_id": 3, "url": "http;//url03"},
            {"batch_id": "batch_1", "download_id": 0, "url": "http;//url10"},
            {"batch_id": "batch_1", "download_id": 1, "url": "http;//url11"},
            {"batch_id": "batch_1", "download_id": 2, "url": "http;//url12"},
            {"batch_id": "batch_4", "download_id": 2, "url": "http;//url42"},
        ])

        batches = batches_table.fetch_items_by_pk("batch_0")

        self.assertEqual(4, len(batches))

        delete_table("batches")

