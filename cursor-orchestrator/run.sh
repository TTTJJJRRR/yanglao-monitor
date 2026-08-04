#!/bin/bash
# Cursor 指挥家快捷启动脚本
#
# 用法:
#   ./run.sh "帮我写代码"            ← 直接传任务
#   ./run.sh tasks/my-task.md        ← 从文件读任务
#   ./run.sh --status                ← 查看状态
#   ./run.sh --list-models           ← 列出模型

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NODE_BIN="C:/Users/tttt/.workbuddy/binaries/node/versions/22.22.2/node.exe"

cd "$SCRIPT_DIR"
"$NODE_BIN" orchestrator.js "$@"
