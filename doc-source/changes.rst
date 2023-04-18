========================
Major changes in 2.x
========================

In ``dom_toml`` 2.x the API has changed considerably. 

The ``loads`` function has been replaced by that from the Python :mod:`tomllib` module (or ``tomli`` on older Python versions).
As a result, the ``decoder`` and ``dict_`` arguments have been removed from ``loads`` and :func:`load`.
The ``dom_toml.decoder`` module has also been removed.