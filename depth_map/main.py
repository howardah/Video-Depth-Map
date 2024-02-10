import os
import sys
import subprocess
from depth_map.log import logger, log_separator
from depth_map.process import process_frames, export_frames
from depth_map.arguments import test_mode, out_format, output, process_averages, process_id
from depth_map.hygene import clean_up, prepare
from depth_map.average import average_images

def make_depth_maps(args):

    prepare()

    # Print a separator
    log_separator()

    # Log the current time and date
    arg_string = "\', \'".join(args)
    arg_string = f"'{arg_string}'"
    logger(f"Running depth.py with arguments [{arg_string}]")
    logger(" ")

    # Check if the file path is provided
    if len(args) < 1:
        logger("No file path provided")
        sys.exit(1)

    use_output = False
    given_output = output()

    if given_output:
        use_output = True
        if len(args) > 1:
            use_output = False
            logger("Output directory provided with multiple files. Ignoring output directory.")
            logger(" ")


    # Get the file path from the command line arguments
    file_paths = args

    # Loop through the file paths
    for file_path in file_paths:
        # Print a separator
        log_separator()

        # Check if the file exists and is an mp4 file
        if not os.path.exists(file_path):
            logger("File does not exist")
            sys.exit(1)

        # Get file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Get file extension
        file_extension = os.path.splitext(file_path)[1]

        # Get file output
        out_file = f"{file_name}_depth.mp4"
        if use_output:
            out_file = f"{given_output}"

        # Print status
        logger(f"Processing {file_name}{file_extension}", temporary=True)

        # Launch ffmpeg command to calculate the fps of the video and save it to variable fps
        fps = os.popen(f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate \"{file_path}\"").read().strip()

        # Clear print status
        logger(f" " * (11 + len(file_name) + len(file_extension)), temporary=True)

        # Print status
        logger(f"Exporting frames for processing...", temporary=True)

        # Export the frames into the frames folder using ffmpeg
        export_frames(file_path)

        # Clear print status
        logger(f" " * 35, temporary=True)

        # Remove spaces from the file name
        file_name = file_name.replace(" ", "_")

        # Process the frames
        output_folder = process_frames(file_name)

        # If the output file already exists, remove it
        if os.path.exists(f"{out_file}"):
            os.system(f"rm {out_file}")

        if not test_mode():
            if process_averages():
                average_images(output_folder)
                output_folder = f"{output_folder}/averaged"

            # Merge the frames into a video using ffmpeg and save it to the output folder
            merge_frames=f"ffmpeg -r {fps} -i {output_folder}/%08d.{out_format} -c:v libx264 -pix_fmt yuv420p -nostdin \"{out_file}\""

            # Run the ffmpeg command to merge the frames into a video
            with open("ffmpeg_log.txt", "w") as log_file:  # Open a log file in write mode
                subprocess.run(merge_frames, shell=True, stdout=log_file, stderr=subprocess.STDOUT, check=True)

            # Append _audio to the output filename just before the file extension
            with_audio = out_file.split(".")
            with_audio[-2] = with_audio[-2] + "_audio"
            with_audio = ".".join(with_audio)

            # Copy the audio from the original video to the processed video
            # os.system(f"ffmpeg -i {file_path} -vn -acodec copy {out_file}")
            os.system(f"ffmpeg -i \"{out_file}\" -i \"{file_path}\" -c copy -map 0:0 -map 1:1 -shortest \"{with_audio}\" -loglevel error -nostdin")

            # Remove {out_file} and rename {file_name}_sound.mp4 to output file
            os.system(f"rm {out_file}")
            os.system(f"mv {with_audio} {out_file}")

            # determine the max character length from the file name
            char_width = len(file_name) + 50

            # Clear the line after processing all the frames
            logger(f" " * char_width, temporary=True)

            # Clean up the temporary files
            pid = process_id(file_name)
            clean_up(pid)

        # Print the path to the processed video
        logger(f"Exported {out_file}", temporary=False)

        # Print a separator
        log_separator()
    