# Platform Agent

## 📋 项目状态 (2024年最新)

**🎯 项目已从 "Fast Agent" 重命名为 "Platform Agent"**，专注于平台工程和DevOps基础设施管理。

**✅ 当前功能状态**:
- ✅ **多Agent协作系统**：基于CrewAI框架的智能助手
- ✅ **工具集成**：支持K8s管理和网络工具
- ✅ **智能启动脚本**：自动环境检测和依赖管理
- ✅ **工具缓存系统**：MCP工具自动发现和缓存
- ✅ **完整验证系统**：环境检查和功能验证

---

An intelligent multi-agent platform for DevOps and infrastructure management, powered by `crewAI` and modern LLMs.

This project aims to create a "Platform Agent" that enables platform engineering teams to interact with complex infrastructure and operational tasks using natural language. It dramatically simplifies platform operations and improves team productivity through AI-driven automation.

## 📚 Documentation

For a detailed understanding of the project's vision, features, and MVP plan, please refer to our documentation:

- **[Product Requirements Document (PRD.md)](./doc/PRD.md)**: Defines the "what" and "why" of this project.
- **[Technical Architecture (ARCHITECTURE.md)](./doc/ARCHITECTURE.md)**: Outlines the technical design and "how" we will build it.

## 🚀 Getting Started (MVP)

_Instructions to be refined as development progresses._

1.  **Setup Environment**:
    ```bash
    # Create a virtual environment using uv
    uv venv

    # Activate the environment
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    # Install required packages
    uv pip install -r requirements.txt
    ```

3.  **Configure**:
    - Copy `.env.example` to `.env`.
    - Fill in your `OPENROUTER_API_KEY`.

4.  **Run the CLI**:
    ```bash
    python src/main.py
    ``` 