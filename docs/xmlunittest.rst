.. py:module:: xmlunittest

===============
Test assertions
===============

.. autoclass:: XmlTestCase

.. autoclass:: XmlTestMixin


Document assertions
===================

.. automethod:: XmlTestMixin.assertXmlDocument

.. automethod:: XmlTestMixin.assertXmlPartial


Element assertions
==================

.. automethod:: XmlTestMixin.assertXmlNamespace

.. automethod:: XmlTestMixin.assertXmlHasAttribute

.. automethod:: XmlTestMixin.assertXmlNode


XPath expression assertions
===========================

.. automethod:: XmlTestMixin.assertXpathsExist

.. automethod:: XmlTestMixin.assertXpathsOnlyOne

.. automethod:: XmlTestMixin.assertXpathsUniqueValue

.. automethod:: XmlTestMixin.assertXpathValues


XML schema conformance assertion
================================

The following methods let you check the conformance of an XML document or node
according to a schema. Any validation schema language that is supported by
`lxml <http://lxml.de/>`_ may be used:

- DTD
- XSchema
- RelaxNG
- Schematron

Please read `Validation with lxml <http://lxml.de/validation.html>`_ to build
your own schema objects in these various schema languages.

.. automethod:: XmlTestMixin.assertXmlValidDTD

.. automethod:: XmlTestMixin.assertXmlValidXSchema

.. automethod:: XmlTestMixin.assertXmlValidRelaxNG


XML documents comparison assertion
==================================

Sometimes, one may want to check a global XML document, because they know
exactly what is expected, and can rely on a kind of "string compare". Of
course, XML is not a simple string, and requires more than just an
``assert data == expected``, because order of elements can vary, order of
attributes too, namespaces can come into play, etc.

In these cases, one can use the powerful - also dangerous - feature of `LXML
Output Checker`. See also the documentation of the module
`doctestcompare <http://lxml.de/api/lxml.doctestcompare-module.html>`_ for
more information on the underlying implementation.

And as always, remember that the whole purpose of this :py:mod:`xmlunittest`
is to **avoid** any comparison of XML formated strings. But, whatever, this
function could help. Maybe.

.. automethod:: XmlTestMixin.assertXmlEquivalentOutputs(data, expected)
