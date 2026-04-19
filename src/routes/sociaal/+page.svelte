<script>
  let { data } = $props();

  let visibleDays = $state({
    Dinsdag: true,
    Woensdag: true,
    Donderdag: true,
    Vrijdag: true,
    Zaterdag: true,
    Zondag: true
  });

  let socialStats = $derived.by(() => {
    if (!data?.rawData) return { pairs: [], popular: [], wolves: [] };

    const shiftsByMoment = {};
    const loneWolfCounts = {};
    const individualPartners = {};
    const pairs = {};

    const filteredData = data.rawData.filter((row) => {
      if (!row.Dag) return false;
      return visibleDays[row.Dag.trim()] === true;
    });

    filteredData.forEach((row) => {
      const momentKey = `${row['Week van']}-${row.Dag}-${row.Shift}`;
      if (!shiftsByMoment[momentKey]) shiftsByMoment[momentKey] = [];
      shiftsByMoment[momentKey].push(String(row.Naam).trim());
    });

    Object.values(shiftsByMoment).forEach((people) => {
      if (people.length === 1) {
        const wolf = people[0];
        loneWolfCounts[wolf] = (loneWolfCounts[wolf] || 0) + 1;
      } else if (people.length >= 2) {
        for (let i = 0; i < people.length; i++) {
          for (let j = i + 1; j < people.length; j++) {
            const p1 = people[i];
            const p2 = people[j];

            const pairKey = [p1, p2].sort().join(' & ');
            pairs[pairKey] = (pairs[pairKey] || 0) + 1;

            if (!individualPartners[p1]) individualPartners[p1] = new Set();
            if (!individualPartners[p2]) individualPartners[p2] = new Set();
            individualPartners[p1].add(p2);
            individualPartners[p2].add(p1);
          }
        }
      }
    });

    return {
      pairs: Object.entries(pairs)
        .map(([pair, count]) => ({ pair, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 15),
      popular: Object.entries(individualPartners)
        .map(([name, partners]) => ({ name, count: partners.size }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10),
      wolves: Object.entries(loneWolfCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10)
    };
  });
</script>

<div class="social-layout">
  <aside class="sidebar">
    <section class="filter-section">
      <h3>Dagen Filter</h3>
      <div class="day-grid">
        {#each Object.keys(visibleDays) as day (day)}
          <label class="day-label">
            <input type="checkbox" bind:checked={visibleDays[day]} />
            {day}
          </label>
        {/each}
      </div>
    </section>
  </aside>

  <main class="main-content">
    <h1>Sociale Trends</h1>

    <div class="grid-container">
      <section class="card">
        <h2>❤️ Top Duo's</h2>
        <div class="list">
          {#each socialStats.pairs as { pair, count } (pair)}
            <div class="pair-row">
              <span class="name-text">{pair}</span>
              <div class="bar-bg">
                <div
                  class="bar-fill"
                  style="width: {(count / (socialStats.pairs[0]?.count || 1)) * 100}%"
                ></div>
              </div>
              <span class="val"><strong>{count}</strong>x</span>
            </div>
          {/each}
        </div>
      </section>

      <section class="card">
        <h2>🤝 Met de meeste verschillende mensen gestaan</h2>
        <div class="list">
          {#each socialStats.popular as person, i (person.name)}
            <div class="row">
              <span class="rank">#{i + 1}</span>
              <span class="name">{person.name}</span>
              <span class="val">{person.count} partners</span>
            </div>
          {/each}
        </div>
      </section>

      <section class="card">
        <h2>🐺 Eenzame Wolf Ranking</h2>
        <div class="list">
          {#each socialStats.wolves as wolf, i (wolf.name)}
            <div class="row">
              <span class="rank">#{i + 1}</span>
              <span class="name">{wolf.name}</span>
              <span class="val"><strong>{wolf.count}</strong> solo's</span>
            </div>
          {/each}
        </div>
      </section>
    </div>
  </main>
</div>

<style>
  .social-layout {
    display: flex;
    height: calc(100vh - 65px);
  }

  .sidebar {
    width: 250px;
    background: white;
    border-right: 1px solid #e0e0e0;
    padding: 1.5rem;
  }

  .main-content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    background: #fcfcfc;
  }

  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
  }

  .card {
    background: white;
    padding: 1.25rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }

  .day-grid {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  .day-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.9rem;
  }

  h1 {
    margin: 0;
  }
  h2 {
    font-size: 1.1rem;
    border-bottom: 2px solid #f8f8f8;
    padding-bottom: 0.5rem;
  }

  .row,
  .pair-row {
    display: flex;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #fcfcfc;
  }
  .rank {
    width: 30px;
    color: #ccc;
    font-weight: bold;
  }
  .name {
    flex: 1;
  }

  .name-text {
    width: 140px;
    font-size: 0.85rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .bar-bg {
    flex: 1;
    background: #eee;
    height: 8px;
    border-radius: 4px;
    margin: 0 10px;
  }
  .bar-fill {
    background: #ff9a9e;
    height: 100%;
    border-radius: 4px;
  }
  .val {
    font-size: 0.85rem;
    color: #666;
    min-width: 60px;
    text-align: right;
  }
</style>
