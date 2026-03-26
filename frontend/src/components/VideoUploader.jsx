import { useState } from "react";

function VideoUploader({ onFileSelect, text }) {
  const [dragging, setDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    onFileSelect(file);
  };

  return (
    <label
      className={`uploader ${dragging ? "dragging" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFile(e.dataTransfer.files?.[0]);
      }}
    >
      <input
        type="file"
        accept=".mp4,.mov,.m4v,.jpg,.jpeg,.png,.webp"
        onChange={(e) => handleFile(e.target.files?.[0])}
        hidden
      />
      <p>{text.dropTitle}</p>
      <span>{text.dropSub}</span>
    </label>
  );
}

export default VideoUploader;
