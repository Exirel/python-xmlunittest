===================
Python XML-Unittest
===================

.. toctree::
   :maxdepth: 2

   xmlunittest

Anyone uses XML, for RSS, for configuration files, for... well, we all use XML
for our own reasons (folk says one can not simply uses XML, but still...).

So, your code generates XML, and everything is fine. As you follow best
practices (if you don’t, I think you should), you have written some good
unit-tests, where you compare code’s result with an expected result. I mean you
compare string with string. One day, something bad might happen.

XML is not a simple string, it is a structured document. One can not simply
compare two XML string and expect everything to be fine: attributes’s order can
change unexpectedly, elements can be optional, and no one can explain simply
how spaces and tabs works in XML formatting.

Here comes XML unittest TestCase: if you want to use the built-in unittest
package (or if it is a requirement), and you are not afraid of using xpath
expression with ``lxml``, this library is made for you.

You will be able to test your XML document, and use the power of xpath and
various schema languages to write tests that matter.


Links
=====

- Distribution: https://pypi.python.org/pypi/xmlunittest
- Documentation: http://python-xmlunittest.readthedocs.org/en/latest/
- Source: https://github.com/Exirel/python-xmlunittest


Compatibility
=============

Python ``xmlunittest`` has been tested with ``lxml`` version 4.0 and 5.0
with Python 3.10.


How to
======

- Extends :py:class:`xmlunittest.XmlTestCase`
- Write your tests, using the function or method that generate XML document
- Use ``xmlunittest.XmlTestCase``'s assertion methods to validate
- Keep your test readable!

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
           root = self.assertXmlDocument(data.encode('utf-8'))

           # Check namespace
           self.assertXmlNamespace(root, 'ns', 'uri')

           # Check
           self.assertXpathsUniqueValue(root, ('./leaf/@id', ))
           self.assertXpathValues(root, './leaf/@active', ('on', 'off'))


Alternativly, one can use the :py:class:`XmlTestMixin` instead of the
:py:class:`XmlTestCase`, as long as their own class also extends
:py:class:`unittest.TestCase`.

This is convenient when there is already a subclass of
:py:class:`unittest.TestCase` and one also wants to profit of XML assertions.


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

           self.assertXmlDocument(data.encode('utf-8'))


Contribute
==========

First of all, thanks for reading this!

You use ``xmlunittest`` and you have to write the same utility method again
and again? If it is related only to XML tests, maybe you can share it?

**Good!** How can you do that?

First, you can fork the `project's github repository`__, then you will need
some tools for development: all dependencies are available into the
``requirements.txt`` file. You should also use a virtualenv (use two for each
version, or use tox).

See an example of install (without virtualenv)::

   $ git clone git@github.com:YourRepo/python-xmlunittest.git xmlunittest
   $ cd xmlunittest
   $ pip install -r requirements.txt
   $ pytest test.py
   ... all should be green here!

.. __: https://github.com/Exirel/python-xmlunittest

.. note::

   Installing lxml is not easy if you are not prepared. You will need some
   extra source package on your favorite OS (in particular some XML libs and
   python sources).
