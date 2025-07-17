# 🧠 Therapy Sentiment Analyzer – MindScribe

Welcome to **MindScribe**, an intelligent NLP-powered platform designed to support therapists in understanding and tracking patient emotions. This application performs sentiment and emotion analysis on therapy session text inputs, helping therapists visualize emotional trends and generate meaningful insights.

## 🔗 Live App

👉 [Launch the App on Streamlit](https://therapy-sentiment-analyzer-h3mwbadt9dappmiuhktvars.streamlit.app/)

---

## 📌 Features

- ✅ **Therapist Login System**
- 🧠 **Emotion & Sentiment Analysis** of patient text inputs
- 📈 **Dynamic Dashboard** for patient insights
- 🧾 **Exportable Reports** of session summaries and emotional patterns
- 💬 **Patient-wise Session Tracking**
- 📊 **Visualizations** for sentiment trends
- 🛠️ **Custom CSS Styling**
- 🔐 **Session Authentication & State Management**

---

## 🏗️ Tech Stack

| Component          | Technology              |
|--------------------|--------------------------|
| Web Framework      | [Streamlit](https://streamlit.io) |
| Language           | Python 3.x               |
| NLP Tools          | TextBlob, NLTK, Scikit-learn |
| Database           | SQLite                   |
| Styling            | Custom CSS               |
| Deployment         | Streamlit Cloud          |

---

## 🚀 How to Run Locally

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sruthykbenni/Therapy-Sentiment-Analyzer.git
   cd Therapy-Sentiment-Analyzer

2. **Create a Virtual Environment** (optional)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

4. **Run the App**
   ```bash
   streamlit run app.py

---

## 📁 Project Structure
```graphql
Therapy-Sentiment-Analyzer/
│
├── app.py                       # Main application entry point
├── requirements.txt             # List of dependencies
├── database.db                  # SQLite database (auto-generated)
│
├── assets/                      # CSS and static assets
│   └── style.css
│
├── components/                  # UI rendering modules
│   ├── dashboard.py
│   ├── patient_view.py
│   └── exports.py
│
├── utils/                       # Helper functions
│   ├── auth.py
│   └── database.py
│
└── README.md                    # Project documentation
```
---

## Sample Use Case
A therapist logs in to MindScribe, selects a patient, and enters text from a recent session. The system instantly performs sentiment and emotion analysis, visualizes the results, and stores the session data. Over time, the therapist can track emotional patterns and export session summaries for clinical reporting.

## 🤝 Contributing
Pull requests are welcome! For significant changes, please open an issue first to discuss what you'd like to change.

## 📜 License
This project is licensed under the MIT License.
