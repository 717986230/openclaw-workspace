#!/usr/bin/env node

/**
 * 消息复杂度分析脚本
 * 分析消息特征，返回复杂度评分（0-10）
 */

const fs = require('fs');
const path = require('path');

// 加载规则配置
const rulesPath = path.join(__dirname, '../config/model-rules.json');
const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));

/**
 * 分析消息复杂度
 * @param {string} message - 用户消息
 * @returns {object} - 复杂度分析结果
 */
function analyzeComplexity(message) {
  const result = {
    length: message.length,
    score: 0,
    features: {
      hasCode: false,
      hasVision: false,
      complexity: 'simple',
      keywords: []
    },
    breakdown: {
      lengthScore: 0,
      keywordScore: 0,
      codeScore: 0,
      visionScore: 0
    }
  };

  // 1. 长度评分（权重0.3）
  if (message.length > 500) {
    result.breakdown.lengthScore = 3;
  } else if (message.length > 200) {
    result.breakdown.lengthScore = 2;
  } else if (message.length > 50) {
    result.breakdown.lengthScore = 1;
  }

  // 2. 关键词评分（权重0.4）
  const { complexity_keywords } = rules.rules;
  
  // 检查所有层级的关键词（按优先级：复杂 > 中等 > 简单）
  const complexMatches = complexity_keywords.complex.filter(kw => message.includes(kw));
  const moderateMatches = complexity_keywords.moderate.filter(kw => message.includes(kw));
  const simpleMatches = complexity_keywords.simple.filter(kw => message.includes(kw));
  
  if (complexMatches.length > 0) {
    result.breakdown.keywordScore = 3;
    result.features.complexity = 'complex';
    result.features.keywords = complexMatches;
  } else if (moderateMatches.length > 0) {
    result.breakdown.keywordScore = 2;
    result.features.complexity = 'moderate';
    result.features.keywords = moderateMatches;
  } else if (simpleMatches.length > 0) {
    result.breakdown.keywordScore = 0;
    result.features.complexity = 'simple';
    result.features.keywords = simpleMatches;
  }

  // 3. 代码检测（权重0.2）
  const { code_patterns } = rules.rules.feature_detection;
  const codeMatches = code_patterns.filter(pattern => message.includes(pattern));
  if (codeMatches.length > 0) {
    result.features.hasCode = true;
    result.breakdown.codeScore = codeMatches.length >= 3 ? 3 : 2;
  }

  // 4. 视觉检测（权重0.1）
  const { vision_keywords } = rules.rules.feature_detection;
  const visionMatches = vision_keywords.filter(kw => message.includes(kw));
  if (visionMatches.length > 0) {
    result.features.hasVision = true;
    result.breakdown.visionScore = 3;
  }

  // 计算总分（0-10）
  const { scoring } = rules.rules;
  let baseScore = 
    result.breakdown.lengthScore * scoring.length_weight +
    result.breakdown.keywordScore * scoring.keyword_weight +
    result.breakdown.codeScore * scoring.code_weight +
    result.breakdown.visionScore * scoring.vision_weight;
  
  // 复杂度调整：如果检测到复杂关键词，至少8分
  if (result.features.complexity === 'complex') {
    baseScore = Math.max(baseScore, 8.0);
  }
  // 中等复杂度至少4分
  else if (result.features.complexity === 'moderate') {
    baseScore = Math.max(baseScore, 4.0);
  }
  
  result.score = Math.min(10, baseScore);

  // 四舍五入到1位小数
  result.score = Math.round(result.score * 10) / 10;

  return result;
}

/**
 * 根据复杂度选择模型
 * @param {object} analysis - 复杂度分析结果
 * @returns {string} - 模型ID
 */
function selectModel(analysis) {
  const { thresholds } = rules;
  const { score, features } = analysis;

  // 优先级：视觉 > 代码 > 复杂度
  if (features.hasVision) {
    return rules.models.vision.id;
  }

  if (features.hasCode) {
    return rules.models.coding.id;
  }

  if (score >= thresholds.complex_min_score) {
    return rules.models.complex.id;
  }

  if (score <= thresholds.flash_max_score) {
    return rules.models.flash.id;
  }

  return rules.models.main.id;
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('用法: node analyze-complexity.js "消息内容"');
    process.exit(1);
  }

  const message = args.join(' ');
  const analysis = analyzeComplexity(message);
  const modelId = selectModel(analysis);

  const output = {
    message: message.substring(0, 100) + (message.length > 100 ? '...' : ''),
    analysis,
    selectedModel: modelId,
    timestamp: new Date().toISOString()
  };

  console.log(JSON.stringify(output, null, 2));
}

// 导出函数供其他模块使用
module.exports = { analyzeComplexity, selectModel };

// 如果直接运行脚本
if (require.main === module) {
  main();
}
