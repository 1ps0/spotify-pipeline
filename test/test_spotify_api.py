# -*- coding: utf-8 -*-
#!/usr/bin/env python

import unittest

from hn_proc_test import HNDataObj, Story, Comment

class TestHNDataObj(unittest.TestCase):

    def setUp(self):
        pass

    def testDataIntegrity(self):
        s = Story('18742855')
        self.assertTrue(s.id == '18742855', "Story obj didn't save the id")

    def testDataLoad(self):
        s = Story('18742855')
        data = s.load()
        self.assertTrue(len(data) > 0, "Didnt load data")
        self.assertTrue(type(data) == type({}), "Wrong data type")

    def testParseComment(self):
        pass
        s = Story('18742855').load()
        blob = s['comments'][0]
        obj = HNDataObj(blob)
        body = obj.load()
        print(len(body))
        self.assertTrue(len(body) == 4, f"Error: wrong line count {len(body)}:\n{str(body)}")

    def testDevEdge(self):
        s = Story('18742855').load()
        blob = s['comments'][0]
        obj = HNDataObj(blob)
        body = obj.load()
        print(f"line count {len(body)}:\n{str(body)}")
        obj.runSentiment()
        #self.assertTrue(len(body) == 4, f"Error: wrong line count {len(body)}:\n{str(body)}")




if __name__ == '__main__':
    unittest.main()

