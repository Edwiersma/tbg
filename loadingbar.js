/**
 * loadingbar.js
 * Animated ASCII loading bar for DCRAWL terminal.
 *
 * Usage:
 *   await runLoadingBar(addLine, renderLines);
 *
 * Parameters:
 *   addLine(text, cls)   — function that appends a line object to the lines array
 *   renderLines()        — function that re-renders the output element
 */

async function runLoadingBar(addLine, renderLines) {
  const TOTAL_STEPS = 24;
  const BAR_WIDTH   = 46;
  const STEP_MS     = 96;

  const stages = [
    'Initializing engine',
    'Loading world data ',
    'Compiling map      ',
    'Ready              ',
  ];

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function buildBar(filled) {
    return '[' + '#'.repeat(filled) + '-'.repeat(BAR_WIDTH - filled) + ']';
  }

  // Push a mutable placeholder line that we will update in-place
  const label = { text: '', cls: 'bar' };
  addLine(null, null, label); // pass the object directly (see note below)
  renderLines();

  const stageSteps = Math.floor(TOTAL_STEPS / stages.length);

  for (let s = 0; s < stages.length; s++) {
    for (let i = 0; i <= stageSteps; i++) {
      const done  = s * stageSteps + i;
      const pct   = Math.round(done / TOTAL_STEPS * 100);
      const filled = Math.round(done / TOTAL_STEPS * BAR_WIDTH);

      label.text = stages[s] + ' ' + buildBar(filled) + ' ' + String(pct).padStart(3) + '%';
      renderLines();
      await sleep(STEP_MS);
    }
  }

  label.text = 'Ready              ' + buildBar(BAR_WIDTH) + ' 100%';
  renderLines();
  await sleep(120);
}
