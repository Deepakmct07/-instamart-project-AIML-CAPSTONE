Instamart Support Co-pilot

An AI-powered customer support assistant designed to answer policy-related questions, evaluate refund eligibility, and help route customer issues using retrieval-augmented generation (RAG), rule-based decision logic, and input guardrails.

Live Demo

- Frontend: https://instamart-capstone-frontend.onrender.com
- Backend API Documentation: https://instamart-capstone-project-aiml.onrender.com/docs
- GitHub Repository: https://github.com/Deepakmct07/-instamart-project-AIML-CAPSTONE

Project Overview

The Instamart Support Co-pilot combines policy retrieval and structured support workflows to provide consistent responses to common customer-service questions.

Key Features

- Policy Question Answering: Retrieves relevant information from policy documents using a RAG pipeline.
- Refund Eligibility: Evaluates refund requests against order information and configured business rules.
- Escalation Handling: Identifies cases that require human support or security-team attention.
- Input Guardrails: Tests handling of empty messages, long inputs, and potentially sensitive personal information.
- Evaluation: Includes scripts to evaluate policy-answering and refund-agent scenarios.

Technology Stack

- Python
- Retrieval-Augmented Generation (RAG)
- TF-IDF-based document retrieval
- FastAPI backend
- React frontend
- Automated testing and evaluation with pytest and pandas

Repository Structure

Folder| Purpose
"part_a/"| Synthetic data generation
"part_b/"| Data and business-rule preparation
"part_c/"| Input guardrails and validation tests
"part_d/"| RAG policy assistant, refund agent, backend, and frontend

Run the Evaluations Locally

Run these commands from the project root after installing the required dependencies.

python -m pip install -r part_d/backend/requirements.txt pytest pandas
python -m pytest part_c/test_guardrails.py -q
python part_d/evaluate.py

The evaluation script reports results for policy questions and refund-agent scenarios. Results may also be saved under the project's output directory.

Test Results

In the current local run, the evaluation script reported:

- RAG policy evaluation: 100%
- Refund-agent evaluation: 100%
- Guardrail tests: Passed

These results apply to the included test cases and do not guarantee correctness for every possible input.

Data and Security

The project uses synthetic course-project data. Do not commit API keys, passwords, access tokens, customer information, or other secrets. Keep local environment variables in an untracked ".env" file where required.

Limitations

Responses and decisions depend on the available policy documents, configured rules, and evaluation scenarios. Real-world deployment would require broader testing, monitoring, security review, and human oversight for sensitive or high-impact decisions.

Author

Developed as an AI/ML capstone project.