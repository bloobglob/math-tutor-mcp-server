# Math Tutor Agent Tutorial

# 🧮 Dify Math Tutor Agent Setup with Custom LLM

This guide walks you through setting up [Dify](https://github.com/langgenius/dify), integrating a custom local LLM model, and creating a Math Tutor Agent using the Dify platform for intelligent mathematical tutoring and problem-solving assistance.

---

## 🛠️ Prerequisites

Ensure the following are available:

- Dify (at least v1.6.0) installed and running via Docker. **Do not run on `localhost`**
- A local or remote LLM endpoint (e.g., hosted via FastAPI)
- Access to the LLM model `llm_en_v_1_3_1` or `llm_zh_v_1_3_1` (or your preferred OpenAI-compatible model)
- Python environment with required dependencies

---

## 🚀 Step-by-Step Setup

### Step 1: Add LLM Model to Dify

1. Click the **user icon** in the top-right corner of the interface.
2. Select **Settings** from the dropdown menu.
3. Navigate to the **Model Provider** tab.
4. Install the **OpenAI-API-compatible** model if not already installed.
5. In the **OpenAI-API-compatible** model, click **Add Model** and configure:
   - **Model Type**: `LLM`
   - **Model Name**: `llm_en_v_1_3_1` or `llm_zh_v_1_3_1`
   - **Model display name**: `llm_en_v_1_3_1` or `llm_zh_v_1_3_1`
   - **API endpoint URL**: `http://<your-server-ip>:5001/openai/v1`
   - **Model context size**: `4096`
   - **API Key**: Leave blank if not needed
6. Mark it as **default** if desired.

---

### Step 2: Set up the MCP Server

1. Start the MCP server by navigating to this project directory and running:
   ```bash
   python server.py
   ```
2. At the top of the **Dify interface**, navigate to the **Tool** tab.
3. Click the **MCP** tab.
4. Click **Add MCP Server (HTTP)** and configure:
   - **Server URL**: `http://host.docker.internal:8001/mcp/`
   - **Name & Icon**: `Math Tutor MCP Server`
   - **Server Identifier**: `math-tutor-mcp-server`

---

### Step 3: Create the MCP Agent in Dify

1. On the main interface in Dify, click **Import DSL file** in the **Create App** block.
2. Select `Math Tutor Agent.yml` in this directory.
3. Configure the agent workflow:
   - Connect the **LLM Node** to use your configured model
   - If using `llm_zh_v_1_3_1`, update each LLM block to use this model
   - Define system prompts for mathematical tutoring and problem-solving

---

## ✅ Final Notes

- Ensure the local LLM server is accessible to Dify.
- The MCP server must be running before using the Math Tutor Agent.
- Debug logs can help confirm each stage is functioning as expected.
- Test with simple mathematical problems before attempting complex tutoring scenarios.
- The agent supports both English (`llm_en_v_1_3_1`) and Chinese (`llm_zh_v_1_3_1`) models.

---

## 📎 Resources

- [Dify GitHub](https://github.com/langgenius/dify)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)