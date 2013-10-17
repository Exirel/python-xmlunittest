===============================================
Welcome to Python XML Unittest's documentation!
===============================================

.. toctree::
   :maxdepth: 2

Why XML Unittest?
=================

Anyone uses XML, for RSS, for configuration files, for... well, we all use XML
for our own reasons (folk says one can not simply uses XML, but still...).

So, your code generates XML, and everything is fine. As you follow best
practices (if you don't, I think you should), you have written some good
unit-test, where you compare code's result with an expected result. I mean you
compare string with string. Do you see the issue here? If you don't, well, good
for you. I see a lot of issue with this approach.

XML is not a simple string, it is a structured document. One can not simply
compare two XML string and expect all being fine: attributes's order can change
unexpectedly, elements can be optional, and no one can explain simply how
spaces and tabs works in XML formatting.

Here comes XML unittest TestCase: if you want to use the built-in
:py:mod:`unittest` package (or if it is a requirement), and you are not afraid
of using xpath expression with `lxml`__, this library is made for you.

You will be able to test your XML document, and use the power of xpath
to write tests that matter.

.. __: http://lxml.de/


Simple example
==============

Before we dive into explanations of code, here are some simple examples to
see how :py:mod:`xmlunittest` can be used::

    import xmlunittest
    
    
    class SampleTestCase(xmlunittest.XmlTestCase):
    
        def test(self):
            data = """<?xml version="1.0" encoding="UTF-8" ?>
            <root>
                <child id="1">a</child>
                <child id="2">b</child>
                <child id="3">c</child>
                <child id="4">b</child>
            </root>"""

            root = self.assertXmlDocument(data)
            self.assertXpathUniqueValue(root, './child/@id')
            self.assertXpathValues(root, './child/text()', ['a', 'b', 'c'])


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

