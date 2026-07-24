import CardSwap, { Card } from '../components/CardSwap.jsx';

const SOURCES = [
  { name: 'The Tribune', note: 'Contemporaneous reporting since 2004, plus the 2026 two-decade retrospective this project started from.' },
  { name: 'Careers360', note: 'The single largest source of incident-level detail: arrest counts, dates, and candidate numbers.' },
  { name: 'Newslaundry', note: 'Investigative analysis of ~89 leak cases over a decade, with party- and state-level breakdowns.' },
  { name: 'The Wire', note: 'In-depth coverage of the 2024 NEET-UG leak and its Supreme Court proceedings.' },
  { name: 'Press Trust of India (PTI)', note: 'Wire-service reporting syndicated across most Indian news outlets cited here.' },
  { name: 'ThePrint', note: 'Coverage of UPPSC, JPSC, and other state recruitment-exam leaks.' },
  { name: 'Deccan Herald', note: 'Archival coverage reaching back to some of the earliest 2000s-era incidents.' },
  { name: 'Wikipedia', note: 'Background on the Vyapam scam and the unfolding 2026 NEET controversy.' }
];

const AboutPage = () => (
  <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.2rem' }}>
    <div className="about-grid">
      <div className="about-text">
        <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)' }}>
          About
        </p>
        <h1 style={{ fontSize: 'clamp(1.6rem, 4vw, 2.3rem)', marginBottom: '0.9rem', lineHeight: 1.15 }}>
          Why this exists
        </h1>
        <p style={{ fontSize: '0.95rem', marginBottom: '0.9rem' }}>
          Exam paper leaks in India rarely get tracked in one place. Each one is covered locally, gets a news cycle,
          and then scatters across hundreds of state and national outlets. When the 2026 NEET-UG leak set off protests
          in Delhi, it became clear there was no single, browsable record of how often this has happened, to which
          exams, under which administrations, and with what consequences.
        </p>
        <p style={{ fontSize: '0.95rem', marginBottom: '0.9rem' }}>
          This project pulls that scattered coverage into one dataset: 129 incidents from 2000 to 2026, spanning
          national entrance exams, state recruitment tests, and school board exams. It leans on an AI research
          assistant to do the searching, cross-checking, and structuring at a scale that would take a person weeks
          to do by hand.
        </p>
        <p style={{ fontSize: '0.95rem', marginBottom: '0.9rem' }}>
          That speed comes with a real tradeoff: the underlying research was not independently fact-checked
          incident-by-incident against primary court records. Confidence levels are recorded per row, several
          allegations were later denied by investigators, and coverage skews toward whichever states and years have
          the most searchable English-language press. Treat this as a starting point for further reporting or
          research, not a definitive record.
        </p>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Every incident links back to its original source in the Info tab — that's the place to verify anything you
          plan to rely on.
        </p>
      </div>

      <div className="about-swap">
        <CardSwap width={300} height={230} cardDistance={40} verticalDistance={46} delay={3600} pauseOnHover>
          {SOURCES.map(s => (
            <Card key={s.name}>
              <span className="source-eyebrow">Source</span>
              <h3 className="source-name">{s.name}</h3>
              <p className="source-note">{s.note}</p>
            </Card>
          ))}
        </CardSwap>
      </div>
    </div>
  </section>
);

export default AboutPage;
