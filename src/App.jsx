import { useState, useMemo } from 'react';
import LightRays from './components/LightRays.jsx';
import CardNav from './components/CardNav.jsx';
import DisclaimerModal from './components/DisclaimerModal.jsx';
import ChartsPage from './pages/ChartsPage.jsx';
import InfoPage from './pages/InfoPage.jsx';
import AboutPage from './pages/AboutPage.jsx';
import data from './data/leaks.json';

function App() {
  const [page, setPage] = useState('charts');

  const navItems = useMemo(() => [
    {
      label: 'Charts',
      bgColor: '#eaf3fc',
      textColor: '#16283b',
      links: [
        { label: 'Trends & breakdowns', ariaLabel: 'Go to charts overview', onClick: () => setPage('charts') },
        { label: 'Top exams & states', ariaLabel: 'Go to top exams and states charts', onClick: () => setPage('charts') }
      ]
    },
    {
      label: 'Info',
      bgColor: '#d7e9fa',
      textColor: '#16283b',
      links: [
        { label: 'Browse all incidents', ariaLabel: 'Go to the incident table', onClick: () => setPage('info') },
        { label: 'Filter by status or state', ariaLabel: 'Go to filters', onClick: () => setPage('info') }
      ]
    },
    {
      label: 'About',
      bgColor: '#16283b',
      textColor: '#eaf3fc',
      links: [
        { label: 'Why this exists', ariaLabel: 'Go to the about page', onClick: () => setPage('about') },
        { label: 'Sources used', ariaLabel: 'Go to sources', onClick: () => setPage('about') }
      ]
    }
  ]);

  return (
    <>
      <DisclaimerModal />

      <div className="rays-backdrop">
        <LightRays raysOrigin="top-center" raysColor="#bcdcf7" raysSpeed={0.7} lightSpread={1.4} rayLength={1.6} followMouse mouseInfluence={0.06} noiseAmount={0.03} saturation={0.8} />
      </div>

      <CardNav logoText="Exam Leak Tracker" items={navItems} baseColor="#ffffff" menuColor="#16283b" />

      <div className="app-shell">
        {page === 'charts' && <ChartsPage />}
        {page === 'info' && <InfoPage rows={data.rows} />}
        {page === 'about' && <AboutPage />}
      </div>
    </>
  );
}

export default App;
