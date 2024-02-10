from depth_map.main import make_depth_maps
from depth_map.arguments import get_args, print_id, process_id
import os

# Copy the arguments to new variable
args = get_args()

if print_id():
    for arg in args:
        # Get the file name without extension
        file_name = os.path.splitext(os.path.basename(arg))[0]

        # Print the process id
        print(process_id(file_name))

    # Exit the program
    exit(0)

make_depth_maps(args)