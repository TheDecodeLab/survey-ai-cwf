#!/usr/bin/env bash
set -euo pipefail

activate_eda() {
	if command -v conda >/dev/null 2>&1; then
		eval "$(conda shell.bash hook)"
		conda activate eda || true
	elif command -v mamba >/dev/null 2>&1; then
		eval "$(mamba shell hook --shell bash)"
		mamba activate eda || true
	elif command -v micromamba >/dev/null 2>&1; then
		eval "$(micromamba shell hook --shell bash)"
		micromamba activate eda || true
	fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

activate_eda

python "${SCRIPT_DIR}/make_ai_sankey.py"

echo "Done. See outputs in: ${REPO_ROOT}/outputs/figures" 


