const recordVideoEl = document.getElementById("recordVideo");
const startButton = document.getElementById("startButton");
const recStart = document.getElementById("recStart");
const recStop = document.getElementById("recStop");
const spinner = document.getElementById("uploadSpinner");

let mediaRecorder;
let recordedChunks = [];

const BACKEND_URL = "http://localhost:5000"; // Flask backend URL

startButton.addEventListener("click", () => {
  recStart.disabled = false;
});

recStart.addEventListener("click", () => {
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(recordVideoEl.srcObject, {
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
  spinner.classList.add("hidden");
});

recStop.addEventListener("click", () => {
  mediaRecorder.stop();
  recStop.disabled = true;
  recStart.disabled = false;
  spinner.classList.remove("hidden");
});

// After recording stops, upload the video
function uploadRecording() {
  const blob = new Blob(recordedChunks, { type: "video/webm" });
  const formData = new FormData();
  formData.append("video", blob, "recording.webm");
  if (window.currentMaskType) {
    formData.append("mask", window.currentMaskType);
  }

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
      const mp4Blob = new Blob([blobResp], { type: "video/mp4" });
      const url = URL.createObjectURL(mp4Blob);
      recordVideoEl.srcObject = null;
      recordVideoEl.src = url;
      recordVideoEl.load();
      recordVideoEl.play();
      spinner.classList.add("hidden");
    })
    .catch((err) => {
      console.error(err);
      alert("Upload failed");
      spinner.classList.add("hidden");
    });
}

if (typeof MediaRecorder !== "undefined") {
  recStop.addEventListener("click", () => {
    mediaRecorder.onstop = uploadRecording;
  });
} 