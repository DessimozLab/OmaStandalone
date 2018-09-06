OMA Standalone - orthology inference pipeline among custom and public genomes
-----------------------------------------------------------------------------

The `OMA (Orthologous MAtrix) database <https://omabrowser.org>`_ is a leading 
resource for identifying orthologs, that are homologous genes started diverging
through a speciation event, among publicly available complete genomes. Orthologs
are essential for many applications in molecular biology, including gene function
prediction or species tree reconstruction.

OMA standalone is a standalone package that can infer orthologs with the OMA
algorithm for custom genomes. It is possible to `export genomes
<https://omabrowser.org/export>`_ and their homology relations directly from
the OMA web-browser and combine them with custom genomes or proteomes. 


Documentation
=============

The documentation of OMA standalone is available from `here <https://omabrowser.org/standalone>`_.


Installation
============

We provide `compiled and packaged versions of OMA standalone <https://omabrowser.org/standalone>`_
on the OMA Browser website for Linux and MacOSX. OMA does not run on Windows.

You can also install OMA standalone via `Homebrew <https://brew.sh/>`_ or 
`Linuxbrew <http://linuxbrew.sh/>`_:

.. code-block:: bash
    
    brew tap brewsci/bio
    brew install oma

If you want to use OMA standalone from this repository, make sure you have 
`Darwin <http://bio-recipes.com/darwin/>`_ installed on your system.
