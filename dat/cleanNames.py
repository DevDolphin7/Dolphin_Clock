import main, os

# Define module paths
main_class = main.Data(cleaning=True)
module_paths = main_class.module_paths
new_module_paths = []

# Define new module paths
for count, module_path in enumerate(module_paths):
    if not module_path.find(".") == len(module_path)-4:
        if module_path.rfind(".") > -1:
            new_module_paths.append(module_path[:module_path[:-4].rfind(".")] + ".pyc")

# Rename the modules
for count, module_path in enumerate(module_paths):
    os.rename(module_path,new_module_paths[count])
