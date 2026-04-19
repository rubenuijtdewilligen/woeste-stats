<script>
  import { onMount } from 'svelte';
  import { Line } from 'svelte-chartjs';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    LinearScale,
    PointElement,
    CategoryScale
  } from 'chart.js';
  import { SvelteSet } from 'svelte/reactivity';

  ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

  let { data } = $props();

  const BESTUUR_NAMEN = ['Joran', 'Ruben', 'Ilse', 'Anouk', 'Jasper', 'Thomas vA', 'Thomas Au'];

  const BESTUUR_KLEUREN = [
    '#E63946', // Rood
    '#2A9D8F', // Groen
    '#F4A261', // Oranje
    '#457B9D', // Blauw
    '#9B5DE5', // Paars
    '#F15BB5' // Roze
  ];

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

  const toggleAll = (show) => {
    if (show) selectedNames = new SvelteSet(data.names);
    else selectedNames = new SvelteSet();
  };

  const selectBestuur = () => {
    selectedNames = new SvelteSet(data.names.filter((n) => BESTUUR_NAMEN.includes(n)));
  };

  let filteredNameList = $derived(
    data.names.filter((n) => n.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  let chartData = $derived.by(() => {
    if (!data || !data.rawData || selectedNames.size === 0) return null;

    const filteredRaw = data.rawData.filter(
      (row) => visibleDays[row.Dag] && selectedNames.has(row.Naam)
    );

    const datasets = Array.from(selectedNames).map((name) => {
      const countsPerWeek = data.weeks.map((week) => {
        return filteredRaw.filter((row) => row.Naam === name && row['Week van'] === week).length;
      });

      const color = getPersonColor(name);

      return {
        label: name,
        data: countsPerWeek,
        borderColor: color,
        backgroundColor: color,
        tension: 0.3,
        pointRadius: BESTUUR_NAMEN.includes(name) ? 4 : 2,
        borderWidth: BESTUUR_NAMEN.includes(name) ? 3 : 1.5,
        spanGaps: false
      };
    });

    return { labels: data.weeks, datasets };
  });

  onMount(() => {
    selectBestuur();
    mounted = true;
  });

  function getPersonColor(name) {
    const bestuurIndex = BESTUUR_NAMEN.indexOf(name);

    if (bestuurIndex !== -1) {
      return BESTUUR_KLEUREN[bestuurIndex % BESTUUR_KLEUREN.length];
    }

    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return `hsl(${hash % 360}, 40%, 65%)`;
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { beginAtZero: true, ticks: { stepSize: 1 } }
    }
  };
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
          <label class="name-item" style="--color: {getPersonColor(name)}">
            <input
              type="checkbox"
              checked={selectedNames.has(name)}
              onchange={(e) => {
                if (e.target.checked) selectedNames.add(name);
                else selectedNames.delete(name);
              }}
            />
            <span class="color-dot"></span>
            <span class={BESTUUR_NAMEN.includes(name) ? 'font-bold' : ''}>{name}</span>
          </label>
        {/each}
      </div>
    </div>
  </aside>

  <main class="main-content">
    <h2>Shift Verloop per Persoon</h2>

    {#if mounted && chartData}
      <div class="chart-wrapper">
        <Line data={chartData} {options} />
      </div>
    {:else if selectedNames.size === 0}
      <div class="empty-state">Selecteer minimaal één persoon om de grafiek te zien.</div>
    {:else}
      <p>Laden...</p>
    {/if}
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background-color: #fcfcfc;
  }

  .app-layout {
    display: flex;
    height: 100vh;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .sidebar {
    width: 280px;
    background: white;
    border-right: 1px solid #e0e0e0;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.02);
  }

  .main-content {
    flex: 1;
    padding: 2rem;
    display: flex;
    flex-direction: column;
  }

  .section {
    margin-bottom: 1.5rem;
  }
  h3,
  h4 {
    margin: 0 0 0.75rem 0;
    color: #333;
  }

  .day-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .button-group {
    display: flex;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
  }
  button {
    flex: 1;
    padding: 0.4rem;
    border: 1px solid #ccc;
    background: #fff;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
  }
  button:hover {
    background: #f0f0f0;
  }
  .btn-preset {
    background: #e3f2fd;
    border-color: #2196f3;
    color: #1976d2;
    font-weight: bold;
  }

  .search-input {
    width: 100%;
    box-sizing: border-box;
    padding: 0.6rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .name-list {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #eee;
    border-radius: 4px;
    padding: 0.5rem;
    background: #fafafa;
  }

  .name-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.3rem;
    font-size: 0.85rem;
    cursor: pointer;
    border-radius: 3px;
  }
  .name-item:hover {
    background: #f0f0f0;
  }

  .font-bold {
    font-weight: bold;
    text-decoration: underline;
  }

  .color-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--color);
    display: inline-block;
    border: 1px solid rgba(0, 0, 0, 0.1);
  }

  .chart-wrapper {
    flex: 1;
    position: relative;
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 300px;
    color: #888;
    border: 2px dashed #ddd;
    border-radius: 8px;
  }
</style>
