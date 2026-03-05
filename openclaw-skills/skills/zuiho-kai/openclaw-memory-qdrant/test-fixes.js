/**
 * 自验证测试 - v1.0.11 PII 保护验证
 *
 * 测试修复的问题：
 * - PII 保护：移除 PII 模式从自动捕获触发器
 * - containsPII() 函数正确检测邮箱和电话号码
 * - detectCategory 不再使用 PII 模式
 */

import { shouldCapture, detectCategory, sanitizeInput, containsPII } from './index.js';

// ============================================================================
// 测试工具
// ============================================================================

let testsPassed = 0;
let testsFailed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`✅ PASS: ${message}`);
    testsPassed++;
  } else {
    console.error(`❌ FAIL: ${message}`);
    testsFailed++;
  }
}

function assertEquals(actual, expected, message) {
  if (actual === expected) {
    console.log(`✅ PASS: ${message}`);
    testsPassed++;
  } else {
    console.error(`❌ FAIL: ${message}`);
    console.error(`  Expected: ${expected}`);
    console.error(`  Actual: ${actual}`);
    testsFailed++;
  }
}

// ============================================================================
// 测试套件
// ============================================================================

console.log('\n🧪 开始自验证测试...\n');

// 测试 1: sanitizeInput - HTML 标签清理
console.log('📋 测试组 1: 输入清理 (sanitizeInput)');
{
  const input1 = '<script>alert("xss")</script>Hello';
  const result1 = sanitizeInput(input1);
  assert(!result1.includes('<script>'), '应该移除 script 标签');
  assertEquals(result1, 'alert("xss")Hello', '应该只保留文本内容');

  const input2 = '<b>Bold</b> and <i>italic</i>';
  const result2 = sanitizeInput(input2);
  assertEquals(result2, 'Bold and italic', '应该移除所有 HTML 标签');

  const input3 = 'Normal text';
  const result3 = sanitizeInput(input3);
  assertEquals(result3, 'Normal text', '普通文本应该保持不变');

  const input4 = '  Multiple   spaces  ';
  const result4 = sanitizeInput(input4);
  assertEquals(result4, 'Multiple spaces', '应该规范化空白字符');

  const input5 = 'Line1\x00\x01\x02Line2';
  const result5 = sanitizeInput(input5);
  assert(!result5.includes('\x00'), '应该移除控制字符');
  assertEquals(result5, 'Line1Line2', '应该移除控制字符但保留文本');
}

// 测试 2: detectCategory - 不再使用 PII 模式
console.log('\n📋 测试组 2: 分类检测 (detectCategory - 无 PII 模式)');
{
  // 测试电话号码（不应该被识别为 entity）
  const phone1 = '+1234567890';  // 10 位
  const cat1 = detectCategory(phone1);
  assert(cat1 !== 'entity', '电话号码不应该被自动识别为 entity');

  const phone2 = '+12345678901234';  // 14 位
  const cat2 = detectCategory(phone2);
  assert(cat2 !== 'entity', '超长电话号码不应该被识别为 entity');

  // 测试邮箱（不应该被识别为 entity）
  const email1 = 'test@example.com';
  const cat3 = detectCategory(email1);
  assert(cat3 !== 'entity', '邮箱不应该被自动识别为 entity');

  const email2 = 'invalid@';
  const cat4 = detectCategory(email2);
  assert(cat4 !== 'entity', '无效邮箱不应该被识别为 entity');

  // 测试偏好
  const pref1 = 'I prefer using TypeScript';
  const cat5 = detectCategory(pref1);
  assertEquals(cat5, 'preference', '偏好语句应该被识别为 preference');

  // 测试决策
  const decision1 = 'We decided to use React';
  const cat6 = detectCategory(decision1);
  assertEquals(cat6, 'decision', '决策语句应该被识别为 decision');
}

// 测试 2.5: containsPII - PII 检测功能
console.log('\n📋 测试组 2.5: PII 检测 (containsPII)');
{
  // 测试邮箱检测
  const email1 = 'test@example.com';
  assert(containsPII(email1), '应该检测到邮箱');

  const email2 = 'My email is user@domain.org';
  assert(containsPII(email2), '应该检测到文本中的邮箱');

  const noEmail = 'No email here';
  assert(!containsPII(noEmail), '不应该误检测邮箱');

  // 测试电话号码检测
  const phone1 = '+1234567890';
  assert(containsPII(phone1), '应该检测到 10 位电话号码');

  const phone2 = '+12345678901';
  assert(containsPII(phone2), '应该检测到 11 位电话号码');

  const phone3 = '+123456789012';
  assert(containsPII(phone3), '应该检测到 12 位电话号码');

  const phone4 = '+1234567890123';
  assert(containsPII(phone4), '应该检测到 13 位电话号码');

  const phone5 = '+12345678901234';
  assert(!containsPII(phone5), '不应该检测到 14 位电话号码（超出范围）');

  const noPhone = 'No phone here';
  assert(!containsPII(noPhone), '不应该误检测电话号码');
}

// 测试 3: shouldCapture - 不再触发 PII 捕获
console.log('\n📋 测试组 3: 捕获过滤 (shouldCapture - 无 PII 触发)');
{
  // shouldCapture 不再检查 PII，只检查语义触发器
  // PII 检查由 containsPII 和 autoCapture 逻辑处理

  const email1 = 'My email is test@example.com';
  const result1 = shouldCapture(email1);
  const hasPII1 = containsPII(email1);
  assert(result1 && hasPII1, '包含邮箱的文本会触发捕获，但应该被 PII 检查拦截');

  const phone1 = 'Call me at +1234567890';
  const result2 = shouldCapture(phone1);
  const hasPII2 = containsPII(phone1);
  assert(!result2 || hasPII2, '包含电话号码的文本如果触发捕获，应该被 PII 检查拦截');

  const remember1 = 'Remember to buy milk';
  const result3 = shouldCapture(remember1);
  const hasPII3 = containsPII(remember1);
  assert(result3 && !hasPII3, '包含 remember 关键词且无 PII 的文本应该被捕获');

  const prefer1 = 'I prefer dark mode';
  const result4 = shouldCapture(prefer1);
  const hasPII4 = containsPII(prefer1);
  assert(result4 && !hasPII4, '包含 prefer 关键词且无 PII 的文本应该被捕获');

  const short1 = 'Hi';
  const result5 = shouldCapture(short1);
  assert(!result5, '过短的文本不应该被捕获');

  const long1 = 'a'.repeat(1000);
  const result6 = shouldCapture(long1, 500);
  assert(!result6, '超长文本不应该被捕获');
}

// 测试 4: ReDoS 防护
console.log('\n📋 测试组 4: ReDoS 防护');
{
  // 测试可能导致 ReDoS 的输入
  const malicious1 = '+' + '1'.repeat(100);  // 超长电话号码
  const start1 = Date.now();
  const cat1 = detectCategory(malicious1);
  const duration1 = Date.now() - start1;
  assert(duration1 < 100, `超长电话号码处理应该很快 (${duration1}ms)`);

  const malicious2 = 'a'.repeat(100) + '@' + 'b'.repeat(100) + '.' + 'c'.repeat(100);
  const start2 = Date.now();
  const result2 = shouldCapture(malicious2);
  const duration2 = Date.now() - start2;
  assert(duration2 < 100, `复杂邮箱模式处理应该很快 (${duration2}ms)`);
}

// 测试 5: 边界情况
console.log('\n📋 测试组 5: 边界情况');
{
  // null/undefined 输入
  const result1 = sanitizeInput(null);
  assertEquals(result1, '', 'null 应该返回空字符串');

  const result2 = sanitizeInput(undefined);
  assertEquals(result2, '', 'undefined 应该返回空字符串');

  const result3 = sanitizeInput('');
  assertEquals(result3, '', '空字符串应该返回空字符串');

  // 非字符串输入
  const result4 = sanitizeInput(123);
  assertEquals(result4, '', '数字应该返回空字符串');

  const result5 = sanitizeInput({});
  assertEquals(result5, '', '对象应该返回空字符串');
}

// 测试 6: 中文支持
console.log('\n📋 测试组 6: 中文支持');
{
  const chinese1 = '记住这个重要信息';
  const result1 = shouldCapture(chinese1);
  assert(result1, '中文 "记住" 关键词应该被捕获');

  const chinese2 = '我喜欢用 TypeScript';
  const cat1 = detectCategory(chinese2);
  assertEquals(cat1, 'preference', '中文偏好应该被识别');

  const chinese3 = '我决定使用 React';
  const cat2 = detectCategory(chinese3);
  assertEquals(cat2, 'decision', '中文决策应该被识别');

  const chinese4 = '<b>粗体</b>文本';
  const result2 = sanitizeInput(chinese4);
  assertEquals(result2, '粗体文本', '中文文本应该正确清理 HTML');
}

// ============================================================================
// 测试结果
// ============================================================================

console.log('\n' + '='.repeat(60));
console.log('📊 测试结果汇总');
console.log('='.repeat(60));
console.log(`✅ 通过: ${testsPassed}`);
console.log(`❌ 失败: ${testsFailed}`);
console.log(`📈 通过率: ${((testsPassed / (testsPassed + testsFailed)) * 100).toFixed(1)}%`);
console.log('='.repeat(60));

if (testsFailed === 0) {
  console.log('\n🎉 所有测试通过！代码修复验证成功。\n');
  process.exit(0);
} else {
  console.log('\n⚠️  部分测试失败，请检查代码。\n');
  process.exit(1);
}
