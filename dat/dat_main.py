import importlib, glob, sys, re
from os.path import dirname, basename, isfile, join
from os import walk as osWalk

class Data():
    def __init__(self,cleaning=False):
        # Set class variables
        self.packages = []
        self.package_path = []
        self.module_paths = []
        self.module_list = []
        self.cleaning = cleaning

        self.define_dat_packages()
        self.define_dat_modules()

    def define_dat_packages(self):
        # Define the packages that are in dat at initialization
        relative_path = ".\dat"
        if self.cleaning: relative_path = "./"
        
        all_dirs = [d[0] for d in osWalk(relative_path)]
        
        for dir_name in all_dirs:
            if dir_name == relative_path: continue
            if not "__" in dir_name:
                self.packages.append(dir_name.replace(".\dat","").replace("\\",""))
                # Add dir_name to sys.path to work after compiled
                sys.path.append(dir_name)

    def define_dat_modules(self):
        # Get dat package module paths
        for package in self.packages:
            self.package_path.append(dirname(__file__)+"\\"+package)

        # Create a list of modules in the dat packages
        for paths in self.package_path:
            all_module_paths = glob.glob(join(paths, "*.pyc"))
            for module_path in all_module_paths:
                self.module_paths.append(module_path)
        self.module_list = [ basename(f)[:-4] for f in self.module_paths if isfile(f) and not f.endswith('__init__.py')]

        # Check if any module names appear twice in dat
        if len(set(self.module_list)) < len(self.module_list):
            raise ImportError("Directory \"dat\" contains multiple modules with the same name.")

    def data(self, file_name):
        # Check if file_name is a valid module
        if not file_name in self.module_list:
            raise ValueError("The given module does not exist in the packages within dat")

        # Import the desired module
        for package in self.packages:
            try: data_module = importlib.import_module(file_name)
            except ModuleNotFoundError: pass

        # Return the data
        data = data_module.data()
        return data
