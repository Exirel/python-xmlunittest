.. py:module:: xmlunittest

===================
Python XML-Unittest
===================

.. toctree::
   :maxdepth: 2

Anyone uses XML, for RSS, for configuration files, for... well, we all use XML
for our own reasons (folk says one can not simply uses XML, but still...).

So, your code generates XML, and everything is fine. As you follow best
practices (if you don’t, I think you should), you have written some good
unit-tests, where you compare code’s result with an expected result. I mean you
compare string with string. Do you see the issue here? If you don’t, well,
good for you. I see a lot of issue with this approach.

XML is not a simple string, it is a structured document. One can not simply
compare two XML string and expect all being fine: attributes’s order can change
unexpectedly, elements can be optional, and no one can explain simply how
spaces and tabs works in XML formatting.

Here comes XML unittest TestCase: if you want to use the built-in unittest
package (or if it is a requirement), and you are not afraid of using xpath
expression with lxml, this library is made for you.

You will be able to test your XML document, and use the power of xpath and
various schema languages to write tests that matter.


Links
=====

- Distribution: https://pypi.python.org/pypi/xmlunittest
- Documentation: http://python-xmlunittest.readthedocs.org/en/latest/
- Source: https://github.com/Exirel/python-xmlunittest


How to
======

- Extends xmlunittest.XmlTestCase
- Write your tests, using the function or method that generate XML document
- Use xmlunittest.XmlTestCase‘s assertion methods to validate
- Keep your test readable

Example::

   from xmlunittest import XmlTestCase


   class CustomTestCase(XmlTestCase):

       def test_my_custom_test(self):
           # In a real case, data come from a call to your function/method.
           data = """<?xml version="1.0" encoding="UTF-8" ?>
           <root xmlns:ns="uri">
               <leaf id="1" active="on" />
               <leaf id="2" active="on" />
               <leaf id="3" active="off" />
           </root>"""

           # Everything starts with `assertXmlDocument`
           root = self.assertXmlDocument(data)

           # Check namespace
           self.assertXmlNamespace(root, 'ns', 'uri')

           # Check
           self.assertXpathsUniqueValue(root, ('./leaf@id', ))
           self.assertXpathValues(root, './leaf@active', ('on', 'off'))


Alternativly, one can use the :py:class:`XmlTestMixin` instead of the
:py:class:`XmlTestCase`, as long as its own class also extends
:py:class:`unittest.TestCase`.

This is convenient when there is already a subclass of
:py:class:`unittest.TestCase` and one whant to also profit of XML assertions.


Example::

   import unittest

   from xmlunittest import XmlTestMixin


   class CustomTestCase(unittest.TestCase, XmlTestMixin):

       def test_my_custom_test(self):
           # write exactly the same test as in previous example

           data = """<?xml version="1.0" encoding="UTF-8" ?>
           <root xmlns:ns="uri">
               <leaf id="1" active="on" />
               <leaf id="2" active="on" />
               <leaf id="3" active="off" />
           </root>"""

           self.assertXmlDocument(data)


Assertion methods
=================

.. py:class:: XmlTestCase

   Base class one can extends to use XML assertion methods. As this class
   only provide `assert*` methods, there is nothing more to do.

   Simple as it always should be.

   This class extends :py:class:`unittest.TestCase` and
   :py:class:`XmlTestMixin`. If you want a description of assertion methods,
   you should read next the description of base class :py:class:`XmlTestMixin`.


.. py:class:: XmlTestMixin

   Base class that only provide assertion methods. To use, one must extends
   both :py:class:`unittest.TestCase` and :py:class:`XmlTestMixin`. Of course,
   it can use any subclass of :py:class:`unittest.TestCase`, in combination
   with :py:class:`XmlTestMixin` without effort.

   For example::

      class TestUsingMixin(unittest.TestCase, xmlunittest.XmlTestMixin):

          def test_my_test(self):
              data = my_module.generate_xml()

              # unittest.TestCase assert
              self.assertIsNotNone(data)

              # xmlunittest.XmlTestMixin assert
              self.assertXmlDocument(data)


Document assertions
-------------------

.. py:method:: XmlTestMixin.assertXmlDocument(data)

   :param string data: XML formated string
   :rtype: lxml.etree._Element

   Assert `data` is a valid XML formated string. This method will parse string
   with `lxml.etree.fromstring`. If parsing failed (raise an XMLSyntaxError),
   the test fails.


.. py:method:: XmlTestMixin.assertXmlPartial(partial_data, root_tag=None)

   :param string partial_data: Partial document as XML formated string
   :rtype: lxml.etree._Element

   Assert `partial_data` is a partially XML formated string. This method will
   encapsulate the string into a root element, and then try to parse the string
   as a normal XML document.

   If the parsing failed, test will fail. If the parsing's result does not
   have any element child, the test will also fail, because it expects a
   *partial document**, not just a string.

   .. rubric:: Optional named arguments

   :param string root_tag: Optional, root element's tag name

   One can provide the root element's tag name to the method for his own
   convenience.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
          data = """
             <partial>a</partial>
             <partial>b</partial>
          """

          root = self.assertXmlPartial(data)
          # Make some assert on the result's document.
          self.assertXpathValues(root, './partial/text()', ('a', 'b'))

      # ...


Element assertions
------------------

.. py:method:: XmlTestMixin.assertXmlNamespace(node, prefix, uri)

   :param node: Element node
   :param string prefix: Expected namespace's prefix
   :param string uri: Expected namespace's URI

   Asserts `node` declares namespace `uri` using `prefix`.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
          data = """<?xml version="1.0" encoding="UTF-8" ?>
          <root xmlns:ns="uri"/>"""

          root = self.assertXmlDocument(data)

          self.assertXmlNamespace(root, 'ns', 'uri')

      # ...

.. py:method:: XmlTestMixin.assertXmlHasAttribute(node, attribute, **kwargs)

   :param node: Element node
   :param string attribute: Expected attribute's name (using `prefix:name`
      notation

   Asserts `node` has the given `attribute`.

   Argument `attribute` must be the attribute's name, with namespace's prefix
   (notation 'ns:att' and not '{uri}att').

   .. rubric:: Optional named arguments

   :param string expected_value: Optional, expected attribute's value
   :param tuple expected_values: Optional, list of accepted attribute's value

   `expected_value` and `expected_values` are mutually exclusive.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
         data = """<root a="1" />"""
         root = self.assertXmlDocument(data)

         # All these tests will pass
         self.assertXmlHasAttribute(root, 'a')
         self.assertXmlHasAttribute(root, 'a', expected_value='1')
         self.assertXmlHasAttribute(root, 'a', expected_values=('1', '2'))

      # ...


.. py:method:: XmlTestMixin.assertXmlNode(node, **kwargs)

   Asserts `node` is an element node, and can assert expected tag and value.

   .. rubric:: Optional named arguments

   :param string tag: Expected node's tag name
   :param string text: Expected node's text value
   :param tuple text_in: Accepted node's text values

   `text` and `text_in` are mutually exclusive.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
         data = """<root>some_value</root>"""
         root = self.assertXmlDocument(data)

         # All these tests will pass
         self.assertXmlNode(root)
         self.assertXmlNode(root, tag='root')
         self.assertXmlNode(root, tag='root', text='some_value')
         self.assertXmlNode(root, tag='root', text_in=('some_value', 'other'))

      # ...


XPath expression assertions
---------------------------

.. py:method:: XmlTestMixin.assertXpathsExist(node, xpaths)

   :param node: Element node
   :param tuple xpaths: List of XPath expressions

   Asserts each XPath from `xpaths` evaluates on `node` to at least one element
   or a not `None` value.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
         data = """<root rootAtt="value">
            <child>value</child>
            <child att="1"/>
            <child att="2"/>
         </root>"""
         root = self.assertXmlDocument(data)

         # All these XPath expression returns a not `None` value.
         self.assertXpathsExist(root, ('@rootAtt', './child', './child[@att="1"]'))

      # ...


.. py:method:: XmlTestMixin.assertXpathsOnlyOne(node, xpaths)

   :param node: Element node
   :param tuple xpaths: List of XPath expressions

   Asserts each XPath's result returns only one element.


   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
         data = """<root>
            <child att="1"/>
            <child att="2"/>
            <unique>this element is unique</unique>
         </root>"""
         root = self.assertXmlDocument(data)

         # All these XPath expression returns only one result
         self.assertXpathsOnlyOne(root, ('./unique', './child[@att="1"]'))

      # ...

.. py:method:: XmlTestMixin.assertXpathsUniqueValue(node, xpaths)

   :param node: Element node
   :param tuple xpaths: List of XPath expressions

   Asserts each XPath's result's value is unique in the selected elements.

   One can use this method to check node's value, and node's attribute's value,
   in a set of nodes selected by XPath expression.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
         data = """<?xml version="1.0" encoding="UTF-8" ?>
         <root>
            <sub subAtt="unique" id="1">unique 1</sub>
            <sub subAtt="notUnique" id="2">unique 2</sub>
            <sub subAtt="notUnique" id="3">unique 3</sub>
            <multiple>twice</multiple>
            <multiple>twice</multiple>
         </root>"""
         root = self.assertXmlDocument(data)

         # This will pass
         self.assertXpathsUniqueValue(root, ('./sub/@id', './sub/text()'))

         # These won't pass
         self.assertXpathsUniqueValue(root, ('./sub/@subAtt',))
         self.assertXpathsUniqueValue(root, ('./multiple/text()',))

      # ...


.. py:method:: XmlTestMixin.assertXpathValues(node, xpath, values)

   :param node: Element node
   :param string xpath: XPath expression to select elements
   :param tuple values: List of accepted values

   Asserts each selected element's result from XPath expression is in the list
   of expected values.


   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
         data = """<?xml version="1.0" encoding="UTF-8" ?>
         <root>
            <sub id="1">a</sub>
            <sub id="2">a</sub>
            <sub id="3">b</sub>
            <sub id="4">c</sub>
         </root>"""
         root = self.assertXmlDocument(data)

         # Select attribute's value
         self.assertXpathValues(root, './sub/@id', ('1', '2', '3', '4'))
         # Select node's text value
         self.assertXpathValues(root, './sub/text()', ('a', 'b', 'c'))

      # ...


XML documents comparison assertion
----------------------------------

.. py:method:: XmlTestMixin.assertXmlEquivalent(got, expect)

   :param got: XML as text or Element node
   :param expect: XML as text

   Asserts both XML are equivalent. The comparison ignores spaces within nodes
   and namespaces - if any - may be associated to diffrerent prefixes.

   If a difference is found, a :class:`AssertionError` is raised. You can have
   the detailed mismatch in ``str(exc)``, ``exc`` being the raised exception.

   .. rubric:: Example

   ::

      # ...

      def test_custom_test(self):
          # Same XML (with different spacings placements and attrs order)
          got = b"""<?xml version="1.0" encoding="UTF-8" ?>
          <root>
              <tag foo="bar" bar="foo">foo</tag>
          </root>"""
          got_root = self.assertXmlDocument(got)
          expected = b"""<?xml version="1.0" encoding="UTF-8" ?>
          <root><tag bar="foo" foo="bar"> foo </tag></root>"""

          self.assertXmlEquivalent(got, expected)
          self.assertXmlEquivalent(got_root, expected)

          # Same XML, but with different namespace prefixes
          got = b"""<?xml version="1.0" encoding="UTF-8" ?>
          <root xmlns:foo="mynamespace">
              <foo:tag>foo</foo:tag>
          </root>"""
          got_root = self.assertXmlDocument(got)
          expected = b"""<?xml version="1.0" encoding="UTF-8" ?>
          <root xmlns:bar="mynamespace">
              <bar:tag>foo</bar:tag>
          </root>"""
          self.assertXmlEquivalent(got, expected)
          self.assertXmlEquivalent(got_root, expected)

          # Check comparison failure
          got = b"""<?xml version="1.0" encoding="UTF-8" ?>
          <root xmlns:foo="mynamespace">
              <foo:tag> difference here </foo:tag>
          </root>"""
          got_root = self.assertXmlDocument(got)
          with self.assertRaises(self.failureException):
              self.assertXmlEquivalent(got, expected)
          with self.assertRaises(self.failureException):
              self.assertXmlEquivalent(got_root, expected)


XML schema conformance assertion
--------------------------------

The following methods let you check the conformance of an XML document or node
according to a schema. Any validation schema language that is supported by
`lxml <http://lxml.de/>`_ may be used:

- DTD
- XSchema
- RelaxNG
- Schematron

Please read `Validation with lxml <http://lxml.de/validation.html>`_ to build
your own schema objects in these various schema languages.


.. py:method:: XmlTestMixin.assertXmlValidDTD(node, dtd=None, filename=None)

   :param node: Node element to valid using a DTD
   :type node: :py:class:`lxml.etree.Element`

   Asserts that the given `node` element can be validated successfuly by
   the given DTD.

   The DTD can be provided as a simple string, or as a previously parsed DTD
   using :py:class:`lxml.etree.DTD`. It can be also provided by a filename.

   .. rubric:: Optional arguments

   One can provide either a DTD as a string, or a DTD element from LXML, or
   the filename of the DTD.

   :param dtd: DTD used to valid the given node element.
               Can be a string or an LXML DTD element
   :type dtd: `string` | :py:class:`lxml.etree.DTD`
   :param string filename: Path to the expected DTD for validation.

   `dtd` and `filename` are mutualy exclusive.

   .. rubric:: Example using a filename

   ::

      def my_custom_test(self):
          """Check XML generated using DTD at path/to/file.dtd.

          The content of the DTD file is:

              <!ELEMENT root (child)>
              <!ELEMENT child EMPTY>
              <!ATTLIST child id ID #REQUIRED>

          """
          dtd_filename = 'path/to/file.dtd'
          data = b"""<?xml version="1.0" encoding="utf-8"?>
          <root>
             <child id="child1"/>
          </root>
          """
          root = test_case.assertXmlDocument(data)
          self.assertXmlValidDTD(root, filename=dtd_filename)


.. py:method:: XmlTestMixin.assertXmlValid(xml, schema)

   :param xml: XML to validate as text or Element node
   :param schema: Any schema object provided by lxml

   Asserts the XML document or Element node complies with the structure and
   data constraints from the schema.

   If this method raises an :class:`AssertionError` exception, ``str(exc)``
   provides details about validation issues, ``exc`` being the exception
   object.

   .. rubric:: Example

   ::

      import io
      from lxml import etree

      # ...

      # Our old style DTD
      dtd = """<!ELEMENT root (child*)>
      <!ELEMENT child (#PCDATA)>
      <!ATTLIST child name CDATA #IMPLIED>
      """
      dtd = etree.DTD(io.StringIO(dtd))  # -> DTD objet

      # Same in XSchema (noisy)
      xschema = """<?xml version="1.0"?>
      <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <xsd:element name="root">
          <xsd:complexType>
            <xsd:sequence>
              <xsd:element name="child" minOccurs="0" maxOccurs="unbounded">
                <xsd:complexType>
                  <xsd:simpleContent>
                    <xsd:extension base="xsd:string">
                      <xsd:attribute name="name" type="xsd:string" use="optional" />
                    </xsd:extension>
                  </xsd:simpleContent>
                </xsd:complexType>
              </xsd:element>
            </xsd:sequence>
          </xsd:complexType>
        </xsd:element>
      </xsd:schema>
      """
      xschema = etree.XMLSchema(etree.XML(xschema))  # -> XMLSchema object

      # Same in RelaxNG
      relaxng = """<rng:element name="root" xmlns:rng="http://relaxng.org/ns/structure/1.0">
        <rng:zeroOrMore>
          <rng:element name="child">
            <rng:optional>
              <rng:attribute name="name">
                <rng:text />
              </rng:attribute>
            </rng:optional>
            <rng:text />
          </rng:element>
        </rng:zeroOrMore>
      </rng:element>
      """
      relaxng = etree.RelaxNG(etree.XML(relaxng))  # -> RelaxNG object

      # ...

      valid_xml = b"""<?xml version="1.0" encoding="UTF-8" ?>
      <root>
        <child name="hello">blah blah</child>
        <child>hello</child>
      </root>
      """
      valid_xml = etree.XML(valid_xml)

      invalid_xml = b"""<?xml version="1.0" encoding="UTF-8" ?>
      <root>
        <child name="hello">blah blah</child>
        <father>hello</father>
      </root>
      """
      invalid_xml = etree.XML(invalid_xml)

      class MyValidationTests(XmlTestCase):

          # ...

          def _test_validate(self, schema):
              """Common test method
              """
              # Valid is valid
              self.assertXmlValid(valid_xml, schema)

              # As well as invalid is invalid
              with self.assertRaises(self.failureException) as cm:
                  self.assertXmlValid(invalid_xml, schema)

              # And we have a trace of the unknown element in the error message
              self.assertIn('father', str(cm.exception))


          def test_validate_all(self):
              """Checking our XML (in) valid stuffs with various schemas
              """
              self._test_validate(dtd)
              self._test_validate(xschema)
              self._test_validate(relaxng)
