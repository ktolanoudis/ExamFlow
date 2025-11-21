# ExamFlow
This repository contains the full codebase and resources for ExamFlow, an AI-driven examination platform developed at the Agentic Systems Lab, ETH Zurich. ExamFlow enables students to practice oral exams with AI-generated questions.

##  Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.8+  
- Git  
- Optional but recommended: virtual environment tool (`venv` or `virtualenv`)  
- 
### 1. Clone the repository
.. code:: bash

    git clone https://github.com/ktolanoudis/ExamFlow.git
    cd ExamFlow

### 2. Set up a virtual environment (recommended)
.. code:: bash

    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux\

    venv\Scripts\activate # Windows

### 3. Install dependencies
.. code:: bash

    ip install -r requirements.txt

### 4. Run the application
.. code:: bash
    
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
#### Example:
.. code:: bash

    uvicorn app.main:app --host 0.0.0.0 --port 8000

### 5. Visit in your browser
http://localhost:8000