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

You will be able to test your XML document, and use the power of xpath to
write tests that matter.


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


Assertion methods
=================

.. py:class:: XmlTestCase

   Base class one must extends to use XML assertion methods. As this class
   only provide `assert*` methods, there is nothing more to do.

   Simple as it always should be.


Document assertions
-------------------

.. py:method:: XmlTestCase.assertXmlDocument(data)

   :param string data: XML formated string
   :rtype: lxm.etree._Element

   Assert `data` is a valid XML formated string. This method will parse string
   with `lxml.etree.fromstring`. If parsing failed (raise an XMLSyntaxError),
   the test fails.


Element assertions
------------------

.. py:method:: XmlTestCase.assertXmlNamespace(node, prefix, uri)

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

          root = test_case.assertXmlDocument(data)

          self.assertXmlNamespace(root, 'ns', 'uri')

      # ...

.. py:method:: XmlTestCase.assertXmlHasAttribute(node, attribute, **kwargs)

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


.. py:method:: XmlTestCase.assertXmlNode(node, **kwargs)

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

.. py:method:: XmlTestCase.assertXpathsExist(node, xpaths)

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


.. py:method:: XmlTestCase.assertXpathsOnlyOne(node, xpaths)

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

.. py:method:: XmlTestCase.assertXpathsUniqueValue(node, xpaths)

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


.. py:method:: XmlTestCase.assertXpathValues(node, xpath, values)

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
