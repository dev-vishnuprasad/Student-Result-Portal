# 🎓 Student Result Portal

A sleek and interactive web app to fetch and display student results from [resultcrescent.mastersofterp.in](https://resultcrescent.mastersofterp.in) using registration number, date of birth, and CAPTCHA. Built with ❤️ using [Streamlit](https://streamlit.io/).

![Streamlit UI](https://img.shields.io/badge/Built%20With-Streamlit-red?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)

---

## ✨ Features

- 🔐 CAPTCHA-protected login
- 📄 Displays student info, result status, and SGPA
- 📊 Detailed subject-wise result table
- 📈 Summary metrics: total credits, S/A grade count
- 💾 Download raw data in JSON format
- ♻️ Refresh CAPTCHA and Clear Results buttons
- 📱 Fully responsive layout

---

## 📸 Preview

![image](https://github.com/user-attachments/assets/2447d5ec-6201-4f53-bdc0-df832418a1b3)


---

## 🚀 Live Demo

👉 **Try it now**: [student-result.streamlit.app](https://student-result-app-4dsthzbl2aeyjc5bpmvsnb.streamlit.app/)

---

## 🛠️ Tech Stack

- **Frontend / Backend**: [Streamlit](https://streamlit.io)
- **HTTP Requests**: `requests`
- **Image Handling**: `Pillow`
- **Data Handling**: `pandas`

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/student-result-portal.git
cd student-result-portal

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run student_result_app.py
