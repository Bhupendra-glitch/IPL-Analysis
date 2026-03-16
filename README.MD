# 📊 Telco Customer Churn Classification
### Customer Segmentation & Retention Analysis using Machine Learning

---

## 📌 Project Overview

Customer churn is a major challenge in the telecom industry. Customers have many service providers to choose from, and companies must understand why customers leave in order to improve retention.

This project focuses on **predicting customer churn using machine learning techniques**. By analyzing customer demographics, service usage, and billing information, we can identify patterns that indicate whether a customer is likely to leave the company.

The project includes **data analysis, feature engineering, and classification models** to predict churn and provide insights for improving customer retention.

---

## 🎯 Problem Statement

In the telecom industry, customers can choose from many companies for communication and internet services. Customers evaluate service quality continuously, and even a small negative experience may cause them to switch providers.

A **churned customer** is one who cancels or does not renew their subscription.

High churn rates lead to:

- Revenue loss
- Increased customer acquisition cost
- Reduced long-term customer value

Using data analysis and machine learning, companies can **identify potential churn customers and take preventive actions**.

---

## 🎯 Project Aim

- Classify potential churn customers based on numerical and categorical features.
- Build a **binary classification model** to predict churn.
- Analyze factors influencing customer churn.
- Provide insights for improving **customer retention strategies**.

---

## 📂 Dataset Information

The dataset contains information about telecom customers including demographics, services used, and billing information.

### Dataset Attributes

| Feature | Description |
|------|-------------|
| customerID | Unique customer identifier |
| gender | Male or Female |
| SeniorCitizen | Whether the customer is a senior citizen (1 or 0) |
| Partner | Whether the customer has a partner |
| Dependents | Whether the customer has dependents |
| tenure | Number of months customer stayed with the company |
| PhoneService | Whether the customer has phone service |
| MultipleLines | Whether the customer has multiple phone lines |
| InternetService | Type of internet service (DSL, Fiber optic, No) |
| OnlineSecurity | Whether customer has online security |
| OnlineBackup | Whether customer has online backup |
| DeviceProtection | Whether customer has device protection |
| TechSupport | Whether customer has technical support |
| StreamingTV | Whether customer uses streaming TV |
| StreamingMovies | Whether customer uses streaming movies |
| Contract | Contract type (Month-to-month, One year, Two year) |
| PaperlessBilling | Whether billing is paperless |
| PaymentMethod | Customer payment method |
| MonthlyCharges | Monthly service charges |
| TotalCharges | Total amount charged |
| Churn | Whether customer churned (Yes / No) |

---

## 🔍 Exploratory Data Analysis (EDA)

Exploratory Data Analysis was performed to understand customer behavior and identify patterns related to churn.

EDA includes:

- Distribution of customer demographics
- Service usage analysis
- Tenure vs churn relationship
- Monthly charges vs churn
- Contract type analysis
- Correlation between features

Visualization tools used:

- **Matplotlib**
- **Seaborn**
- **Pandas**

---

## ⚙️ Feature Engineering

Data preprocessing steps include:

- Handling missing values
- Converting categorical features into numerical format
- Label Encoding / One-Hot Encoding
- Feature scaling
- Handling imbalanced dataset (if applied)

---

## 🤖 Machine Learning Models Used

The following classification models were applied:

- Logistic Regression
- Decision Tree
- Random Forest
- K-Nearest Neighbors (KNN)
- Support Vector Machine (SVM)
- Gradient Boosting

---

## 📊 Model Evaluation

Models were evaluated using the following metrics:

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- ROC-AUC Score

These metrics help determine the best-performing model for churn prediction.

---

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter Notebook

---

## 📁 Project Structure
Telco-Customer-Churn
│
├── data
│ └── telco_churn.csv
│
├── notebooks
│ └── churn_analysis.ipynb
│
├── models
│ └── churn_model.pkl
│
├── app
│ └── streamlit_app.py
│
└── README.md

## 📈 Key Insights

Some important observations from the analysis:

- Customers with **month-to-month contracts churn more frequently**
- Customers with **fiber optic internet services have higher churn**
- Customers with **short tenure are more likely to churn**
- **Higher monthly charges increase churn probability**
- Customers without **technical support or online security** are more likely to leave
