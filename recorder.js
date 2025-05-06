const videoElement = document.getElementById("videoElement");
const startButton = document.getElementById("startButton");
const recStart = document.getElementById("recStart");
const recStop = document.getElementById("recStop");
const processedVideo = document.getElementById("processedVideo");

let mediaRecorder;
let recordedChunks = [];

const BACKEND_URL = "http://localhost:5000"; // Flask backend URL

startButton.addEventListener("click", () => {
  recStart.disabled = false;
});

recStart.addEventListener("click", () => {
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(videoElement.srcObject, {
    mimeType: "video/webm;codecs=vp8",
  });

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      recordedChunks.push(e.data);
    }
  };

  mediaRecorder.start();
  recStart.disabled = true;
  recStop.disabled = false;
});

recStop.addEventListener("click", () => {
  mediaRecorder.stop();
  recStop.disabled = true;
  recStart.disabled = false;
});

// After recording stops, upload the video
function uploadRecording() {
  const blob = new Blob(recordedChunks, { type: "video/webm" });
  const formData = new FormData();
  formData.append("video", blob, "recording.webm");

  fetch(`${BACKEND_URL}/process-inline`, {
    method: "POST",
    body: formData,
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error("Processing failed");
      }
      return res.blob();
    })
    .then((blobResp) => {
      // Ensure the blob has a proper MIME type so the video element
      // knows how to decode it (some servers omit the header).
      const mp4Blob = new Blob([blobResp], { type: "video/mp4" });
      // Revoke any previous object URL to avoid memory leaks.
      if (processedVideo.src && processedVideo.src.startsWith("blob:")) {
        URL.revokeObjectURL(processedVideo.src);
      }
      const url = URL.createObjectURL(mp4Blob);
      processedVideo.src = url;
      processedVideo.load();
      processedVideo.play();
    })
    .catch((err) => {
      console.error(err);
      alert("Upload failed");
    });
}

if (typeof MediaRecorder !== "undefined") {
  recStop.addEventListener("click", () => {
    mediaRecorder.onstop = uploadRecording;
  });
} 