#!/usr/bin/env node

/**
 * Cursor 指挥家 —— WorkBuddy 与 Cursor AI 的桥梁
 *
 * 用法:
 *   node orchestrator.js tasks/my-task.md          ← 从文件读任务
 *   node orchestrator.js "帮我写一个排序算法"        ← 直接传任务文本
 *   node orchestrator.js --list-models              ← 列出可用模型
 *   node orchestrator.js --status                   ← 查看配置状态
 *
 * 分工原则:
 *   - WorkBuddy: 拆解任务、写任务文件、汇总结果
 *   - Cursor:    执行复杂任务，调用昂贵模型，消耗用户额度
 */

import { Agent } from "@cursor/sdk";
import { readFile, writeFile, mkdir, access, readdir } from "fs/promises";
import { existsSync } from "fs";
import { resolve, join, dirname, basename } from "path";
import { fileURLToPath } from "url";
import { createInterface } from "readline";

const __dirname = dirname(fileURLToPath(import.meta.url));
const TASKS_DIR = resolve(__dirname, process.env.TASKS_DIR || "./tasks");
const RESULTS_DIR = resolve(__dirname, process.env.RESULTS_DIR || "./results");

// ============= 1. 加载环境变量 =============

async function loadEnv() {
  const envPath = resolve(__dirname, ".env");
  if (!existsSync(envPath)) {
    throw new Error(`❌ 未找到 .env 文件，请从 .env.example 复制并填入你的 API Key`);
  }
  const content = await readFile(envPath, "utf-8");
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const val = trimmed.slice(eqIdx + 1).trim();
    if (!process.env[key]) process.env[key] = val;
  }
}

// ============= 2. 检查配置 =============

function checkConfig() {
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey || apiKey === "your_api_key_here") {
    throw new Error(
      "❌ 未设置 CURSOR_API_KEY！\n" +
      "请编辑 cursor-orchestrator/.env 文件，填入你的 API Key。\n" +
      "去 https://cursor.com/dashboard/api 生成。"
    );
  }
  return {
    apiKey,
    model: process.env.CURSOR_MODEL || "composer-2",
    tasksDir: TASKS_DIR,
    resultsDir: RESULTS_DIR,
  };
}

// ============= 3. 获取时间戳 =============

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
}

// ============= 4. 主执行函数 =============

async function runTask(taskDescription, { model, apiKey, label }) {
  const taskId = label || `task-${timestamp()}`;
  const resultFile = join(RESULTS_DIR, `${taskId}.md`);

  console.log(`\n🎯 [指挥家] 分配任务给 Cursor Agent`);
  console.log(`   模型: ${model}`);
  console.log(`   任务ID: ${taskId}`);
  console.log(`   任务摘要: ${taskDescription.slice(0, 100)}...\n`);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

  // 确保结果目录存在
  if (!existsSync(RESULTS_DIR)) {
    await mkdir(RESULTS_DIR, { recursive: true });
  }

  // 创建 Agent（本地模式，消耗用户额度）
  const agent = await Agent.create({
    apiKey,
    model: { id: model },
    local: { cwd: process.cwd() },
  });

  console.log("🚀 Cursor Agent 已启动，开始执行...\n");

  const startTime = Date.now();
  const outputParts = [];
  let toolCalls = 0;

  try {
    const run = await agent.send(taskDescription);

    for await (const event of run.stream()) {
      switch (event.type) {
        case "text":
          process.stdout.write(event.text);
          outputParts.push(event.text);
          break;

        case "tool_call":
          toolCalls++;
          console.log(`\n🔧 [工具调用 #${toolCalls}] ${event.name}`);
          break;

        case "tool_result":
          const preview = JSON.stringify(event.result).slice(0, 200);
          console.log(`   ✅ 结果: ${preview}...`);
          break;

        case "thinking":
          process.stdout.write(`\n💭 [思考] ${event.text.slice(0, 100)}...\n`);
          break;

        case "error":
          console.error(`\n❌ 错误: ${event.error}`);
          outputParts.push(`\n[ERROR] ${event.error}\n`);
          break;

        case "done":
          const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
          console.log(`\n\n✅ 任务完成！耗时 ${elapsed}s，工具调用 ${toolCalls} 次`);
          break;

        default:
          // 忽略其他事件类型
          break;
      }
    }
  } catch (err) {
    console.error(`\n❌ 执行失败: ${err.message}`);
    outputParts.push(`\n[FATAL] ${err.message}\n`);
  }

  // 保存结果
  const fullOutput = outputParts.join("");
  const resultContent = [
    `# Cursor Agent 执行结果`,
    ``,
    `- **任务ID**: ${taskId}`,
    `- **模型**: ${model}`,
    `- **时间**: ${new Date().toISOString()}`,
    `- **耗时**: ${((Date.now() - startTime) / 1000).toFixed(1)}s`,
    `- **工具调用**: ${toolCalls} 次`,
    ``,
    `---`,
    ``,
    `## 原始任务`,
    ``,
    "```",
    taskDescription,
    "```",
    ``,
    `---`,
    ``,
    `## 执行输出`,
    ``,
    fullOutput || "(无输出)",
  ].join("\n");

  await writeFile(resultFile, resultContent, "utf-8");
  console.log(`\n📄 结果已保存: ${resultFile}`);

  return { taskId, resultFile, output: fullOutput, toolCalls };
}

// ============= 5. 列出可用模型 =============

async function listModels({ apiKey }) {
  try {
    const response = await fetch("https://api.cursor.com/v1/models", {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    const data = await response.json();
    if (data.models) {
      console.log("\n📋 可用模型:");
      for (const m of data.models) {
        console.log(`   - ${m.id} (${m.name || "N/A"})`);
      }
    } else {
      console.log("无法获取模型列表，默认可用: composer-2, gpt-5.5, claude-opus-4-5 等");
    }
  } catch {
    console.log("⚠️ 无法连接 Cursor API 获取模型列表，请检查网络和 API Key");
    console.log("已知可用模型: composer-2, gpt-5.5, claude-opus-4-5, gpt-4o 等");
  }
}

// ============= 6. 入口 =============

async function main() {
  const args = process.argv.slice(2);

  await loadEnv();

  if (args.includes("--status")) {
    const config = checkConfig();
    console.log("\n📊 Cursor 指挥家 状态:");
    console.log(`   API Key: ${config.apiKey.slice(0, 8)}...${config.apiKey.slice(-4)}`);
    console.log(`   默认模型: ${config.model}`);
    console.log(`   任务目录: ${config.tasksDir}`);
    console.log(`   结果目录: ${config.resultsDir}`);
    const taskFiles = existsSync(TASKS_DIR) ? await readdir(TASKS_DIR) : [];
    console.log(`   待处理任务: ${taskFiles.filter(f => f.endsWith(".md")).length} 个`);
    process.exit(0);
  }

  if (args.includes("--list-models")) {
    await listModels(checkConfig());
    process.exit(0);
  }

  // 读取任务
  let taskDescription;
  let taskLabel;

  if (args.length > 0) {
    const input = args[0];
    if (existsSync(input)) {
      // 从文件读取
      taskDescription = await readFile(input, "utf-8");
      taskLabel = basename(input, ".md");
    } else {
      // 直接传入的任务文本
      taskDescription = input;
    }
  } else {
    // 交互式输入
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    taskDescription = await new Promise((resolve) => {
      rl.question("请输入任务描述：", (answer) => {
        rl.close();
        resolve(answer);
      });
    });
  }

  if (!taskDescription || !taskDescription.trim()) {
    console.error("❌ 任务描述不能为空");
    process.exit(1);
  }

  const config = checkConfig();

  await runTask(taskDescription.trim(), {
    model: config.model,
    apiKey: config.apiKey,
    label: taskLabel,
  });
}

main().catch((err) => {
  console.error(`\n💥 ${err.message}`);
  process.exit(1);
});
