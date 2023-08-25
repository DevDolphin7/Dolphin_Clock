Importing the modules with a blank __init__.py script will automatically make a compiles python script.
Copy / paste the .pyc and replace the .py file in the dat sub-directories.
Use cleanNames.py to remove the cython extention in the name (python can't import modules with "." in the name)


In your script:
from dat import main as data_main
...
self.dat = data_main.Data()
...
audio_visual_data = self.dat.data("file_name_without_extension")


Folder structure:
/program
programscript.py

        /dat
	main.py
	cleanNames.py - single use!

	    /img
	    __init__.py
	    image1.pyc

	    /etc
	    __init__.py
	    audioVisual2.pyc
