# ResolveAI — AI Customer Support Resolution Agent

ResolveAI is a production-style AI customer support resolution system designed to automatically understand customer issues, validate order and payment information, execute controlled backend actions, and escalate unresolved cases to human support when necessary.

The system combines **FastAPI, LangGraph, LangChain, MCP, PostgreSQL, SQLAlchemy, Alembic, and LLM-based reasoning** to create a structured customer-support agent rather than a simple chatbot.

The core design principle is:

> **LLM handles language and reasoning. Deterministic backend services handle business truth and database operations.**

This separation makes the system safer, more predictable, testable, and closer to how production AI systems are designed.

---

## 📑 Table of Contents

- [Architecture](#-architecture)
- [Features](#-features)
- [Core Principle](#-core-principle)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [System Workflow](#-system-workflow)
- [AI Issue Classification](#-ai-issue-classification)
- [Supported Customer Issues](#-supported-customer-issues)
- [Duplicate Payment Resolution](#-duplicate-payment-resolution)
- [Failed Payment Resolution](#-failed-payment-resolution)
- [Refund Workflow](#-refund-workflow)
- [Missing Order](#-missing-order)
- [Wrong Order Status](#-wrong-order-status)
- [Order Cancellation](#-order-cancellation)
- [Human Escalation](#-human-escalation)
- [Authorization](#-authorization)
- [Layered Backend Architecture](#-layered-backend-architecture)
- [LLM Gateway](#-llm-gateway)
- [Model Routing & Fallback](#-model-routing--fallback)
- [LangGraph Agent Workflow](#-langgraph-agent-workflow)
- [MCP Integration](#-mcp-integration)
- [Database](#-database)
- [Order & Payment Data Flow](#-order--payment-data-flow)
- [Testing](#-testing)
- [Docker](#-docker)
- [Database Migrations](#-database-migrations)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Running PostgreSQL](#-running-postgresql)
- [Running Migrations](#-running-migrations)
- [Running the Application](#-running-the-application)
- [API Example](#-api-example)
- [Escalation API](#-escalation-api)
- [Design Decisions](#-design-decisions)
- [Security Considerations](#-security-considerations)
- [Future Improvements](#-future-improvements)
- [Project Goals](#-project-goals)
- [Key Engineering Highlights](#-key-engineering-highlights)
- [What This Project Demonstrates](#-what-this-project-demonstrates)
- [Author](#-author)
- [License](#-license)

---

# 🏗️ Architecture

ResolveAI follows a layered AI-agent architecture where the LLM is responsible for understanding and reasoning, while deterministic backend services remain responsible for business operations and database state.

```text
                         ┌──────────────────────┐
                         │      Customer        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │      REST API        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  AI Resolution Agent │
                         │      LangGraph       │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐             ┌──────────────────┐
          │ Issue Classifier │             │ Decision /       │
          │       LLM        │             │ Routing Logic    │
          └────────┬─────────┘             └────────┬─────────┘
                   │                                │
                   └───────────────┬────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │         MCP          │
                         │   Controlled Tools   │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
     │ Order Tools  │      │Payment Tools │      │Support Tools │
     └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   Service Layer      │
                       │ Deterministic Logic  │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   Repository Layer   │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │      SQLAlchemy      │
                       │         ORM          │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │     PostgreSQL       │
                       └──────────────────────┘
```

---

# 🚀 Features

- AI-powered customer issue classification
- Stateful agent workflows using LangGraph
- LLM integration using LangChain
- Structured LLM outputs
- Model routing and fallback handling
- MCP-based controlled tool access
- Order validation
- Payment validation
- Duplicate payment detection
- Failed payment resolution
- Refund request handling
- Missing order handling
- Wrong order status handling
- Order cancellation
- Human-in-the-loop escalation
- Customer and order authorization
- PostgreSQL database
- SQLAlchemy ORM
- Alembic database migrations
- Repository / Service architecture
- FastAPI REST API
- Pydantic validation
- JWT authentication
- Automated testing with Pytest
- Docker Compose PostgreSQL environment
- Environment-based configuration
- Deterministic business logic
- Controlled AI-to-backend interaction

---

# 🧠 Core Principle

ResolveAI follows a strict separation between **AI reasoning** and **business logic**.

The LLM is responsible for:

- Understanding natural-language customer requests
- Classifying customer issues
- Selecting the appropriate workflow
- Reasoning about which controlled capability should be used
- Generating the customer-facing response

The LLM does **not** directly modify the database.

Instead, the system follows:

```text
Customer Message
       ↓
      LLM
       ↓
Issue Classification
       ↓
LangGraph Workflow
       ↓
MCP Tool
       ↓
Backend Service
       ↓
Repository
       ↓
PostgreSQL
```

This ensures that transactional operations such as refunds, cancellations, payment validation, and order modifications remain controlled by deterministic backend logic.

---

# 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| AI Framework | LangChain |
| Agent Orchestration | LangGraph |
| Tool Protocol | MCP |
| LLM Providers | Groq, Gemini, xAI, Qwen |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Authentication | JWT |
| Database Migration | Alembic |
| Testing | Pytest |
| Containerization | Docker / Docker Compose |
| Package Manager | uv |
| ASGI Server | Uvicorn |

---

# 📁 Project Structure

```text
ResolveAI/
│
├── app/
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   └── routing.py
│   │
│   ├── ai/
│   │   ├── classifier.py
│   │   ├── gateway.py
│   │   ├── router.py
│   │   └── providers/
│   │
│   ├── mcp/
│   │   ├── server.py
│   │   └── tools/
│   │
│   ├── services/
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── refund_service.py
│   │   └── escalation_service.py
│   │
│   ├── repositories/
│   │   ├── customer_repository.py
│   │   ├── order_repository.py
│   │   ├── payment_repository.py
│   │   └── support_repository.py
│   │
│   ├── models/
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── support_case.py
│   │   └── escalation.py
│   │
│   ├── schemas/
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── support.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   └── main.py
│
├── alembic/
│
├── tests/
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_ai.py
│   ├── test_orders.py
│   ├── test_payments.py
│   ├── test_refunds.py
│   ├── test_escalation.py
│   └── test_integration.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

---

# 🔄 System Workflow

The complete customer-support workflow is:

```text
Customer Request
       ↓
FastAPI Endpoint
       ↓
Authentication / Validation
       ↓
AI Issue Classification
       ↓
Structured Classification
       ↓
LangGraph Routing
       ↓
Relevant Workflow
       ↓
MCP Tool
       ↓
Backend Service
       ↓
Repository
       ↓
PostgreSQL
       ↓
Business Decision
       ↓
┌──────────────────────────────┐
│                              │
▼                              ▼
Auto Resolution           Human Escalation
│                              │
▼                              ▼
Resolution Response       Support Case
```

---

# 🤖 AI Issue Classification

ResolveAI uses an LLM to understand the customer's natural-language request and classify it into a supported issue type.

The classifier produces structured output instead of relying on unstructured text parsing.

Example:

```json
{
  "issue_type": "duplicate_payment",
  "confidence": 0.94,
  "order_id": "ORD-1023"
}
```

The structured result is then passed into the LangGraph workflow.

---

# 📋 Supported Customer Issues

ResolveAI currently supports the following customer-support scenarios:

| Issue | Description |
|---|---|
| `payment_failed` | Customer reports that a payment failed |
| `refund_request` | Customer requests a refund |
| `duplicate_payment` | Customer reports being charged multiple times |
| `missing_order` | Customer cannot locate or receive an expected order |
| `wrong_order_status` | Customer reports an incorrect order status |
| `cancel_order` | Customer requests order cancellation |

---

# 💳 Duplicate Payment Resolution

Duplicate payment handling follows a deterministic process:

```text
Customer reports duplicate payment
            ↓
AI classifies issue
            ↓
LangGraph routes workflow
            ↓
MCP payment tool
            ↓
Fetch payment history
            ↓
Verify duplicate transaction
            ↓
Business logic
            ↓
Refund / escalation decision
```

The LLM does not determine whether two transactions are actually duplicates.

The backend verifies the payment records before taking any action.

---

# 💰 Failed Payment Resolution

For failed payments, the system follows:

```text
Customer reports payment failure
            ↓
Issue classification
            ↓
Payment status lookup
            ↓
Backend validation
            ↓
Determine payment state
            ↓
Generate resolution
            ↓
Escalate if required
```

The AI explains the situation while the backend remains responsible for payment truth.

---

# 💸 Refund Workflow

Refund requests follow a controlled workflow:

```text
Refund Request
      ↓
Validate Customer
      ↓
Validate Order Ownership
      ↓
Check Payment Status
      ↓
Check Refund Eligibility
      ↓
Create Refund
      ↓
Update Support Case
      ↓
Return Result
```

Refund creation is performed by deterministic backend logic rather than directly by the LLM.

---

# 📦 Missing Order

When a customer reports a missing order:

```text
Customer Message
       ↓
Issue Classification
       ↓
Order Lookup
       ↓
Authorization Check
       ↓
Order Status Verification
       ↓
Resolution / Escalation
```

The system verifies that the requested order belongs to the authenticated customer before exposing customer-specific order information.

---

# 📊 Wrong Order Status

The system can investigate situations where a customer reports that the displayed order status is incorrect.

The workflow validates:

- Customer ownership
- Order existence
- Current order state
- Relevant backend information

The result is then either resolved automatically or escalated to human support.

---

# ❌ Order Cancellation

Cancellation requests are processed through deterministic business rules:

```text
Cancellation Request
        ↓
Validate Customer
        ↓
Validate Order
        ↓
Check Order State
        ↓
Check Cancellation Eligibility
        ↓
Cancel Order
        ↓
Return Result
```

The AI does not directly modify the order database record.

---

# 🧑‍💼 Human Escalation

Not every customer issue should be automatically resolved.

When the system cannot safely resolve an issue, it creates or updates a support case and escalates the case to a human agent.

The escalation lifecycle is:

```text
open
  ↓
in_progress
  ↓
resolved
  ↓
closed
```

This creates a human-in-the-loop workflow instead of forcing the AI to resolve every customer request.

---

# 🔐 Authorization

ResolveAI validates customer ownership before allowing access to customer-specific resources.

Example:

```text
Authenticated Customer
        ↓
Request Order
        ↓
Check Order Ownership
        ↓
┌─────────────────────┐
│                     │
▼                     ▼
Authorized         Unauthorized
│                     │
▼                     ▼
Continue            Reject
```

This prevents one customer from accessing another customer's orders or payment information.

---

# 🧱 Layered Backend Architecture

The backend follows a layered architecture:

```text
Route
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

## Route Layer

Responsible for:

- HTTP endpoints
- Request handling
- Authentication dependencies
- Response formatting

## Service Layer

Responsible for:

- Business rules
- Transaction workflows
- Validation
- Deterministic decisions

## Repository Layer

Responsible for:

- Database queries
- CRUD operations
- Data persistence

## Database Layer

PostgreSQL stores the application's persistent transactional data.

---

# 🧠 LLM Gateway

ResolveAI uses an abstraction layer between the application and LLM providers.

```text
                    ┌───────────────┐
                    │  Application  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  LLM Gateway  │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ Model Router  │
                    └───────┬───────┘
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
          Groq           Gemini             xAI
            │
            ▼
          Qwen
```

This abstraction prevents the rest of the application from becoming tightly coupled to a single model provider.

---

# 🔀 Model Routing & Fallback

The system supports model routing and fallback handling.

Simplified flow:

```text
Application Request
       ↓
Model Router
       ↓
Primary Model
       ↓
Success?
 ┌─────┴─────┐
 │           │
Yes          No
 │           │
 ▼           ▼
Response   Fallback
             ↓
          Next Model
```

This allows the application to use an alternative model when the primary provider fails or becomes unavailable.

---

# 🔗 LangGraph Agent Workflow

LangGraph is used to represent the customer-support agent as a stateful workflow.

Conceptually:

```text
START
  ↓
Classify Issue
  ↓
Validate Context
  ↓
Route Issue
  ↓
Execute Tool
  ↓
Validate Result
  ↓
Resolve / Escalate
  ↓
END
```

Conditional routing allows different customer issues to follow different workflows.

```text
                 ┌── payment_failed
                 │
                 ├── refund_request
Classify ────────┼── duplicate_payment
                 │
                 ├── missing_order
                 │
                 ├── wrong_order_status
                 │
                 └── cancel_order
```

---

# 🔌 MCP Integration

Model Context Protocol (MCP) provides a controlled interface between the AI agent and backend capabilities.

The system exposes controlled tools such as:

```text
get_order
get_payment_history
check_payment_status
create_refund
create_support_case
create_escalation
```

The agent does not receive unrestricted database access.

Instead:

```text
AI Agent
   ↓
MCP Tool
   ↓
Validated Backend Operation
   ↓
Service Layer
   ↓
Repository
   ↓
Database
```

This keeps AI actions constrained to explicitly defined capabilities.

---

# 🗄️ Database

ResolveAI uses PostgreSQL as the primary relational database.

The database layer is implemented using:

- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations
- Repository pattern

Core entities include:

```text
Customer
Order
Payment
Support Case
Escalation
```

---

# 🔄 Order & Payment Data Flow

ResolveAI separates customer-support reasoning from transactional backend operations.

Order and payment information is retrieved through controlled services and repositories.

This ensures that AI-generated reasoning is backed by actual application data rather than allowing the model to invent transactional information.

---

# 🧪 Testing

ResolveAI includes an automated test suite covering:

- AI classification
- Resolution services
- Duplicate payment workflows
- Failed payment workflows
- Refund workflows
- Authorization
- Escalation
- API endpoints
- Database workflows
- Integration workflows

Latest complete test result:

```text
84 passed, 0 failed
```

Run the test suite with:

```bash
uv run pytest
```

---

# 🐳 Docker

PostgreSQL can be started using Docker Compose.

Start the database:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

Stop the environment:

```bash
docker compose down
```

---

# 🗃️ Database Migrations

Alembic is used to manage database schema migrations.

Create a migration:

```bash
uv run alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Check the current migration:

```bash
uv run alembic current
```

---

# ⚙️ Installation

## Prerequisites

Make sure the following are installed:

- Python 3.12+
- uv
- Docker
- Docker Compose
- Git
- PostgreSQL through Docker Compose

## 1. Clone the Repository

```bash
git clone https://github.com/Ravi718r/ResolveAI.git
cd ResolveAI
```

## 2. Create Virtual Environment

Using `uv`:

```bash
uv venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
uv sync
```

---

# 🔑 Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/resolveai

SECRET_KEY=your_secret_key

GROQ_API_KEY=your_groq_api_key

GEMINI_API_KEY=your_gemini_api_key
```

Never commit `.env` files or API keys to GitHub.

---

# 🐘 Running PostgreSQL

Start PostgreSQL using Docker Compose:

```bash
docker compose up -d
```

Verify the database container:

```bash
docker compose ps
```

The PostgreSQL container should be running before starting the application.

---

# 🔄 Running Database Migrations

Apply the latest migrations:

```bash
uv run alembic upgrade head
```

Check the current migration:

```bash
uv run alembic current
```

---

# 🚀 Running the Application

Start the FastAPI server:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# 📡 API Example

A customer can submit a support request through the API.

Example:

```http
POST /support
Content-Type: application/json
Authorization: Bearer <token>
```

Request body:

```json
{
  "message": "I was charged twice for my order",
  "order_id": "ORD-1023"
}
```

The system then executes:

```text
Request
   ↓
Authentication
   ↓
AI Classification
   ↓
LangGraph Routing
   ↓
MCP Tool
   ↓
Payment Service
   ↓
Database
   ↓
Resolution / Escalation
```

---

# 🧑‍💼 Escalation API

Support cases can be escalated when automated resolution is not appropriate.

Example:

```http
POST /support/escalate
Authorization: Bearer <token>
```

The escalation workflow creates a support case that can move through:

```text
open
  ↓
in_progress
  ↓
resolved
  ↓
closed
```

---

# 🎯 Design Decisions

## Why LangGraph?

LangGraph provides explicit stateful workflows and conditional routing.

Customer-support workflows are not simple one-shot LLM calls. They often require:

```text
Classification
      ↓
Validation
      ↓
Tool Execution
      ↓
Decision
      ↓
Resolution / Escalation
```

LangGraph makes this workflow explicit and controllable.

---

## Why MCP?

MCP provides a structured interface for exposing controlled capabilities to the AI agent.

Instead of giving the model unrestricted access to application internals, the system exposes specific tools.

This improves:

- Control
- Modularity
- Security
- Testability
- Maintainability

---

## Why PostgreSQL?

Customer-support systems contain relational transactional data such as:

```text
Customers
Orders
Payments
Refunds
Support Cases
Escalations
```

PostgreSQL provides relational consistency and transactional capabilities for this type of data.

---

## Why Repository / Service Architecture?

Separating business logic from database access makes the application easier to:

- Test
- Maintain
- Extend
- Debug
- Refactor

---

## Why Deterministic Business Logic?

LLMs are probabilistic.

Transactional operations such as:

```text
Refund money
Cancel order
Verify payment
Modify order state
```

should not depend entirely on probabilistic model output.

Therefore:

```text
LLM
→ Understands the request

Backend
→ Verifies the truth

Service
→ Applies business rules

Database
→ Stores application state
```

---

# 🔐 Security Considerations

ResolveAI follows several security-oriented design principles:

- JWT authentication
- Password hashing
- Customer/order ownership validation
- Controlled MCP tools
- No unrestricted database access for the LLM
- Environment-based secrets
- API validation using Pydantic
- Separation between AI reasoning and transactional operations
- Deterministic backend business logic

Sensitive configuration such as API keys and database credentials should be stored in environment variables rather than committed to source control.

---

# 🔮 Future Improvements

Potential future improvements include:

- Redis-based caching
- Production observability
- Distributed tracing
- LangSmith integration
- Advanced agent evaluation
- Conversation memory
- Streaming responses
- Rate limiting
- Background task processing
- Event-driven architecture
- Notification services
- Admin dashboard
- Customer support dashboard
- Production deployment
- CI/CD pipeline
- Advanced model routing
- Automatic evaluation and regression testing
- Human-agent feedback loops

---

# 🎯 Project Goals

ResolveAI was built to demonstrate practical understanding of modern AI application engineering rather than simply calling an LLM API.

The project combines:

```text
LLMs
  +
Agentic Workflows
  +
LangGraph
  +
LangChain
  +
MCP
  +
FastAPI
  +
PostgreSQL
  +
Deterministic Backend Logic
  +
Authentication
  +
Testing
  +
Docker
```

The main objective is to demonstrate how AI agents can be integrated with real backend systems while keeping transactional operations controlled, validated, and deterministic.

---

# 📌 Key Engineering Highlights

- Production-style AI customer support architecture
- Stateful LangGraph agent workflow
- Structured LLM outputs
- Multi-provider LLM abstraction
- Model routing and fallback
- MCP-based controlled tool execution
- Deterministic business logic
- FastAPI REST backend
- Repository / Service architecture
- PostgreSQL persistence
- SQLAlchemy ORM
- Alembic migrations
- JWT authentication
- Authorization checks
- Human-in-the-loop escalation
- Dockerized PostgreSQL
- Automated testing
- 84 passing Pytest tests

---

# 📚 What This Project Demonstrates

```text
Generative AI
LLM Applications
AI Agents
Agentic Workflows
LangChain
LangGraph
MCP
Prompt Engineering
Structured Outputs
Model Routing
Fallback Systems
FastAPI
REST APIs
PostgreSQL
SQLAlchemy
Alembic
JWT Authentication
Repository Pattern
Service Layer
Docker
Pytest
Production-Oriented Architecture
```

---

# 👨‍💻 Author

**Ravi Yadav**

B.Tech — Electronics & Communication Engineering

Interested in:

- AI Engineering
- Generative AI
- Agentic AI
- LLM Applications
- Backend Engineering
- AI Infrastructure

---

# 📄 License

This project is intended for educational and portfolio purposes.

You are free to study and modify the code for learning and experimentation.
