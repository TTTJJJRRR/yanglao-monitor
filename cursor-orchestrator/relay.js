#!/usr/bin/env node
/**
 * 指挥家·接力模式 — WorkBuddy → Cursor 任务委托工具
 *
 * 用法:
 *   node relay.js 任务文件.md    ← 读取任务，显示给用户在 Cursor 里粘贴
 *   node relay.js --check         ← 检查是否有新产生的结果文件
 *   node relay.js --watch         ← 持续监控 results/ 目录变化
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = __dirname;
const TASKS_DIR = path.join(ROOT, 'tasks');
const RESULTS_DIR = path.join(ROOT, 'results');

// ========== 颜色输出 ==========
const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  red: '\x1b[31m',
};

// ========== 核心功能 ==========

/**
 * 显示任务 — 格式化输出供用户在 Cursor 中粘贴
 */
function showTask(taskFile) {
  const taskPath = path.resolve(taskFile);
  if (!fs.existsSync(taskPath)) {
    console.log(`${c.red}✗ 任务文件不存在: ${taskPath}${c.reset}`);
    process.exit(1);
  }

  const content = fs.readFileSync(taskPath, 'utf-8');
  const taskName = path.basename(taskFile, path.extname(taskFile));

  console.log('');
  console.log(`${c.bold}${c.cyan}╔══════════════════════════════════════════════════╗${c.reset}`);
  console.log(`${c.bold}${c.cyan}║         🎻 指挥家任务·接力模式                   ║${c.reset}`);
  console.log(`${c.bold}${c.cyan}╚══════════════════════════════════════════════════╝${c.reset}`);
  console.log('');
  console.log(`${c.bold}📋 任务名:${c.reset} ${taskName}`);
  console.log(`${c.dim}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${c.reset}`);
  console.log('');
  console.log(`${c.bold}📝 请将以下内容复制到 Cursor 聊天框 (Ctrl+L):${c.reset}`);
  console.log('');
  console.log(`${c.yellow}${'═'.repeat(56)}${c.reset}`);
  console.log(content);
  console.log(`${c.yellow}${'═'.repeat(56)}${c.reset}`);
  console.log('');
  console.log(`${c.bold}${c.green}📌 操作步骤:${c.reset}`);
  console.log(`  1. ${c.cyan}选中上面黄色区域的内容${c.reset}`);
  console.log(`  2. ${c.cyan}复制 (Ctrl+C)${c.reset}`);
  console.log(`  3. ${c.cyan}切换到 Cursor 编辑器${c.reset}`);
  console.log(`  4. ${c.cyan}打开 AI 聊天 (Ctrl+I 或 Ctrl+L)${c.reset}`);
  console.log(`  5. ${c.cyan}粘贴并发送${c.reset}`);
  console.log(`  6. ${c.cyan}等 Cursor 完成后，回来对我喊 "完成"${c.reset}`);
  console.log('');
}

/**
 * 检查 results/ 目录的结果文件
 */
function checkResults() {
  if (!fs.existsSync(RESULTS_DIR)) {
    console.log(`${c.yellow}⚠ results/ 目录不存在${c.reset}`);
    return [];
  }

  // 排除 .gitkeep
  const files = fs.readdirSync(RESULTS_DIR)
    .filter(f => !f.startsWith('.') && f !== '.gitkeep')
    .map(f => ({
      name: f,
      path: path.join(RESULTS_DIR, f),
      mtime: fs.statSync(path.join(RESULTS_DIR, f)).mtime,
      size: fs.statSync(path.join(RESULTS_DIR, f)).size,
    }))
    .sort((a, b) => b.mtime - a.mtime);

  if (files.length === 0) {
    console.log(`${c.dim}(暂无结果文件)${c.reset}`);
  } else {
    console.log(`\n${c.bold}📂 results/ 目录现有文件:${c.reset}`);
    for (const f of files) {
      const sizeKB = (f.size / 1024).toFixed(1);
      console.log(`   ${c.green}${f.name}${c.reset} ${c.dim}(${sizeKB} KB, ${f.mtime.toLocaleTimeString('zh-CN')})${c.reset}`);
    }
  }

  return files;
}

/**
 * 监控 results/ 目录变化
 */
function watchResults() {
  if (!fs.existsSync(RESULTS_DIR)) {
    fs.mkdirSync(RESULTS_DIR, { recursive: true });
  }

  const knownFiles = new Set(fs.readdirSync(RESULTS_DIR));

  console.log(`\n${c.bold}${c.magenta}👁 开始监控 results/ 目录...${c.reset}`);
  console.log(`${c.dim}(按 Ctrl+C 停止)${c.reset}\n`);

  fs.watch(RESULTS_DIR, (eventType, filename) => {
    if (filename.startsWith('.') || filename === '.gitkeep') return;

    const filePath = path.join(RESULTS_DIR, filename);
    const exists = fs.existsSync(filePath);

    if (eventType === 'rename' && exists && !knownFiles.has(filename)) {
      knownFiles.add(filename);
      const size = fs.statSync(filePath).size;
      console.log(`\n${c.bold}${c.green}🆕 新结果! ${filename}${c.reset} ${c.dim}(${(size/1024).toFixed(1)} KB)${c.reset}`);
      console.log(`   ${c.cyan}路径:${c.reset} ${filePath}`);
    }

    if (eventType === 'change' && exists) {
      const size = fs.statSync(filePath).size;
      console.log(`   ${c.yellow}✏ ${filename} 已更新${c.reset} ${c.dim}(${(size/1024).toFixed(1)} KB)${c.reset}`);
    }
  });

  // 保持进程运行
  setInterval(() => {}, 60000);
}

/**
 * 列出可用任务
 */
function listTasks() {
  if (!fs.existsSync(TASKS_DIR)) {
    console.log(`${c.red}✗ tasks/ 目录不存在${c.reset}`);
    return [];
  }

  const tasks = fs.readdirSync(TASKS_DIR)
    .filter(f => f.endsWith('.md') && !f.startsWith('.'))
    .map(f => ({
      name: f,
      path: path.join(TASKS_DIR, f),
    }));

  if (tasks.length === 0) {
    console.log(`${c.dim}(暂无任务)${c.reset}`);
    return [];
  }

  console.log(`\n${c.bold}📋 tasks/ 可用任务:${c.reset}`);
  for (const t of tasks) {
    // 读第一行作为标题
    const lines = fs.readFileSync(t.path, 'utf-8').split('\n');
    const title = lines[0].replace(/^#+\s*/, '') || t.name;
    console.log(`   ${c.cyan}${t.name}${c.reset} → ${title}`);
  }

  return tasks;
}

// ========== 主入口 ==========

const args = process.argv.slice(2);

if (args.length === 0) {
  console.log(`
${c.bold}${c.cyan}🎻 Cursor 指挥家·接力模式${c.reset}

${c.bold}用法:${c.reset}
  node relay.js <任务文件.md>    显示任务，复制到 Cursor 执行
  node relay.js --list           列出可用任务
  node relay.js --check          检查结果文件
  node relay.js --watch          监控结果目录变化
  node relay.js --help           显示此帮助

${c.bold}典型工作流:${c.reset}
  1. node relay.js tasks/test-001.md     ← 读取任务
  2. 复制到 Cursor，让 AI 执行               ← 手动一步
  3. node relay.js --check              ← 检查结果
  4. 我 (WorkBuddy) 读取结果交付给你      ← 自动化
`);
  process.exit(0);
}

const cmd = args[0];

if (cmd === '--help' || cmd === '-h') {
  console.log('使用 node relay.js (无参数) 查看帮助');
  process.exit(0);
}

if (cmd === '--list') {
  listTasks();
  checkResults();
  process.exit(0);
}

if (cmd === '--check') {
  checkResults();
  process.exit(0);
}

if (cmd === '--watch') {
  checkResults();
  watchResults();
}

// 默认：显示任务
showTask(cmd);
checkResults();
