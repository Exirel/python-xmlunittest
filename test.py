# -*- conding: utf-8 -*-
import unittest

from lxml import etree
from xmlunittest import XmlTestCase


class TestXmlTestCase(unittest.TestCase):
    """

        Basic test on an XML document.

        This tests how the XML assertions work.

        data = '''<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns:prefix="uri">
            <child att="1" prefix:nsAtt="x"/>
            <child att="1" prefix:nsAtt="y"/>
            <child att="1" prefix:nsAtt="z"/>
        </root>
        '''

        doc = self.assertXmlDocument(data)
        self.assertXmlNamespace(doc, 'prefix', 'uri')

        for node in doc.xpath('//child'):
            self.assertXmlAttribute(node, 'att', expected_value='1')
            self.assertXmlAttribute(node, 'prefix:nsAtt',
                                    expected_values=['x', 'y', 'z'])

    """

    # -------------------------------------------------------------------------

    def test_assertXmlDocument(self):
        test_case = XmlTestCase(methodName='assertXmlDocument')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root/>"""

        root = test_case.assertXmlDocument(data)
        self.assertIsInstance(root, etree._Element)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlDocument('not an XML document')

    # -------------------------------------------------------------------------

    def test_assertXmlNamespace(self):
        test_case = XmlTestCase(methodName='assertXmlNamespace')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns:ns="uri"/>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNamespace(root, 'ns', 'uri')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNamespace(root, 'wrong_ns', 'uri')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNamespace(root, 'ns', 'wrong_uri')

    # -------------------------------------------------------------------------

    def test_assertXmlHasAttribute(self):
        test_case = XmlTestCase(methodName='assertXmlHasAttribute')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root att="value" />"""

        root = test_case.assertXmlDocument(data)
        test_case.assertXmlHasAttribute(root, 'att')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlHasAttribute(root, 'no_att')

    def test_assertXmlHasAttribute_value(self):
        test_case = XmlTestCase(methodName='assertXmlHasAttribute')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root att="value" />"""

        root = test_case.assertXmlDocument(data)
        test_case.assertXmlHasAttribute(root, 'att', expected_value='value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlHasAttribute(root, 'att',
                                            expected_value='invalid')

    def test_assertXmlHasAttribute_values(self):
        test_case = XmlTestCase(methodName='assertXmlHasAttribute')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <child att="1"/>
            <child att="3"/>
        </root>"""

        root = test_case.assertXmlDocument(data)

        for node in root.xpath('//child'):
            test_case.assertXmlHasAttribute(node, 'att',
                                            expected_values=['1', '3'])

            with self.assertRaises(test_case.failureException):
                test_case.assertXmlHasAttribute(node, 'att',
                                                expected_values=['2', '4'])

    # -------------------------------------------------------------------------

    def test_assertXmlNode(self):
        """
        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root)
        test_case.assertXmlNode(root, tag='root')
        test_case.assertXmlNode(root, text='text_value')
        test_case.assertXmlNode(root, tag='root', text='text_value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot', text='text_value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, text='invalid')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='root', text='invalid')

    # -------------------------------------------------------------------------

    def test_assertXpathExistForEachNodes(self):
        test_case = XmlTestCase(methodName='assertXpathExistForEachNodes')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <child att="1">
                <sub subAtt="input"/>
                <sub subAtt="none"/>
                <sub/>
            </child>
            <child att="2">
                <sub subAtt="input"/>
            </child>
        </root>"""

        root = test_case.assertXmlDocument(data)
        required_for_each = ['@att',
                             './sub',
                             './sub[@subAtt="input"]']
        test_case.assertXpathExistForEachNodes(list(root), required_for_each)

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathExistForEachNodes(list(root), ['@invalidAtt'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathExistForEachNodes(list(root),
                                                 ['./invalidChild'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathExistForEachNodes(list(root),
                                                 ['./sub[@subAtt="none"]'])

    # -------------------------------------------------------------------------

    def test_assertXpathUniqueForEachNodes(self):
        test_case = XmlTestCase(methodName='assertXpathUniqueForEachNodes')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <child att="1">
                <sub subAtt="unique"/>
                <sub subAtt="notUnique"/>
                <sub subAtt="notUnique"/>
                <uniqueSub/>
                <onlyHere/>
            </child>
            <child att="2">
                <sub subAtt="unique"/>
                <uniqueSub/>
            </child>
        </root>"""

        root = test_case.assertXmlDocument(data)
        unique_for_each = ['./uniqueSub',
                           './sub[@subAtt="unique"]']
        test_case.assertXpathUniqueForEachNodes(list(root), unique_for_each)

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathUniqueForEachNodes(list(root),
                                                    ['./invalidChild'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathUniqueForEachNodes(list(root),
                                                ['./sub[@subAtt="notUnique"]'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathUniqueForEachNodes(list(root),
                                                    ['./onlyHere'])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_assertXmlDocument']
    unittest.main()
