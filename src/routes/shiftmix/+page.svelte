<script>
  import { onMount } from 'svelte';
  import { Bar } from 'svelte-chartjs';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    LinearScale,
    CategoryScale
  } from 'chart.js';
  import { SvelteSet } from 'svelte/reactivity';

  ChartJS.register(Title, Tooltip, Legend, BarElement, LinearScale, CategoryScale);

  let { data } = $props();

  const BESTUUR_NAMEN = ['Joran', 'Ruben', 'Ilse', 'Anouk', 'Jasper', 'Thomas vA', 'Thomas Au'];
  const BESTUUR_KLEUREN = ['#E63946', '#2A9D8F', '#F4A261', '#457B9D', '#9B5DE5', '#F15BB5'];

  let mounted = $state(false);
  let searchTerm = $state('');
  let selectedNames = $state(new SvelteSet());

  let visibleDays = $state({
    Dinsdag: true,
    Woensdag: true,
    Donderdag: true,
    Vrijdag: false,
    Zaterdag: false,
    Zondag: false
  });

  function getPersonColor(name) {
    const bestuurIndex = BESTUUR_NAMEN.indexOf(name);
    if (bestuurIndex !== -1) return BESTUUR_KLEUREN[bestuurIndex % BESTUUR_KLEUREN.length];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return `hsl(${hash % 360}, 45%, 65%)`;
  }

  const selectBestuur = () => {
    selectedNames = new SvelteSet(data.names.filter((n) => BESTUUR_NAMEN.includes(n)));
  };

  const toggleAll = (show) => {
    if (show) selectedNames = new SvelteSet(data.names);
    else selectedNames = new SvelteSet();
  };

  let filteredNameList = $derived(
    data.names.filter((n) => n.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  let shiftMixData = $derived.by(() => {
    if (!data || !data.rawData || selectedNames.size === 0) return null;

    const shiftTypen = ['Open', 'Spits', 'Sluit', 'Naschoonmaak'];
    const namesArray = Array.from(selectedNames);

    const filteredRaw = data.rawData.filter((row) => {
      if (!row.Dag) return false;
      const dagSchoon = row.Dag.trim();
      return visibleDays[dagSchoon] === true;
    });

    const datasets = shiftTypen.map((type) => {
      const colors = {
        Open: '#4cc9f0',
        Spits: '#4895ef',
        Sluit: '#4361ee',
        Naschoonmaak: '#3f37c9'
      };

      return {
        label: type,
        data: namesArray.map((name) => {
          return filteredRaw.filter(
            (d) =>
              String(d.Naam).trim() === String(name).trim() &&
              String(d.Shift).trim() === String(type).trim()
          ).length;
        }),
        backgroundColor: colors[type] || '#ccc'
      };
    });

    return { labels: namesArray, datasets };
  });

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true, ticks: { stepSize: 1 } }
    }
  };

  onMount(() => {
    console.log('Check rawData Shift values:', data.rawData[0]?.Shift);
    selectBestuur();
    mounted = true;
  });

  let averageStats = $derived.by(() => {
    if (!data || !data.rawData || selectedNames.size === 0) return [];

    const weeksArray = data.weeks;
    const namesArray = Array.from(selectedNames);

    return namesArray
      .map((name) => {
        const personShifts = data.rawData.filter(
          (d) => String(d.Naam).trim() === String(name).trim()
        );

        if (personShifts.length === 0) return { name, avg: 0, total: 0 };

        const weekIndices = personShifts
          .map((s) => weeksArray.indexOf(s['Week van']))
          .filter((i) => i !== -1);
        const firstWeekIdx = Math.min(...weekIndices);
        const lastWeekIdx = Math.max(...weekIndices);

        const activeWeeksCount = lastWeekIdx - firstWeekIdx + 1;
        const totalShifts = personShifts.length;
        const avg = totalShifts / activeWeeksCount;

        return {
          name,
          avg: avg.toFixed(2),
          total: totalShifts,
          activeWeeks: activeWeeksCount
        };
      })
      .sort((a, b) => b.avg - a.avg);
  });
</script>

<div class="app-layout">
  <aside class="sidebar">
    <div class="section">
      <h4>Dagen</h4>
      <div class="day-grid">
        {#each Object.keys(visibleDays) as day (day)}
          <label class="check-label">
            <input type="checkbox" bind:checked={visibleDays[day]} />
            {day}
          </label>
        {/each}
      </div>
    </div>

    <div class="section">
      <h4>Personen ({selectedNames.size})</h4>
      <div class="button-group">
        <button onclick={selectBestuur} class="btn-preset">Bestuur</button>
        <button onclick={() => toggleAll(true)}>Alles</button>
        <button onclick={() => toggleAll(false)}>Niks</button>
      </div>

      <input type="text" placeholder="Zoek naam..." bind:value={searchTerm} class="search-input" />

      <div class="name-list">
        {#each filteredNameList as name (name)}
          <label class="name-item">
            <input
              type="checkbox"
              checked={selectedNames.has(name)}
              onchange={(e) => {
                if (e.target.checked) selectedNames.add(name);
                else selectedNames.delete(name);
              }}
            />
            <span class="color-dot" style="background-color: {getPersonColor(name)}"></span>
            <span class={BESTUUR_NAMEN.includes(name) ? 'font-bold' : ''}>{name}</span>
          </label>
        {/each}
      </div>
    </div>
  </aside>

  <main class="main-content">
    <header>
      <h2>Shift Mix per Persoon</h2>
    </header>

    {#if mounted && shiftMixData}
      <div class="chart-wrapper">
        <Bar data={shiftMixData} options={barOptions} />
      </div>
    {:else if selectedNames.size === 0}
      <div class="empty-state">Selecteer personen om de verdeling te zien.</div>
    {:else}
      <div class="empty-state">Laden of geen data gevonden...</div>
    {/if}

    <section class="stats-section">
      <div class="spacer"></div>
      <h2>Gemiddelde Shifts per Week per Persoon</h2>

      <div class="stats-grid">
        {#each averageStats as stat (stat.name)}
          <div class="stat-card" style="border-left: 4px solid {getPersonColor(stat.name)}">
            <div class="stat-header">
              <span class="stat-name {BESTUUR_NAMEN.includes(stat.name) ? 'font-bold' : ''}">
                {stat.name}
              </span>
              <span class="stat-avg">{stat.avg}</span>
            </div>
            <div class="stat-details">
              <span>Totaal: <strong>{stat.total}</strong> shifts</span>
              <span>Periode: <strong>{stat.activeWeeks}</strong> weken</span>
            </div>
          </div>
        {/each}
      </div>
    </section>
  </main>
</div>

<style>
  .app-layout {
    display: flex;
    height: calc(100vh - 65px);
  }
  .sidebar {
    width: 280px;
    background: white;
    border-right: 1px solid #e0e0e0;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
  }
  .main-content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    background: #fcfcfc;
  }
  .chart-wrapper {
    height: 550px;
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }
  .section {
    margin-bottom: 1.5rem;
  }
  .day-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }
  .button-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  button {
    flex: 1;
    padding: 0.4rem;
    cursor: pointer;
    border: 1px solid #ccc;
    background: white;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  .btn-preset {
    background: #e3f2fd;
    color: #1976d2;
    border-color: #2196f3;
    font-weight: bold;
  }
  .search-input {
    width: 100%;
    padding: 0.6rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
    margin: 0.5rem 0;
  }
  .name-list {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #eee;
    padding: 0.5rem;
    border-radius: 4px;
    background: #fafafa;
  }
  .name-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.3rem;
    font-size: 0.85rem;
    cursor: pointer;
  }
  .color-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
  }
  .font-bold {
    font-weight: bold;
    text-decoration: underline;
  }
  .empty-state {
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed #ddd;
    color: #888;
    border-radius: 8px;
  }
  h2 {
    margin: 0;
  }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .stat-card {
    background: white;
    padding: 1rem;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .stat-name {
    font-size: 1rem;
    color: #333;
  }
  .stat-avg {
    font-size: 1.4rem;
    font-weight: bold;
    color: #1976d2;
  }

  .stat-details {
    display: flex;
    flex-direction: column;
    font-size: 0.8rem;
    color: #666;
  }

  .spacer {
    height: 3rem;
  }
</style>
