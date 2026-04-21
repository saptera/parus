:html_theme.sidebar_secondary.remove: true

.. Light-mode banner
.. image:: _static/banner.svg
   :class: only-light parus-banner
   :alt: PARUS

.. Dark-mode banner, redeclare to avoid white background injection
.. image:: _static/banner.svg
   :class: only-dark parus-banner
   :alt: PARUS

PARUS API Documentation
=======================

**PARUS** is a fully automated real-time spike analysis system.

This site documents the public Python API, generated directly from the project's Google-style docstrings.

----

.. grid:: 1 2 2 2
   :gutter: 3
   :margin: 2 2 0 0

   .. grid-item-card:: :octicon:`rocket;1.2em;sd-mr-1` Install
      :link: getting-started
      :link-type: ref

      Install ``parus`` from PyPI and start importing the modules in your own pipelines.

   .. grid-item-card:: :octicon:`book;1.2em;sd-mr-1` API Reference
      :link: _api/parus
      :link-type: doc

      Browse every public sub-package, module, class and function exposed by ``parus``.

   .. grid-item-card:: :octicon:`mark-github;1.2em;sd-mr-1` Source on GitHub
      :link: https://github.com/saptera/parus

      Read the source, file an issue, or contribute back to the project.

   .. grid-item-card:: :octicon:`search;1.2em;sd-mr-1` Index
      :link: genindex
      :link-type: ref

      Alphabetical index of every documented symbol.

----

.. _getting-started:

Getting Started
---------------

.. tab-set::

   .. tab-item:: PyPI

      .. code-block:: bash

         pip install parus

      .. warning::

         ``pip`` cannot detect your local **CUDA** runtime, so the CPU-only build of
         `PyTorch <https://pytorch.org/get-started/locally/>`_ is pulled in by default.
         For GPU acceleration, install a CUDA-matched ``torch`` wheel **before** running the command above,
         or use the *With automation scripts* tab - it detects CUDA for you.

   .. tab-item:: From source

      .. code-block:: bash

         git clone https://github.com/saptera/parus.git
         cd parus
         pip install -e .

      .. warning::

         ``pip`` cannot detect your local **CUDA** runtime, so the CPU-only build of
         `PyTorch <https://pytorch.org/get-started/locally/>`_ is pulled in by default.
         For GPU acceleration, install a CUDA-matched ``torch`` wheel **before** running ``pip install -e .``,
         or use the *With automation scripts* tab - it detects CUDA for you.

   .. tab-item:: With automation scripts

      1. Download the source as a ZIP from
         `the GitHub repository <https://github.com/saptera/parus>`_
         (*Code* → *Download ZIP*) and extract it.
      2. From the extracted project root, run the installer for your platform:

      .. tab-set::

         .. tab-item:: Linux / macOS

            .. code-block:: bash

               cd automation/POSIX
               ./install_parus.sh

         .. tab-item:: Windows

            .. code-block:: bat

               cd automation\Windows
               install_parus.bat

      The installer is interactive — follow the prompts to complete the setup.


Then import the sub-packages you need, for example:

.. code-block:: python

   from parus.fio import fdata
   from parus.data import sig

The full module layout is listed in the :doc:`API reference <_api/parus>`.

.. admonition:: Looking for the CLI or GUI?
   :class: note

   The ``parus.scripts`` (command-line) and ``parus.gui`` (graphical) sub-packages
   are documented separately and are intentionally excluded from this API reference.


.. toctree::
   :hidden:
   :caption: Reference

   _api/parus
