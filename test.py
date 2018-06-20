# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import os
import unittest

from lxml import etree

from xmlunittest import XmlTestCase

DEFAULT_NS = 'https://www.w3.org/XML'
TEST_NS = 'https://docs.python.org/3.4/library/unittest.html'


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
        data = b"""<root/>"""

        root = test_case.assertXmlDocument(data)
        self.assertIsInstance(root, etree._Element)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlDocument('not an XML document')

    def test_assertXmlDocument_with_encoding(self):
        """Asserts assertXmlDocument works with utf-8 and other encoding."""
        test_case = XmlTestCase(methodName='assertXmlDocument')

        # utf-8
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root>àéèçßù</root>"""
        root = test_case.assertXmlDocument(data.encode('utf-8'))
        self.assertIsInstance(root, etree._Element)

        # Check we can raise AssertionError with this document to check
        # formatting of error messages
        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['//something'])

        # iso-8859-15
        data = """<?xml version="1.0" encoding="iso-8859-15" ?>
        <root>àéèçßù</root>"""
        root = test_case.assertXmlDocument(data.encode('iso-8859-15'))
        self.assertIsInstance(root, etree._Element)

        # Check we can raise AssertionError with this document to check
        # formatting of error messages
        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['//something'])

    # -------------------------------------------------------------------------

    def test_assertXmlPartial(self):
        """Asserts assertXmlPartial raises when data is invalid.

        Method assertXmlPartial must be able to take a partial XML formated
        string and returns a valid XML document, or raise an error.

        """
        test_case = XmlTestCase(methodName='assertXmlPartial')
        data = b"""<partial>1</partial>
        <partial>2</partial>"""

        root = test_case.assertXmlPartial(data)
        self.assertIsInstance(root, etree._Element)

        self.assertEqual(root.tag, test_case.default_partial_tag)
        self.assertEqual(len(root), 2)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlPartial(b'<invalidChar>&</invalidChar>')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlPartial(b'not even a partial XML document')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlPartial(b'<missingEndTag>')

    def test_assertXmlPartial_name(self):
        """Asserts assertXmlPartial raises when data is invalid.

        Method assertXmlPartial accept a `root_tag` parameter to tell
        method the root element's tag name.

        """
        test_case = XmlTestCase(methodName='assertXmlPartial')
        data = b"""<partial>1</partial>
        <partial>2</partial>"""

        root = test_case.assertXmlPartial(data, root_tag='customTag')
        self.assertIsInstance(root, etree._Element)

        self.assertEqual(root.tag, 'customTag')
        self.assertEqual(len(root), 2)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlPartial(b'<invalidChar>&</invalidChar>',
                                       root_tag='customTag')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlPartial(b'not even a partial XML document',
                                       root_tag='customTag')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlPartial(b'<missingEndTag>',
                                       root_tag='customTag')

    # -------------------------------------------------------------------------

    def test_assertXmlNamespace(self):
        """Asserts assertXmlNamespace raises namespace is invalid.

        When an element declare an xml namespace, this element and each child
        reference this namespace, and thus it can be tested.

        """
        test_case = XmlTestCase(methodName='assertXmlNamespace')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
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
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
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
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
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
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
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
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
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
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
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
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root, text='text_value')
        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, text='invalid')

    def test_assertXmlNode_tag_text(self):
        """Asserts assertXmlNode raises when node is invalid.

        Method assertXmlNode raises if node has not the expected tag name
        or the expected text value.

        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>text_value</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root, tag='root', text='text_value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='root', text='invalid')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot', text='text_value')

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, tag='noRoot', text='invalid')

    def test_assertXmlNode_text_in(self):
        """Asserts assertXmlNode raises when node is invalid.

        Method assertXmlNode raises if node's text value is not in the list
        of valid values.

        """
        test_case = XmlTestCase(methodName='assertXmlNode')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>valid</root>"""

        root = test_case.assertXmlDocument(data)

        test_case.assertXmlNode(root, text_in=['valid', 'ok'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlNode(root, text_in=['invalid', 'ok'])

    # -------------------------------------------------------------------------

    def test_assertXpathsExist(self):
        """Asserts assertXpathsExist raises when validation failed.

        Method assertXpathsExist raises when any xpath does not select a least
        one result.

        """
        test_case = XmlTestCase(methodName='assertXpathsExist')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root att="exists">
            <sub subAtt="input"/>
            <sub/>
        </root>"""

        root = test_case.assertXmlDocument(data)
        xpaths = ['@att', './sub', './sub[@subAtt="input"]']
        test_case.assertXpathsExist(root, xpaths)

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['@invalidAtt'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['./invalidChild'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['./sub[@subAtt="invalid"]'])

    def test_assertXpathsExist_namespaces_default_prefix(self):
        """Asserts assertXpathsExist works with default namespaces."""
        test_case = XmlTestCase(methodName='assertXpathsExist')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root att="exists" xmlns="https://www.w3.org/XML">
            <sub subAtt="input"/>
            <sub/>
        </root>"""

        root = test_case.assertXmlDocument(data)
        xpaths = ['@att', './ns:sub', './ns:sub[@subAtt="input"]']
        test_case.assertXpathsExist(root, xpaths)

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['@invalidAtt'])

        with self.assertRaises(test_case.failureException):
            # Without the namespace prefix, it does not work
            test_case.assertXpathsExist(root, ['./sub'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['./ns:invalidChild'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root, ['./ns:sub[@subAtt="invalid"]'])

    def test_assertXpathsExist_namespaces_custom_prefix(self):
        """Asserts assertXpathsExist works with custom default namespaces."""
        test_case = XmlTestCase(methodName='assertXpathsExist')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root att="exists" xmlns="https://www.w3.org/XML">
            <sub subAtt="input"/>
            <sub/>
        </root>"""

        root = test_case.assertXmlDocument(data)
        # With a custom default prefix
        xpaths = ['@att', './custom:sub', './custom:sub[@subAtt="input"]']
        test_case.assertXpathsExist(root, xpaths, default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root,
                                        ['@invalidAtt'],
                                        default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            # Without the namespace prefix, it does not work
            test_case.assertXpathsExist(root,
                                        ['./sub'],
                                        default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            # With the wrong namespace it does not work either
            test_case.assertXpathsExist(root,
                                        ['./ns:sub'],
                                        default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root,
                                        ['./custom:invalidChild'],
                                        default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsExist(root,
                                        ['./custom:sub[@subAtt="invalid"]'],
                                        default_ns_prefix='custom')

    def test_assertXpathsExist_namespaces(self):
        """Asserts assertXpathsExist works with namespaces."""
        test_case = XmlTestCase(methodName='assertXpathsExist')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root att="exists" xmlns="%s" xmlns:test="%s">
            <sub subAtt="DEFAULT_ATT" test:subAtt="NODE_NS-ATT"/>
            <sub/>
            <test:sub subAtt="NS-NODE_ATT" />
            <test:sub test:subAtt="NS-NODE_NS-ATT" />
        </root>""" % (DEFAULT_NS, TEST_NS)

        root = test_case.assertXmlDocument(data.encode('utf-8'))
        xpaths = [
            # attribute without namespace
            '@att',
            # node with default namespace with a namespaced attribute
            './ns:sub[@test:subAtt="NODE_NS-ATT"]',
            # namespaced node
            './test:sub',
            # namespaced node with non-namespaced attribute
            './test:sub[@subAtt="NS-NODE_ATT"]',
            # namespaced node with namespaced attribute
            './test:sub[@test:subAtt="NS-NODE_NS-ATT"]']
        test_case.assertXpathsExist(root, xpaths)

        with self.assertRaises(test_case.failureException):
            # This attribute does not exist with such namespace
            test_case.assertXpathsExist(root, ['@test:att'])

        with self.assertRaises(test_case.failureException):
            # This node with this attribute does not have this value,
            # only the namespaced attribute of this node has this value.
            test_case.assertXpathsExist(root, ['./ns:sub[@subAtt="NODE_NS-ATT"]'])

        with self.assertRaises(test_case.failureException):
            # We just make sure we use XPath properly and we don't hack the
            # XML document with "ignore all namespaces". We are respectful of
            # namespaces.
            test_case.assertXpathsExist(root, ['./ns:sub[@test:subAtt="DEFAULT_ATT"]'])

        with self.assertRaises(test_case.failureException):
            # Really, we don't mess with namespaces.
            test_case.assertXpathsExist(root, ['./ns:sub[@ns:subAtt="DEFAULT_ATT"]'])

    # -------------------------------------------------------------------------

    def test_assertXpathsOnlyOne(self):
        """Asserts assertXpathsOnlyOne raises when validation failed.

        Method assertXpathsOnlyOne raises when one of XPath
        expressions does not select one and exactly one result.

        """
        test_case = XmlTestCase(methodName='assertXpathsOnlyOne')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <sub subAtt="unique" id="1" />
            <sub subAtt="notUnique" id="2"/>
            <sub subAtt="notUnique" id="3"/>
            <uniqueSub/>
        </root>"""

        root = test_case.assertXmlDocument(data)
        unique_for_each = ['./uniqueSub',
                           './sub[@subAtt="unique"]']
        test_case.assertXpathsOnlyOne(root, unique_for_each)

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsOnlyOne(root, ['./invalidChild'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsOnlyOne(root, ['./sub[@subAtt="notUnique"]'])

    def test_assertXpathsOnlyOne_namespaces_default_prefix(self):
        """Asserts assertXpathsOnlyOne works with default namespace prefix"""
        test_case = XmlTestCase(methodName='assertXpathsOnlyOne')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="https://www.w3.org/XML">
            <sub subAtt="unique" id="1" />
            <sub subAtt="notUnique" id="2"/>
            <sub subAtt="notUnique" id="3"/>
            <uniqueSub/>
        </root>"""

        root = test_case.assertXmlDocument(data)
        unique_for_each = ['./ns:uniqueSub',
                           './ns:sub[@subAtt="unique"]']
        test_case.assertXpathsOnlyOne(root, unique_for_each)

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsOnlyOne(root, ['./ns:invalidChild'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsOnlyOne(root, ['./ns:sub[@subAtt="notUnique"]'])

    def test_assertXpathsOnlyOne_namespaces_custom_prefix(self):
        """Asserts assertXpathsOnlyOne works with custom namespace prefix"""
        test_case = XmlTestCase(methodName='assertXpathsOnlyOne')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="https://www.w3.org/XML">
            <sub subAtt="unique" id="1" />
            <sub subAtt="notUnique" id="2"/>
            <sub subAtt="notUnique" id="3"/>
            <uniqueSub/>
        </root>"""

        root = test_case.assertXmlDocument(data)
        unique_for_each = ['./custom:uniqueSub',
                           './custom:sub[@subAtt="unique"]']
        test_case.assertXpathsOnlyOne(root,
                                      unique_for_each,
                                      default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsOnlyOne(root,
                                          ['./custom:invalidChild'],
                                          default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            # Wrong namespace: the node exists but not with this namespace.
            # That's why namespaces exist after all.
            test_case.assertXpathsOnlyOne(root,
                                          ['./ns:uniqueSub'],
                                          default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsOnlyOne(root, ['./custom:sub[@subAtt="notUnique"]'])

    def test_assertXpathsOnlyOne_namespaces(self):
        """Asserts assertXpathsOnlyOne works with namespace"""
        test_case = XmlTestCase(methodName='assertXpathsOnlyOne')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="%s" xmlns:test="%s">
            <sub subAtt="unique" id="1" />
            <sub subAtt="notUnique" id="2"/>
            <sub subAtt="notUnique" id="3"/>
            <test:sub subAtt="notUnique" id="2"/>
            <test:sub subAtt="notUnique" id="3"/>
            <sub test:subAtt="unique" id="1" />
            <uniqueSub/>
            <test:uniqueSub/>
        </root>""" % (DEFAULT_NS, TEST_NS)

        root = test_case.assertXmlDocument(data.encode('utf-8'))
        unique_for_each = ['./ns:sub[@subAtt="unique"]',
                           './ns:sub[@test:subAtt="unique"]',
                           './ns:uniqueSub',
                           './test:uniqueSub']
        test_case.assertXpathsOnlyOne(root, unique_for_each)

        with self.assertRaises(test_case.failureException):
            # ns:sub appears multiple time with subAtt == notUnique
            test_case.assertXpathsOnlyOne(root, [
                './ns:sub[@subAtt="notUnique"]'
            ])

        with self.assertRaises(test_case.failureException):
            # test:sub appears multiple time with subAtt == notUnique
            test_case.assertXpathsOnlyOne(root, [
                './test:sub[@subAtt="notUnique"]'
            ])

    # -------------------------------------------------------------------------

    def test_assertXpathsUniqueValue(self):
        """Asserts assertXpathsUniqueValue raises when validation failed.

        Method assertXpathsUniqueValue raises when one of XPath expression
        select does not returns unique results.

        """
        test_case = XmlTestCase(methodName='assertXpathsUniqueValue')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <sub subAtt="unique" id="1">unique 1</sub>
            <sub subAtt="notUnique" id="2">unique 2</sub>
            <sub subAtt="notUnique" id="3">unique 3</sub>
            <multiple>twice</multiple>
            <multiple>twice</multiple>
        </root>"""
        root = test_case.assertXmlDocument(data)

        test_case.assertXpathsUniqueValue(root, ['./sub/@id',
                                                 './sub/text()'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root, ['./sub/@subAtt'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root, ['./multiple/text()'])

    def test_assertXpathsUniqueValue_namespaces_default_prefix(self):
        """Asserts assertXpathsUniqueValue works with default namespace prefix."""
        test_case = XmlTestCase(methodName='assertXpathsUniqueValue')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="http://www.w3c.org/XML">
            <sub subAtt="unique" id="1">unique 1</sub>
            <sub subAtt="notUnique" id="2">unique 2</sub>
            <sub subAtt="notUnique" id="3">unique 3</sub>
            <multiple>twice</multiple>
            <multiple>twice</multiple>
        </root>"""
        root = test_case.assertXmlDocument(data)

        test_case.assertXpathsUniqueValue(root,
                                          ['./ns:sub/@id', './ns:sub/text()'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root, ['./ns:sub/@subAtt'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root, ['./ns:multiple/text()'])

    def test_assertXpathsUniqueValue_namespaces_custom_prefix(self):
        """Asserts assertXpathsUniqueValue works with custom namespace prefix.
        """
        test_case = XmlTestCase(methodName='assertXpathsUniqueValue')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="http://www.w3c.org/XML">
            <sub subAtt="unique" id="1">unique 1</sub>
            <sub subAtt="notUnique" id="2">unique 2</sub>
            <sub subAtt="notUnique" id="3">unique 3</sub>
            <multiple>twice</multiple>
            <multiple>twice</multiple>
        </root>"""
        root = test_case.assertXmlDocument(data)

        test_case.assertXpathsUniqueValue(root,
                                          ['./custom:sub/@id',
                                           './custom:sub/text()'],
                                          default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root, ['./custom:sub/@subAtt'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root,
                                              ['./custom:multiple/text()'])

    def test_assertXpathsUniqueValue_namespaces(self):
        """Asserts assertXpathsUniqueValue works with namespace."""
        test_case = XmlTestCase(methodName='assertXpathsUniqueValue')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="%s" xmlns:test="%s">
            <sub subAtt="unique" id="1">unique 1</sub>
            <sub subAtt="notUnique" id="2">unique 2</sub>
            <sub subAtt="notUnique" id="3">unique 3</sub>
            <test:sub subAtt="unique" id="1">unique 1</test:sub>
            <test:sub subAtt="notUnique" id="2">unique 2</test:sub>
            <test:sub subAtt="notUnique" id="3">unique 3</test:sub>
            <multiple>twice</multiple>
            <multiple>twice</multiple>
            <test:multiple>twice</test:multiple>
            <test:multiple>twice</test:multiple>
        </root>""" % (DEFAULT_NS, TEST_NS)
        root = test_case.assertXmlDocument(data.encode('utf-8'))

        # Note: the default namespace and test namespace create different nodes
        # so their values and attributes are *not* in the same group.
        # This is how XML namespaces work.
        test_case.assertXpathsUniqueValue(root, [
            # Node with default namespace: attribute ID
            './ns:sub/@id',
            # Node with default namespace: text
            './ns:sub/text()',
            # Node with "test" namespace: attribute ID
            './test:sub/@id',
            # Node with "test" namespace: text
            './test:sub/text()',
        ])

        with self.assertRaises(test_case.failureException):
            # Not unique attribute subAtt on ns:sub
            test_case.assertXpathsUniqueValue(root, ['./ns:sub/@subAtt'])

        with self.assertRaises(test_case.failureException):
            # Not unique text value of ns:multiple
            test_case.assertXpathsUniqueValue(root,
                                              ['./ns:multiple/text()'])

        with self.assertRaises(test_case.failureException):
            # Not unique attribute subAtt on test:sub
            test_case.assertXpathsUniqueValue(root, ['./test:sub/@subAtt'])

        with self.assertRaises(test_case.failureException):
            # Not unique text value of test:multiple
            test_case.assertXpathsUniqueValue(root,
                                              ['./test:multiple/text()'])

    # -------------------------------------------------------------------------

    def test_assertXpathValues(self):
        """Asserts assertXpathValues raises when validation failed.

        Method assertXpathValues raises when not each XPath expression's result
        is in the expected values.

        """
        test_case = XmlTestCase(methodName='assertXpathValues')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <sub id="1">a</sub>
            <sub id="2">a</sub>
            <sub id="3">b</sub>
            <sub id="4">c</sub>
        </root>"""
        root = test_case.assertXmlDocument(data)

        test_case.assertXpathValues(root, './sub/@id', ['1', '2', '3', '4'])
        test_case.assertXpathValues(root, './sub/text()', ['a', 'b', 'c'])

        # This pass because the XPath expression returns 0 element.
        # So "all" the existing values are one of the expected values.
        # One should use assertXpathsExist instead
        test_case.assertXpathValues(root, './absentSub/@id', ['1', '2'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathValues(root, './sub/@id', ['1', '2'])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathValues(root, './sub/text()', ['a', 'b'])

    def test_assertXpathValues_namespaces_default_prefix(self):
        """Asserts assertXpathValues works with default namespaces."""
        test_case = XmlTestCase(methodName='assertXpathValues')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="http://www.w3c.org/XML">
            <sub id="1">a</sub>
            <sub id="2">a</sub>
            <sub id="3">b</sub>
            <sub id="4">c</sub>
        </root>"""
        root = test_case.assertXmlDocument(data)

        test_case.assertXpathValues(root, './ns:sub/@id', ['1', '2', '3', '4'])
        test_case.assertXpathValues(root, './ns:sub/text()', ['a', 'b', 'c'])

        with self.assertRaises(test_case.failureException):
            # @id in ['3', '4'] is missing
            test_case.assertXpathValues(root, './ns:sub/@id', ['1', '2'])

        with self.assertRaises(test_case.failureException):
            # text() == c is missing
            test_case.assertXpathValues(root, './ns:sub/text()', ['a', 'b'])

        with self.assertRaises(test_case.failureException):
            # Unknown namespace
            test_case.assertXpathValues(root, './custom:sub/@id', ['1', '2', '3', '4'])

    def test_assertXpathValues_namespaces_custom_prefix(self):
        """Asserts assertXpathValues works with custom namespaces."""
        test_case = XmlTestCase(methodName='assertXpathValues')
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="http://www.w3c.org/XML">
            <sub id="1">a</sub>
            <sub id="2">a</sub>
            <sub id="3">b</sub>
            <sub id="4">c</sub>
        </root>"""
        root = test_case.assertXmlDocument(data)

        # Attribute value
        test_case.assertXpathValues(root,
                                    './custom:sub/@id',
                                    ['1', '2', '3', '4'],
                                    default_ns_prefix='custom')
        # Node text value
        test_case.assertXpathValues(root,
                                    './custom:sub/text()',
                                    ['a', 'b', 'c'],
                                    default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathValues(root,
                                        './custom:sub/@id',
                                        ['1', '2'],
                                        default_ns_prefix='custom')

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathValues(root,
                                        './custom:sub/text()',
                                        ['a', 'b'],
                                        default_ns_prefix='custom')

    def test_assertXpathValues_namespaces(self):
        """Assert assertXpathValues works with namespaces."""
        test_case = XmlTestCase(methodName='assertXpathValues')
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="%s" xmlns:test="%s">
            <sub test:id="1">a</sub>
            <sub id="2">a</sub>
            <sub id="3">b</sub>
            <sub id="4">c</sub>
            <test:sub>ns-a</test:sub>
        </root>""" % (DEFAULT_NS, TEST_NS)
        root = test_case.assertXmlDocument(data.encode('utf-8'))

        # Attribute value without namespace
        test_case.assertXpathValues(root,
                                    './ns:sub/@id',
                                    ['2', '3', '4'])

        test_case.assertXpathValues(root,
                                    './test:sub/text()',
                                    ['ns-a'])

        with self.assertRaises(test_case.failureException):
            # Only the test:id attribute has value 1
            test_case.assertXpathValues(root,
                                        './ns:sub/@id',
                                        ['1'])

        with self.assertRaises(test_case.failureException):
            # There is only one test:id attribute, and its value is not here
            test_case.assertXpathValues(root,
                                        './ns:sub/@test:id',
                                        ['2', '3', '4'])

    # -------------------------------------------------------------------------

    def test_assertXmlValidDTD(self):
        """Asserts assertXmlValidDTD raises when DTD does not valid XML."""
        test_case = XmlTestCase(methodName='assertXmlValidDTD')

        dtd = """<!ELEMENT root (child)>
        <!ELEMENT child EMPTY>
        <!ATTLIST child id ID #REQUIRED>
        """

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        # Document is valid according to DTD
        test_case.assertXmlValidDTD(root, dtd)

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        # Document is invalid according to DTD (multiple child element)
        with self.assertRaises(test_case.failureException):
            test_case.assertXmlValidDTD(root, dtd)

    def test_assertXmlValidDTD_filename(self):
        """Asserts assertXmlValidDTD accepts a filename as DTD."""
        test_case = XmlTestCase(methodName='assertXmlValidDTD')

        filename = 'test_assertXmlValidDTD_filename.dtd'
        dtd = """<!ELEMENT root (child)>
        <!ELEMENT child EMPTY>
        <!ATTLIST child id ID #REQUIRED>
        """

        with open(filename, 'w') as dtd_file:
            dtd_file.write(dtd)

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        # Document is valid according to DTD
        try:
            test_case.assertXmlValidDTD(root, filename=filename)
        except:
            os.unlink(filename)
            raise

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        try:
            # Document is invalid according to DTD (multiple child element)
            with self.assertRaises(test_case.failureException):
                test_case.assertXmlValidDTD(root, filename=filename)
        finally:
            os.unlink(filename)

    def test_assertXmlValidDTD_DTD(self):
        """Asserts assertXmlValidDTD accepts an LXML DTD object."""
        test_case = XmlTestCase(methodName='assertXmlValidDTD')

        dtd = """<!ELEMENT root (child)>
        <!ELEMENT child EMPTY>
        <!ATTLIST child id ID #REQUIRED>
        """
        schema = etree.DTD(io.StringIO(dtd))

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        # Document is valid according to DTD
        test_case.assertXmlValidDTD(root, schema)

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        # Document is invalid according to DTD (multiple child element)
        with self.assertRaises(test_case.failureException):
            test_case.assertXmlValidDTD(root, schema)

    def test_assertXmlValidDTD_no_dtd(self):
        """Asserts assertXmlValidDTD raises ValueError without any DTD."""
        test_case = XmlTestCase(methodName='assertXmlValidDTD')

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        # No DTD: ValueError
        with self.assertRaises(ValueError):
            test_case.assertXmlValidDTD(root)

    # -------------------------------------------------------------------------

    def test_assertXmlValidXSchema(self):
        """Asserts assertXmlValidXSchema raises when schema does not valid XML.
        """
        test_case = XmlTestCase(methodName='assertXmlValidXSchema')

        xschema = b"""<?xml version="1.0" encoding="utf-8"?>
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="root">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="child" minOccurs="1" maxOccurs="1">
                            <xsd:complexType>
                                <xsd:simpleContent>
                                    <xsd:extension base="xsd:string">
                                        <xsd:attribute name="id" type="xsd:string" use="required" />
                                    </xsd:extension>
                                </xsd:simpleContent>
                            </xsd:complexType>
                        </xsd:element>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
        """

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        test_case.assertXmlValidXSchema(root, xschema)

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
            <child id="tooManyChild"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlValidXSchema(root, xschema)

    def test_assertXmlValidXSchema_filename(self):
        """Asserts assertXmlValidXSchema raises when schema does not valid XML.
        """
        test_case = XmlTestCase(methodName='assertXmlValidXSchema')

        xschema = """<?xml version="1.0" encoding="utf-8"?>
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="root">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="child" minOccurs="1" maxOccurs="1">
                            <xsd:complexType>
                                <xsd:simpleContent>
                                    <xsd:extension base="xsd:string">
                                        <xsd:attribute name="id" type="xsd:string" use="required" />
                                    </xsd:extension>
                                </xsd:simpleContent>
                            </xsd:complexType>
                        </xsd:element>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
        """

        filename = 'test_assertXmlValidXSchema_filename.xml'
        with open(filename, 'w') as xchema_file:
            xchema_file.write(xschema)

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        try:
            test_case.assertXmlValidXSchema(root, filename=filename)
        except:
            os.unlink(filename)
            raise

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
            <child id="tooManyChild"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        try:
            with self.assertRaises(test_case.failureException):
                test_case.assertXmlValidXSchema(root, filename=filename)
        finally:
            os.unlink(filename)

    def test_assertXmlValidXSchema_xschema(self):
        """Asserts assertXmlValidXSchema raises when schema does not valid XML.
        """
        test_case = XmlTestCase(methodName='assertXmlValidXSchema')

        xschema = b"""<?xml version="1.0" encoding="utf-8"?>
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="root">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="child" minOccurs="1" maxOccurs="1">
                            <xsd:complexType>
                                <xsd:simpleContent>
                                    <xsd:extension base="xsd:string">
                                        <xsd:attribute name="id" type="xsd:string" use="required" />
                                    </xsd:extension>
                                </xsd:simpleContent>
                            </xsd:complexType>
                        </xsd:element>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
        """

        xml_schema = etree.XMLSchema(etree.XML(xschema))

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        test_case.assertXmlValidXSchema(root, xml_schema)

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
            <child id="tooManyChild"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlValidXSchema(root, xml_schema)

    def test_assertXmlValidXSchema_no_xchema(self):
        """Asserts assertXmlValidXSchema raises ValueError without any schema.
        """
        test_case = XmlTestCase(methodName='assertXmlValidXSchema')

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        # No DTD: ValueError
        with self.assertRaises(ValueError):
            test_case.assertXmlValidXSchema(root)

    # -------------------------------------------------------------------------

    def test_assertXmlValidRelaxNG(self):
        """Asserts assertXmlValidRelaxNG raises when schema does not valid XML.
        """
        test_case = XmlTestCase(methodName='assertXmlValidRelaxNG')

        relaxng = b"""<?xml version="1.0" encoding="utf-8"?>
        <rng:element name="root" xmlns:rng="http://relaxng.org/ns/structure/1.0">
            <rng:element name="child">
                <rng:attribute name="id">
                    <rng:text />
                </rng:attribute>
            </rng:element>
        </rng:element>
        """

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        test_case.assertXmlValidRelaxNG(root, relaxng)

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
            <child id="tooManyChild"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlValidRelaxNG(root, relaxng)

    def test_assertXmlValidRelaxNG_filename(self):
        """Asserts assertXmlValidRelaxNG raises when schema does not valid XML.
        """
        test_case = XmlTestCase(methodName='assertXmlValidRelaxNG')

        relaxng = """<?xml version="1.0" encoding="utf-8"?>
        <rng:element name="root" xmlns:rng="http://relaxng.org/ns/structure/1.0">
            <rng:element name="child">
                <rng:attribute name="id">
                    <rng:text />
                </rng:attribute>
            </rng:element>
        </rng:element>
        """

        filename = 'test_assertXmlValidRelaxNG_filename.xml'
        with open(filename, 'w') as relaxng_file:
            relaxng_file.write(relaxng)

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        try:
            test_case.assertXmlValidRelaxNG(root, filename=filename)
        except:
            os.unlink(filename)
            raise

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
            <child id="tooManyChild"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        try:
            with self.assertRaises(test_case.failureException):
                test_case.assertXmlValidRelaxNG(root, filename=filename)
        finally:
            os.unlink(filename)

    def test_assertXmlValidRelaxNG_relaxng(self):
        """Asserts assertXmlValidRelaxNG raises when schema does not valid XML.
        """
        test_case = XmlTestCase(methodName='assertXmlValidRelaxNG')

        relaxng = b"""<?xml version="1.0" encoding="utf-8"?>
        <rng:element name="root" xmlns:rng="http://relaxng.org/ns/structure/1.0">
            <rng:element name="child">
                <rng:attribute name="id">
                    <rng:text />
                </rng:attribute>
            </rng:element>
        </rng:element>
        """

        xml_relaxng = etree.RelaxNG(etree.XML(relaxng))

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        test_case.assertXmlValidRelaxNG(root, xml_relaxng)

        data_invalid = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="valid"/>
            <child id="tooManyChild"/>
        </root>
        """
        root = test_case.assertXmlDocument(data_invalid)

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlValidRelaxNG(root, xml_relaxng)

    def test_assertXmlValidRelaxNG_no_relaxng(self):
        """Asserts assertXmlValidRelaxNG raises ValueError without any RelaxNG.
        """
        test_case = XmlTestCase(methodName='assertXmlValidRelaxNG')

        data = b"""<?xml version="1.0" encoding="utf-8"?>
        <root>
            <child id="child1"/>
        </root>
        """
        root = test_case.assertXmlDocument(data)

        # No DTD: ValueError
        with self.assertRaises(ValueError):
            test_case.assertXmlValidRelaxNG(root)

    # -------------------------------------------------------------------------

    def test_assertXmlEquivalentOutputs(self):
        """Asserts assertXmlEquivalentOutputs raises when comparison failed.

        Basic assertion: same document, with different order of attributes,
        text with useless spaces, etc.

        """
        test_case = XmlTestCase(methodName='assertXmlEquivalentOutputs')

        # Same XML (with different spacings placements and attrs order)
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <tag foo="bar" bar="foo">foo</tag>
        </root>"""
        expected = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root><tag bar="foo" foo="bar"> foo </tag></root>"""

        test_case.assertXmlEquivalentOutputs(data, expected)

        # Not the right element given
        wrong_element = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <notTag foo="bar" bar="foo">foo</notTag>
        </root>"""

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlEquivalentOutputs(wrong_element, expected)

        # Too many tag elements
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root>
            <tag foo="bar" bar="foo">foo</tag>
            <tag foo="bar" bar="foo">foo</tag>
        </root>"""

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlEquivalentOutputs(wrong_element, expected)

    def test_assertXmlEquivalentOutputs_namespaces(self):
        """Asserts assertXmlEquivalentOutputs raises when comparison failed.

        Assertion with different namespaces: the namespace URI is the same,
        but the prefix is different. In this case, the two XML are equivalents.

        """
        test_case = XmlTestCase(methodName='assertXmlEquivalentOutputs')

        # Same XML, but with different namespace prefixes
        data = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns:foo="mynamespace">
            <foo:tag>foo</foo:tag>
        </root>"""

        expected = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns:bar="mynamespace">
            <bar:tag>foo</bar:tag>
        </root>"""

        test_case.assertXmlEquivalentOutputs(data, expected)

        wrong_namespace = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns:foo="not_the_same_namespace">
            <foo:tag>foo</foo:tag>
        </root>
        """

        with self.assertRaises(test_case.failureException):
            test_case.assertXmlEquivalentOutputs(wrong_namespace, expected)


class TestIntegrationXmlTestCase(unittest.TestCase):
    def test_full_document(self):
        data = """<?xml version="1.0" encoding="UTF-8" ?>
        <root xmlns="%s" xmlns:test="%s" rootAtt="attValue" test:rootAtt="nsValue">
            <emptyElement />
            <attrElement id="1" attr="simple" test:attr="namespaced" />
            <textElement>assemblée</textElement>
            <multipleElement />
            <multipleElement />
            <parent>
                <emptyElement />
                <attrElement id="2" attr="simple" test:attr="namespaced" uniqueAttr="" />
                <textElement>text</textElement>
                <multipleElement />
                <multipleElement />
            </parent>
            <test:parent>
                <emptyElement />
                <attrElement id="3" attr="simple" test:attr="namespaced" />
                <textElement>text</textElement>
                <multipleElement />
                <multipleElement />
            </test:parent>
        </root>""" % (DEFAULT_NS, TEST_NS)

        test_case = XmlTestCase(methodName='assertXmlDocument')

        # It is a valid document.
        root = test_case.assertXmlDocument(data.encode('utf-8'))
        # The root node has these namespaces
        test_case.assertXmlNamespace(root, None, DEFAULT_NS)
        test_case.assertXmlNamespace(root, 'test', TEST_NS)
        # The root node has this attribute with this value
        test_case.assertXmlHasAttribute(
            root, 'rootAtt', expected_value='attValue')
        # The root node has this test:attribute with this value
        # Note that we can not use the test:rootAtt syntax and must rely on
        # the {uri}rootAtt syntax instead.
        # That's why XPath is better for us
        test_case.assertXmlHasAttribute(
            root, '{%s}rootAtt' % TEST_NS, expected_value='nsValue')

        # Same tests on attributes with xpath
        test_case.assertXpathsExist(root, [
            '@rootAtt',  # No default namespace on attribute
            '@test:rootAtt',  # rootAtt with test namespace
            # There are many element with the ID attribute
            '//@id',
            # attrElement's attr
            './ns:attrElement/@attr',
            '//ns:attrElement[@attr]',
            '//ns:parent/ns:attrElement/@attr',
            '//test:parent/ns:attrElement/@attr',
            # Specific values
            '@rootAtt="attValue"',
            '@test:rootAtt="nsValue"',
        ])

        # Let's play with XPath and attribute values
        test_case.assertXpathsUniqueValue(root, [
            # All ID are unique
            '//@id',
            # This takes only the direct children of <root>
            './ns:attrElement/@attr',
            # This takes only the children of <ns:parent>
            '//ns:parent/ns:attrElement/@attr',
            # This takes only the children of <test:parent>
            '//test:parent/ns:attrElement/@attr',
        ])

        with self.assertRaises(test_case.failureException):
            test_case.assertXpathsUniqueValue(root, [
                # This take all attrElement in the tree
                '//ns:attrElement/@attr',
            ])

        # Some node exists once and only once - it depends on the expression
        test_case.assertXpathsOnlyOne(root, [
            # Direct child
            './ns:attrElement',
            # All children, but with specific attribute's value
            '//ns:attrElement[@id=1]',
            '//ns:attrElement[@id=2]',
            '//ns:attrElement[@id=3]',
            # It is the only element with this attribute
            '//ns:attrElement[@uniqueAttr]',
            # This attribute is the only on under test:parent's node
            '//test:parent/ns:attrElement',
            '//test:parent/ns:attrElement[@id=3]',
        ])

        # Let's check @id's values
        test_case.assertXpathValues(root, '//@id', ['1', '2', '3'])


if __name__ == "__main__":
    unittest.main()
