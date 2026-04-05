import torch
import cv2
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

class SAMModel:
    def __init__(self, model_path):
        device = "cpu"
        print("Using device:", device)

        self.sam = sam_model_registry["vit_b"](checkpoint=model_path)
        self.sam.to(device)

        self.mask_generator = SamAutomaticMaskGenerator(
            self.sam,
            points_per_side=24,
            pred_iou_thresh=0.88,
            stability_score_thresh=0.9,
            min_mask_region_area=800
        )

    def generate_masks(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        masks = self.mask_generator.generate(image_rgb)
        return masks