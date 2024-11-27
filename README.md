# Medical Drug Interaction and Analysis API

This project provides a **Medical Drug Interaction and Analysis API**, allowing users to extract detailed medication-related information from multiple online sources, analyze drug interactions, and manage this data via a backend API.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Endpoints](#endpoints)
- [Technical Details](#technical-details)
- [Contributing](#contributing)

---

## Overview

The API integrates:

1. Web scraping from trusted medical resources (e.g., **drugs.com**, **1mg.com**).
2. Natural language processing for content extraction and categorization using **ChatGroq** and **LangChain**.
3. Persistent storage and querying of drug metadata using **ChromaDB**.
4. RESTful endpoints for user interaction with medication data.

This project is built using Python with the Flask web framework and supports asynchronous background task execution via threading.

---

## Key Features

1. **Drug Data Extraction**
   - Scrapes drug information from reliable sources.
   - Uses a sophisticated language model (ChatGroq) for text processing and data extraction.

2. **Drug Interaction Analysis**
   - Identifies potential interactions between drugs.
   - Records metadata and interaction details for easy querying.

3. **User Medication Management**
   - Links user-provided medication data with detailed drug analysis.

4. **Persistent Storage**
   - Stores drug metadata and interaction data in **ChromaDB**.
   - Enables fast querying of existing records.

5. **REST API**
   - Provides endpoints to trigger background tasks and fetch/update medication data.

---

## Project Structure

```
project/
├── Files/
│   ├── Original.py           # Main Python File
│ # Background task handling
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- API key for **ChatGroq**
- Libraries: Flask, BeautifulSoup, requests, ChromaDB, LangChain

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/krishnaAg16/DailyDoseLLM.git
   cd DailyDoseLLM.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure **ChatGroq** API key:
   - Replace `YOUR_API_KEY` in `app.py` with your actual API key.

4. Run the Flask application:
   ```bash
   python app.py
   ```

---

## Endpoints

### 1. **Add Drug Data for a User**

**`GET /addDrug/<usr>`**

- **Description**: Triggers a background task to scrape, analyze, and store drug data for a specific user.
- **Parameters**:
  - `usr`: The user identifier.
- **Response**:
  - `202 Accepted`: Task started successfully.
  - `500 Internal Server Error`: Task initialization failed.

**Example**:
```bash
curl -X GET http://127.0.0.1:5000/addDrug/user123
```

---

## Technical Details

### 1. **Web Scraping**

- **Data Sources**:
  - Drugs.com
  - 1mg.com
- **Tools Used**:
  - `BeautifulSoup` for HTML parsing.
  - `requests` for making HTTP requests.

### 2. **Natural Language Processing**

- **LLM**: ChatGroq (Llama-3.1-70B)
- **Processing Steps**:
  - Scraped text is passed to the ChatGroq model via the LangChain pipeline.
  - Extracted details include:
    - Drug Name
    - Recommended and avoided foods
    - Interacting drugs
    - Common and serious side effects
    - Treatment use cases

### 3. **Database (ChromaDB)**

- **Purpose**:
  - Store and query drug metadata.
- **Data Model**:
  ```json
  {
    "name": "DrugName",
    "super_food": ["list of recommended foods"],
    "bad_food": ["list of foods to avoid"],
    "interactive_drug": [
      {"name": "InteractingDrug", "delta": "time in hours"}
    ],
    "common_symptom": ["list of common side effects"],
    "serious_symptom": ["list of serious side effects"],
    "treatment": ["medical conditions treated"]
  }
  ```

### 4. **Asynchronous Tasks**

- Background tasks are handled using Python's `threading` module.
- Tasks include:
  - Fetching and analyzing user medication data.
  - Updating drug interactions in the database.

---

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of changes.

---

