# sql-agent-interviewer
A production-ready GenAI &amp; MLOps platform featuring an adaptive SQL interview coach for Data Engineering candidates. Built with FastAPI, Streamlit, and SQLite (in-memory execution), the system leverages structured LLM outputs to progressively adjust question difficulty based on user performance. 
```
graph TD
    %% Styling
    classDef domain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef infra fill:#bbf,stroke:#333,stroke-width:2px;
    classDef app fill:#fbf,stroke:#333,stroke-width:2px;
    classDef devops fill:#bfb,stroke:#333,stroke-width:2px;

    %% Repository Structure
    subgraph Repo_Structure [1. Repository File Structure]
        direction LR
        Root["sql-learning-chatbot/"]
        Root --> CI[".github/workflows/ci.yml"]
        Root --> Src["src/"]
        Root --> Dk["docker/"]
        Root --> Dc["docker-compose.yml"]
        
        Src --> App["app/ (API & UI)"]
        Src --> Dom["domain/ (Business Logic)"]
        Src --> Inf["infrastructure/ (LLM & DB)"]
        
        Dom --> Models["models.py (Pydantic Contracts)"]
        Dom --> Val["validator.py (Pandas Engine)"]
        
        Inf --> DB["database/ (SQLite & Seed Mock Data)"]
        Inf --> LLM["llm/ (Abstract Clients & Prompts)"]
    end

    %% Application & MLOps Architecture
    subgraph Architecture [2. Data Flow & Production Architecture]
        User([User / Candidate]) <--> |Interacts| UI[Streamlit Frontend]
        UI <--> |REST API Requests| API[FastAPI Backend]
        
        subgraph Core_Backend [FastAPI Application Layer]
            API --> |1. Request Question| LLM_Svc[LLM Service Interface]
            LLM_Svc --> |Structured JSON Output| Pydantic[Pydantic Validation]
            
            API --> |2. Submit Answer| Check[Validation Engine]
            Check --> |Run User vs Expected SQL| SQLite[In-Memory SQLite DB]
            SQLite --> |Extract DataFrames| Pandas[Pandas Frame Comparison]
        end
        
        LLM_Svc -.-> |Async Tracking| Langfuse[(Langfuse / Observability Hub)]
        LLM_Svc <--> |API Call| External_LLM([External LLM: Groq / OpenAI])
    end

    %% MLOps Pipeline Steps
    subgraph Pipeline [3. Development & CI/CD Sequence]
        Step1[Phase 1: Setup Core Python & In-Memory SQLite Engine] --> 
        Step2[Phase 2: Build Pydantic Contracts & FastAPI Endpoints] --> 
        Step3[Phase 3: Connect Abstract LLM Client & Langfuse Monitoring] --> 
        Step4[Phase 4: Dockerize Multi-Stage Containers & Write GitHub Actions CI]
    end

    %% Apply Classes
    class Dom,Models,Val domain;
    class Inf,DB,LLM,SQLite,Pandas,External_LLM infra;
    class App,API,UI app;
    class CI,Dk,Dc,Langfuse,Pipeline devops;
```