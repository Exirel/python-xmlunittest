===================
Python XML-Unittest
===================

.. image:: https://travis-ci.org/Exirel/python-xmlunittest.svg?branch=master
    :target: https://travis-ci.org/Exirel/python-xmlunittest
.. image:: https://coveralls.io/repos/Exirel/python-xmlunittest/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/Exirel/python-xmlunittest?branch=master
.. image:: https://gemnasium.com/Exirel/python-xmlunittest.svg
    :target: https://gemnasium.com/Exirel/python-xmlunittest
.. image:: https://badge.fury.io/py/xmlunittest.svg
    :target: http://badge.fury.io/py/xmlunittest

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

- Extends ``xmlunittest.XmlTestCase``
- Write your tests, using the function or method that generate XML document
- Use xmlunittest.XmlTestCase‘s assertion methods to validate
- Keep your test readable

Example:

.. code-block:: python

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
            self.assertXpathsUniqueValue(root, ('./leaf/@id', ))
            self.assertXpathValues(root, './leaf/@active', ('on', 'off'))
