
---

````markdown
# T.O.N.Y – Text-Oriented Neural Yield 🤖🧠

An interactive AI assistant built with **LLAMA2**, **LangChain**, and **Streamlit**, designed to answer user queries and generate visual responses. T.O.N.Y combines the power of local LLMs and prompt engineering to deliver a seamless and intuitive AI chat experience enhanced with visuals.

## 🚀 Features

- **LLAMA2 via Ollama Integration** – Leverages local LLMs for privacy-friendly, intelligent responses.
- **Dynamic UI with Streamlit** – Clean, responsive interface enabling smooth user interaction.
- **LangChain Orchestration** – Manages prompt flow, memory, and tool usage behind the scenes.
- **Visual Output Support** – Generates diagrams and illustrations based on queries for better understanding.
- **Prompt Engineering** – Optimized prompts ensure coherent and relevant outputs.

## 🛠️ Tech Stack

- **Python**
- **LangChain**
- **LLAMA2 (via Ollama)**
- **Streamlit**
- **Matplotlib / PIL** (for generating visuals)

## 📸 Demo

![screenshot](https://github.com/MugiwaraROBIN/T.O.N.Y-Chatbot/blob/main/assets/demo.png)

## ⚙️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MugiwaraROBIN/T.O.N.Y-Chatbot.git
   cd T.O.N.Y-Chatbot
````

2. **Set Up Python Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # For Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama & Pull LLAMA2**

   ```bash
   ollama run llama2
   ```

5. **Run the App**

   ```bash
   streamlit run main.py
   ```

## 📁 Project Structure

```
T.O.N.Y-Chatbot/
│
├── main.py               # Streamlit app
├── prompts/              # Prompt templates for LangChain
├── utils.py              # Helper functions
├── assets/               # Visuals and icons
└── requirements.txt      # Python dependencies
```

## 💡 Use Cases

* Educational visual explanations (e.g., graphs, charts, code flow)
* AI-powered Q\&A with contextual memory
* Lightweight private assistant using local models

## 🤝 Contributions

Contributions are welcome! Feel free to open issues or submit PRs.

## 📜 License

This project is open-sourced under the [MIT License](LICENSE).

```

---

Let me know if you'd like it tailored for a portfolio/demo audience or if you plan to deploy it publicly (I can add deployment instructions too).
```
