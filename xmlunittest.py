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
        except XMLSyntaxError, e:
            raise self.fail('Input is not a valid XML document: %s' % e)

        return doc

    def assertXmlNamespace(self, node, prefix, uri):
        """Asserts `node` declare namespace `uri` using `prefix`.

        One can use this method on element node.

        """
        assert prefix in node.nsmap
        assert node.nsmap.get(prefix) == uri

    def assertXmlHasAttribute(self, node, attribute, **kwargs):
        """Asserts `node` has the given `attribute`.

        Argument `attribute` must be the attribute's name, with
        namespace's prefix (notation 'ns:att' and not '{uri}att').

        """
        assert attribute in node.attrib

        if 'expected_value' in kwargs:
            assert node.attrib.get(attribute) == kwargs.get('expected_value')
        elif 'expected_values' in kwargs:
            assert node.attrib.get(attribute) in kwargs.get('expected_values')

    def assertXmlNode(self, node, **kwargs):
        """Asserts `node` is an element node with expected tag and value.

        """
        pass  # no assertion yet

    def assertXpathExistForEachNodes(self, nodes, xpaths):
        """Asserts `xpaths` are valid for each node of `nodes`.

        """
        expressions = [etree.XPath(xpath) for xpath in xpaths]
        for node in nodes:
            for expression in expressions:
                if not expression.evaluate(node):
                    self.fail('No result found for XPath on element %s:\n'
                              'XPath: %s\n'
                              'Element:\n'
                              '%s' % (node.tag,
                                      expression.path,
                                      etree.tostring(node, pretty_print=True)))

    def assertXpathUniqueForEachNodes(self, nodes, xpaths):
        """Asserts each xpath's result is unique for each node.
        """
        expressions = [etree.XPath(xpath) for xpath in xpaths]
        for node in nodes:
            for expression in expressions:
                result = expression.evaluate(node)
                if not result:
                    self.fail('No result found for XPath on element %s:\n'
                              'XPath: %s\n'
                              'Element:\n'
                              '%s' % (node.tag,
                                      expression.path,
                                      etree.tostring(node, pretty_print=True)))
                count = len(result)
                if count > 1:
                    self.fail('Too many results found (%d) for XPath on '
                              'element %s:\n'
                              'XPath: %s\n'
                              'Element:\n'
                              '%s' % (count,
                                      node.tag,
                                      expression.path,
                                      etree.tostring(node, pretty_print=True)))
