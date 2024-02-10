from depth_map.arguments import test_mode, out_format, processor, zoe_processors, dpt_processors
from depth_map.log import logger, log_separator
import time
from PIL import Image
import os

# Print loading message
logger(f"Loading model from for {processor()}.")

if not test_mode() and processor() in zoe_processors:
    import torch

    log_separator()

    # Hugging Face repo
    repo = "isl-org/ZoeDepth"

    ##### sample prediction
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    p = processor()

    if p in ["zoe", "zoe-nk", "ZoeD_NK"]:
        model = torch.hub.load(repo, "ZoeD_NK", pretrained=True, verbose=False)

    if p in ["zoe-n", "ZoeD_N"]:
        model = torch.hub.load(repo, "ZoeD_N", pretrained=True, verbose=False)

    if p in ["zoe-k", "ZoeD_K"]:
        model = torch.hub.load(repo, "ZoeD_K", pretrained=True, verbose=False)


    # ============================================================================= #
    #  TODO: Attempt to sort out loading the model from a local file
    # ============================================================================= #

    # model = torch.hub.load("model/ZoeD_M12_NK.pt", "ZoeD_NK", pretrained=True, verbose=False)

    # model_path = os.path.join(os.path.dirname(__file__), "../model/ZoeD_M12_NK.pt")
    # conf = get_config("zoedepth", "infer", pretrained_resource=f"local::{model_path}")
    # model = build_model(conf)
    
    # load model from 'model' folder
    # model = torch.load(model_path, map_location=torch.device(DEVICE))

    # ============================================================================= #
    #  TODO: Load the model with the default arguments but suppress the output except for errors
    # ============================================================================= #

    # THIS IS HOW YOU DO IT -> torch.hub.load(".", "ZoeD_N", source="local", pretrained=True)

    # # Do the same as the above line to load the model with the default arguments but suppress the output except for errors
    # model = subprocess.run(f"python -c 'import torch; torch.hub.load(\"{repo}\", \"ZoeD_NK\", pretrained=True, verbose=False)'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # # If the model is not loaded successfully, print the error message and exit
    # if model.returncode != 0:
    #     logger(model.stderr)
    #     exit(1)

    # # If the model is loaded successfully, set the model to the output of the command
    # model = model.stdout

    # # Print the model name
    # logger(f"Loaded model")
    # ============================================================================= #
    # ============================================================================= #

    zoe = model.to(DEVICE)

def zoe_process(image, out_file):
    # Infer depth
    depth = zoe.infer_pil(image, output_type="tensor")

    # Colorize output
    from depth_map.utils.misc import colorize

    colored = colorize(depth)

    # save colored output (Convert to RGB to save as jpg)
    Image.fromarray(colored).convert('RGB').save(out_file)

    return True

if not test_mode() and processor() == "sd15":
    from transformers import pipeline
    import numpy as np

    depth_estimator = pipeline('depth-estimation')

def sd15_process(image, out_file):
    image = depth_estimator(image)['depth']
    image = np.array(image)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    control_image = Image.fromarray(image)

    control_image.save(out_file)

    return True


if not test_mode() and processor() in dpt_processors:
    from transformers import DPTImageProcessor, DPTForDepthEstimation

    # Load the model
    if processor() == "dpt-large":
        image_processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")
        model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")
    else:
        image_processor = DPTImageProcessor.from_pretrained("Intel/dpt-hybrid-midas")
        model = DPTForDepthEstimation.from_pretrained("Intel/dpt-hybrid-midas", low_cpu_mem_usage=True)

def dpt_process(image, out_file):
    import numpy as np
    import torch

    # prepare image for the model
    inputs = image_processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        predicted_depth = outputs.predicted_depth

    # interpolate to original size
    prediction = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=image.size[::-1],
        mode="bicubic",
        align_corners=False,
    )

    # visualize the prediction
    output = prediction.squeeze().cpu().numpy()
    formatted = (output * 255 / np.max(output)).astype("uint8")
    depth = Image.fromarray(formatted)

    # save the image
    depth.save(out_file)

    return True



def process_image(image_path, output="output", input="frames"):
    # Set the output file path
    out_file = image_path.replace(input, output).replace(".jpg", f".{out_format}")

    # If the output image already exists, skip processing
    if os.path.exists(out_file):
        return False
    
    if test_mode():
        logger(f"Processing {image_path}", temporary=True)
        logger(f"Saving to {out_file}", temporary=True)
        # Pause for .3 seconds to simulate processing
        time.sleep(.3)
        return True

    # Load Image
    image = Image.open(image_path)  # Or cv2.imread(image_path)

    if processor() in zoe_processors:
        return zoe_process(image, out_file)
    
    if processor() == "sd15":
        return sd15_process(image, out_file)
    
    if processor() in dpt_processors:
        return dpt_process(image, out_file)

    return False