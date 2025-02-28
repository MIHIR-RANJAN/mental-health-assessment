# Mental Health Assessment (OldGeek)

This is a **Streamlit-based mental health assessment** tool that evaluates user responses and provides insights using **BERT-based NLP models**. The application includes:

- A structured **mental health questionnaire**
- **AI-powered analysis** to predict possible conditions
- **Dynamic recommendations** based on user responses
- **Chatbot-generated explanations** for better understanding

---

## 🚀 Features

✅ **Mental Health Screening** using NLP models  
✅ **BERT-based Classification** for condition prediction  
✅ **Interactive Streamlit UI** for easy access  
✅ **Resource Recommendations** for self-care  
<!-- ✅ **Chatbot Integration** for personalized explanations   -->

---

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MIHIR-RANJAN/mental-health-assessment.git
   cd mental-health-assessment/Main
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the BERT model from Google Drive:
   - **[Download Here](https://drive.google.com/drive/folders/1KpMp17fMIxHCWS9jhncwB8ovZ39MFbSL?usp=sharing)**
   - Place the `mental_health_bert_model` folder inside the project directory

4. Run the application:
   ```bash
   streamlit run app.py
   ```

--- 

## 📂 Project Directory Structure
```
mental-health-assessment
│
├── dataset/        # Contains all datasets
├── Main/           # Contains core project files
│   ├── app.py      # Streamlit application
│   ├── main.ipynb  #Main file training code
│   ├── mental_health_bert_model/  # BERT model directory
│   ├── mental_health_bert.pkl    #.pkl file
│   ├── requirements.txt  # Dependencies list
│   ├── requirementsForTraining.txt  # Dependencies list during training
```

---

## 🛠️ Requirements

Ensure you have the following installed:

- **Python 3.7+**
- **Streamlit**
- **Transformers (Hugging Face)**
- **Torch**
- **BeautifulSoup**
- **Requests**
- **Matplotlib**

---

## 📜 Usage

- Start the application and complete the questionnaire.
- The system will analyze responses and classify potential conditions.
- Recommendations and chatbot insights will be displayed.
- Use the provided links and resources for further assistance.

---

## 🤖 Model Details

- Uses **BERT-based NLP model** for classification.
- Responses are **converted into text** and analyzed.
- Generates **personalized explanations** using a chatbot.

---


## 📸 Step-by-Step App Walkthrough

Below are snapshots demonstrating the working of the Mental Health Assessment tool:

### 1️⃣ Home Screen  
The landing page introduces users to the tool and its purpose.  
![Step 1 - Home Screen](images/1.png)

### 2️⃣ User Information Entry  
Users provide basic details before starting the assessment.  
![Step 2 - User Information](images/2.png)

### 3️⃣ Questionnaire Begins  
A structured questionnaire gathers user responses for evaluation.  
![Step 3 - Questionnaire](images/3.png)

### 4️⃣ Answering Questions  
Users respond to mental health-related questions dynamically.  
![Step 4 - Answering Questions](images/4.png)

### 5️⃣ AI Analysis in Progress  
The BERT-based NLP model processes the responses.  
![Step 5 - AI Processing](images/5.png)

### 6️⃣ Primary Assessment Result  
A high-level analysis of the user's mental health status.  
![Step 6 - Primary Result](images/6.png)

### 7️⃣ Detailed Condition Breakdown  
The system provides further classification of possible conditions.  
![Step 7 - Detailed Analysis](images/7.png)

### 8️⃣ Recommendations & Resources  
Based on results, personalized self-care resources are displayed.  
![Step 8 - Recommendations](images/8.png)

### 9️⃣ Chatbot Explanation  
An AI chatbot offers insights and explanations about the results.  
![Step 9 - Chatbot Insights](images/9.png)

---



## 📌 Disclaimer

This tool is for informational purposes **only** and does not replace professional medical advice. If you or someone you know is struggling, please consult a qualified mental health professional.

---

### 🔗 Contact
Name: Mihir Ranjan & Shuvo Mistry  
📞 Phone: +91 9631997254 & +91 8218160597  
📧 Email: [mihir29062001@gmail.com](mailto:mihir29062001@gmail.com) & [shuvomistry.nfsu@gmail.com](mailto:shuvomistry.nfsu@gmail.com)  
🔗 GitHub: [MIHIR-RANJAN](https://github.com/MIHIR-RANJAN)  
🔗 LinkedIn: [Mihir Ranjan](https://www.linkedin.com/in/mihir-ranjan-328503201/)
