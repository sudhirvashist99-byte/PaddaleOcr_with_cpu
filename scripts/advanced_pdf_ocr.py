import os
import cv2
import json
import subprocess
from multiprocessing import Pool, cpu_count
from paddleocr import PaddleOCR
from tqdm import tqdm

INPUT_DIR = "/mydata/input_pdfs"
IMAGE_DIR = "/mydata/work_images"
OUTPUT_DIR = "/mydata/output_json"

DET_MODEL = "/mydata/server_models/en_PP-OCRv4_det_server_infer"
REC_MODEL = "/mydata/server_models/en_PP-OCRv4_rec_server_infer"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# FORCE SERVER MODEL
ocr = PaddleOCR(
    use_gpu=False,
    lang="en",
    ocr_version="PP-OCRv4",
    det_limit_side_len=1536,
    det_db_thresh=0.2,
    det_db_box_thresh=0.5,
    rec_batch_num=4,
    drop_score=0.4,
    use_angle_cls=True,
    show_log=False
)

# ---------------- PDF → Images (400 DPI + Grayscale)
def convert_pdf(pdf_file):
    name = os.path.splitext(pdf_file)[0]
    pdf_path = os.path.join(INPUT_DIR, pdf_file)
    out_folder = os.path.join(IMAGE_DIR, name)
    os.makedirs(out_folder, exist_ok=True)

    subprocess.run([
        "pdftoppm",
        "-gray",
        "-png",
        "-r", "400",
        pdf_path,
        os.path.join(out_folder, "page")
    ])

# ---------------- Deskew
def deskew(image):
    coords = cv2.findNonZero(255 - image)
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)

# ---------------- Preprocess
def preprocess(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 15
    )
    return deskew(thresh)

# ---------------- OCR Single Page
def ocr_page(args):
    img_path, pdf_name = args
    processed = preprocess(img_path)
    result = ocr.ocr(processed, cls=False)

    page_data = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]
            conf = float(line[1][1])

            # Basic post correction
            text = text.replace("0", "O") if conf < 0.6 else text
            text = text.strip()

            page_data.append({
                "text": text,
                "confidence": conf,
                "box": line[0]
            })
    return page_data

# ---------------- MAIN PIPELINE
for pdf in os.listdir(INPUT_DIR):
    if not pdf.lower().endswith(".pdf"):
        continue

    print(f"Processing {pdf}")

    convert_pdf(pdf)

    pdf_name = os.path.splitext(pdf)[0]
    image_folder = os.path.join(IMAGE_DIR, pdf_name)

    images = sorted([
        os.path.join(image_folder, img)
        for img in os.listdir(image_folder)
        if img.endswith(".png")
    ])

    with Pool(cpu_count()) as pool:
        results = list(tqdm(
            pool.imap(ocr_page, [(img, pdf_name) for img in images]),
            total=len(images)
        ))

    # Merge pages into single JSON
    merged = {
        "document": pdf_name,
        "pages": results
    }

    with open(os.path.join(OUTPUT_DIR, pdf_name + ".json"), "w") as f:
        json.dump(merged, f, indent=2)

print("All PDFs processed successfully.")
