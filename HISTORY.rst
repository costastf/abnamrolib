.. :changelog:

History
-------

0.0.1 (19-07-2019)
---------------------

* First code creation


0.1.0 (19-07-2019)
------------------

* initial code implementation


0.2.0 (20-07-2019)
------------------

* Exposed transaction objects


0.2.1 (20-07-2019)
------------------

* Reverted to default provided value for account transaction amount


0.3.0 (21-07-2019)
------------------

* Removed uneeded properties from account transaction


0.4.0 (21-07-2019)
------------------

* Exposed actually existing attribute


1.0.0 (24-07-2019)
------------------

* Initial working version with accounts, foreign accounts and transaction retrieval.


1.0.1 (25-07-2019)
------------------

* made credit card a Comparable


1.0.2 (25-07-2019)
------------------

* Generalized the comparison of Comparable objects


2.0.0 (26-07-2019)
------------------

* Implemented a credit card contract to make credit cards compatible with bank accounts


3.0.0 (26-07-2019)
------------------

* Refactored code to use external dependency and implemented a contract interface standardizing the retrieval of accounts.


3.0.1 (28-07-2019)
------------------

* Fixed session dropping issue


3.0.2 (28-07-2019)
------------------

* Made error in retrieving non breaking


3.0.3 (28-07-2019)
------------------

* Made retrieving of objects safe and implemented backoff for get methods


3.0.4 (28-07-2019)
------------------

* Removed unnecessary method call


3.0.5 (28-07-2019)
------------------

* Extended logging


3.0.6 (28-07-2019)
------------------

* Updated dependencies


3.0.7 (28-07-2019)
------------------

* Added logging


3.0.8 (28-07-2019)
------------------

* Updated logging


3.0.9 (28-07-2019)
------------------

* Removed unneeded logging


3.0.10 (30-07-2019)
-------------------

* Extended logging


3.1.0 (02-08-2019)
------------------

* Uniquely identify a transaction and an account


3.1.1 (16-08-2019)
------------------

* renamed underlying dependency and updated the code accordingly and fixed bug with a pop up covering the submission of the login.


3.2.0 (17-08-2019)
------------------

* Shortened timout on click event on log in.


3.2.1 (29-08-2019)
------------------

* Added latest popup window


4.0.0 (13-09-2019)
------------------

* Implemented cookie based authentication


5.0.0 (09-12-2019)
------------------

* Implemented cookie authentication for credit card and moved relevant shared code into a common module.


5.1.0 (10-12-2019)
------------------

* Implemented retrieving transaction by date, by ranges of dates and since a date.


5.2.0 (10-12-2019)
------------------

* Fixed name of method.


5.2.1 (26-10-2020)
------------------

* Fixed bug with new cookie header required by ICS.


5.2.2 (16-04-2021)
------------------

* Made retrieval by date ranges a bit stricter on the accepted input and bumped dependencies.


5.3.0 (06-07-2021)
------------------

* Implemented date retrieval, fixed a bug with short cookies.


5.3.1 (07-07-2021)
------------------

* Added pipeline and bumped dependencies.


5.3.2 (07-07-2021)
------------------

* Added pipeline and bumped dependencies.
