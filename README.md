## 🧠 Architecture Overview

This project implements a serverless email automation system using AWS cloud services. The goal is to send personalized emails based on subscriber preferences stored in DynamoDB, using SES templates and Lambda functions.

### ✅ Key Components:
- **AWS Lambda**: Core logic to fetch data and send templated emails.
- **Amazon SES**: Sends transactional emails using dynamic templates.
- **Amazon DynamoDB**: Stores user preferences and metadata.
- **CloudWatch**: Logs and monitors Lambda executions.
- **IAM Roles**: Secure access across services.

---

## 🗺️ Architecture Diagram

![Architecture Diagram](EmailwithAWSarch.jpeg)

---

## 🔁 Flow Summary
1. Lambda is triggered (manually or via schedule).
2. It fetches subscriber data from **DynamoDB**.
3. (Optionally) pulls real-time data from external APIs.
4. Populates an **SES template** with personalized content.
5. Sends email via **Amazon SES**.
6. Logs activity in **CloudWatch**.

---
