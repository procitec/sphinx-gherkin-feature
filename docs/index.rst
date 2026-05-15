sphinx-gherkin-feature
======================

This page demonstrates the ``gherkin:feature`` directive.

.. gherkin:feature::
   :filename: login

   Feature: Login

     Scenario: Successful login
       Given a user account exists
       When the user logs in
       Then the dashboard is shown

Generated files
---------------

With the configuration in ``docs/conf.py``, the example above is written to
``_build/html/features/login.feature`` when building HTML documentation.
