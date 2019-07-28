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
