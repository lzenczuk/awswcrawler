import unittest
from awswcrawler.aws.path import split_request_string
from awswcrawler.aws.path import split_path_string
from awswcrawler.aws.path import is_param
from awswcrawler.aws.path import split_query_string
from awswcrawler.aws.path import parse_path_string
from awswcrawler.aws.path import parse_query_string
from awswcrawler.aws.path import parse_request_string


class TestPath(unittest.TestCase):
    def test_splitting_empty_path(self):
        path1 = None
        path2 = ""
        path3 = "  "
        with self.assertRaises(ValueError):
            split_request_string(path1)
        with self.assertRaises(ValueError):
            split_request_string(path2)
        with self.assertRaises(ValueError):
            split_request_string(path3)

    def test_splitting_path_containing_spaces(self):
        path1 = "lkjlk lkjl"
        path2 = "a\tb"
        path3 = "a\r"
        with self.assertRaises(ValueError):
            split_request_string(path1)
        with self.assertRaises(ValueError):
            split_request_string(path2)
        with self.assertRaises(ValueError):
            split_request_string(path3)

    def test_splitting_path_without_query(self):
        path1 = "/test/test"
        self.assertEqual(("test/test", ""), split_request_string(path1))
        path2 = "test/test"
        self.assertEqual(("test/test", ""), split_request_string(path2))
        path3 = "test/test/"
        self.assertEqual(("test/test", ""), split_request_string(path3))
        path4 = "test/test/{test}"
        self.assertEqual(("test/test/{test}", ""), split_request_string(path4))

    def test_splitting_path_only_with_query(self):
        path1 = "?test=test&q={id}"
        self.assertEqual(("", "test=test&q={id}"), split_request_string(path1))
        path2 = "?"
        self.assertEqual(("", ""), split_request_string(path2))

    def test_splitting_path(self):
        path1 = "/test?test=test&q={id}"
        self.assertEqual(("test", "test=test&q={id}"), split_request_string(path1))
        path2 = "test?test=test&q={id}"
        self.assertEqual(("test", "test=test&q={id}"), split_request_string(path2))
        path3 = "test/test?test=test&q={id}"
        self.assertEqual(("test/test", "test=test&q={id}"), split_request_string(path3))
        path3 = "test/test?"
        self.assertEqual(("test/test", ""), split_request_string(path3))

    def test_is_param(self):
        p0 = ""
        with self.assertRaises(ValueError):
            is_param(p0)
        p01 = " "
        with self.assertRaises(ValueError):
            is_param(p01)
        p1 = "test"
        self.assertFalse(is_param(p1))
        p2 = "{test}"
        self.assertTrue(is_param(p2))
        p3 = "{test"
        with self.assertRaises(ValueError):
            is_param(p3)
        p4 = "test}"
        with self.assertRaises(ValueError):
            is_param(p4)

    def test_split_path(self):
        p1 = ""
        self.assertSequenceEqual([], split_path_string(p1))
        p11 = "/"
        self.assertSequenceEqual([], split_path_string(p11))
        p2 = "test"
        self.assertSequenceEqual(["test"], split_path_string(p2))
        p3 = "/test"
        self.assertSequenceEqual(["test"], split_path_string(p3))
        p4 = "test1/test2"
        self.assertSequenceEqual(["test1", "test2"], split_path_string(p4))
        p5 = "test1/test2/"
        self.assertSequenceEqual(["test1", "test2"], split_path_string(p5))
        p6 = "/test1/test2"
        self.assertSequenceEqual(["test1", "test2"], split_path_string(p6))
        p7 = "/test1/test2/"
        self.assertSequenceEqual(["test1", "test2"], split_path_string(p7))
        p8 = "test1/test2/test3"
        self.assertSequenceEqual(["test1", "test2", "test3"], split_path_string(p8))
        p9 = "test1/test2//test3"
        with self.assertRaises(ValueError):
            split_path_string(p9)

    def test_split_query(self):
        q1 = ""
        self.assertDictEqual({}, split_query_string(q1))
        q2 = "&"
        with self.assertRaises(ValueError):
            split_query_string(q2)
        q3 = "test"
        with self.assertRaises(ValueError):
            split_query_string(q3)
        q4 = "test="
        with self.assertRaises(ValueError):
            split_query_string(q4)
        q5 = "test1=test2"
        with self.assertRaises(ValueError):
            split_query_string(q5)
        q6 = "test1={test2}"
        self.assertDictEqual({"test1": "{test2}"}, split_query_string(q6))
        q7 = "test1={test2}&test3=test4"
        with self.assertRaises(ValueError):
            split_query_string(q7)
        q8 = "test1={test2}&test3={test4}"
        self.assertDictEqual({"test1": "{test2}", "test3": "{test4}"}, split_query_string(q8))

    def test_parse_path_string(self):
        p1 = "/"
        rp1 = parse_path_string(p1)
        self.assertEquals(0, len(rp1))

        p2 = "/documents"
        rp2 = parse_path_string(p2)
        self.assertEquals(1, len(rp2))

        self.assertEquals("PATH", rp2[0]['type'])
        self.assertEquals("documents", rp2[0]['request_string'])
        self.assertIsNone(rp2[0]['param_name'])
        self.assertTrue(rp2[0]['required'])

        p3 = "/documents/{document_id}"
        rp3 = parse_path_string(p3)
        self.assertEquals(2, len(rp3))

        self.assertEquals("PATH", rp3[0]['type'])
        self.assertEquals("documents", rp3[0]['request_string'])
        self.assertIsNone(rp3[0]['param_name'])
        self.assertTrue(rp3[0]['required'])

        self.assertEquals("PATH_PARAM", rp3[1]['type'])
        self.assertEquals("{document_id}", rp3[1]['request_string'])
        self.assertEquals("document_id", rp3[1]['param_name'])
        self.assertTrue(rp3[1]['required'])

        p4 = "/documents/{document_id}/pages"
        rp4 = parse_path_string(p4)
        self.assertEquals(3, len(rp4))

        self.assertEquals("PATH", rp4[0]['type'])
        self.assertEquals("documents", rp4[0]['request_string'])
        self.assertIsNone(rp4[0]['param_name'])
        self.assertTrue(rp4[0]['required'])

        self.assertEquals("PATH_PARAM", rp4[1]['type'])
        self.assertEquals("{document_id}", rp4[1]['request_string'])
        self.assertEquals("document_id", rp4[1]['param_name'])
        self.assertTrue(rp4[1]['required'])

        self.assertEquals("PATH", rp4[2]['type'])
        self.assertEquals("pages", rp4[2]['request_string'])
        self.assertIsNone(rp4[2]['param_name'])
        self.assertTrue(rp4[2]['required'])

    def test_parse_query_string(self):
        rq1 = parse_query_string("")
        self.assertSequenceEqual([], rq1)

        with self.assertRaises(ValueError):
            parse_query_string("test")

        with self.assertRaises(ValueError):
            parse_query_string("test=")

        with self.assertRaises(ValueError):
            parse_query_string("test1=test2")

        rq2 = parse_query_string("test1={test2}")
        self.assertEquals(1, len(rq2))

        self.assertEquals("QUERY_PARAM", rq2[0]['type'])
        self.assertEquals("test1", rq2[0]['request_string'])
        self.assertEquals("test2", rq2[0]['param_name'])
        self.assertFalse(rq2[0]['required'])

        rq3 = parse_query_string("test1={test2}&test3={test4}")
        self.assertEquals(2, len(rq3))

        self.assertEquals("QUERY_PARAM", rq3[0]['type'])
        self.assertEquals("test1", rq3[0]['request_string'])
        self.assertEquals("test2", rq3[0]['param_name'])
        self.assertFalse(rq3[0]['required'])

        self.assertEquals("QUERY_PARAM", rq3[1]['type'])
        self.assertEquals("test3", rq3[1]['request_string'])
        self.assertEquals("test4", rq3[1]['param_name'])
        self.assertFalse(rq3[1]['required'])

    def test_parse_request_string(self):
        r1 = ""
        with self.assertRaises(ValueError):
            parse_request_string(r1)

        r2 = "/"
        self.assertSequenceEqual([], parse_request_string(r2))

        r3 = "test"
        self.assertSequenceEqual([
            {"request_string": "test", "type": "PATH", "param_name": None, "required": True}
        ], parse_request_string(r3))

        r4 = "test1/test2"
        self.assertSequenceEqual([
            {"request_string": "test1", "type": "PATH", "param_name": None, "required": True},
            {"request_string": "test2", "type": "PATH", "param_name": None, "required": True}
        ], parse_request_string(r4))

        r5 = "/users/{id}/products"
        self.assertSequenceEqual([
            {"request_string": "users", "type": "PATH", "param_name": None, "required": True},
            {"request_string": "{id}", "type": "PATH_PARAM", "param_name": "id", "required": True},
            {"request_string": "products", "type": "PATH", "param_name": None, "required": True}
        ], parse_request_string(r5))

        r6 = "?type={p_type}&per_page={!per_page}"
        self.assertSequenceEqual([
            {"request_string": "per_page", "type": "QUERY_PARAM", "param_name": "per_page", "required": True},
            {"request_string": "type", "type": "QUERY_PARAM", "param_name": "p_type", "required": False},
        ], parse_request_string(r6))

        r6 = "/users/{id}/products?type={p_type}&per_page={!per_page}"
        self.assertSequenceEqual([
            {"request_string": "users", "type": "PATH", "param_name": None, "required": True},
            {"request_string": "{id}", "type": "PATH_PARAM", "param_name": "id", "required": True},
            {"request_string": "products", "type": "PATH", "param_name": None, "required": True},
            {"request_string": "per_page", "type": "QUERY_PARAM", "param_name": "per_page", "required": True},
            {"request_string": "type", "type": "QUERY_PARAM", "param_name": "p_type", "required": False}
        ], parse_request_string(r6))



if __name__ == '__main__':
    unittest.main()
