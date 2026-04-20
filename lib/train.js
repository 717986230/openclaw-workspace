/**
 * train.js - Reusable training harness for brain.js networks
 * Usage: node lib/train.js [config.json]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const brain = require('brain.js');

const DEFAULT_CONFIG = {
  type: 'NeuralNetwork',
  hiddenLayers: [4],
  iterations: 20000,
  errorThresh: 0.005,
  log: true,
  logPeriod: 1000,
  learningRate: 0.3,
  momentum: 0.1,
  // autoTrain: false = use train(), true = use trainAsync()
  autoTrain: false,
};

function loadConfig(argv) {
  if (argv[2]) {
    try {
      return JSON.parse(fs.readFileSync(argv[2], 'utf8'));
    } catch (e) {
      console.error('Failed to load config:', e.message);
    }
  }
  return {};
}

function createNetwork(type, opts) {
  switch (type) {
    case 'LSTM':
      return new brain.recurrent.LSTM(opts);
    case 'GRU':
      return new brain.recurrent.GRU(opts);
    case 'RNN':
      return new brain.recurrent.RNN(opts);
    case 'NeuralNetwork':
    default:
      return new brain.NeuralNetwork(opts);
  }
}

function train(config, trainingData) {
  const opts = {
    hiddenLayers: config.hiddenLayers,
    iterations: config.iterations,
    errorThresh: config.errorThresh,
    log: config.log ? (msg) => console.log('[train]', msg) : false,
    logPeriod: config.logPeriod,
    learningRate: config.learningRate,
    momentum: config.momentum,
  };

  const net = createNetwork(config.type, opts);

  if (config.autoTrain) {
    // Async training
    net.trainAsync(trainingData).then((result) => {
      console.log('[train] Done. error:', result.error, 'iterations:', result.iterations);
      if (config.output) {
        const json = net.toJSON();
        fs.writeFileSync(config.output, JSON.stringify(json, null, 2));
        console.log('[train] Saved to', config.output);
      }
    }).catch((err) => {
      console.error('[train] Error:', err);
      process.exit(1);
    });
  } else {
    // Sync training
    const result = net.train(trainingData);
    console.log('[train] Done. error:', result.error, 'iterations:', result.iterations);
    if (config.output) {
      const json = net.toJSON();
      fs.writeFileSync(config.output, JSON.stringify(json, null, 2));
      console.log('[train] Saved to', config.output);
    }
    return net;
  }
  return net;
}

function test(net, testData) {
  let correct = 0;
  for (const datum of testData) {
    const output = net.run(datum.input);
    const predicted = Array.isArray(output) ? output.indexOf(Math.max(...output)) : (output > 0.5 ? 1 : 0);
    const expected = Array.isArray(datum.output) ? datum.output.indexOf(Math.max(...datum.output)) : datum.output;
    if (predicted === expected) correct++;
  }
  console.log(`[test] Accuracy: ${correct}/${testData.length} (${(100 * correct / testData.length).toFixed(1)}%)`);
}

module.exports = { train, test, createNetwork };

// CLI mode
if (require.main === module) {
  const config = Object.assign({}, DEFAULT_CONFIG, loadConfig(process.argv));
  console.log('[train] Config:', JSON.stringify(config));

  // Use built-in XOR demo if no data file provided
  let trainingData;
  if (config.data) {
    try {
      trainingData = JSON.parse(fs.readFileSync(config.data, 'utf8'));
      console.log('[train] Loaded', trainingData.length, 'samples from', config.data);
    } catch (e) {
      console.error('Failed to load data:', e.message);
      process.exit(1);
    }
  } else {
    trainingData = [
      { input: [0, 0], output: [0] },
      { input: [0, 1], output: [1] },
      { input: [1, 0], output: [1] },
      { input: [1, 1], output: [0] },
    ];
    console.log('[train] Using XOR demo data');
  }

  const net = train(config, trainingData);

  // Run tests
  console.log('\n[test] Results on training data:');
  test(net, trainingData);
}