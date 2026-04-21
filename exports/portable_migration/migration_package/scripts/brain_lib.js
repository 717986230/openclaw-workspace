/**
 * brain_lib.js - Bridge layer: maps old script API to real brain.js 1.6.1
 * Replaces the old neuralnetwork.js-based exports with live brain.js
 */
'use strict';

const brain = require('brain.js');

exports.NeuralNetwork = brain.NeuralNetwork;
exports.CrossValidate = brain.CrossValidate;
exports.likely = brain.likely;
exports.lookup = brain.lookup;
exports.recurrent = brain.recurrent;

/** @deprecated - alias for backward compatibility */
exports.LSTM = brain.recurrent.LSTM;
exports.RNN = brain.recurrent.RNN;
exports.GRU = brain.recurrent.GRU;