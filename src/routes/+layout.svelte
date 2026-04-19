<script>
  import { resolve } from '$app/paths';
  import { page } from '$app/stores';

  let { children } = $props();
</script>

<nav class="navbar">
  <div class="nav-container">
    <span class="logo">🍻 Woeste Stats </span>
    <small>(c) Ruben Uijtdewilligen, 2026</small>
    <div class="nav-links">
      <a href={resolve('/')} class:active={$page.url.pathname === '/'}> Verloop </a>
      <a href={resolve('/shiftmix')} class:active={$page.url.pathname === '/shiftmix'}>
        Shift Mix
      </a>
    </div>
  </div>
</nav>

<main>
  {@render children()}
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #fcfcfc;
  }

  .navbar {
    background-color: #fff;
    border-bottom: 1px solid #e0e0e0;
    padding: 0.75rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .nav-container {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    font-weight: bold;
    font-size: 1.2rem;
    color: #333;
  }

  .nav-links {
    display: flex;
    gap: 1.5rem;
  }

  .nav-links a {
    text-decoration: none;
    color: #666;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
  }

  .nav-links a:hover {
    color: #1976d2;
  }

  .nav-links a.active {
    color: #1976d2;
    border-bottom-color: #1976d2;
  }

  main {
    padding: 0;
  }
</style>
