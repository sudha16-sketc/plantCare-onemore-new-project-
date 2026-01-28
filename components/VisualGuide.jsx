// src/components/VisualGuide.jsx
export default function VisualGuide({ visualGuide }) {
  if (!visualGuide) return null;

  const fileUrl = typeof visualGuide === 'string' ? visualGuide : visualGuide.file_url;
  
  if (!fileUrl) return null;

  const isImage = fileUrl.endsWith('.png') || fileUrl.endsWith('.jpg') || fileUrl.endsWith('.jpeg');

  return (
    <div style={{ margin: '20px 0' }}>
      <h3>📥 Visual Guide</h3>
      {isImage ? (
        <img
          src={fileUrl}
          alt="Visual Guide"
          style={{ maxWidth: '100%', borderRadius: '8px', marginTop: '10px' }}
        />
      ) : (
        <a
          href={fileUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'blue', textDecoration: 'underline', marginTop: '10px', display: 'inline-block' }}
        >
          Download Visual Care Guide
        </a>
      )}
    </div>
  );
}
