import cv2
import os
from pathlib import Path
from config import CFG

def is_gift(image_path: str) -> bool:
    img = cv2.imread(str(image_path), 0)
    if img is None:
        return False

    # SIFT fallback to ORB if unavailable
    try:
        detector = cv2.SIFT_create()
        norm = cv2.NORM_L2
        use_sift = True
    except Exception:
        detector = cv2.ORB_create(nfeatures=1000)
        norm = cv2.NORM_HAMMING
        use_sift = False

    kp1, des1 = detector.detectAndCompute(img, None)
    if des1 is None:
        return False

    bf = cv2.BFMatcher(norm, crossCheck=False)

    gifts_dir = Path(CFG.get("GIFTS_REF", "gifts_ref"))
    if not gifts_dir.is_dir():
        return False

    valid_ext = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

    for ref_name in os.listdir(gifts_dir):
        ref_path = gifts_dir / ref_name
        if not ref_path.is_file() or ref_path.suffix.lower() not in valid_ext:
            continue

        ref_img = cv2.imread(str(ref_path), 0)
        if ref_img is None:
            continue

        kp2, des2 = detector.detectAndCompute(ref_img, None)
        if des2 is None:
            continue

        matches = bf.knnMatch(des1, des2, k=2)

        # safe unpack of knnMatch results
        good = []
        for pair in matches:
            if len(pair) < 2:
                continue
            m, n = pair[0], pair[1]
            if m.distance < 0.75 * n.distance:
                good.append(m)

        threshold = 10 if use_sift else 20
        if len(good) > threshold:
            return True

    return False