from depth_map.log import logger
import sys

def test_mode():
    if print_id():
        return True
    if "-t" in sys.argv:
        return True
    if "--test" in sys.argv:
        return True
    return False

def quiet_mode():
    if "-q" in sys.argv:
        return True
    if "--quiet" in sys.argv:
        return True
    if "-nq" in sys.argv:
        return False
    if "--not-quiet" in sys.argv:
        return False
    if "--loud" in sys.argv:
        return False
    return True

def output():
    if "-o" in sys.argv:
        return sys.argv[sys.argv.index("-o") + 1]
    if "--output" in sys.argv:
        return sys.argv[sys.argv.index("--output") + 1]
    return ""

def output_ignored():
    args = get_args()
    if len(args) > 1 and output():
        return True
    return False

def print_id():
    if "--print-id" in sys.argv:
        return True
    
def process_averages():
    if "--average" in sys.argv:
        return True
    return False

zoe_processors = ["zoe", "zoe-nk", "ZoeD_NK", "zoe-n", "ZoeD_N", "zoe-k", "ZoeD_K"]
dpt_processors = ["dpt", "dpt-large", "dpt-hybrid"]

def processor():
    # accepted_processors = ["ZoeD_NK", "ZoeD_M12_NK"]
    accepted_processors = [*zoe_processors, "sd15", *dpt_processors]
    processor = "zoe"
    if "--processor" in sys.argv:
        processor = sys.argv[sys.argv.index("--processor") + 1]
    if "-p" in sys.argv:
        processor = sys.argv[sys.argv.index("-p") + 1]

    if processor in accepted_processors:
        return processor
    
    logger(f"Invalid processor: {processor} using zoe. Accepted processors: {accepted_processors}")

    return "zoe"

def set_out_format():
    accepted_formats = ["png", "jpg"]
    format = "jpg"
    if "-f" in sys.argv:
        format = sys.argv[sys.argv.index("-f") + 1]
    if "--format" in sys.argv:
        format = sys.argv[sys.argv.index("--format") + 1]
    if "--png" in sys.argv:
        format = "png"
    if "--jpg" in sys.argv:
        format = "jpg"
    
    if format in accepted_formats:
        return format
    
    logger(f"Invalid format: {format} rendering as jpg. Accepted formats: {accepted_formats}")
    return "jpg"

def keep_file_mode():
    if "--keep" in sys.argv:
        return True
    return False

out_format = set_out_format()

supported_flags = ["-t", "--test", "-q", "--quiet", "-nq", "--not-quiet", "--loud", "-f", "--format", "--png", "--jpg", "--keep", "--processor", "-p", "--output", "-o", "--print-id", "--average"]

def get_args():
    # Copy the arguments to new variable and remove all flags
    # as well as, for the case of -f and --format, the format
    # that follows it
    args = sys.argv[1:]

    for flag in supported_flags:
        if flag in args:
            if flag in ["-f", "--format"]:
                args.remove(args[args.index(flag) + 1])
            if flag in ["-p", "--processor"]:
                args.remove(args[args.index(flag) + 1])
            if flag in ["-o", "--output"]:
                args.remove(args[args.index(flag) + 1])
            args.remove(flag)

    # Check for unknown flags
    for arg in args:
        if arg[0] == "-":
            print(f"Unknown flag: {arg}")
            sys.exit(1)

    return args

def process_id(file_name):
    out = output()
    if not out or output_ignored():
        out_name = f"{file_name}_depth"
    else:
        # Get the file name without the path
        out_name = out.split("/")[-1]
        
        # Remove the file extension
        out_name = out_name.split(".")[0]

    processor_name = processor()

    return f"{out_name}_{processor_name}"

