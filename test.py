# -*- conding: utf-8 -*-
import unittest

from lxml import etree
from xmlunittest import XmlTestCase


class TestXmlTestCase(unittest.TestCase):
    """Test the XmlTestCase.

    The issue of testing TestCase can be tough as only error case can be
    tested. So it is important to know what you really want to test.

    XmlTestCase is developped using TDD: tests are written before functionnal
    code. For each successful case a related error case is tested too.

    """
    def test_assertXmlDocument(self):
        """Asserts assertXmlDocument raises when data is invalid.

        At this time, assertXmlDocument only test XML data is a valid XML
        document, but it can be a fragment of XML only. This does not test
        the XML declaration nor any doctype declaration.

        """
        test_case = XmlTestCase(methodName='assertXmlDocument')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root/>"""

        root = test_case.assertXmlDocument(data)
        self.assertIsInstance(root, etree._Element)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlDocument('not an XML document')

    # -------------------------------------------------------------------------

    def test_assertXmlNamespace(self):
        """Asserts assertXmlNamespace raises namespace is invalid.

        When an element declare an xml namespace, this element and each child
        reference this namespace, and thus it can be tested.

        """
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
        """Asserts assertXmlHasAttribute raises when attribute does not exist.

        Method assertXmlHasAttribute can test if attribute exists or not, and
        more - see other tests for that.

        """
        test_case = XmlTestCase(methodName='assertXmlHasAttribute')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root att="value" />"""

        root = test_case.assertXmlDocument(data)
        test_case.assertXmlHasAttribute(root, 'att')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlHasAttribute(root, 'no_att')

    def test_assertXmlHasAttribute_value(self):
        """Asserts assertXmlHasAttribute raises when value is invalid.

        With optional argument `expected_value`, assertXmlHasAttribute can
        assert if attribute's value is the given expected value.

        """
        test_case = XmlTestCase(methodName='assertXmlHasAttribute')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root att="value" />"""

        root = test_case.assertXmlDocument(data)
        test_case.assertXmlHasAttribute(root, 'att', expected_value='value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlHasAttribute(root, 'att',
                                            expected_value='invalid')

    def test_assertXmlHasAttribute_values(self):
        """Asserts assertXmlHasAttribute raises when value is invalid.

        With optional argument `expected_values`, assertXmlHasAttribute can
        assert if attribute's value is one of the given expected values.

        """
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
        """Asserts assertXmlNode raises when node is invalid.

        Method assertXmlNode raise if node does not exists (None) or is not
        an XML Element.

        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)
        test_case.assertXmlNode(root)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(None)

        # Text data is not handled
        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode('<root>text_value</root>')

    def test_assertXmlNode_tag(self):
        """Asserts assertXmlNode raises when node is invalid.

        Method assertXmlNode raise if node has not the expected tag name.

        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root, tag='root')
        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot')

    def test_assertXmlNode_text(self):
        """Asserts assertXmlNode raises when node is invalid.

        Method assertXmlNode raise if node has not the expected text value.

        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root, text='text_value')
        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, text='invalid')

    def test_assertXmlNode_tag_text(self):
        """Asserts assertXmlNode raises when node is invalid.

        Method assertXmlNode raise if node has not the expected tag name
        or the expected text value.

        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root, tag='root', text='text_value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='root', text='invalid')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot', text='text_value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot', text='invalid')

    # -------------------------------------------------------------------------

    def test_assertXpathExistForEachNodes(self):
        """Asserts assertXpathExistForEachNodes raises when validation failed.

        Method assertXpathExistForEachNodes raises when the list of XPath
        expressions returns None for any node of the given nodes.

        """
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
        """Asserts assertXpathUniqueForEachNodes raises when validation failed.

        Method assertXpathUniqueForEachNodes raises when one of XPath
        expressions returns does not returns one result and exactly one result.

        """
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
