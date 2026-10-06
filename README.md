# Smart DSA Tracker 🧠⚡

A modern, high-performance personal dashboard for tracking Data Structures & Algorithms (DSA) interview preparation, powered by an automated **SM-2 spaced-repetition revision engine** and **analytics dashboard**.

---

## 🌟 Key Features

### 1. Core DSA Management & Smart Import
- **LeetCode GraphQL Auto-Fetch ⚡**: Paste any LeetCode problem URL or slug (e.g. `https://leetcode.com/problems/trapping-rain-water/`), and the system automatically queries LeetCode's public GraphQL API to auto-fill title, difficulty, canonical link, inferred algorithmic pattern, and matching topic.
- **Expanded Algorithmic Pattern Tags**: Classify problems with 16 interview patterns: *Two Pointers, Fast & Slow Pointers, Sliding Window, Merge Intervals, Monotonic Stack / Queue, Dynamic Programming, Backtracking, Greedy, Graph Traversal (BFS/DFS), Union Find / Disjoint Set, Binary Search, Top 'K' Elements (Heap), Tree BFS/DFS, Trie, Bit Manipulation, and General*.
- **Problem Bank**: Full CRUD for technical interview problems with topic classification, difficulty levels (*Easy, Medium, Hard*), solution links, and intuition notes.
- **Mastery Tracking**: Interactive 1-click mastery toggle (`⭐ Mastered` vs. `Needs Practice`) to easily filter mastered questions from your active study queue.
- **Multi-criteria Filtering & Search**: Instant filtering by Topic, Difficulty, Pattern, and Mastery status, plus real-time keyword search across titles and notes.
- **Practice Attempts Log**: Track every practice attempt with exact time taken (in minutes), success/failure outcome, and reflection notes on pitfalls and edge cases.
- **User Authentication & Data Isolation**: Secure Django authentication ensuring complete privacy and isolation of your problems and stats.

### 2. Spaced Repetition Engine (SM-2 Algorithm)
Unlike traditional date pickers, Smart DSA Tracker uses a customized implementation of the **SuperMemo-2 (SM-2)** spaced repetition algorithm (the foundation behind Anki and SuperMemo):
- **Active Recall**: Prompts you to mentally reconstruct the algorithmic intuition, data structures, and complexities before revealing your notes.
- **Recall Quality Ratings (0–5)**:
  - `0–2` (Struggled or forgot): Repetitions reset to `0`, interval resets to `1 day` for immediate reinforcement tomorrow.
  - `3–5` (Successful recall): Repetitions increase; intervals scale exponentially based on the dynamic **Ease Factor** ($EF$).
- **Ease Factor ($EF$) Adjustment**: Dynamically scales between $1.3$ and $2.5+$ based on the formula:
  $$EF' = \max\left(1.3, EF + (0.1 - (5 - q) \cdot (0.08 + (5 - q) \cdot 0.02))\right)$$
- **Automatic Queue**: Problems automatically surface on your dashboard and **Today's Revision Queue** when their review date arrives.

### 3. Analytics & Diagnostics Dashboard
- **Topic Mastery Distribution**: Chart.js visualization showing problems solved vs. mastered across every DSA topic.
- **Difficulty Breakdown**: Doughnut chart illustrating Easy / Medium / Hard problem distribution.
- **Weak Pattern Detection**: Automatically flags algorithmic patterns where your average time-to-solve is highest, highlighting where your prep time is best spent.
- **Key Performance Indicators (KPIs)**: Total problems logged, overall mastery rate %, today's overdue revisions count, total study hours, and attempt success percentage.

### 4. Interview Readiness Dossier (Printable PDF & Markdown Export)
- **Printable Readiness Dossier**: Clean, printable HTML view optimized with `@media print` CSS for instant "Save to PDF" generation without external heavy headless libraries.
- **Downloadable Markdown Dossier**: One-click download of a personal `username_dsa_dossier.md` file summarizing solved problems, algorithmic patterns, and key takeaways for offline revision.

---

## 🎨 UI & UX Design Philosophy
Built with a **clean, modern design system**:
- **Light & Dark Theme Toggle**: Instant switching with `localStorage` persistence and automatic Chart.js palette adaptation.
- **Refined Color Palette**:
  - Easy: Subtle emerald green (`#059669` / `#ecfdf5`)
  - Medium: Warm amber (`#d97706` / `#fffbeb`)
  - Hard: Crisp crimson rose (`#e11d48` / `#fff1f2`)
- **Typography**: Google's `Plus Jakarta Sans` for clean readability and `JetBrains Mono` for code and complexity annotations.
- **No AI Slob**: Thoughtful spacing, responsive card elevation, accessible contrast, clean empty states, and subtle micro-interactions.

---

## 📁 Project Architecture & Folder Structure

```
smart_dsa_tracker/
├── manage.py                     # Django management script
├── requirements.txt              # Production & dev dependencies
├── build.sh                      # Render deployment script
├── .env                          # Local environment variables (ignored by git)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
│
├── smart_dsa_tracker/            # Project configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings, Whitenoise, dj-database-url
│   ├── urls.py                   # Root URL dispatcher
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/                     # Authentication App
│   ├── migrations/
│   ├── models.py
│   ├── views.py                  # Signup, login, logout views
│   ├── urls.py
│   └── templates/accounts/
│       ├── login.html            # Clean login form
│       └── signup.html           # User registration form
│
├── tracker/                      # Core DSA Tracking App
│   ├── migrations/
│   │   ├── 0001_initial.py       # Topic, Problem, Attempt, RevisionSchedule
│   │   └── 0002_seed_topics.py   # Data migration seeding standard DSA topics
│   ├── models.py                 # Topic, Problem, Attempt, RevisionSchedule
│   ├── views.py                  # Dashboard, CRUD, filtering, attempt & revision views
│   ├── forms.py                  # ProblemForm, AttemptForm, RevisionQualityForm
│   ├── urls.py                   # App URL patterns
│   ├── admin.py                  # Customized Django admin with inlines & search
│   ├── tests.py                  # 8 unit & integration tests
│   ├── services/
│   │   ├── __init__.py
│   │   ├── revision_engine.py    # SM-2 algorithmic scheduling service
│   │   └── stats.py              # Aggregation queries for dashboard analytics
│   ├── management/
│   │   └── commands/
│   │       └── populate_sample_data.py # Demo data generator
│   ├── templates/tracker/
│   │   ├── dashboard.html        # Interactive analytics dashboard with Chart.js
│   │   ├── problem_list.html     # Filterable problem bank with quick actions
│   │   ├── problem_form.html     # Add / Edit problem form
│   │   ├── problem_detail.html   # Detailed problem view with attempts & SM-2 card
│   │   └── revision_today.html   # Today's revision queue & active recall prompt
│   └── static/tracker/
│       ├── css/style.css         # Modern CSS tokens, dark mode, custom badges
│       └── js/charts.js          # Chart.js initialization & dynamic theme listener
│
└── templates/
    └── base.html                 # Master layout, responsive navbar, flash alerts, theme toggle
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12 - 3.14)
- `pip`

### 2. Setup & Installation
```bash
# Clone or navigate to the project directory
cd "Smart DSA Tracker"

# Install dependencies
pip install -r requirements.txt

# Apply database migrations (automatically seeds standard DSA topics)
python manage.py migrate

# (Optional) Seed realistic demo data (problems, attempts, SM-2 schedules)
python manage.py populate_sample_data

# Run automated test suite
python manage.py test

# Start the local development server
python manage.py runserver
```

Open **`http://127.0.0.1:8000/`** in your browser.
- Demo account credentials:
  - **Username**: `demo`
  - **Password**: `demo1234`
- Or register a brand new account at `http://127.0.0.1:8000/accounts/signup/`.

---

## ☁️ Deployment Guide (Render + Neon PostgreSQL)

1. **Database Setup (Neon)**:
   - Create a free serverless PostgreSQL database at [neon.tech](https://neon.tech).
   - Copy the PostgreSQL connection string.

2. **Render Web Service Setup**:
   - Push this repository to GitHub.
   - In Render, create a new **Web Service** connected to your repo.
   - Configure:
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn smart_dsa_tracker.wsgi`
     - **Environment Variables**:
       - `SECRET_KEY`: `<your-random-production-secret>`
       - `DEBUG`: `False`
       - `ALLOWED_HOSTS`: `<your-service-name>.onrender.com`
       - `DATABASE_URL`: `<your-neon-postgres-connection-string>`

---

## 🧪 Automated Test Suite
Run the test suite anytime:
```bash
python manage.py test
```
**Coverage includes:**
1. SM-2 low quality rating repetition reset (`quality < 3` -> `repetitions=0`, `interval=1`).
2. SM-2 interval expansion on successive high quality ratings (`1 -> 6 -> round(6 * EF)`).
3. Ease factor lower bound constraint ($EF \ge 1.3$).
4. User authentication and URL route protection.
5. Strict user data isolation (User Bob cannot view or modify User Alice's problems).
6. Automatic `RevisionSchedule` creation on problem registration.
7. Interactive mastery toggle logic.
8. Attempt logging and real-time KPI / weak-pattern statistical calculations.
