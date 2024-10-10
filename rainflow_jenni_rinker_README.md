Summary  
-------  
Python code to count rainflow cycles (with or without Goodman correction)  
  
Notes  
-----  
Repository includes a demo script (`demo_rainflow.py`) and the module
(`rainflow.py`).

Rainflow function is a version of some [commonly used Matlab/C code](https://github.com/WISDEM/AeroelasticSE/tree/master/src/AeroelasticSE/rainflow)
that is converted to Python.

Dependencies  
------------  
Numpy >= v1.3

Usage  
-----  
To call the function in a script on array of turning points `ext_array`:  
```python
from rainflow import rainflow  
out_array = rainflow(ext_array)
```  
To run demo script from command line (Windows or UNIX-based):  
`$ python demo_rainflow.py`

License  
-------  
Copyright (C) 2015 Jennifer Rinker  
Email: jennifer.rinker@duke.edu  
Distributed under the GNU General Public License  