# DVSA Vulnerability Discovery and Remediation

## Project Overview
This project is part of the **ICS-344: Information Security** course at KFUPM.  
The goal is to gain hands-on experience in **discovering, exploiting, analyzing, and remediating security vulnerabilities** in a real-world cloud-based serverless application.

We use the **OWASP DVSA (Damn Vulnerable Serverless Application)**, which is intentionally designed with security flaws to help students understand modern cloud security risks and secure design practices.

The project focuses on:
- Identifying vulnerabilities in a serverless AWS environment  
- Exploiting them in a controlled and ethical way  
- Understanding their root causes and impact  
- Applying proper fixes based on secure design principles  
- Verifying that the fixes resolve the issues without breaking functionality  

---

## Objectives
- Analyze the architecture of a serverless application (API Gateway, Lambda, DynamoDB, S3, IAM)
- Demonstrate **10 official vulnerabilities**
- Provide:
  - Reproduction steps  
  - Evidence (screenshots, logs, responses)  
  - Root cause analysis  
  - Fix implementation  
  - Post-fix verification  
- Apply security principles such as:
  - Input validation  
  - Least privilege  
  - Secure authentication  
  - Defense in depth  

---

## Technologies & Environment
- **Cloud Platform:** AWS (non-production environment)
- **Architecture:** Serverless (Event-driven)

### Core Services
- Amazon API Gateway  
- AWS Lambda  
- Amazon DynamoDB  
- Amazon S3  
- AWS IAM  
- Amazon Cognito  
- CloudWatch Logs  

### Tools Used
- Postman / curl  
- AWS Console  
- Browser DevTools  

---

## Covered Vulnerabilities
1. Event Injection  
2. Broken Authentication  
3. Sensitive Data Exposure  
4. Insecure Cloud Configuration  
5. Broken Access Control  
6. Denial of Service (DoS)  
7. Over-Privileged Functions  
8. Logic Vulnerabilities  
9. Vulnerable Dependencies  
10. Unhandled Exceptions  

---

## How to Use This Repository
1. Follow the setup guide in `/setup/` to deploy DVSA  
2. Navigate to `/vulnerabilities/`  
3. Open any lesson folder  
4. Follow:
   - Exploit steps  
   - Evidence  
   - Fix instructions  
   - Verification  

---

## References & Resources
- OWASP DVSA GitHub:  
  https://github.com/OWASP/DVSA  

- OWASP DVSA Project Page:  
  https://owasp.org/www-project-dvsa/  

- AWS Documentation:  
  https://docs.aws.amazon.com/  

---

## Team Members
- Hayat Alghamdi  
- Lena Alqaissom  
- Maiss Khalaf  

---

## Project Goal Summary
For each vulnerability, this repository demonstrates:
1. The vulnerability and its impact  
2. How it can be exploited  
3. Proof of the issue  
4. The applied fix  
5. Verification that the issue is resolved  
