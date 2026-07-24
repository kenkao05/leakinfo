import { useMemo, useState } from 'react';
import DataTable from '../components/DataTable.jsx';

const Select = ({ label, value, onChange, options }) => (
  <label style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
    {label}
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      style={{
        padding: '0.45rem 0.6rem',
        borderRadius: 8,
        border: '1px solid var(--border-strong)',
        background: 'var(--surface-soft)',
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-body)',
        fontSize: '0.82rem'
      }}
    >
      <option value="">All</option>
      {options.map(o => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
    </select>
  </label>
);

const InfoPage = ({ rows }) => {
  const [status, setStatus] = useState('');
  const [bodyType, setBodyType] = useState('');
  const [pm, setPm] = useState('');
  const [confidence, setConfidence] = useState('');

  const statusOptions = useMemo(() => [...new Set(rows.map(r => r.leak_status))].sort(), [rows]);
  const bodyTypeOptions = useMemo(() => [...new Set(rows.map(r => r.body_type))].sort(), [rows]);
  const pmOptions = useMemo(() => [...new Set(rows.map(r => r.pm))], [rows]);
  const confidenceOptions = useMemo(() => [...new Set(rows.map(r => r.confidence))].sort(), [rows]);

  const filtered = useMemo(
    () =>
      rows.filter(
        r =>
          (!status || r.leak_status === status) &&
          (!bodyType || r.body_type === bodyType) &&
          (!pm || r.pm === pm) &&
          (!confidence || r.confidence === confidence)
      ),
    [rows, status, bodyType, pm, confidence]
  );

  const resetFilters = () => {
    setStatus('');
    setBodyType('');
    setPm('');
    setConfidence('');
  };

  return (
    <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.2rem' }}>
      <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)' }}>
        Info
      </p>
      <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 2rem)', marginBottom: '0.5rem' }}>Browse the raw dataset</h1>
      <p style={{ fontSize: '0.9rem', marginBottom: '1.2rem', maxWidth: 640 }}>
        Every row from the underlying CSV, filterable by status, conducting body, administration, and source
        confidence. Click any row to expand its full note and source link.
      </p>

      <div
        style={{
          display: 'flex',
          gap: '0.9rem',
          flexWrap: 'wrap',
          alignItems: 'flex-end',
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          padding: '1rem 1.1rem',
          marginBottom: '1.2rem'
        }}
      >
        <Select label="Leak status" value={status} onChange={setStatus} options={statusOptions} />
        <Select label="Conducting body" value={bodyType} onChange={setBodyType} options={bodyTypeOptions} />
        <Select label="Administration" value={pm} onChange={setPm} options={pmOptions} />
        <Select label="Confidence" value={confidence} onChange={setConfidence} options={confidenceOptions} />
        <button
          onClick={resetFilters}
          style={{
            padding: '0.5rem 0.9rem',
            borderRadius: 8,
            border: '1px solid var(--border-strong)',
            background: 'var(--surface-soft)',
            color: 'var(--accent-deep)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.8rem',
            cursor: 'pointer'
          }}
        >
          Reset filters
        </button>
      </div>

      <DataTable rows={filtered} />
    </section>
  );
};

export default InfoPage;
