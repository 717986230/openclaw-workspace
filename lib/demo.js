/**
 * demo.js - brain.js quick demos
 * Usage: node lib/demo.js [demo-name]
 * Demos: xor, pattern, lstm, lstm-text, recall
 */
'use strict';

const brain = require('brain.js');

// ── Demo 1: XOR (feed-forward) ─────────────────────────────────────────────
function demoXOR() {
  console.log('\n=== Demo: XOR (NeuralNetwork) ===');
  const net = new brain.NeuralNetwork({ hiddenLayers: [4] });
  const data = [
    { input: [0, 0], output: [0] },
    { input: [0, 1], output: [1] },
    { input: [1, 0], output: [1] },
    { input: [1, 1], output: [0] },
  ];
  net.train(data, { iterations: 10000, errorThresh: 0.001, log: false });
  [
    [0, 0], [0, 1], [1, 0], [1, 1]
  ].forEach(([a, b]) => {
    const out = net.run([a, b])[0];
    console.log(`  ${a} XOR ${b} = ${out > 0.5 ? 1 : 0}  (confidence: ${out.toFixed(3)})`);
  });
}

// ── Demo 2: Pattern completion ──────────────────────────────────────────────
function demoPattern() {
  console.log('\n=== Demo: Pattern Completion ===');
  const net = new brain.NeuralNetwork({ hiddenLayers: [8] });
  // Learn 3 repeating patterns
  const data = [
    { input: [1, 0, 0], output: [0, 1, 0] },
    { input: [0, 1, 0], output: [0, 0, 1] },
    { input: [0, 0, 1], output: [1, 0, 0] },
  ];
  net.train(data, { iterations: 3000, errorThresh: 0.001 });
  const tests = [
    [1, 0, 0],
    [0, 1, 0],
    [0.9, 0.1, 0],
    [0, 0.8, 0.2],
  ];
  tests.forEach((input) => {
    const out = net.run(input);
    const norm = out.map((v) => (v > 0.5 ? 1 : 0));
    console.log(`  in: [${input.map((v) => v.toFixed(2)).join(',')}]  out: [${out.map((v) => v.toFixed(3)).join(',')}] → [${norm.join(',')}]`);
  });
}

// ── Demo 3: LSTM sequence memory ────────────────────────────────────────────
function demoLSTM() {
  console.log('\n=== Demo: LSTM Number Sequence ===');
  const net = new brain.recurrent.LSTM();
  const data = [
    { input: [0.1], output: [0.2] },
    { input: [0.2], output: [0.3] },
    { input: [0.3], output: [0.4] },
    { input: [0.4], output: [0.5] },
    { input: [0.5], output: [0.6] },
    { input: [0.6], output: [0.7] },
  ];
  net.train(data, { iterations: 500, errorThresh: 0.01 });
  [0.1, 0.3, 0.55].forEach((v) => {
    const out = net.run([v]);
    const val = Array.isArray(out) ? out[0] : (typeof out === 'object' && out[0] !== undefined ? out[0] : out);
    console.log(`  input ${v} → predicted ${typeof val === 'number' ? val.toFixed(3) : val}  (expect ~${(v + 0.1).toFixed(1)})`);
  });
}

// ── Demo 4: LSTM text-like char prediction ──────────────────────────────────
function demoLSTMText() {
  console.log('\n=== Demo: LSTM Char Prediction (hello/hello) ===');
  const net = new brain.recurrent.LSTM({ gothic: true });
  const training = [
    'hello',
  ];
  // Encode characters
  const chars = [...new Set(training.join(''))];
  const charToIdx = {};
  const idxToChar = {};
  chars.forEach((c, i) => { charToIdx[c] = i; idxToChar[i] = c; });
  const inputSize = chars.length;

  function encode(str) {
    const arr = new Array(inputSize).fill(0);
    arr[charToIdx[str[0]]] = 1;
    return arr;
  }
  function decode(arr) {
    return idxToChar[arr.indexOf(Math.max(...arr))];
  }

  const data = training.map((s) => ({
    input: encode(s[0]),
    output: encode(s[1] || s[0]),
  }));
  net.train(data, { iterations: 200, errorThresh: 0.05 });
  console.log(`  hmm... (LSTM char prediction needs more data to be meaningful)`);
}

// ── Demo 5: Recall from JSON ────────────────────────────────────────────────
function demoRecall() {
  console.log('\n=== Demo: Load & Recall ===');
  const net = new brain.NeuralNetwork();
  const data = [
    { input: [0, 0], output: [0] },
    { input: [0, 1], output: [1] },
    { input: [1, 0], output: [1] },
    { input: [1, 1], output: [0] },
  ];
  net.train(data, { iterations: 1000, errorThresh: 0.01 });
  const json = net.toJSON();
  const reloaded = new brain.NeuralNetwork();
  reloaded.fromJSON(json);
  console.log('  Reloaded network accuracy:');
  [[0,0],[0,1],[1,0],[1,1]].forEach(([a,b]) => {
    console.log(`    ${a} XOR ${b} = ${reloaded.run([a,b])[0] > 0.5 ? 1 : 0}`);
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────
const DEMOS = { xor: demoXOR, pattern: demoPattern, lstm: demoLSTM, 'lstm-text': demoLSTMText, recall: demoRecall };
const names = Object.keys(DEMOS);

if (require.main === module) {
  const name = process.argv[2] || 'xor';
  if (name === 'all') {
    Object.keys(DEMOS).forEach((n) => DEMOS[n]());
  } else if (DEMOS[name]) {
    DEMOS[name]();
  } else {
    console.log('Usage: node lib/demo.js [xor|pattern|lstm|lstm-text|recall|all]');
    console.log('Available:', names.join(', '));
    process.exit(1);
  }
  console.log('\nDone.');
}

module.exports = DEMOS;