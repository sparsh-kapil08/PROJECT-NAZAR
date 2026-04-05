import cv2
import numpy as np


# ---------------- BASIC FEATURES ---------------- #

def area_ratio(mask):
    return np.sum(mask) / (mask.shape[0] * mask.shape[1])


def intensity_std(image, mask):
    region = image[mask]
    if len(region) == 0:
        return 0
    return np.std(region)


# ---------------- TEXTURE FEATURES ---------------- #

def texture_variance(image, mask):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    region = gray[mask]

    if len(region) == 0:
        return 0

    return np.var(region)


def laplacian_variance(image, mask):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)

    region = lap[mask]

    if len(region) == 0:
        return 0

    return np.var(region)


# ---------------- EDGE FEATURES ---------------- #

def edge_density(image, mask):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    edge_pixels = edges[mask]

    return np.sum(edge_pixels > 0) / (np.sum(mask) + 1)


# ---------------- SHAPE FEATURE ---------------- #

def shape_irregularity(mask):
    seg_uint8 = mask.astype(np.uint8) * 255

    contours, _ = cv2.findContours(seg_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return 0

    cnt = contours[0]

    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)

    if area == 0:
        return 0

    return (perimeter ** 2) / area


# ---------------- MAIN FEATURE FUNCTION ---------------- #

def extract_features(image, mask):

    features = {}

    features["area_ratio"] = area_ratio(mask)
    features["intensity_std"] = intensity_std(image, mask)
    features["texture_var"] = texture_variance(image, mask)
    features["laplacian_var"] = laplacian_variance(image, mask)
    features["edge_density"] = edge_density(image, mask)
    features["shape_irregularity"] = shape_irregularity(mask)

    return features