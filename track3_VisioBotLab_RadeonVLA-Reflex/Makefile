# Convenience targets for RadeonVLA-Reflex
# Usage: make help

.PHONY: help install-local check smoke record-local record-basic expert-demo remote-check remote-full audit

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

help:
	@echo "RadeonVLA-Reflex — common targets"
	@echo ""
	@echo "  make install-local   # pip install -e . + local requirements (torch separate)"
	@echo "  make check           # env + audit + pytest + ruff"
	@echo "  make smoke           # 1-episode end-to-end smoke"
	@echo "  make record-local    # record a few local episodes (SUITE/EPISODES overridable)"
	@echo "  make record-basic    # alias: basic suite, 10 episodes"
	@echo "  make expert-demo     # scripted demos (MODE=mix|basic|hard)"
	@echo "  make all-local       # full local one-click record pipeline"
	@echo "  make remote-check    # strict AMD gate (on Radeon machine)"
	@echo "  make remote-full     # full AMD train/eval pipeline"
	@echo "  make audit           # submission structure audit only"
	@echo ""
	@echo "Examples:"
	@echo "  EPISODES=20 SUITE=basic make record-local"
	@echo "  MODE=hard make expert-demo"
	@echo "  EPISODES=100 SUITE=full make remote-full"

install-local:
	python -m pip install -r requirements.local.txt
	python -m pip install -e .

check:
	bash scripts/check_local.sh

smoke:
	bash scripts/run_pipeline_smoke.sh

record-local:
	bash scripts/run_record.sh

record-basic:
	EPISODES=$${EPISODES:-10} SUITE=basic bash scripts/run_record.sh

expert-demo:
	bash scripts/run_expert_demo.sh

all-local:
	bash scripts/run_all_local.sh

remote-check:
	bash scripts/check_remote_amd.sh

remote-full:
	bash scripts/run_full_remote.sh

audit:
	python -m radeonvla.submission_audit
