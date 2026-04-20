/**
 * brain_integration.js
 * Unified entry point for brain.js neural network integration.
 * Supports: NeuralNetwork, NeuralNetworkGPU, LSTM, RNN, GRU (via recurrent)
 */
'use strict';

const brain = require('brain.js');

/** NeuralNetwork - feed-forward network */
const NeuralNetwork = brain.NeuralNetwork;

/** CrossValidate - k-fold cross validation */
const CrossValidate = brain.CrossValidate;

/** likely - prediction confidence helper */
const likely = brain.likely;

/** lookup - input/output normalization */
const lookup = brain.lookup;

/** recurrent factories: LSTM, GRU, RNN, etc. */
const recurrent = brain.recurrent;

module.exports = {
  NeuralNetwork,
  CrossValidate,
  likely,
  lookup,
  recurrent,
  // Convenience factories
  createFF: (opts) => new NeuralNetwork(opts),
  createLSTM: (opts) => new recurrent.LSTM(opts),
  createGRU: (opts) => new recurrent.GRU(opts),
  createRNN: (opts) => new recurrent.RNN(opts),
};