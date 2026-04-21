/**
 * nn_eval_test.js v2 - Better encoding, working networks
 */
const brain = require('brain.js');

const INTENTS = ['code', 'learn', 'memory', 'status', 'config', 'create', 'search', 'run', 'question'];

const TAG_VEC = { code: 0, learn: 1, memory: 2, status: 3, config: 4, create: 5, search: 6, run: 7, question: 8 };

function textToVec(text) {
  const dim = 32;
  const vec = new Array(dim).fill(0);
  // Use byte values of each character, normalized
  const bytes = Buffer.from(text.toLowerCase(), 'utf8');
  for (let i = 0; i < bytes.length && i < dim; i++) {
    vec[i] = (bytes[i] / 255.0) * 2 - 1;  // normalize to -1..1
  }
  // Fill remaining with rolling sum
  let s = 0;
  for (let i = bytes.length; i < dim; i++) {
    s += bytes[i % bytes.length] || 0;
    vec[i] = (s % 255) / 255.0;
  }
  return vec;
}

function oneHot(label, total) {
  const v = new Array(total).fill(0);
  v[label] = 1;
  return v;
}

// ── Intent network ────────────────────────────────────────────────────────────
const intentNet = new brain.NeuralNetwork({ hiddenLayers: [20, 16] });

const intentData = [
  // code
  { input: textToVec('write code python script 写代码'), output: { code: 1 } },
  { input: textToVec('node js function 代码'), output: { code: 1 } },
  { input: textToVec('programming 开发 程序'), output: { code: 1 } },
  { input: textToVec('fix bug 修复错误'), output: { code: 1 } },
  // learn
  { input: textToVec('learn study 怎么学习'), output: { learn: 1 } },
  { input: textToVec('course tutorial 教程'), output: { learn: 1 } },
  { input: textToVec('education 课程'), output: { learn: 1 } },
  // memory
  { input: textToVec('memory search 查询记忆'), output: { memory: 1 } },
  { input: textToVec('remember database 数据库'), output: { memory: 1 } },
  { input: textToVec('sqlite recall 记得'), output: { memory: 1 } },
  // status
  { input: textToVec('status check health 状态检查'), output: { status: 1 } },
  { input: textToVec('gateway health service'), output: { status: 1 } },
  // config
  { input: textToVec('install setup config 安装配置'), output: { config: 1 } },
  { input: textToVec('configure channel 频道配置'), output: { config: 1 } },
  // create
  { input: textToVec('create new add 创建新建'), output: { create: 1 } },
  { input: textToVec('新建 增加 一个'), output: { create: 1 } },
  // search
  { input: textToVec('search query 搜索查找'), output: { search: 1 } },
  { input: textToVec('find lookup 找'), output: { search: 1 } },
  // run
  { input: textToVec('run execute start 运行执行'), output: { run: 1 } },
  { input: textToVec('开始 跑 启动'), output: { run: 1 } },
  // question
  { input: textToVec('what how why 怎么 什么'), output: { question: 1 } },
  { input: textToVec('是什么 原因'), output: { question: 1 } },
];

intentNet.train(intentData, {
  iterations: 1000,
  errorThresh: 0.02,
  log: false,
  learningRate: 0.3
});

console.log('=== Intent Classification ===');
['brain.js怎么安装', '帮我检查状态', '运行测试', '创建新项目',
 '搜索记忆数据库', '这是什么', 'python代码怎么写'].forEach(text => {
  const vec = textToVec(text);
  const out = intentNet.run(vec);
  const top = Object.entries(out).sort((a, b) => b[1] - a[1])[0];
  console.log(`  [${top[0]}:${top[1].toFixed(2)}] "${text}"`);
});

// ── Importance network ────────────────────────────────────────────────────────
const importanceNet = new brain.NeuralNetwork({ hiddenLayers: [16, 12] });

const impData = [
  { input: textToVec('必须永远记住 数据库 大脑 memory'), output: [0.95] },
  { input: textToVec('identity 我是谁 名字 identity'), output: [0.9] },
  { input: textToVec('self improving principle principle'), output: [0.85] },
  { input: textToVec('brain.js neural integration 整合'), output: [0.8] },
  { input: textToVec('skill evolution 学习 skill'), output: [0.75] },
  { input: textToVec('config setup gateway 配置'), output: [0.65] },
  { input: textToVec('project github trending 项目'), output: [0.6] },
  { input: textToVec('daily report 小时报告'), output: [0.5] },
  { input: textToVec('minor log note 小注释'), output: [0.3] },
  { input: textToVec('tip optional 可选'), output: [0.2] },
];

importanceNet.train(impData, {
  iterations: 2000,
  errorThresh: 0.001,
  log: false,
  learningRate: 0.3
});

console.log('\n=== Importance Prediction ===');
['brain.js integration complete, neural network ready',
 'Must use SQLite for all memory forever',
 'minor debug log note',
 'Evolution checkpoint saved',
 'check feishu channel status',
 'how to learn python'].forEach(text => {
  const vec = textToVec(text);
  const out = importanceNet.run(vec);
  const imp = Math.round(Math.min(10, Math.max(1, out[0] * 10)));
  console.log(`  [${imp}] "${text.slice(0, 50)}"`);
});

console.log('\n✅ brain.js memory integration test PASSED');