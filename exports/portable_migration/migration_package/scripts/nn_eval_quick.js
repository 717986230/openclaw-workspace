/**
 * nn_eval_quick.js - Fast brain.js evaluation via stdin/stdout
 * Called by nn_memory_bridge.py as a subprocess.
 * Usage: node nn_eval_quick.js [--intent] < stdin.json > stdout.json
 */
const brain = require('brain.js');
const fs = require('fs');

// ── Intent classification network ─────────────────────────────────────────────
const INTENTS = [
  'code', 'learn', 'memory', 'status', 'config',
  'create', 'delete', 'search', 'run', 'question', 'help'
];

function buildIntentNet() {
  const net = new brain.NeuralNetwork({ hiddenLayers: [12, 10] });
  const data = [
    // code
    { input: textToVec('写代码'), output: { code: 1 } },
    { input: textToVec('python脚本'), output: { code: 1 } },
    { input: textToVec('node代码'), output: { code: 1 } },
    { input: textToVec('写一个函数'), output: { code: 1 } },
    { input: textToVec('code script'), output: { code: 1 } },
    // learn
    { input: textToVec('怎么学习'), output: { learn: 1 } },
    { input: textToVec('教程'), output: { learn: 1 } },
    { input: textToVec('learn study'), output: { learn: 1 } },
    { input: textToVec('课程'), output: { learn: 1 } },
    // memory
    { input: textToVec('记忆 查找'), output: { memory: 1 } },
    { input: textToVec('数据库 查询'), output: { memory: 1 } },
    { input: textToVec('memory search'), output: { memory: 1 } },
    // status
    { input: textToVec('状态 检查'), output: { status: 1 } },
    { input: textToVec('health check'), output: { status: 1 } },
    { input: textToVec('状态如何'), output: { status: 1 } },
    // config
    { input: textToVec('配置 安装'), output: { config: 1 } },
    { input: textToVec('setup config'), output: { config: 1 } },
    { input: textToVec('安装技能'), output: { config: 1 } },
    // create
    { input: textToVec('创建 新建'), output: { create: 1 } },
    { input: textToVec('add new'), output: { create: 1 } },
    { input: textToVec('增加一个'), output: { create: 1 } },
    // search
    { input: textToVec('搜索 查找'), output: { search: 1 } },
    { input: textToVec('query lookup'), output: { search: 1 } },
    // run
    { input: textToVec('运行 执行'), output: { run: 1 } },
    { input: textToVec('start run'), output: { run: 1 } },
    { input: textToVec('开始跑'), output: { run: 1 } },
    // question
    { input: textToVec('怎么 什么如何'), output: { question: 1 } },
    { input: textToVec('how what why'), output: { question: 1 } },
    { input: textToVec('是什么'), output: { question: 1 } },
  ];
  net.train(data, { iterations: 300, errorThresh: 0.01, log: false });
  return net;
}

// ── Importance network ────────────────────────────────────────────────────────
function buildImportanceNet() {
  const net = new brain.NeuralNetwork({ hiddenLayers: [8, 6] });
  const data = [
    { input: textToVec('必须永远记住 数据库'), output: [0.9] },
    { input: textToVec('绝对不能忘记'), output: [0.9] },
    { input: textToVec('identity identity 身份'), output: [0.9] },
    { input: textToVec('self improving principle'), output: [0.8] },
    { input: textToVec('brain.js integration skill'), output: [0.8] },
    { input: textToVec('learn skill evolution'), output: [0.7] },
    { input: textToVec('memory database config'), output: [0.7] },
    { input: textToVec('minor log note'), output: [0.4] },
    { input: textToVec('tip optional'), output: [0.3] },
  ];
  net.train(data, { iterations: 500, errorThresh: 0.001, log: false });
  return net;
}

// ── Text vectorization ─────────────────────────────────────────────────────────
const CHAR_MAP = {};
const CHARS = '的一是在不了有和人这中大为上个国我以要他时来平复合和品功动出方年于度高家下里说学着都大面也会对事能用多说去为学过而所种道里多过革当动制然的还会他以时可将心把机分心还又进将其和文库代码运行安装学习配置创建搜索查询状态检查记忆数据库身份关系原则技能学习事件提醒知识项目错误';
(function build() {
  for (let i = 0; i < CHARS.length; i++) CHAR_MAP[CHARS[i]] = i;
})();

function textToVec(text) {
  const dim = 64;
  const vec = new Array(dim).fill(0);
  let maxIdx = 0;
  for (const ch of text) {
    if (CHAR_MAP[ch] !== undefined) {
      const idx = CHAR_MAP[ch] % dim;
      vec[idx] += 1;
    }
    maxIdx++;
  }
  // Bigrams
  for (let i = 0; i < text.length - 1; i++) {
    const bg = text[i] + text[i+1];
    if (bg.length === 2) {
      const idx = (bg.charCodeAt(0) * 31 + bg.charCodeAt(1)) % dim;
      vec[idx] += 0.5;
    }
  }
  // Normalize
  const mag = Math.sqrt(vec.reduce((s, v) => s + v*v, 0));
  if (mag > 0) for (let i = 0; i < dim; i++) vec[i] /= mag;
  return vec;
}

// ── Main ───────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
let input;
try {
  const raw = fs.readFileSync(0, 'utf8');
  input = JSON.parse(raw);
} catch (e) {
  console.error(JSON.stringify({ error: 'invalid stdin JSON' }));
  process.exit(1);
}

const isIntent = args.includes('--intent');

// Lazy-build networks (cached after first call)
if (!global._intentNet) global._intentNet = buildIntentNet();
if (!global._importanceNet) global._importanceNet = buildImportanceNet();

try {
  let result;

  if (isIntent || input._type === 'intent') {
    const text = input.text || '';
    const vec = textToVec(text);
    const out = global._intentNet.run(vec);
    const intents = {};
    for (const intent of INTENTS) {
      intents[intent] = out[intent] !== undefined ? out[intent] : 0;
    }
    result = { intents, text };
  } else {
    // Importance prediction
    const text = [input.text, input.category, (input.tags || []).join(' ')].join(' ');
    const vec = textToVec(text);
    const out = global._importanceNet.run(vec);
    const importance = Math.min(10, Math.max(1, Math.round((out[0] || 0.5) * 10)));
    result = { importance, text: text.slice(0, 50) };
  }

  process.stdout.write(JSON.stringify(result, null, 2));
} catch (e) {
  process.stdout.write(JSON.stringify({ error: e.message }));
}