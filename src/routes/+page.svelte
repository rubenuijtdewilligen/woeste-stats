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

  ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

  let { data } = $props();

  let mounted = $state(false);

  let visibleDays = $state({
    Dinsdag: true,
    Woensdag: true,
    Donderdag: true,
    Vrijdag: false,
    Zaterdag: false,
    Zondag: false
  });

  let chartData = $derived.by(() => {
    if (!data || !data.rawData) return null;

    const filteredRaw = data.rawData.filter((row) => visibleDays[row.Dag]);

    const datasets = data.names.map((name) => {
      const countsPerWeek = data.weeks.map((week) => {
        return filteredRaw.filter((row) => row.Naam === name && row['Week van'] === week).length;
      });

      return {
        label: name,
        data: countsPerWeek,
        borderColor: getRandomColor(name),
        backgroundColor: getRandomColor(name),
        tension: 0.3,
        spanGaps: false
      };
    });

    return {
      labels: data.weeks,
      datasets
    };
  });

  onMount(() => {
    mounted = true;
  });

  function getRandomColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return `hsl(${hash % 360}, 70%, 50%)`;
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'right' } }
  };
</script>

<div class="chart-container">
  <div class="controls">
    {#each Object.keys(visibleDays) as day (day)}
      <label>
        <input type="checkbox" bind:checked={visibleDays[day]} />
        {day}
      </label>
    {/each}
  </div>

  {#if mounted && chartData}
    <div style="height: 600px; position: relative;">
      <Line data={chartData} {options} />
    </div>
  {:else}
    <p>Laden...</p>
  {/if}
</div>

<style>
  .chart-container {
    width: 95%;
    margin: 0 auto;
    font-family: sans-serif;
  }
  .controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    background: #f4f4f4;
    padding: 1rem;
    border-radius: 8px;
  }
  label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.9rem;
  }
</style>
