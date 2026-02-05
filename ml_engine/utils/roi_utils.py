from core.config import CEILING_ROI



def extract_roi(frame):
    h, w, _ = frame.shape
    x1 = int(CEILING_ROI[0] * w)
    y1 = int(CEILING_ROI[1] * h)
    x2 = int(CEILING_ROI[2] * w)
    y2 = int(CEILING_ROI[3] * h)
    return frame[y1:y2, x1:x2]


def extract_floor(frame):
    h, w, _ = frame.shape
    return frame[int(0.35*h):h, 0:w]   # bottom 65% of frame
