import { Fragment, useMemo, useState } from 'react';

const COLUMNS = [
  { key: 'date', label: 'Date' },
  { key: 'exam_name', label: 'Exam' },
  { key: 'body_type', label: 'Body' },
  { key: 'area', label: 'Area' },
  { key: 'leak_status', label: 'Status' },
  { key: 'confidence', label: 'Confidence' }
];

const PAGE_SIZE = 20;

const statusColor = status => {
  switch (status) {
    case 'Confirmed':
      return 'var(--confirmed)';
    case 'Alleged':
      return 'var(--alleged)';
    case 'Denied':
      return 'var(--denied)';
    default:
      return 'var(--suspected)';
  }
};

const DataTable = ({ rows }) => {
  const [query, setQuery] = useState('');
  const [sortKey, setSortKey] = useState('date');
  const [sortDir, setSortDir] = useState('desc');
  const [visible, setVisible] = useState(PAGE_SIZE);
  const [expanded, setExpanded] = useState(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let out = rows;
    if (q) {
      out = rows.filter(r =>
        [r.exam_name, r.area, r.conducting_body, r.note].join(' ').toLowerCase().includes(q)
      );
    }
    out = [...out].sort((a, b) => {
      const av = a[sortKey] ?? '';
      const bv = b[sortKey] ?? '';
      const cmp = String(av).localeCompare(String(bv));
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return out;
  }, [rows, query, sortKey, sortDir]);

  const toggleSort = key => {
    if (key === sortKey) {
      setSortDir(d => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  return (
    <div style={{ position: 'relative', zIndex: 3 }}>
      <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.9rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search exam, state, or body..."
          value={query}
          onChange={e => {
            setQuery(e.target.value);
            setVisible(PAGE_SIZE);
          }}
          style={{
            flex: '1 1 240px',
            padding: '0.5rem 0.75rem',
            borderRadius: 8,
            border: '1px solid var(--border-strong)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.85rem',
            background: 'var(--surface-soft)',
            color: 'var(--text-primary)'
          }}
        />
        <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {filtered.length} of {rows.length} incidents
        </span>
      </div>

      <div
        style={{
          overflowX: 'auto',
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'rgba(255, 255, 255, 0.55)',
          backdropFilter: 'blur(14px)',
          WebkitBackdropFilter: 'blur(14px)'
        }}
      >        
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ background: 'var(--bg-deep)' }}>
              {COLUMNS.map(col => (
                <th
                  key={col.key}
                  onClick={() => toggleSort(col.key)}
                  style={{
                    textAlign: 'left',
                    padding: '0.6rem 0.75rem',
                    cursor: 'pointer',
                    userSelect: 'none',
                    color: 'var(--text-secondary)',
                    fontWeight: 600,
                    whiteSpace: 'nowrap'
                  }}
                >
                  {col.label}
                  {sortKey === col.key ? (sortDir === 'asc' ? ' \u2191' : ' \u2193') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, visible).map(r => (
              <Fragment key={r.id}>
                <tr
                  key={r.id}
                  onClick={() => setExpanded(expanded === r.id ? null : r.id)}
                  style={{ borderTop: '1px solid var(--border)', cursor: 'pointer' }}
                >
                  <td className="mono" style={{ padding: '0.55rem 0.75rem', whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>
                    {r.date}
                  </td>
                  <td style={{ padding: '0.55rem 0.75rem', maxWidth: 280 }}>{r.exam_name}</td>
                  <td style={{ padding: '0.55rem 0.75rem' }}>{r.body_type}</td>
                  <td style={{ padding: '0.55rem 0.75rem' }}>{r.area}</td>
                  <td style={{ padding: '0.55rem 0.75rem' }}>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '0.15rem 0.55rem',
                        borderRadius: 999,
                        fontSize: '0.72rem',
                        color: '#fff',
                        background: statusColor(r.leak_status)
                      }}
                    >
                      {r.leak_status}
                    </span>
                  </td>
                  <td style={{ padding: '0.55rem 0.75rem', color: 'var(--text-muted)' }}>{r.confidence}</td>
                </tr>
                {expanded === r.id && (
                  <tr key={`${r.id}-detail`} style={{ background: 'var(--bg-deep)' }}>
                    <td colSpan={COLUMNS.length} style={{ padding: '0.9rem 1rem', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      <p style={{ marginBottom: '0.5rem' }}>{r.note}</p>
                      <p className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        Conducting body: {r.conducting_body} · Arrests: {r.arrests || '—'} · Convictions: {r.convictions || '—'} ·
                        Aspirants affected: {r.aspirants_affected ? Number(r.aspirants_affected).toLocaleString('en-IN') : '—'}
                      </p>
                      <p style={{ marginTop: '0.4rem' }}>
                        Source:{' '}
                        <a href={r.source_url} target="_blank" rel="noreferrer">
                          {r.source_name}
                        </a>
                      </p>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {visible < filtered.length && (
        <button
          onClick={() => setVisible(v => v + PAGE_SIZE)}
          style={{
            marginTop: '0.8rem',
            padding: '0.5rem 1rem',
            borderRadius: 8,
            border: '1px solid var(--border-strong)',
            background: 'var(--surface-soft)',
            color: 'var(--accent-deep)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.82rem',
            cursor: 'pointer'
          }}
        >
          Show {Math.min(PAGE_SIZE, filtered.length - visible)} more
        </button>
      )}
    </div>
  );
};

export default DataTable;
