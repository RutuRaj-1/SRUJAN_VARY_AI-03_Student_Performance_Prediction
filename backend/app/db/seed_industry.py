"""
Seed reference industry roles and competency requirements.
Run idempotently to populate standard technical roles.
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import select
from app.db.session import get_session_local
from app.models.enums import CompetencyCategory, IndustryImportance
from app.models.syllabus import IndustryRoleProfile, IndustryCompetencyRequirement

ROLES_DATA = [
    {
        "role_title": "Software Development Engineer - Backend",
        "role_family": "Software Development",
        "description": "Designs, implements, and maintains scalable server-side systems, REST/gRPC APIs, databases, and microservices architectures.",
        "experience_tier": "Entry-Level / Fresher",
        "requirements": [
            ("Object-Oriented & Functional Programming", CompetencyCategory.PROGRAMMING, 4, IndustryImportance.HIGH, "Mastery of core language paradigms, design patterns, clean code principles, and encapsulation."),
            ("Data Structures & Algorithm Optimization", CompetencyCategory.ANALYTICAL, 4, IndustryImportance.HIGH, "Time and space complexity analysis, trees, graphs, sorting, searching, and dynamic programming."),
            ("Relational & NoSQL Database Design", CompetencyCategory.TOOLS_TECHNOLOGIES, 4, IndustryImportance.HIGH, "Schema normalization, indexing, transaction isolation (ACID), and query optimization."),
            ("RESTful API & Service Architecture", CompetencyCategory.PRACTICAL, 4, IndustryImportance.HIGH, "HTTP spec, authentication, rate limiting, error formatting, and stateless API design."),
            ("Process Concurrency & Thread Synchronization", CompetencyCategory.THEORETICAL, 3, IndustryImportance.HIGH, "Locks, semaphores, race conditions, deadlocks, and event loops."),
            ("Automated Testing & Test-Driven Development", CompetencyCategory.PRACTICAL, 3, IndustryImportance.HIGH, "Unit testing, integration testing, mocking, and coverage reporting."),
            ("Containerization with Docker", CompetencyCategory.TOOLS_TECHNOLOGIES, 3, IndustryImportance.MEDIUM, "Creating reproducible Dockerfiles, multi-stage builds, and container networking."),
            ("Distributed Caching & Message Queues", CompetencyCategory.TOOLS_TECHNOLOGIES, 3, IndustryImportance.MEDIUM, "In-memory caching with Redis, message brokers like Kafka or RabbitMQ.")
        ]
    },
    {
        "role_title": "Full-Stack Web Developer",
        "role_family": "Software Development",
        "description": "Builds end-to-end web applications bridging responsive client frontends with scalable server backends.",
        "experience_tier": "Entry-Level / Fresher",
        "requirements": [
            ("Modern TypeScript & JavaScript (ES6+)", CompetencyCategory.PROGRAMMING, 4, IndustryImportance.HIGH, "Closures, promises, async/await, DOM APIs, and static typing with TypeScript."),
            ("Component-Driven Frontend Architecture", CompetencyCategory.PRACTICAL, 4, IndustryImportance.HIGH, "Building reactive component trees using React, state management, and props flow."),
            ("Web APIs & Client-Server Integration", CompetencyCategory.PRACTICAL, 4, IndustryImportance.HIGH, "Fetch APIs, TanStack Query, error boundaries, and optimistic UI updates."),
            ("Responsive Layout & CSS Frameworks", CompetencyCategory.PRACTICAL, 3, IndustryImportance.MEDIUM, "Flexbox, CSS Grid, mobile-first responsive design, Tailwind CSS."),
            ("Backend API Implementation", CompetencyCategory.PROGRAMMING, 4, IndustryImportance.HIGH, "Node.js/FastAPI routes, middleware, request validation, and database queries."),
            ("Web Security Fundamentals", CompetencyCategory.THEORETICAL, 3, IndustryImportance.HIGH, "CORS, CSRF, XSS prevention, JWT handling, and input sanitization.")
        ]
    },
    {
        "role_title": "Data Engineer",
        "role_family": "Data & AI",
        "description": "Constructs robust data extraction, transformation, loading (ETL/ELT) pipelines, data warehouses, and analytics infrastructure.",
        "experience_tier": "Entry-Level / Fresher",
        "requirements": [
            ("Advanced SQL & Query Optimization", CompetencyCategory.PROGRAMMING, 5, IndustryImportance.HIGH, "Complex joins, window functions, CTEs, query plan execution analysis, and index tuning."),
            ("Python for Data Manipulation", CompetencyCategory.PROGRAMMING, 4, IndustryImportance.HIGH, "Data structures, pandas, polars, file formats (Parquet, JSON, Avro), and data cleaning."),
            ("Data Warehousing & Dimensional Modeling", CompetencyCategory.THEORETICAL, 4, IndustryImportance.HIGH, "Star schema, snowflake schema, fact/dimension tables, and SCD types."),
            ("Distributed Computing Fundamentals", CompetencyCategory.THEORETICAL, 3, IndustryImportance.HIGH, "MapReduce paradigm, Apache Spark resilient distributed datasets (RDDs), data shuffling."),
            ("Pipeline Orchestration", CompetencyCategory.TOOLS_TECHNOLOGIES, 3, IndustryImportance.HIGH, "DAG-based workflow schedulers such as Apache Airflow or Prefect."),
            ("Data Quality & Validation", CompetencyCategory.ANALYTICAL, 3, IndustryImportance.MEDIUM, "Schema drift detection, anomaly detection, Great Expectations, and pipeline monitoring.")
        ]
    },
    {
        "role_title": "Machine Learning Engineer",
        "role_family": "Data & AI",
        "description": "Develops, evaluates, trains, and operationalizes machine learning models into production software products.",
        "experience_tier": "Entry-Level / Fresher",
        "requirements": [
            ("Linear Algebra & Statistical Foundations", CompetencyCategory.THEORETICAL, 4, IndustryImportance.HIGH, "Matrix decompositions, eigenvalues, probability distributions, hypothesis testing, Bayes theorem."),
            ("Supervised & Unsupervised Learning", CompetencyCategory.ANALYTICAL, 4, IndustryImportance.HIGH, "Regression, classification, decision trees, random forests, clustering, dimensionality reduction."),
            ("Deep Learning & Neural Architectures", CompetencyCategory.THEORETICAL, 4, IndustryImportance.HIGH, "Backpropagation, gradient descent variants, CNNs, RNNs, and transformer attention mechanisms."),
            ("Python ML Frameworks", CompetencyCategory.TOOLS_TECHNOLOGIES, 4, IndustryImportance.HIGH, "PyTorch, TensorFlow, Scikit-Learn, and Hugging Face transformers."),
            ("Model Validation & Metrics Analysis", CompetencyCategory.ANALYTICAL, 4, IndustryImportance.HIGH, "Precision, recall, F1, ROC-AUC, confusion matrices, cross-validation, and bias-variance tradeoff."),
            ("MLOps & Model Deployment", CompetencyCategory.PRACTICAL, 3, IndustryImportance.HIGH, "Exporting ONNX/TorchScript models, containerized inference endpoints, model registry.")
        ]
    },
    {
        "role_title": "DevOps & Cloud Systems Engineer",
        "role_family": "Infrastructure",
        "description": "Automates software delivery pipelines, manages cloud infrastructure, and guarantees system reliability and security.",
        "experience_tier": "Entry-Level / Fresher",
        "requirements": [
            ("Linux Systems Administration & Bash", CompetencyCategory.PRACTICAL, 4, IndustryImportance.HIGH, "Process control, signals, systemd, file permissions, shell scripting, and network debugging tools."),
            ("Containerization with Docker", CompetencyCategory.TOOLS_TECHNOLOGIES, 4, IndustryImportance.HIGH, "Container lifecycle, volumes, security scanning, multi-stage builds, and Docker Compose."),
            ("Container Orchestration with Kubernetes", CompetencyCategory.TOOLS_TECHNOLOGIES, 3, IndustryImportance.HIGH, "Pods, Deployments, Services, ConfigMaps, Ingress, and basic helm charts."),
            ("Continuous Integration & Deployment (CI/CD)", CompetencyCategory.PRACTICAL, 4, IndustryImportance.HIGH, "GitHub Actions / GitLab CI workflows, test automation triggers, and automated releases."),
            ("Infrastructure as Code (IaC)", CompetencyCategory.TOOLS_TECHNOLOGIES, 3, IndustryImportance.MEDIUM, "Terraform state management, providers, modules, and declarative infrastructure."),
            ("System Observability & Monitoring", CompetencyCategory.ANALYTICAL, 3, IndustryImportance.HIGH, "Metrics aggregation (Prometheus), log streaming, alerting rules, and Grafana dashboards.")
        ]
    }
]


def seed_industry_roles():
    session_factory = get_session_local()
    if not session_factory:
        print("Database not configured or connection failed.")
        return
    session = session_factory()
    try:
        created_roles = 0
        created_reqs = 0

        for role_spec in ROLES_DATA:
            stmt = select(IndustryRoleProfile).where(IndustryRoleProfile.role_title == role_spec["role_title"])
            existing_role = session.execute(stmt).scalars().first()

            if not existing_role:
                existing_role = IndustryRoleProfile(
                    id=uuid.uuid4(),
                    role_title=role_spec["role_title"],
                    role_family=role_spec["role_family"],
                    description=role_spec["description"],
                    experience_tier=role_spec["experience_tier"],
                )
                session.add(existing_role)
                session.flush()
                created_roles += 1

            # Seed requirements
            for req_name, cat, depth, imp, desc in role_spec["requirements"]:
                req_stmt = select(IndustryCompetencyRequirement).where(
                    IndustryCompetencyRequirement.role_id == existing_role.id,
                    IndustryCompetencyRequirement.competency_name == req_name,
                )
                existing_req = session.execute(req_stmt).scalars().first()
                if not existing_req:
                    new_req = IndustryCompetencyRequirement(
                        id=uuid.uuid4(),
                        role_id=existing_role.id,
                        competency_name=req_name,
                        category=cat.value,
                        required_depth=depth,
                        importance=imp.value,
                        description=desc,
                    )
                    session.add(new_req)
                    created_reqs += 1

        session.commit()
        print(f"Successfully seeded {created_roles} industry roles and {created_reqs} competency requirements.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding industry roles: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_industry_roles()
