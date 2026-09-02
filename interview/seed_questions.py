import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerai.settings')
django.setup()

from interview.models import InterviewQuestionBank

def seed_interview_questions():
    questions = [
        # ==========================================
        # PYTHON DEVELOPER (Sections 1 to 5)
        # ==========================================
        {
            "role": "python", "section": 1, "section_title": "Python Fundamentals", "difficulty": "easy",
            "topic": "Data Structures",
            "question_text": "What is the difference between a List and a Tuple in Python?",
            "expected_concepts": "List is mutable, tuple is immutable. Lists use square brackets [], tuples use parentheses (). Tuples are memory efficient and faster for read-only sequences.",
            "keywords": "mutable, immutable, tuple, list, memory, performance, brackets, parentheses",
            "hint": "Think about mutability, syntax brackets, and read-only memory efficiency.",
            "explanation": "A List is mutable (can be changed after creation using append/pop). A Tuple is immutable (read-only sequence created using parentheses). Tuples consume less memory and execute faster."
        },
        {
            "role": "python", "section": 1, "section_title": "Python Fundamentals", "difficulty": "medium",
            "topic": "Memory Management",
            "question_text": "How does memory management and garbage collection work in Python?",
            "expected_concepts": "Python manages memory via reference counting and a cyclic garbage collector. The sys.getrefcount() checks references, and the gc module detects cycles.",
            "keywords": "reference counting, garbage collection, gc module, cyclic references, memory allocation",
            "hint": "Focus on reference counting, reference cycles, and Python's gc module.",
            "explanation": "Python tracks objects using reference counting. When an object's reference count drops to zero, memory is deallocated. To clean circular references (A -> B -> A), Python uses a cyclic garbage collector (gc module)."
        },
        {
            "role": "python", "section": 2, "section_title": "OOP & Advanced Python", "difficulty": "medium",
            "topic": "Decorators",
            "question_text": "Explain Python decorators and how to write a custom decorator with arguments.",
            "expected_concepts": "A decorator wraps a function to extend behavior without modifying source code. It takes a function as input, defines an inner wrapper function, and uses @functools.wraps.",
            "keywords": "decorator, wrapper, wraps, higher-order function, arguments, functools",
            "hint": "Consider higher-order functions, inner wrappers, and @functools.wraps.",
            "explanation": "A decorator is a function that takes another function as an argument, wraps it with additional functionality, and returns the wrapped function without altering the original code."
        },
        {
            "role": "python", "section": 2, "section_title": "OOP & Advanced Python", "difficulty": "hard",
            "topic": "Metaclasses",
            "question_text": "What is a metaclass in Python and when would you use type or __metaclass__?",
            "expected_concepts": "A metaclass is the class of a class. Classes define object behavior, metaclasses define class creation behavior. Type is the built-in metaclass.",
            "keywords": "metaclass, type, class creation, __new__, __init__, reflection, dynamic attributes",
            "hint": "Think of metaclasses as 'classes that create classes' using type or __new__.",
            "explanation": "In Python, everything is an object, including classes. Metaclasses define how classes themselves are constructed, validated, or modified during import time."
        },
        {
            "role": "python", "section": 3, "section_title": "Django & APIs", "difficulty": "medium",
            "topic": "ORM Optimization",
            "question_text": "How do select_related and prefetch_related optimize Django ORM queries?",
            "expected_concepts": "select_related performs SQL JOIN for single-valued relationships (ForeignKey, OneToOne). prefetch_related performs a separate query for multi-valued relationships (ManyToMany, Reverse ForeignKeys).",
            "keywords": "select_related, prefetch_related, JOIN, N+1 query problem, queryset optimization, ORM",
            "hint": "Distinguish between single SQL JOINs vs separate Python prefetch queries for N+1 optimization.",
            "explanation": "select_related creates a single SQL JOIN query for ForeignKeys/OneToOne relationships. prefetch_related runs separate SQL queries and joins them in Python for ManyToMany/Reverse ForeignKeys, preventing N+1 query performance bottlenecks."
        },
        {
            "role": "python", "section": 4, "section_title": "SQL & Database", "difficulty": "medium",
            "topic": "SQL Joins",
            "question_text": "Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN.",
            "expected_concepts": "INNER JOIN returns matching rows in both tables. LEFT JOIN returns all rows from left table plus matched right table rows. FULL JOIN returns all rows when there is a match in either.",
            "keywords": "INNER JOIN, LEFT JOIN, FULL OUTER JOIN, ON clause, null values, matching rows",
            "hint": "Think about matching rows vs left table retention vs full table union.",
            "explanation": "INNER JOIN returns only rows where join condition matches in both tables. LEFT JOIN returns all rows from left table regardless of right table match. FULL JOIN returns all rows from both tables."
        },
        {
            "role": "python", "section": 5, "section_title": "Problem Solving", "difficulty": "hard",
            "topic": "Algorithms",
            "question_text": "How would you detect a loop in a linked list using Floyd's Cycle Finding Algorithm?",
            "expected_concepts": "Use two pointers: slow pointer moving 1 step and fast pointer moving 2 steps. If they meet at the same node, a cycle exists. Time complexity O(N), Space complexity O(1).",
            "keywords": "pointers, slow pointer, fast pointer, cycle detection, linked list, time complexity, space complexity",
            "hint": "Recall the Tortoise and Hare approach with slow and fast pointers.",
            "explanation": "Floyd's algorithm uses two pointers moving through the list at different speeds (slow = 1 step, fast = 2 steps). If the list contains a cycle, the fast pointer will eventually catch up and meet the slow pointer."
        },

        # ==========================================
        # DATA SCIENTIST (Sections 1 to 5)
        # ==========================================
        {
            "role": "data_science", "section": 1, "section_title": "Python & Data Wrangling", "difficulty": "easy",
            "topic": "Pandas",
            "question_text": "How do loc and iloc differ in Pandas DataFrames?",
            "expected_concepts": "loc is label-based indexing using row/column names. iloc is integer position-based indexing using numerical indices.",
            "keywords": "loc, iloc, label-based, integer index, slicing, DataFrame, Pandas",
            "hint": "Focus on string label-based vs zero-based integer index slicing.",
            "explanation": "loc accesses rows/columns by explicit labels or boolean arrays. iloc accesses by integer position index (0 to N-1)."
        },
        {
            "role": "data_science", "section": 2, "section_title": "Statistics & Probability", "difficulty": "medium",
            "topic": "Hypothesis Testing",
            "question_text": "What is p-value and how do you interpret a p-value less than 0.05?",
            "expected_concepts": "p-value is the probability of observing data as extreme assuming null hypothesis is true. p < 0.05 indicates statistically significant evidence to reject null hypothesis.",
            "keywords": "p-value, null hypothesis, significance level, alpha, stat test, reject null",
            "hint": "Define p-value relative to the Null Hypothesis and alpha threshold 0.05.",
            "explanation": "The p-value measures the probability that observed results occurred by random chance under the null hypothesis. A p-value < 0.05 means results are statistically significant, allowing rejection of H0."
        },
        {
            "role": "data_science", "section": 3, "section_title": "Machine Learning", "difficulty": "medium",
            "topic": "Overfitting & Bias-Variance",
            "question_text": "Explain the Bias-Variance Tradeoff and strategies to prevent overfitting.",
            "expected_concepts": "High bias leads to underfitting; high variance leads to overfitting. Prevent overfitting via cross-validation, regularization (L1/L2), pruning, or adding training data.",
            "keywords": "bias, variance, overfitting, underfitting, regularization, cross validation, hyperparameter",
            "hint": "Relate high bias (underfitting) vs high variance (overfitting) and mitigation methods.",
            "explanation": "Bias represents simplifying assumptions (underfitting). Variance represents sensitivity to small fluctuations in training data (overfitting). Overfitting is prevented via L1/L2 regularization, dropout, pruning, and K-Fold cross-validation."
        },
        {
            "role": "data_science", "section": 4, "section_title": "Deep Learning", "difficulty": "hard",
            "topic": "Neural Networks",
            "question_text": "Explain Vanishing Gradient Problem in deep neural networks and how ReLU resolves it.",
            "expected_concepts": "Sigmoid/Tanh activation functions saturate at extremes, causing gradients to shrink exponentially during backpropagation. ReLU has constant derivative 1 for positive inputs.",
            "keywords": "vanishing gradient, backpropagation, activation function, ReLU, Sigmoid, Tanh, derivative",
            "hint": "Think about activation function derivatives during chain rule backpropagation.",
            "explanation": "Sigmoid/Tanh derivatives decay to small decimals (< 0.25). Multiplying small numbers over many layers reduces gradients to zero. ReLU f(x) = max(0, x) has derivative 1 for positive values, preventing gradient decay."
        },
        {
            "role": "data_science", "section": 5, "section_title": "SQL & Data Projects", "difficulty": "medium",
            "topic": "Window Functions",
            "question_text": "What is an SQL window function (e.g. ROW_NUMBER(), RANK(), DENSE_RANK())?",
            "expected_concepts": "Window functions perform calculations across a set of table rows related to current row without collapsing rows into a single summary output like GROUP BY.",
            "keywords": "OVER clause, PARTITION BY, ROW_NUMBER, RANK, DENSE_RANK, window function, aggregation",
            "hint": "Explain how OVER() and PARTITION BY compute metrics without collapsing rows.",
            "explanation": "Window functions compute aggregated values across row partitions defined by OVER(PARTITION BY...) while maintaining individual row records in the output dataset."
        },

        # ==========================================
        # ML ENGINEER (Sections 1 to 5)
        # ==========================================
        {
            "role": "ml_engineer", "section": 1, "section_title": "Python & Numerics", "difficulty": "easy",
            "topic": "Vectorization",
            "question_text": "Why is NumPy vectorization faster than Python for loops?",
            "expected_concepts": "NumPy executes operations in contiguous C memory blocks using SIMD CPU vector instructions, avoiding Python dynamic typing and GIL loop overhead.",
            "keywords": "vectorization, C array, SIMD, contiguous memory, GIL, NumPy performance",
            "hint": "Consider contiguous C array memory layout and SIMD CPU vector instructions.",
            "explanation": "NumPy performs element-wise array operations using compiled C routines and SIMD CPU instructions in contiguous memory blocks, avoiding Python interpreter loop overhead and dynamic type checking."
        },
        {
            "role": "ml_engineer", "section": 2, "section_title": "Machine Learning Models", "difficulty": "medium",
            "topic": "Ensemble Learning",
            "question_text": "Compare Random Forest (Bagging) vs Gradient Boosting (Boosting).",
            "expected_concepts": "Bagging builds independent trees in parallel to reduce variance. Boosting builds sequential trees where each tree corrects errors of previous tree to reduce bias.",
            "keywords": "Bagging, Boosting, Random Forest, XGBoost, variance, bias, sequential, parallel",
            "hint": "Distinguish between parallel independent trees (reduce variance) vs sequential error-correcting trees (reduce bias).",
            "explanation": "Random Forest (Bagging) trains parallel independent decision trees on random subsets to lower variance. Gradient Boosting (Boosting) trains sequential trees that iteratively fit the residual errors of prior trees to lower bias."
        },
        {
            "role": "ml_engineer", "section": 3, "section_title": "Deep Learning & PyTorch", "difficulty": "hard",
            "topic": "Transformers",
            "question_text": "Explain the Multi-Head Self-Attention mechanism in Transformer architectures.",
            "expected_concepts": "Self-attention computes Q (Query), K (Key), V (Value) matrices. Scaled dot-product attention computes softmax(QK^T / sqrt(d_k))V. Multi-head splits Q, K, V into multiple subspaces.",
            "keywords": "Query, Key, Value, self-attention, Softmax, multi-head attention, Transformer, positional encoding",
            "hint": "Recall Query (Q), Key (K), Value (V) projections and softmax scaled dot-product math.",
            "explanation": "Self-attention computes dynamic weight relationships between sequence tokens using Query (Q), Key (K), and Value (V) representations: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V."
        },
        {
            "role": "ml_engineer", "section": 4, "section_title": "NLP & LLMs", "difficulty": "hard",
            "topic": "Embeddings & Vector Search",
            "question_text": "How do sentence embeddings and cosine similarity enable semantic search?",
            "expected_concepts": "Transformers convert text into high-dimensional dense vector embeddings. Cosine similarity calculates dot product of normalized vectors measuring semantic angle alignment.",
            "keywords": "embeddings, dense vectors, cosine similarity, dot product, semantic search, vector database",
            "hint": "Explain mapping text into dense vector space and calculating angular similarity.",
            "explanation": "Embedding models map semantic meaning of sentences into high-dimensional vector spaces. Cosine similarity measures the inner product of normalized vectors, evaluating distance and contextual alignment."
        },
        {
            "role": "ml_engineer", "section": 5, "section_title": "MLOps & Deployment", "difficulty": "medium",
            "topic": "Model Serving",
            "question_text": "What steps are required to serve an ML model via REST API and containerize with Docker?",
            "expected_concepts": "Pickle/ONNX model serialization, wrap in FastAPI/Django endpoint, define Dockerfile with python base image, copy code, install requirements.txt, expose port.",
            "keywords": "serialization, FastAPI, Django, Dockerfile, image, container, port mapping, deployment",
            "hint": "Cover serialization, REST framework wrapping, Dockerfile steps, and port exposure.",
            "explanation": "Serialize trained model weights (e.g. pickle/ONNX), build a REST service wrapper (Django/FastAPI), package app and dependencies inside a Docker container image, and deploy to container registry or cloud cluster."
        },

        # ==========================================
        # DATA ANALYST (Sections 1 to 5)
        # ==========================================
        {
            "role": "data_analyst", "section": 1, "section_title": "Excel & Business Analytics", "difficulty": "easy",
            "topic": "Pivot Tables",
            "question_text": "How do Pivot Tables help analyze large transactional datasets?",
            "expected_concepts": "Pivot tables aggregate, summarize, sort, and group large tabular datasets without writing formulas, enabling fast metric calculations.",
            "keywords": "pivot table, aggregation, grouping, summary metrics, business intelligence",
            "hint": "Focus on drag-and-drop aggregation, grouping, and summary metrics.",
            "explanation": "Pivot tables aggregate raw transactional data into structured summaries across multiple dimensions without complex formulas."
        },
        {
            "role": "data_analyst", "section": 2, "section_title": "SQL & Databases", "difficulty": "medium",
            "topic": "SQL Aggregation",
            "question_text": "Difference between WHERE and HAVING clauses in SQL?",
            "expected_concepts": "WHERE filters rows before grouping. HAVING filters aggregated group results after GROUP BY is applied.",
            "keywords": "WHERE, HAVING, GROUP BY, aggregation, row filtering, group filtering",
            "hint": "Consider execution order: pre-aggregation filtering vs post-GROUP BY filtering.",
            "explanation": "WHERE filters individual rows before grouping takes place. HAVING filters aggregated group metrics (COUNT, SUM, AVG) after GROUP BY is evaluated."
        },
        {
            "role": "data_analyst", "section": 3, "section_title": "Python for Analytics", "difficulty": "medium",
            "topic": "Data Cleaning",
            "question_text": "How do you handle missing values in Pandas using dropna and fillna?",
            "expected_concepts": "dropna removes rows or columns containing NaN. fillna imputes missing values using constant, mean, median, or forward/backward fill.",
            "keywords": "dropna, fillna, missing values, NaN, mean median imputation, data cleaning",
            "hint": "Differentiate between removing missing rows (dropna) vs statistical imputation (fillna).",
            "explanation": "dropna() deletes rows/columns containing null values. fillna() imputes missing cells with specific values, column means, medians, or forward/backward fills."
        },
        {
            "role": "data_analyst", "section": 4, "section_title": "Data Visualization", "difficulty": "easy",
            "topic": "Charts",
            "question_text": "When should you use a Bar Chart vs a Line Chart vs a Histogram?",
            "expected_concepts": "Bar charts compare categorical groups. Line charts display trends over continuous time. Histograms show frequency distributions of continuous variables.",
            "keywords": "bar chart, line chart, histogram, categorical, time series, distribution",
            "hint": "Categorical comparison vs time series trends vs frequency distributions.",
            "explanation": "Bar charts compare discrete categories. Line charts depict temporal trends over continuous time. Histograms illustrate numerical data frequency distributions."
        },
        {
            "role": "data_analyst", "section": 5, "section_title": "Case Studies & Metrics", "difficulty": "medium",
            "topic": "KPIs",
            "question_text": "What is Churn Rate and how do you calculate Customer Lifetime Value (CLV)?",
            "expected_concepts": "Churn rate is percentage of customers lost in a period. CLV = Average Purchase Value * Purchase Frequency * Customer Lifespan.",
            "keywords": "churn rate, customer retention, CLV, purchase frequency, business metrics",
            "hint": "Define customer loss percentage and lifetime customer revenue formula.",
            "explanation": "Churn Rate is the percentage of subscribers lost over a given period. Customer Lifetime Value (CLV) predicts net profit generated throughout the entire customer relationship."
        },

        # ==========================================
        # DJANGO DEVELOPER (Sections 1 to 5)
        # ==========================================
        {
            "role": "django", "section": 1, "section_title": "Python Core", "difficulty": "easy",
            "topic": "Modules & Packages",
            "question_text": "What is __init__.py used for in Python packages?",
            "expected_concepts": "__init__.py marks a directory as a Python package and initializes package-level imports and namespace variables.",
            "keywords": "__init__.py, package, module, import, namespace, initialization",
            "hint": "Think about directory recognition as a package and package-level initialization.",
            "explanation": "__init__.py tells Python that a directory should be treated as an importable package, and executes package initialization code."
        },
        {
            "role": "django", "section": 2, "section_title": "Django ORM & Models", "difficulty": "medium",
            "topic": "Migrations",
            "question_text": "Explain makemigrations and migrate commands in Django.",
            "expected_concepts": "makemigrations inspects models.py changes and writes SQL migration files. migrate executes pending migration files against the database schema.",
            "keywords": "makemigrations, migrate, schema, database migration, SQL execution, models.py",
            "hint": "Creating migration files (makemigrations) vs applying changes to SQL database (migrate).",
            "explanation": "makemigrations inspects model changes and generates Python migration scripts. migrate applies those migration scripts directly to update the underlying SQL database schema."
        },
        {
            "role": "django", "section": 3, "section_title": "REST APIs & DRF", "difficulty": "medium",
            "topic": "Serializers",
            "question_text": "What is a Django REST Framework Serializer and how does it handle validation?",
            "expected_concepts": "Serializers convert complex queryset/model instances to Python primitives (JSON). They validate incoming payloads via field validators and validate() methods.",
            "keywords": "Serializer, ModelSerializer, JSON, validation, is_valid(), data binding",
            "hint": "Converting ORM objects to JSON primitives and validating request data.",
            "explanation": "Serializers translate Django queryset/model instances to JSON/XML representations for API responses and validate incoming payload data before saving to ORM."
        },
        {
            "role": "django", "section": 4, "section_title": "Authentication & Security", "difficulty": "medium",
            "topic": "CSRF & Auth",
            "question_text": "How does Django protect against Cross-Site Request Forgery (CSRF)?",
            "expected_concepts": "Django injects secret CSRF tokens in forms and checks HTTP request headers/cookies on POST/PUT requests using CsrfViewMiddleware.",
            "keywords": "CSRF, token, CsrfViewMiddleware, secret key, POST header, security",
            "hint": "CSRF tokens in forms and CsrfViewMiddleware validation on non-GET requests.",
            "explanation": "Django provides built-in CSRF protection by setting a user-specific secret token in cookies and requiring forms/headers to supply matching tokens on POST/PUT requests."
        },
        {
            "role": "django", "section": 5, "section_title": "Deployment & Architecture", "difficulty": "hard",
            "topic": "WSGI & ASGI",
            "question_text": "Difference between WSGI and ASGI in Django deployments?",
            "expected_concepts": "WSGI (Gunicorn/uWSGI) is synchronous request-response protocol. ASGI (Daphne/Uvicorn) supports async Python, WebSockets, and long polling.",
            "keywords": "WSGI, ASGI, Gunicorn, Uvicorn, async, WebSockets, synchronous, deployment",
            "hint": "Synchronous request-response (WSGI) vs asynchronous WebSockets protocol (ASGI).",
            "explanation": "WSGI handles synchronous HTTP request-response cycles (e.g. Gunicorn). ASGI handles asynchronous events, WebSockets, HTTP/2, and async Python code (e.g. Uvicorn/Daphne)."
        }
    ]

    for item in questions:
        InterviewQuestionBank.objects.get_or_create(
            role=item["role"],
            question_text=item["question_text"],
            defaults=item
        )

    print(f"Successfully seeded {len(questions)} interview questions with hints and detailed explanations!")

if __name__ == '__main__':
    seed_interview_questions()
