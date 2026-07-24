import MagicBento from '../components/MagicBento.jsx';
import LineSidebar from '../components/LineSidebar.jsx';
import ChartCanvas, { PALETTE } from '../components/ChartCanvas.jsx';
import CardHeader from '../components/CardHeader.jsx';
import data from '../data/leaks.json';

const SECTION_IDS = ['kpis', 'trend', 'eras', 'body-type', 'leak-status', 'top-exams', 'top-states', 'actions'];
const SECTION_LABELS = ['Overview', 'Yearly trend', 'By administration', 'Central vs state', 'Leak status', 'Top exams', 'Top states', 'Actions taken'];

const KpiCard = ({ label, value }) => (
  <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 14, padding: '1rem 1.1rem' }}>
    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>{label}</p>
    <p className="mono" style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>{value}</p>
  </div>
);

const ChartsPage = () => {
  const { kpis, yearly_counts, era_data, body_type_counts, leak_status_counts, action_data, top_states, top_exams } = data;

  const yearlyTrend = {
    labels: Object.keys(yearly_counts),
    datasets: [{ label: 'Incidents', data: Object.values(yearly_counts), backgroundColor: '#a7c9ea', borderColor: '#3f7cb8', borderRadius: 4 }]
  };

  const eraChart = {
    labels: era_data.map(e => e.pm),
    datasets: [
      { label: 'Incidents per year in office', data: era_data.map(e => e.rate_per_year), backgroundColor: PALETTE, borderRadius: 6 }
    ]
  };

  const bodyTypeChart = {
    labels: Object.keys(body_type_counts),
    datasets: [{ data: Object.values(body_type_counts), backgroundColor: ['#6fa8dc', '#cfe6fb'] }]
  };

  const leakStatusChart = {
    labels: Object.keys(leak_status_counts),
    datasets: [{ data: Object.values(leak_status_counts), backgroundColor: ['#4f8fce', '#9cc2e8', '#e3b8a0', '#c9d6e3'] }]
  };

  const actionChart = {
    labels: action_data.map(a => a.label),
    datasets: [{ label: 'Incidents', data: action_data.map(a => a.count), backgroundColor: '#8fb8dd', borderRadius: 4 }]
  };

  const topExamsChart = {
    labels: top_exams.map(e => (e.exam_name.length > 34 ? e.exam_name.slice(0, 34) + '…' : e.exam_name)),
    datasets: [{ label: 'Aspirants affected', data: top_exams.map(e => e.aspirants_affected), backgroundColor: '#6fa8dc', borderRadius: 4 }]
  };

  const topStatesChart = {
    labels: top_states.map(s => s.state),
    datasets: [{ label: 'Incidents', data: top_states.map(s => s.count), backgroundColor: '#a7c9ea', borderRadius: 4 }]
  };

  const cards = [
    {
      id: 'trend',
      size: 'wide',
      content: (
        <>
          <CardHeader eyebrow="2000–2026" title="Leaks per year" caveat="COVID-era dips likely reflect fewer exams held, not fewer leaks." />
          <ChartCanvas type="bar" data={yearlyTrend} height={240} />
        </>
      )
    },
    {
      id: 'eras',
      content: (
        <>
          <CardHeader eyebrow="Normalized" title="Incidents per year in office" caveat="Raw totals would mislead — these three terms cover very different lengths of time." />
          <ChartCanvas type="bar-horizontal" data={eraChart} height={200} />
        </>
      )
    },
    {
      id: 'body-type',
      content: (
        <>
          <CardHeader eyebrow="Scope" title="Central vs. state bodies" caveat="Counts incidents, not exams held — central bodies run far fewer, larger exams." />
          <ChartCanvas type="doughnut" data={bodyTypeChart} height={200} />
        </>
      )
    },
    {
      id: 'leak-status',
      content: (
        <>
          <CardHeader eyebrow="Verification" title="Confirmed, alleged, denied" caveat="A meaningful share were later denied or downgraded by investigators." />
          <ChartCanvas type="doughnut" data={leakStatusChart} height={200} />
        </>
      )
    },
    {
      id: 'top-exams',
      content: (
        <>
          <CardHeader eyebrow="Where known" title="Top exams by aspirants affected" caveat="Many rows have no public estimate — this ranks reported numbers, not true scale." />
          <ChartCanvas type="bar-horizontal" data={topExamsChart} height={230} />
        </>
      )
    },
    {
      id: 'top-states',
      content: (
        <>
          <CardHeader eyebrow="Geography" title="Top states by incident count" caveat="Likely reflects reporting intensity as much as underlying leak frequency." />
          <ChartCanvas type="bar-horizontal" data={topStatesChart} height={230} />
        </>
      )
    },
    {
      id: 'actions',
      size: 'wide',
      content: (
        <>
          <CardHeader eyebrow="Response" title="Action taken breakdown" caveat="Parsed from a free-text field — treat as an approximate categorization." />
          <ChartCanvas type="bar" data={actionChart} height={220} />
        </>
      )
    }
  ];

  return (
    <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.2rem 3rem' }}>
      <div id="kpis">
        <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)' }}>
          Charts
        </p>
        <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 2rem)', marginBottom: '0.4rem' }}>India exam leak tracker, 2000–2026</h1>
        <p style={{ fontSize: '0.9rem', marginBottom: '1.2rem', maxWidth: 640 }}>
          {kpis.total_incidents} incidents logged. Not exhaustive — see the About tab for what this dataset does and doesn't capture.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.8rem', marginBottom: '1.6rem' }}>
          <KpiCard label="Total incidents" value={kpis.total_incidents} />
          <KpiCard label="Confirmed" value={`${kpis.confirmed_pct}%`} />
          <KpiCard label="Total arrests" value={kpis.total_arrests.toLocaleString('en-IN')} />
          <KpiCard label="States / UTs hit" value={kpis.distinct_states} />
        </div>
      </div>

      <MagicBento cards={cards} />

      <aside className="charts-sidebar" aria-label="Jump to chart section">
        <LineSidebar
          items={SECTION_LABELS}
          showIndex
          onItemClick={index => {
            document.getElementById(SECTION_IDS[index])?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
        />
      </aside>
    </section>
  );
};

export default ChartsPage;
