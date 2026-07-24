import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const PALETTE = ['#6fa8dc', '#a7c9ea', '#3f7cb8', '#cfe6fb', '#8fb8dd', '#274a68'];

Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";
Chart.defaults.color = '#4d6a85';
Chart.defaults.borderColor = '#e3eefa';

/**
 * type: 'bar' | 'line' | 'doughnut' | 'bar-horizontal'
 * data: Chart.js-style { labels, datasets }
 */
const ChartCanvas = ({ type, data, options = {}, height = 220 }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const resolvedType = type === 'bar-horizontal' ? 'bar' : type;
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: type === 'bar-horizontal' ? 'y' : 'x',
      plugins: {
        legend: {
          display: type === 'doughnut',
          position: 'bottom',
          labels: { boxWidth: 10, padding: 12, font: { size: 11 } }
        },
        tooltip: {
          backgroundColor: '#16283b',
          titleFont: { family: "'IBM Plex Sans', sans-serif" },
          bodyFont: { family: "'IBM Plex Mono', monospace" },
          padding: 10,
          cornerRadius: 8
        }
      },
      scales:
        type === 'doughnut'
          ? undefined
          : {
              x: { grid: { display: type === 'bar-horizontal' }, ticks: { font: { size: 11 } } },
              y: { grid: { color: '#eef6ff' }, ticks: { font: { size: 11 } }, beginAtZero: true }
            }
    };

    chartRef.current = new Chart(canvasRef.current, {
      type: resolvedType,
      data,
      options: { ...baseOptions, ...options }
    });

    return () => chartRef.current?.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type, JSON.stringify(data), JSON.stringify(options)]);

  return (
    <div style={{ position: 'relative', height, width: '100%' }}>
      <canvas ref={canvasRef} />
    </div>
  );
};

export { PALETTE };
export default ChartCanvas;
