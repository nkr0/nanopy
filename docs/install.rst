Installation
############
nanopy includes ``C`` extensions for work generation and signing.

.. code-block:: bash

   sudo apt-get install gcc python3-dev
   pip install nanopy

* Instead of the default (``gcc``), point to another ``C`` compiler by prepending the installation command with ``CC=path/to/c/compiler``.
   .. code-block:: bash
   
      CC=path/to/c/compiler pip install nanopy

   * When using ``Visual C``, additionally prepend the installation command with ``USE_VC=1``.
      .. code-block:: bash
      
         CC=path/to/visual/c USE_VC=1 pip install nanopy

* For GPU, appropriate ``OpenCL ICD`` headers are required.
   .. code-block:: bash
   
      sudo apt-get install ocl-icd-opencl-dev nvidia/amd-opencl-icd

   * Enable GPU usage by prepending the installation command with ``USE_GPU=1``.
      .. code-block:: bash
      
         USE_GPU=1 pip install nanopy

