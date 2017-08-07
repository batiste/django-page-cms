=======================
Contribute to Gerbi CMS
=======================

I recommend to `create a fork on github  <http://github.com/batiste/django-page-cms>`_ and
make modifications in your branch. Please follow those instructions:

  * Add your name to the AUTHORS file.
  * Write tests for any new code. Try to keep the test coverage >= 90%.
  * Follow the PEP-08 as much as possible.
  * If a new dependency is introduced, justify it.
  * Be careful of performance regresssion.
  * Every new CMS setting should start with PAGE_<something>
  * Every new template_tag should start with pages_<something>

Then create a pull request. A short explanation of what you did and why you did it goes a long way.

Write tests
-----------

Gerbi CMS try to keep the code base stable. The test coverage is higher
than 90% and we try to keep it that way.

To run all the tests::

    $ python pages/test_runner.py

To run a specific test case::

    $ python pages/test_runner.py pages.tests.test_selenium.SeleniumTestCase

To run a specific test in a test case::

    $ python pages/test_runner.py pages.tests.test_selenium.SeleniumTestCase.test_admin_move_page


Translations
------------

`We use transifex for translations <https://www.transifex.com/batiste/django-page-cms-1/>`_
