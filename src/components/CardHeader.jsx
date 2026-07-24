const CardHeader = ({ eyebrow, title, caveat }) => (
  <div style={{ marginBottom: '0.85rem', position: 'relative', zIndex: 3 }}>
    {eyebrow && (
      <p
        className="mono"
        style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)', margin: '0 0 0.2rem' }}
      >
        {eyebrow}
      </p>
    )}
    <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>{title}</h3>
    {caveat && <p style={{ fontSize: '0.78rem', marginTop: '0.3rem', color: 'var(--text-muted)' }}>{caveat}</p>}
  </div>
);

export default CardHeader;
