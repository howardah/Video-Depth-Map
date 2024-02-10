import os

def remove_temp_vars():
    if os.path.exists(".start_frame"):
        os.system("rm -f .start_frame")
    
    if os.path.exists(".start_time"):
        os.system("rm -f .start_time")

    if os.path.exists(".current_time"):
        os.system("rm -f .current_time")

    if os.path.exists(".last_time"):
        os.system("rm -f .last_time")

    if os.path.exists(".average_time"):
        os.system("rm -f .average_time")

def prepare():
    # Create .temp folder if it does not exist
    if not os.path.exists(".temp"):
        os.system("mkdir .temp")

    remove_temp_vars()



def clean_up(pid=""):
    # Remove the start_frame, .start_time, and .current_time files if they exist
    remove_temp_vars()

    # Check all output and frames folders in the .temp directory
    # And remove them if the lock.txt file does not exist
    for folder in os.listdir(".temp"):
        check_output = folder.startswith("output_")
        if pid:
            check_output = folder == f"output_{pid}"
        if check_output or folder.startswith("frames_"):
            if not os.path.exists(f".temp/{folder}/lock.txt"):
                os.system(f"rm -rf .temp/{folder}")

    # If the .temp directory is empty, remove it
    if not os.listdir(".temp"):
        os.system("rm -rf .temp")