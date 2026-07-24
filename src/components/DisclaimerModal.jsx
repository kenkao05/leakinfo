import { useState } from 'react';

const DisclaimerModal = () => {
  const [open, setOpen] = useState(true);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="disclaimer-title"
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(22, 40, 59, 0.45)',
        backdropFilter: 'blur(2px)',
        zIndex: 200,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.2rem'
      }}
    >
      <div
        style={{
          background: 'var(--surface)',
          borderRadius: 18,
          border: '1px solid var(--border)',
          maxWidth: 460,
          width: '100%',
          padding: '1.6rem 1.6rem 1.4rem',
          boxShadow: '0 30px 70px rgba(22, 40, 59, 0.3)'
        }}
      >
        <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)', marginBottom: '0.4rem' }}>
          Before you dig in
        </p>
        <h2 id="disclaimer-title" style={{ fontSize: '1.25rem', marginBottom: '0.7rem' }}>
          Compiled with AI assistance
        </h2>
        <p style={{ fontSize: '0.88rem', marginBottom: '0.7rem' }}>
          This dataset and dashboard were researched and assembled with the help of an AI assistant (Claude), drawing
          on openly published news articles, government statements, and retrospective reports.
        </p>
        <p style={{ fontSize: '0.88rem', marginBottom: '1.1rem' }}>
          Some entries are confirmed by courts or official probes; others are allegations that were later disputed,
          denied, or never conclusively resolved. Confidence levels are noted per incident, but nothing here should be
          treated as a verified legal record. Please cross-check anything decision-critical against the linked
          primary sources.
        </p>
        <button
          onClick={() => setOpen(false)}
          style={{
            width: '100%',
            padding: '0.65rem',
            borderRadius: 10,
            border: 'none',
            background: 'var(--accent-deep)',
            color: '#fff',
            fontFamily: 'var(--font-body)',
            fontSize: '0.9rem',
            fontWeight: 500,
            cursor: 'pointer'
          }}
        >
          Understood, continue
        </button>
      </div>
    </div>
  );
};

export default DisclaimerModal;
