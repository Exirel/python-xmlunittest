"""Unittest module for XML testing purpose."""
from __future__ import unicode_literals

import unittest

from lxml import etree
from lxml.etree import XMLSyntaxError


class XmlTestCase(unittest.TestCase):
    """XML test case for unit test using python unittest built-in package.

    One can extends this class for his test case and use helpful assertion
    method.

    XML parsing uses python lxml.etree.

    """
    def assertXmlDocument(self, data):
        """Asserts `data` is an XML document and returns it.

        Assertion and XML parsing using lxml.

        """
        # no assertion yet
        try:
            doc = etree.fromstring(data)
        except XMLSyntaxError as e:
            raise self.fail('Input is not a valid XML document: %s' % e)

        return doc

    def assertXmlNamespace(self, node, prefix, uri):
        """Asserts `node` declares namespace `uri` using `prefix`.

        One can use this method on element node.

        """
        self.assertIn(prefix, node.nsmap)
        self.assertEqual(node.nsmap.get(prefix), uri)

    def assertXmlHasAttribute(self, node, attribute, **kwargs):
        """Asserts `node` has the given `attribute`.

        Argument `attribute` must be the attribute's name, with
        namespace's prefix (notation 'ns:att' and not '{uri}att').

        """
        assert attribute in node.attrib

        if 'expected_value' in kwargs:
            self.assertEqual(node.attrib.get(attribute),
                              kwargs.get('expected_value'))
        elif 'expected_values' in kwargs:
            self.assertIn(node.attrib.get(attribute),
                          kwargs.get('expected_values'))

    def assertXmlNode(self, node, **kwargs):
        """Asserts `node` is an element node with expected tag and value.

        """
        # Assert `node` is an element node and not None or a string or
        # anything like this
        self.assertIsInstance(node, etree._Element)

        if 'tag' in kwargs:
            tag = kwargs.get('tag')
            self.assertEqual(node.tag, tag)

        if 'text' in kwargs:
            self.assertEqual(node.text, kwargs.get('text'))

        if 'text_in' in kwargs:
            self.assertIn(node.text, kwargs.get('text_in'))

    def assertXpathsExist(self, node, xpaths):
        """Asserts each XPath is valid for element `node`."""
        expressions = [etree.XPath(xpath) for xpath in xpaths]
        for expression in expressions:
            if not expression.evaluate(node):
                self.fail('No result found for XPath on element %s:\n'
                          'XPath: %s\n'
                          'Element:\n'
                          '%s' % (node.tag,
                                  expression.path,
                                  etree.tostring(node, pretty_print=True)))

    def assertXpathsOnlyOne(self, node, xpaths):
        """Asserts each xpath's result returns only one element."""
        expressions = [etree.XPath(xpath) for xpath in xpaths]

        for expression in expressions:
            results = expression.evaluate(node)
            if not results:
                self.fail('No result found for XPath on element %s:\n'
                          'XPath: %s\n'
                          'Element:\n%s'
                          % (node.tag, expression.path,
                             etree.tostring(node, pretty_print=True)))
            count = len(results)
            if count > 1:
                self.fail('Too many results found (%d) for XPath on '
                          'element %s:\n'
                          'XPath: %s\n'
                          'Element:\n'
                          '%s' % (count,
                                  node.tag,
                                  expression.path,
                                  etree.tostring(node, pretty_print=True)))

    def assertXpathsUniqueValue(self, node, xpaths):
        """Asserts each xpath's value is unique in the selected elements.
        """
        expressions = [etree.XPath(xpath) for xpath in xpaths]

        for expression in expressions:
            results = expression.evaluate(node)

            if len(results) != len(set(results)):
                self.fail('Value is not unique for element %s:\n'
                          'XPath: %s\n'
                          'Element:\n%s'
                          % (node.tag, expression.path,
                             etree.tostring(node, pretty_print=True)))

    def assertXpathValues(self, node, xpath, values):
        """Asserts each xpath's value is in the expected values.
        """
        results = node.xpath(xpath)

        for result in results:
            if result not in values:
                self.fail('Invalid value found for node %s\n'
                          'XPath: %s\n'
                          'Value found: %s\n'
                          'Element:\n%s'
                          % (node.tag, xpath, result,
                             etree.tostring(node, pretty_print=True)))
