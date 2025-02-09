quiz-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User model (id, username, email, password, role, approved)
│   │   │   ├── quiz.py          # Quiz model (id, title, description, duration)
│   │   │   ├── question.py      # Question model (quiz_id, text, options, correct_answers)
│   │   │   └── attempt.py       # Attempt model (user_id, quiz_id, score, completed_at)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py          # Login, signup, logout routes
│   │       ├── admin.py         # Admin routes (user approval, analytics)
│   │       └── quiz.py          # Quiz routes (take quiz, submit answers)
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── static/
    │   ├── css/
    │   │   ├── style.css        # Common styles
    │   │   ├── auth.css         # Authentication styles
    │   │   ├── quiz.css         # Quiz interface styles
    │   │   ├── admin.css        # Admin dashboard styles
    │   │   └── dashboard.css    # User dashboard styles
    │   ├── js/
    │   │   ├── main.js          # Common functions
    │   │   ├── auth.js          # Authentication logic
    │   │   ├── quiz.js          # Quiz timer, submission logic
    │   │   ├── admin.js         # Admin dashboard functions
    │   │   └── dashboard.js     # User dashboard functions
    │   └── img/                 # Images and icons
    └── templates/
        ├── auth/
        │   ├── login.html
        │   └── signup.html
        ├── admin/
        │   ├── dashboard.html    # Admin main page
        │   ├── users.html        # User approval page
        │   ├── quiz-create.html  # Create quiz page
        │   └── analytics.html    # Performance analytics
        ├── quiz/
        │   ├── list.html         # Available quizzes
        │   ├── take.html         # Quiz interface
        │   └── results.html      # Quiz results page
        ├── dashboard/
        │   ├── home.html         # User dashboard
        │   ├── attempts.html     # Past attempts
        │   └── performance.html  # Performance analysis
        ├── base.html
        └── index.html
