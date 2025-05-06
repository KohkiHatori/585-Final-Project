from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename
import subprocess, uuid, pathlib
from flask_cors import CORS
import tempfile, os

# Directories for uploads and processed videos (relative to backend folder)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # project root
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
MASK_PATH = BASE_DIR / "masks" / "cat.png"  # Default mask

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/upload", methods=["POST"])
def upload():
    """Receive a webm video, process with custom model, return processed URL."""
    if "video" not in request.files:
        return jsonify({"error": "No video field in form"}), 400

    video_file = request.files["video"]

    # Save uploaded file with a unique name
    in_name = secure_filename(f"{uuid.uuid4()}.webm")
    input_path = UPLOAD_DIR / in_name
    video_file.save(input_path)

    # Prepare output path
    out_name = input_path.stem + "_mask.mp4"
    output_path = PROCESSED_DIR / out_name

    # Call overlay processor as subprocess to avoid loading heavy libs in web thread
    cmd = [
        "python",
        str(BASE_DIR / "backend" / "overlay_processor.py"),
        str(input_path),
        str(MASK_PATH),
        str(output_path)
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("[ERROR] overlay_processor failed:", e.stderr.decode())
        return jsonify({"error": "Processing failed", "details": e.stderr.decode()}), 500

    return jsonify({"processed_url": f"/processed/{out_name}"})

@app.route("/processed/<path:fname>")
def processed(fname):
    """Serve processed video files."""
    return send_from_directory(PROCESSED_DIR, fname, as_attachment=False)

@app.route("/process-inline", methods=["POST"])
def process_inline():
    """Receive a video, run overlay processor, stream the processed MP4 back."""
    if "video" not in request.files:
        return jsonify({"error": "No video field in form"}), 400

    # 1) Persist the incoming video to a *temp* file.
    src_file = request.files["video"]
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_in:
        src_file.save(tmp_in)
        input_path = tmp_in.name

    # 2) Convert the WebM to an intermediate MP4 that OpenCV can read.
    interm_fd, interm_mp4 = tempfile.mkstemp(suffix=".mp4")
    os.close(interm_fd)
    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-movflags", "+faststart",
            interm_mp4,
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        os.unlink(input_path)
        os.unlink(interm_mp4)
        return jsonify({"error": "Failed to convert WebM", "details": e.stderr.decode()}), 500

    # 3) Prepare a temporary destination for the processed (masked) video.
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
        output_path = tmp_out.name

    # 4) Invoke the existing overlay processor CLI on the intermediate MP4.
    cmd = [
        "python",
        str(BASE_DIR / "backend" / "overlay_processor.py"),
        interm_mp4,
        str(MASK_PATH),
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # Clean up temp files before returning the error.
        os.unlink(input_path)
        os.unlink(interm_mp4)
        os.unlink(output_path)
        return jsonify({"error": "Processing failed", "details": e.stderr.decode()}), 500

    # 4) Transcode to a standards-compliant H.264 MP4 using ffmpeg. Browsers
    # are picky about codecs. This guarantees compatibility if ffmpeg is
    # installed.
    fd, final_mp4 = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)  # Close immediately so ffmpeg can write on Windows
    try:
        subprocess.run([
            "ffmpeg",
            "-y",  # overwrite existing
            "-i", str(output_path),
            "-vf", "fps=30",  # force constant fps & generate proper PTS/ DTS
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-movflags", "+faststart",
            final_mp4,
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # If ffmpeg is missing or fails, fall back to the raw file.
        print("[WARN] ffmpeg transcode failed, serving raw output", e.stderr.decode())
        final_mp4 = output_path

    # Read the processed (and transcoded) video into memory.
    with open(final_mp4, "rb") as fh:
        video_bytes = fh.read()

    # Cleanup
    os.unlink(input_path)
    os.unlink(interm_mp4)
    os.unlink(output_path)
    if os.path.exists(final_mp4) and final_mp4 != output_path:
        os.unlink(final_mp4)

    # 5) Stream the bytes back to the client.
    resp = Response(video_bytes, mimetype="video/mp4")
    # Allow browsers to treat this like a regular MP4 file rather than forcing download
    resp.headers["Content-Disposition"] = "inline; filename=processed.mp4"
    print("[DEBUG] returning", len(video_bytes), "bytes from process-inline")
    return resp

@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True) 