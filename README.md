# Personalized Email Delivery Platform with AWS

This project implements a serverless solution to automate personalized email delivery using AWS cloud services. It integrates AWS Lambda, SES, DynamoDB, CloudWatch, and IAM to send templated newsletter emails tailored to individual user preferences.

## Features

- Sends dynamic, personalized emails with AWS SES
- Pulls real-time data from external sources for content enrichment
- Subscriber preferences stored in DynamoDB
- Fully serverless and scalable using AWS Lambda
- Monitored and secured via CloudWatch and IAM

## Services Used

- **AWS Lambda**: Executes the core logic for email personalization and delivery  
- **Amazon SES**: Sends emails using predefined templates with dynamic placeholders  
- **Amazon DynamoDB**: Stores subscriber preferences and user data  
- **Amazon CloudWatch**: Monitors performance and logs Lambda executions  
- **AWS IAM**: Manages fine-grained access control for services  

## Architecture Overview

This project follows a serverless architecture to ensure scalability, cost-efficiency, and minimal operational overhead. The system retrieves user preferences from DynamoDB, fetches real-time content from an external API (NewsAPI), then injects this data into an SES template for personalized email delivery.

## Architecture Diagram

![Architecture Diagram](EmailwithAWSarch.jpeg)

## Workflow Summary


1. **Trigger**: Admin or user triggers the Lambda function manually or on a schedule.  
2. **Data Fetching**:
   - Subscriber preferences are retrieved from **DynamoDB**.
   - External content (e.g., news or sports updates) is fetched via a **News API**.  
3. **Email Preparation**:
   - Dynamic content is injected into **SES** templates.  
4. **Delivery**:
   - Email is sent to the recipient via **Amazon SES**.
5. **Monitoring & Security**:
   - Execution logs and errors are monitored via **CloudWatch**.
   - **IAM** manages roles and permissions between services. 
