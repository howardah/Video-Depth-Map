import os
from glob import glob
from datetime import timedelta
from depth_map.log import logger
from depth_map.arguments import keep_file_mode, process_id
import subprocess
from depth_map.processors import process_image

def process_frames(file_name):
    # Remove spaces from the file name
    file_name = file_name.replace(" ", "_")
    pid = process_id(file_name)
    output=""

    # If there are any output folders, check the lock.txt file in each folder
    # To see if the file name is the same as the current file name.
    # If a lock.txt file exists and the file name is the same, set the output folder to the current folder
    for folder in os.listdir(".temp"):
        if folder.startswith("output_"):
            if os.path.exists(f".temp/{folder}/lock.txt"):
                if open(f".temp/{folder}/lock.txt", "r").read().strip() == pid:
                    output = f".temp/{folder}"
                    break

    # If an existing output folder is not found, set the output folder to 'output_{file_name}'
    if not output:
        output = f".temp/output_{pid}"

        # If the output folder already exists, add a number to the end of the folder name
        if os.path.exists(output):
            i = 1
            while os.path.exists(f"{output}_{i}"):
                i += 1
            output = f"{output}_{i}"

    # Set frames folder path as input
    input = f".temp/frames_{file_name}"

    # Add id to lock.txt for the input folder
    os.system(f"echo {pid} >> {input}/lock.txt")

    # Create the output folder if it does not exist
    if not os.path.exists(output):
        os.system(f"mkdir {output}")

    # If lock.txt does not exist, create it and write the file name to it
    if not os.path.exists(f"{output}/lock.txt"):
        os.system(f"touch {output}/lock.txt")
        os.system(f"echo {pid} > {output}/lock.txt")

    # Load images from the 'frames' directory
    images = glob(f"{input}/*.jpg")
    images.sort()

    logger("Processing frames: 0.0%", temporary=True)

    # Set variables to help keep track of the process
    count = 0
    start_time_path = f"{output}/.start_time"
    last_time_path = f"{output}/.last_time"
    current_time_path = f"{output}/.current_time"
    average_time_path = f"{output}/.average_time"


    # Start timer to estimate the time it will take to process the frames
    os.system(f"date +'%s' > {start_time_path}")


    # Process each image
    for image in images:
        processed = process_image(image, output, input)

        if not processed:
            continue

        count += 1

        # Print progress
        current_frame = images.index(image) + 1
        total_frames = len(images)

        if os.path.exists(last_time_path):
            last_time = int(open(last_time_path, "r").read().strip())
        else:
            last_time = int(open(start_time_path, "r").read().strip())

        os.system(f"date +'%s' > {current_time_path}")
        current_time = int(open(current_time_path, "r").read().strip())

        delta_time = current_time - last_time
        average_time = delta_time

        if os.path.exists(average_time_path):    
            average_time = float(open(average_time_path, "r").read().strip())

        # Weighted average of the time it takes to process the frames
        # The weight is the number of frames processed or 19, whichever is larger
        # This allows the average to remain stable but also change quickly if the time to process
        # the frames changes dramatically
        weight = count if count > 19 else 19

        # Calculate the estimated time to process the frames
        average_time = (average_time * weight + delta_time) / (weight + 1)

        os.system(f"echo {(average_time)} > {average_time_path}")

        remaining_frames = total_frames - current_frame
        remaining_time = remaining_frames * average_time

        # Convert the estimated time to HH:MM:SS format
        estimated_time = str(timedelta(seconds=round(remaining_time)))

        # Save current_time to last_time file
        os.system(f"echo {current_time} > {last_time_path}")

        # Print progress as "Processing frames: x.x%" and clear the line before printing the next progress
        logger(f"Processing frames: {round(current_frame / total_frames * 100, 1)}% | Time Remaining ~{estimated_time}", temporary=True)

    # Remove the start_time, current_time, last_time, and average_time files if they exist
    for file in [start_time_path, last_time_path, current_time_path, average_time_path]:
        if os.path.exists(file):
            os.system(f"rm -f {file}")

    # Remove the lock.txt file
    if not keep_file_mode():
        os.system(f"rm {output}/lock.txt")

    # Remove the id from lock.txt
    os.system(f"sed -i'' -e '/{pid}/d' {input}/lock.txt")

    # If the lock.txt file is empty, remove it
    if os.stat(f"{input}/lock.txt").st_size == 0:
        os.system(f"rm {input}/lock.txt")

    logger(f"Finished processing {file_name}")

    return output



def export_frames(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0].replace(" ", "_")

    # Frames folder path
    frame_folder = f".temp/frames_{file_name}"

    # If the frames folder already exists, check if it was completely exported
    if os.path.exists(f"{frame_folder}"):
        if os.path.exists(f"{frame_folder}/export_complete.txt"):
            logger(f"Frames already exported for {file_path}")
            return len(glob(f"{frame_folder}/*.jpg"))
        
        # If the export was not complete, remove the folder and re-export the frames
        os.system(f"rm -r {frame_folder}")
        
    # (Re)Create the 'frames' directory 
    os.system(f"mkdir {frame_folder}")

    # Export the frames into the frames folder using ffmpeg
    export_frames=f"ffmpeg -i \"{file_path}\" -qmin 1 -qscale:v 1 -loglevel error -nostdin {frame_folder}/%08d.jpg"

    # Create a log file for ffmpeg
    os.system("touch ffmpeg_log.txt")

    with open("ffmpeg_log.txt", "w") as log_file:  # Open a log file in write mode
        subprocess.run(export_frames, shell=True, stdout=log_file, stderr=subprocess.STDOUT, check=True)

    # Add a text file which indicates that the export is complete
    os.system(f"touch {frame_folder}/export_complete.txt")

    # Log the number of frames extracted
    frames = len(glob(f"{frame_folder}/*.jpg"))
    logger(f"Extracted {frames} frames from {file_path}")

    return frames

def import_test():
    print("Imported!")