How to run OMA Standalone on diamond based homolog search
=========================================================

Requirements
------------

  - You need to have diamond compiled and either put it to the PATH or prefix the 
    calls to diamond with the full path to the binary

  - Create a python3 environment (tested with python 3.5) for the conversion script
    blast xml-format to darwin AllAll files. The following packages are required and 
    should be installable with pip:

.. code:: bash

        pip install Cython numpy
        pip install biopython
        pip install --no-binary pyopa pyopa


Running Diamond
---------------

Put your dataset into DB/. You then need to convert all fasta files to a diamond/blast database:

.. code:: sh

    # we first convert the genomes to OMA standalone format (this requires that oma is in the PATH,
    # otherwise full path to oma start script):
    oma -c
    
    cat DB/*fa > DB/diamond_all.faa
    diamond makedb --in DB/diamond_all.faa --db DB/diamond_all.db


Now, let's run diamond. The important part is to produce xml output and sensible 
values for the E-Value cutoff. So far, there are no good estimates what should be used.

.. code:: sh

    diamond blastp --db DB/diamond_all.db.dmnd --query DB/diamond_all.faa --compress 1 --evalue 1e-2 --outfmt 5 --out DB/diamond_matches.xml.gz --sensitive


alternative options would be 'more-sensitive', min bitscore, blocksize,... Fell free to investigate and to report back here!


Converting diamond matches to OMA Cache/AllAll
----------------------------------------------

The next step is now to convert the diamond output to the OMA Cache/DB and Cache/AllAll files (i.e. the type of Ouput that the All-All-Phase of OMA produces). Afterwards, we will continue with the rest of the OMA pipeline.

.. code:: sh

    # activate the virtual env if you didn not so far. eg:
    pyenv activate diamond-oma
    
    # run the conversion:
    python utils/blast_to_oma.py -v DB/diamond_matches.xml.gz DB/*fa


Once this has been run successfully, continue with the rest of the OmaStandalone pipeline. I suggest you make sure that you use the bottom-up HOGs (see parameters.drw) and fix the species tree if possible. also, turn off any un-needed output. see oma standalone docu for more info.

.. code:: sh

    oma


this should it be...



