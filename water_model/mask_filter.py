import cv2
import numpy as np


# ---------------- FEATURE FUNCTIONS ---------------- #

def shape_irregularity(segmentation):
    seg_uint8 = segmentation.astype(np.uint8) * 255

    contours, _ = cv2.findContours(seg_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return 0

    cnt = contours[0]

    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)

    if area == 0:
        return 0

    return (perimeter ** 2) / area


def intensity_variance(image, segmentation):
    region = image[segmentation]

    if len(region) == 0:
        return 0

    return np.var(region)


def touches_border(segmentation):
    H, W = segmentation.shape

    if segmentation[0,:].any(): return True
    if segmentation[-1,:].any(): return True
    if segmentation[:,0].any(): return True
    if segmentation[:,-1].any(): return True

    return False


# ---------------- SCORING FUNCTION ---------------- #

def compute_mask_score(mask, image):

    seg = mask['segmentation']
    area = mask['area']

    shape_score = shape_irregularity(seg)
    var = intensity_variance(image, seg)

    score = 0

    # ✅ Area preference (water is not tiny)
    if area > 800:
        score += 2
    if area > 3000:
        score += 2

    # ✅ Shape irregularity (water spreads)
    if shape_score > 8:
        score += 2
    if shape_score > 15:
        score += 1

    # ✅ Moderate variance (water has distortion)
    if var > 5:
        score += 1

    # ❌ Too reflective → penalize (your wall problem)
    if var > 50:
        score -= 2

    # ❌ Border touching → likely background / wall
    if touches_border(seg):
        score -= 2

    return score


# ---------------- MAIN FUNCTION ---------------- #

def get_final_mask(masks, image, top_k=5):

    scored_masks = []

    print("\n---- MASK DEBUG ----")

    for i, mask in enumerate(masks):
        score = compute_mask_score(mask, image)

        print(f"Mask {i}: Area={mask['area']} Score={score}")

        scored_masks.append((score, mask))

    # Sort by score
    scored_masks.sort(key=lambda x: x[0], reverse=True)

    # Take top masks
    top_masks = [m for s, m in scored_masks[:top_k] if s > 0]

    if len(top_masks) == 0:
        print("⚠️ No valid masks found")
        return None

    # Merge masks
    combined_mask = np.zeros_like(top_masks[0]['segmentation'], dtype=bool)

    for mask in top_masks:
        combined_mask = combined_mask | mask['segmentation']

    return combined_mask