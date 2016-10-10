# -*- coding: utf-8 -*-
"""Unittest module for XML testing purpose."""
from __future__ import unicode_literals

import io
import unittest

from lxml import etree
from lxml.doctestcompare import PARSE_XML, LXMLOutputChecker
from lxml.etree import XMLSyntaxError, XPathSyntaxError

__all__ = ['XmlTestMixin', 'XmlTestCase']


class XmlTestMixin(object):
    """Base mixin class for XML unittest.

    One may want to extends unittest.TestCase itself, and then uses this
    mixin class to add specific XML assertions.
    """
    default_partial_tag = 'partialTest'
    error_encoding = 'utf-8'

    def fail_xpath_error(self, node, xpath, exception):
        """Format an xpath ``expression`` error for the given ``node``.

        This method should be used instead of the ``fail`` method.
        """
        doc = etree.tostring(
            node, pretty_print=True, encoding=self.error_encoding)
        self.fail(
            'Invalid XPath expression for element %s: %s\n'
            'Xpath: %s\n'
            'Element:\n'
            '%s' % (
                node.tag,
                str(exception),
                xpath,
                doc.decode(self.error_encoding)))

    def fail_xpath_not_found(self, node, expression):
        doc = etree.tostring(
            node, pretty_print=True, encoding=self.error_encoding)
        self.fail(
            'No result found for XPath for element %s\n'
            'XPath: %s\n'
            'Element:\n'
            '%s' % (
                node.tag,
                expression.path,
                doc.decode(self.error_encoding)))

    def build_xpath_expressions(self, node, xpaths, default_ns_prefix='ns'):
        namespaces = dict(
            (prefix or default_ns_prefix, url)
            for prefix, url in node.nsmap.items())

        for xpath in xpaths:
            try:
                yield etree.XPath(xpath, namespaces=namespaces)
            except XPathSyntaxError as error:
                self.fail_xpath_error(node, xpath, error)

    def build_xpath_expression(self, node, xpath, default_ns_prefix='ns'):
        namespaces = dict(
            (prefix or default_ns_prefix, url)
            for prefix, url in node.nsmap.items())

        try:
            return etree.XPath(xpath, namespaces=namespaces)
        except XPathSyntaxError as error:
            self.fail_xpath_error(node, xpath, error)

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
        tag_name = (
            root_tag if root_tag is not None
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
        self.assertIn(attribute, node.attrib)

        if 'expected_value' in kwargs:
            self.assertEqual(node.attrib.get(attribute),
                             kwargs.get('expected_value'))
        elif 'expected_values' in kwargs:
            self.assertIn(node.attrib.get(attribute),
                          kwargs.get('expected_values'))

    def assertXmlNode(self, node, **kwargs):
        """Asserts `node` is an element node with expected tag and value."""
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

    def assertXpathsExist(self, node, xpaths, default_ns_prefix='ns'):
        """Asserts each XPath is valid for element `node`."""
        expressions = self.build_xpath_expressions(node,
                                                   xpaths,
                                                   default_ns_prefix)
        for expression in expressions:
            try:
                if not expression.evaluate(node):
                    self.fail_xpath_not_found(node, expression)
            except etree.XPathEvalError as error:
                self.fail_xpath_error(node, expression.path, error)

    def assertXpathsOnlyOne(self, node, xpaths, default_ns_prefix='ns'):
        """Asserts each xpath's result returns only one element."""
        expressions = self.build_xpath_expressions(node,
                                                   xpaths,
                                                   default_ns_prefix)

        for expression in expressions:
            try:
                results = expression.evaluate(node)
            except etree.XPathEvalError as error:
                self.fail_xpath_error(node, expression.path, error)

            if not results:
                self.fail_xpath_not_found(node, expression)

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

    def assertXpathsUniqueValue(self, node, xpaths, default_ns_prefix='ns'):
        """Asserts each xpath's value is unique in the selected elements."""
        expressions = self.build_xpath_expressions(node,
                                                   xpaths,
                                                   default_ns_prefix)

        for expression in expressions:
            try:
                results = expression.evaluate(node)
            except etree.XPathEvalError as error:
                self.fail_xpath_error(node, expression.path, error)

            if len(results) != len(set(results)):
                self.fail('Value is not unique for element %s:\n'
                          'XPath: %s\n'
                          'Element:\n%s'
                          % (node.tag, expression.path,
                             etree.tostring(node, pretty_print=True)))

    def assertXpathValues(self, node, xpath, values, default_ns_prefix='ns'):
        """Asserts each xpath's value is in the expected values."""
        expression = self.build_xpath_expression(node,
                                                 xpath,
                                                 default_ns_prefix)
        try:
            results = expression.evaluate(node)
        except etree.XPathEvalError as error:
            self.fail_xpath_error(node, expression.path, error)

        for result in results:
            if result not in values:
                self.fail('Invalid value found for node %s\n'
                          'XPath: %s\n'
                          'Value found: %s\n'
                          'Element:\n%s'
                          % (node.tag, xpath, result,
                             etree.tostring(node, pretty_print=True)))

    def assertXmlValidDTD(self, node, dtd=None, filename=None):
        """Asserts XML node is valid according to the given DTD."""
        schema = None

        if isinstance(dtd, etree.DTD):
            schema = dtd
        elif dtd is not None:
            schema = etree.DTD(io.StringIO(dtd))

        if schema is None and filename is not None:
            with open(filename, 'r') as fd:
                schema = etree.DTD(fd)

        if schema is None:
            raise ValueError('No valid DTD given.')

        if not schema.validate(node):
            self.fail(schema.error_log.last_error)

    def assertXmlValidXSchema(self, node, xschema=None, filename=None,
                              encoding='utf-8'):
        """Asserts XML node is valid according to the given XML Schema."""
        schema = None

        if xschema is not None and not isinstance(xschema, etree.XMLSchema):
            schema = etree.XMLSchema(etree.XML(xschema))
        elif isinstance(xschema, etree.XMLSchema):
            schema = xschema

        if xschema is None and filename is not None:
            with open(filename, 'r') as xschema_file:
                schema = etree.XMLSchema(
                    etree.XML(xschema_file.read().encode(encoding)))

        if schema is None:
            raise ValueError('No valid XMLSchema given.')

        if not schema.validate(node):
            self.fail(schema.error_log.last_error)

    def assertXmlValidRelaxNG(self, node, relaxng=None, filename=None,
                              encoding='utf-8'):
        """Asserts XML node is valid according to the given RelaxNG."""
        schema = None

        if relaxng is not None and not isinstance(relaxng, etree.RelaxNG):
            schema = etree.RelaxNG(etree.XML(relaxng))
        elif isinstance(relaxng, etree.RelaxNG):
            schema = relaxng

        if relaxng is None and filename is not None:
            with open(filename, 'r') as relaxng_file:
                schema = etree.RelaxNG(
                    etree.XML(relaxng_file.read().encode(encoding)))

        if schema is None:
            raise ValueError('No valid RelaxNG given.')

        if not schema.validate(node):
            self.fail(schema.error_log.last_error)

    def assertXmlEquivalentOutputs(self, data, expected):
        """Asserts both XML outputs are equivalent.

        This assertion use the powerful but dangerous feature of
        LXMLOutputChecker. Powerful because one can compare two XML document
        in their meaning, but dangerous because sometimes there is more to
        check than just a kind of output.

        See LXMLOutputChecker documentation for more information.
        """
        checker = LXMLOutputChecker()

        if not checker.check_output(expected, data, PARSE_XML):
            self.fail('Output are not equivalent:\n'
                      'Given: %s\n'
                      'Expected: %s'
                      % (data, expected))


class XmlTestCase(unittest.TestCase, XmlTestMixin):
    """XML test case for unit test using python unittest built-in package.

    One can extends this class for their test cases and use helpful assertion
    methods.

    XML parsing uses python lxml.etree.
    """
    pass
