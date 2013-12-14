"""Unittest module for XML testing purpose."""
from __future__ import unicode_literals

import doctest
import io
import unittest

from lxml import etree
from lxml.etree import XMLSyntaxError
from lxml.doctestcompare import LXMLOutputChecker, PARSE_XML


class XmlTestMixin(object):
    """Base mixin class for XML unittest.

    One may want to extends unittest.TestCase itself, and then uses this
    mixin class to add specific XML assertions.

    """
    default_partial_tag = 'partialTest'

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

    def assertXmlPartial(self, partial_data, root_tag=None):
        """Asserts `data` is an XML partial document, and returns result."""
        tag_name = (root_tag
                        if root_tag is not None
                        else self.default_partial_tag)
        consolidated = '<%s>%s</%s>' % (tag_name, partial_data, tag_name)

        try:
            doc = etree.fromstring(consolidated)
        except XMLSyntaxError as e:
            raise self.fail('Input is not a valid partial XML document: %s'
                            % e)

        if not len(doc):
            self.fail('Input does not have any elements to check.')

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
        """Asserts each xpath's value is unique in the selected elements."""
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
        """Asserts each xpath's value is in the expected values."""
        results = node.xpath(xpath)

        for result in results:
            if result not in values:
                self.fail('Invalid value found for node %s\n'
                          'XPath: %s\n'
                          'Value found: %s\n'
                          'Element:\n%s'
                          % (node.tag, xpath, result,
                             etree.tostring(node, pretty_print=True)))

    def assertXmlEquivalent(self, got, expect):
        """Asserts both xml parse to the same results
        `got` may be an XML string or lxml Element
        """
        checker = LXMLOutputChecker()

        if isinstance(got, etree._Element):
            got = etree.tostring(got)

        if not checker.check_output(expect, got, PARSE_XML):
            message = checker.output_difference(doctest.Example("", expect), got, PARSE_XML)
            self.fail(message)

    def assertXmlValid(self, xml, schema):
        """Validates xml (string or lxml _Element) against a schema.

        :param xml: XML string or lxml Element to validate
        :param schema: a DTD, XSchema, RelaxNG or Schematron instance
        """
        if not isinstance(xml, etree._Element):
            xml = etree.XML(xml)
        if not schema.validate(xml):
            message = schema.error_log.last_error
            self.fail(message)

    def assertXmlValidDTD(self, node, dtd=None, filename=None):
        """Asserts XML node is valid according to the given DTD."""

        schema = None

        if dtd is not None and not isinstance(dtd, etree.DTD):
            schema = etree.DTD(io.StringIO(dtd))
        elif isinstance(dtd, etree.DTD):
            schema = dtd

        if schema is None and filename is not None:
            with open(filename, 'r') as fd:
                schema = etree.DTD(fd)

        if schema is None:
            raise ValueError('No valid dtd given.')

        if not schema.validate(node):
            self.fail(schema.error_log.last_error)


class XmlTestCase(unittest.TestCase, XmlTestMixin):
    """XML test case for unit test using python unittest built-in package.

    One can extends this class for his test case and use helpful assertion
    method.

    XML parsing uses python lxml.etree.

    """
    pass
