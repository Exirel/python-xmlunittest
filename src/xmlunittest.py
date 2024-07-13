"""Unittest module for XML testing purpose."""
from __future__ import annotations

import io
import unittest
from typing import TYPE_CHECKING

from lxml import etree
from lxml.doctestcompare import PARSE_XML, LXMLOutputChecker
from lxml.etree import XMLSyntaxError, XPathSyntaxError

if TYPE_CHECKING:
    from typing import Any, Union

__all__ = ['XmlTestMixin', 'XmlTestCase']


class XmlTestMixin:
    """Base mixin class for XML unittest.

    This class provides assertion methods only. To use, one must extends
    both :py:class:`unittest.TestCase` and :py:class:`XmlTestMixin`. Of course,
    it can use any subclass of :py:class:`unittest.TestCase`, in combination
    with :py:class:`XmlTestMixin`.

    For example::

      class TestUsingMixin(unittest.TestCase, xmlunittest.XmlTestMixin):

          def test_my_test(self):
              data: bytes = my_module.generate_xml()

              # unittest.TestCase assert
              self.assertIsNotNone(data)

              # xmlunittest.XmlTestMixin assert
              self.assertXmlDocument(data)
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

    def assertXmlDocument(self, data: bytes):
        """Assert ``data`` is an XML document and return it.

        :param data: XML formated string

        Assert ``data`` is a valid XML formated string. This method will parse
        string with ``lxml.etree.fromstring``. If parsing failed (raise an
        ``XMLSyntaxError``), the test fails::

            class CustomTestCase(XmlTestCase):

                def test_my_custom_test(self):
                    # generate a XML formatted string from your code
                    data: bytes = this_is_your_function()

                    # start with `assertXmlDocument`
                    root = self.assertXmlDocument(data)

        .. note::

            This assertion method requires a :class:`bytes`, as your string
            should be properly encoded first.

        """
        # no assertion yet
        try:
            doc = etree.fromstring(data)
        except XMLSyntaxError as e:
            raise self.fail('Input is not a valid XML document: %s' % e)

        return doc

    def assertXmlPartial(
        self,
        partial_data: str,
        root_tag: Union[str, None] = None,
    ):
        """Assert ``data`` is an XML partial document, and return result.

        :param partial_data: Partial document as XML formated string
        :param root_tag: Optional, root element's tag name

        This method encapsulates the ``partial_data`` into a root element then
        parse the string as an XML document.

        By default, this method uses :attr:`default_partial_tag` as the root
        element's tag name, or you can provide a ``root_tag``.

        If the parsing fails, the test will fail. If the parsing's result does
        not have any child element, the test will also fail, because it expects
        a **partial document**, and not just a string.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"
                    <partial>a</partial>
                    <partial>b</partial>
                \"\"\"

                root = self.assertXmlPartial(data)
                # Make some assert on the result's document.
                self.assertXpathValues(root, './partial/text()', ('a', 'b'))

            # ...

        """
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

    def assertXmlNamespace(self, node, prefix: str, uri: str):
        """Assert ``node`` declares a namespace ``uri`` using ``prefix``.

        :param node: Element node
        :param prefix: Expected namespace's prefix
        :param uri: Expected namespace's URI

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<?xml version="1.0" encoding="UTF-8" ?>
                <root xmlns:ns="uri"/>\"\"\"

                root = self.assertXmlDocument(data.encode('utf-8)'))

                self.assertXmlNamespace(root, 'ns', 'uri')

            # ...
        """
        self.assertIn(prefix, node.nsmap)
        self.assertEqual(node.nsmap.get(prefix), uri)

    def assertXmlHasAttribute(
        self,
        node,
        attribute:  str,
        *,
        expected_value: Union[str, None] = None,
        expected_values: Union[str, None] = None,
    ):
        """Assert ``node`` has the given ``attribute``.

        :param node: Element node
        :param attribute: Expected attribute's name (using ``prefix:name``
                          notation)
        :param expected_value: Optional, expected attribute's value
        :param expected_values: Optional, list of accepted attribute's value

        Argument ``attribute`` must be the attribute's name, with
        namespace's prefix (notation ``'ns:att'`` and not ``'{uri}att'``).

        .. note::

            If ``expected_value`` is not ``None``, then ``expected_values``
            will be ignored.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<root a="1" />\"\"\"
                root = self.assertXmlDocument(data.encode('utf-8'))

                # All these tests will pass
                self.assertXmlHasAttribute(root, 'a')
                self.assertXmlHasAttribute(root, 'a', expected_value='1')
                self.assertXmlHasAttribute(
                    root, 'a', expected_values=('1', '2')
                )

            # ...

        """
        self.assertIn(attribute, node.attrib)

        if expected_value is not None:
            self.assertEqual(node.attrib.get(attribute), expected_value)

        elif expected_values is not None:
            self.assertIn(node.attrib.get(attribute), expected_values)

    def assertXmlNode(
        self,
        node: Any,
        *,
        tag: Union[str, None] = None,
        text: Union[str, None] = None,
        text_in: Union[tuple, None] = None,
    ):
        """Assert ``node`` is an element node.

        :param node: Element node
        :param tag: Expected node's tag name
        :param text: Expected node's text value
        :param text_in: Accepted node's text values

        This method tests that ``node`` is an element node. It can also test
        that it has the expected ``tag`` and/or ``text``, and/or that the text
        is one of ``text_in``.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<root>some_value</root>\"\"\"
                root = self.assertXmlDocument(data.encode('utf-8'))

                # All these tests will pass
                self.assertXmlNode(root)
                self.assertXmlNode(root, tag='root')
                self.assertXmlNode(root, tag='root', text='some_value')
                self.assertXmlNode(
                    root, tag='root', text_in=('some_value', 'other')
                )

            # ...

        """
        # Assert `node` is an element node and not None or a string or
        # anything like this
        self.assertIsInstance(node, etree._Element)

        if tag is not None:
            self.assertEqual(node.tag, tag)

        if text is not None:
            self.assertEqual(node.text, text)

        if text_in is not None:
            self.assertIn(node.text, text_in)

    def assertXpathsExist(
        self,
        node,
        xpaths: tuple,
        default_ns_prefix: str = 'ns',
    ):
        """Assert at least one value is found for each ``xpaths``.

        :param node: Element node
        :param xpaths: List of XPath expressions
        :param default_ns_prefix: Optional, value of the default namespace
                                  prefix

        This method tests that all XPath expressions from ``xpaths``
        evaluate on ``node`` to at least one element or a not ``None`` value.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<root rootAtt="value">
                    <child>value</child>
                    <child att="1"/>
                    <child att="2"/>
                </root>\"\"\"
                root = self.assertXmlDocument(data.encode('utf-8'))

                # All these XPath expression returns a not `None` value.
                self.assertXpathsExist(
                    root, ('@rootAtt', './child', './child[@att="1"]')
                )

            # ...

        """
        expressions = self.build_xpath_expressions(node,
                                                   xpaths,
                                                   default_ns_prefix)
        for expression in expressions:
            try:
                if not expression(node):
                    self.fail_xpath_not_found(node, expression)
            except etree.XPathEvalError as error:
                self.fail_xpath_error(node, expression.path, error)

    def assertXpathsOnlyOne(
        self,
        node,
        xpaths: tuple,
        default_ns_prefix: str = 'ns',
    ):
        """Assert ``xpaths`` expressions return only one element each.

        :param node: Element node
        :param xpaths: List of XPath expressions
        :param default_ns_prefix: Optional, value of the default namespace
                                  prefix

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<root>
                    <child att="1"/>
                    <child att="2"/>
                    <unique>this element is unique</unique>
                </root>\"\"\"
                root = self.assertXmlDocument(data.encode('utf-8'))

                # All these XPath expression returns only one result
                self.assertXpathsOnlyOne(
                    root, ('./unique', './child[@att="1"]')
                )

            # ...
        """
        expressions = self.build_xpath_expressions(node,
                                                   xpaths,
                                                   default_ns_prefix)

        for expression in expressions:
            try:
                results = expression(node)
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

    def assertXpathsUniqueValue(
        self,
        node,
        xpaths: tuple,
        default_ns_prefix: str = 'ns',
    ):
        """Assert values found by ``xpaths`` are unique per XPath expression.

        :param node: Element node
        :param xpaths: List of XPath expressions
        :param default_ns_prefix: Optional, value of the default namespace
                                  prefix

        This method tests that all the values are unique per XPath expression.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<?xml version="1.0" encoding="UTF-8" ?>
                <root>
                    <sub subAtt="unique" id="1">unique 1</sub>
                    <sub subAtt="notUnique" id="2">unique 2</sub>
                    <sub subAtt="notUnique" id="3">unique 3</sub>
                    <multiple>twice</multiple>
                    <multiple>twice</multiple>
                </root>\"\"\"
                root = self.assertXmlDocument(data.encode('utf-8'))

                # This will pass
                self.assertXpathsUniqueValue(
                    root, ('./sub/@id', './sub/text()')
                )

                # These won't pass
                self.assertXpathsUniqueValue(root, ('./sub/@subAtt',))
                self.assertXpathsUniqueValue(root, ('./multiple/text()',))

            # ...

        """
        expressions = self.build_xpath_expressions(node,
                                                   xpaths,
                                                   default_ns_prefix)

        for expression in expressions:
            try:
                results = expression(node)
            except etree.XPathEvalError as error:
                self.fail_xpath_error(node, expression.path, error)

            if len(results) != len(set(results)):
                self.fail('Value is not unique for element %s:\n'
                          'XPath: %s\n'
                          'Element:\n%s'
                          % (node.tag, expression.path,
                             etree.tostring(node, pretty_print=True)))

    def assertXpathValues(
        self,
        node,
        xpath: str,
        values: tuple,
        default_ns_prefix: str = 'ns',
    ):
        """Assert all values found by ``xpath`` match expected ``values``.

        :param node: Element node
        :param xpath: XPath expression to select elements
        :param values: List of accepted values
        :param default_ns_prefix: Optional, value of the default namespace
                                  prefix

        This method tests if all the values found from the given XPath
        expression match any element in ``values``.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                data = \"\"\"<?xml version="1.0" encoding="UTF-8" ?>
                <root>
                    <sub id="1">a</sub>
                    <sub id="2">a</sub>
                    <sub id="3">b</sub>
                    <sub id="4">c</sub>
                </root>\"\"\"
                root = self.assertXmlDocument(data.encode('utf-8'))

                # Select attribute's value
                self.assertXpathValues(root, './sub/@id', ('1', '2', '3', '4'))
                # Select node's text value
                self.assertXpathValues(root, './sub/text()', ('a', 'b', 'c'))

            # ...

        """
        expression = self.build_xpath_expression(node,
                                                 xpath,
                                                 default_ns_prefix)
        try:
            results = expression(node)
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
        """Assert XML node is valid according to a DTD.

        :param node: Node element to valid using a DTD
        :param dtd: DTD used to valid the given node element. Can be a string
                    or an LXML DTD element
        :param filename: Path to the expected DTD for validation.

        This method tests if the given ``node`` complies with a DTD.
        This DTD can be provided as a string, as a :py:class:`lxml.etree.DTD`
        object, or from a file (with the ``filename`` parameter).

        .. rubric:: Example using a filename

        ::

            def my_custom_test(self):
                \"\"\"Check XML generated using DTD at path/to/file.dtd.

                The content of the DTD file is:

                    <!ELEMENT root (child)>
                    <!ELEMENT child EMPTY>
                    <!ATTLIST child id ID #REQUIRED>

                \"\"\"
                dtd_filename = 'path/to/file.dtd'
                data = \"\"\"<?xml version="1.0" encoding="utf-8"?>
                <root>
                    <child id="child1"/>
                </root>
                \"\"\"
                root = test_case.assertXmlDocument(data.encode('utf-8'))
                self.assertXmlValidDTD(root, filename=dtd_filename)

        """
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
        """Assert XML node is valid according to a XML Schema.

        :param node: Node element to valid using an XML Schema
        :param xschema: XMLSchema used to valid the given node element.
                        Can be a string or an LXML XMLSchema element
        :param filename: Path to the expected XMLSchema for validation.

        This method tests if the given ``node`` complies with an XML schema.
        This schema can be provided as a string, as a
        :py:class:`lxml.etree.XMLSChema` object, or from a file (with the
        ``filename`` parameter).

        .. rubric:: Example using a filename

        ::

            def my_custom_test(self):
                \"\"\"Check XML using XMLSchema at path/to/xschema.xml.

                The content of the XMLSchema file is::

                    <?xml version="1.0" encoding="utf-8"?>
                    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <xsd:element name="root">
                        <xsd:complexType>
                            <xsd:sequence>
                                <xsd:element
                                    name="child"
                                    minOccurs="1"
                                    maxOccurs="1"
                                >
                                    <xsd:complexType>
                                        <xsd:simpleContent>
                                            <xsd:extension base="xsd:string">
                                                <xsd:attribute
                                                    name="id"
                                                    type="xsd:string"
                                                    use="required"
                                                />
                                            </xsd:extension>
                                        </xsd:simpleContent>
                                    </xsd:complexType>
                                </xsd:element>
                            </xsd:sequence>
                        </xsd:complexType>
                    </xsd:element>
                    </xsd:schema>

                \"\"\"
                xschema_filename = 'path/to/xschema.xml'
                data = \"\"\"<?xml version="1.0" encoding="utf-8"?>
                <root>
                    <child id="child1"/>
                </root>
                \"\"\"
                root = test_case.assertXmlDocument(data.encode('utf-8'))
                self.assertXmlValidXSchema(root, filename=xschema_filename)

        """
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

    def assertXmlValidRelaxNG(
        self,
        node,
        relaxng=None,
        filename=None,
        encoding='utf-8',
    ):
        """Assert XML node is valid according to a RelaxNG schema.

        :param node: Node element to valid using a RelaxNG
        :param relaxng: RelaxNG used to valid the given node element.
                        Can be a string or an LXML RelaxNG element
        :param filename: Path to the expected RelaxNG for validation.
        :param encoding: expected encoding for the file

        This method tests if the given ``node`` complies with a RelaxNG schema.
        This schema can be provided as a string, as a
        :py:class:`lxml.etree.RelaxNG` object, or from a file (with the
        ``filename`` parameter).

        .. rubric:: Example using a filename

        ::

            def my_custom_test(self):
                \"\"\"Check XML generated using RelaxNG at path/to/relaxng.xml.

                The content of the RelaxNG file is:

                    <?xml version="1.0" encoding="utf-8"?>
                    <rng:element
                        name="root"
                        xmlns:rng="http://relaxng.org/ns/structure/1.0"
                    >
                        <rng:element name="child">
                            <rng:attribute name="id">
                                <rng:text />
                            </rng:attribute>
                        </rng:element>
                    </rng:element>

                \"\"\"
                relaxng_filename = 'path/to/relaxng.xml'
                data = \"\"\"<?xml version="1.0" encoding="utf-8"?>
                <root>
                    <child id="child1"/>
                </root>
                \"\"\"
                root = test_case.assertXmlDocument(data.encode('utf-8'))
                self.assertXmlValidRelaxNG(root, filename=relaxng_filename)

        """
        schema = None

        if relaxng is not None and not isinstance(relaxng, etree.RelaxNG):
            schema = etree.RelaxNG(etree.XML(relaxng))
        elif isinstance(relaxng, etree.RelaxNG):
            schema = relaxng

        if relaxng is None and filename is not None:
            with open(filename, 'r', encoding=encoding) as relaxng_file:
                schema = etree.RelaxNG(
                    etree.XML(relaxng_file.read().encode(encoding)))

        if schema is None:
            raise ValueError('No valid RelaxNG given.')

        if not schema.validate(node):
            self.fail(schema.error_log.last_error)

    def assertXmlEquivalentOutputs(
        self,
        data: Union[str, bytes],
        expected: Union[str, bytes],
    ):
        """Asserts both XML outputs are equivalent.

        :param data: XML formated string to check
        :param expected: XML formated string used as reference

        This assertion uses the powerful but dangerous feature of
        ``LXMLOutputChecker``. Powerful because one can compare two XML
        document in their meaning, but dangerous because sometimes there is
        more to check than just a kind of output.

        See ``LXMLOutputChecker`` documentation for more information.

        Asserts both XML formated string are equivalent. The comparison ignores
        spaces within nodes and namespaces may be associated to diffrerent
        prefixes, thus requiring only the same URL.

        If a difference is found, an :py:exc:`AssertionError` is raised, with
        the comparison failure's message as error's message.

        .. note::

            The name ``assertXmlEquivalentOutputs`` is a way to prevent
            user to missunderstand the meaning of this assertion: it checks
            only similar **outputs**, not **document**.

        .. note::

            This method only accept a string (either ``str`` or ``bytes``) as
            arguments. This is an opinionated implementation choice, as the
            purpose of this method is to check the result outputs of an XML
            document, and not the document itself.

        .. rubric:: Example

        ::

            # ...

            def test_custom_test(self):
                \"\"\"Same XML (with variable output)\"\"\"
                # This XML string should come from the code one want to test
                data = b\"\"\"<?xml version="1.0" encoding="UTF-8" ?>
                <root><tag bar="foo" foo="bar"> foo </tag></root>\"\"\"

                # This is the former XML document one can expect,
                # pretty printed
                expected = b\"\"\"<?xml version="1.0" encoding="UTF-8" ?>
                <root>
                    <tag foo="bar" bar="foo">foo</tag>
                </root>\"\"\"

                # This will pass
                test_case.assertXmlEquivalentOutputs(data, expected)

                # This is another example of result, with a missing attribute
                data = b\"\"\"<?xml version="1.0" encoding="UTF-8" ?>
                <root>
                    <tag foo="bar"> foo </tag>
                </root>
                \"\"\"

                # This won't pass
                test_case.assertXmlEquivalentOutputs(data, expected)

        """
        checker = LXMLOutputChecker()

        if not checker.check_output(expected, data, PARSE_XML):
            self.fail('Output are not equivalent:\n'
                      'Given: %s\n'
                      'Expected: %s'
                      % (data, expected))


class XmlTestCase(unittest.TestCase, XmlTestMixin):
    """Test case for XML document with ``lxml`` and ``unittest``.

    This can serve as a base class for any test case using unittest::

        import xmlunittest

        class MyTestCase(xmlunittest.XmlTestCase):
            def test_my_case(self):
                # use XmlTestCase's assertion methods
                ...

    This class extends :py:class:`unittest.TestCase` and
    :py:class:`XmlTestMixin`. If you want a description of assertion methods,
    you should read next the description of base class
    :py:class:`XmlTestMixin`.
    """
