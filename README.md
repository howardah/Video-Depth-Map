# Video Depth Map
 Python script for processing depth maps from videos

## About

This library is largely inspired by jankais3r's [Video-Depthify](https://github.com/jankais3r/Video-Depthify) and uses publically available Pre-Trained AI Models [ZoeDepth](https://github.com/isl-org/ZoeDepth) and [DPT-Hybrid](https://huggingface.co/Intel/dpt-hybrid-midas)/[DPT-Large](https://huggingface.co/Intel/dpt-large).

## Installation

Install dependencies with:
```
mamba create -n depth_map -f environment.yml # Or environment-osx.yml
mamba activate depth_map
```

or

```
conda create -n depth_map -f environment.yml # Or environment-osx.yml
conda activate depth_map
```

In addition, the script relies on [ffmpeg](https://ffmpeg.org/) so you will need to install that as well. You can do so from the 'Download' tab on their website or with `apt install ffmpeg` / `yum install ffmpeg` / `brew install ffmpeg`

## Usage

Once you have the dependencies installed and your environment active, you can simply run the 'depth.py' script like this:
```
python depth.py <your-video-file>
```

This will export file next to the depth.py file called `<your-video-file>_depth.mp4` if you would like to change the output file you can use the output flag.

## Options

| Option | Description | Short Flag | Long Flag | Default | Accepted Values |
|---|---|---|---|---|---|
| Test Mode | Enables test mode features | `-t` | `--test` | `False` | None |
| Quiet Mode | Logs output to log file | `-q` | `--quiet` | `True` | None |
| Loud Mode | Prints output in terminal | `-nq` | `--not-quiet`, `--loud` | `False` | None |
| Print ID | Prints a unique identifier for the current run | None | `--print-id` | `False` | None |
| Process Averages | Analyzes and prints average values | None | `--average` | `False` | None |
| Output File | Specifies the output file name | `-o` | `--output` | `""` | Valid file path |
| Ignore Output Option | Ignores user-specified output file | None | None | `False` | None |
| Processor | Selects the processing algorithm | `-p` | `--processor` | `"zoe"` | `zoe_processors`, `dpt_processors`, `"sd15"` |
| Image Format | Sets the output image format used in processing | `-f` | `--format`, `--png`, `--jpg` | `"jpg"` | `"png"`, `"jpg"` |
| Keep File Mode | Keeps temporary files after processing | None | `--keep` | `False` | None |