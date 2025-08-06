# Google Sheets Integration for Quiz Data Tracking

## Overview

This implementation adds Google Sheets integration to track individual quiz attempts for each user. When a user takes a quiz, each question attempt is logged to their personal worksheet in Google Sheets.

## Features

### 1. **Automatic Worksheet Creation**
- When a user registers or logs in for the first time, a personal worksheet is created
- Worksheet name is derived from the username (special characters removed)
- Headers are automatically added to the first row

### 2. **Real-time Quiz Logging**
- Each question attempt is logged immediately after submission
- Works for both MCQ and numerical questions
- Tracks time used per question (120 seconds - remaining time)

### 3. **Data Structure**

Each row in the worksheet contains:
- **Topic**: The subject area (e.g., algebra, geometry)
- **Level**: Difficulty level (easy, medium, hard)
- **Question**: The full text of the question
- **Correct Answer**: The right answer to the question
- **User's Answer**: The answer given by the user
- **Status**: "Correct" or "Wrong"
- **Time Used**: Time in seconds the user took to answer
- **Timestamp**: Current date-time when the attempt was made

## Implementation Details

### Backend (app.py)

1. **Worksheet Creation** (`create_user_worksheet`):
   - Creates new worksheet for each user
   - Adds standardized headers
   - Handles special characters in usernames

2. **Quiz Logging** (`log_quiz_attempt`):
   - Logs each question attempt to user's worksheet
   - Handles both MCQ and numerical questions
   - Includes error handling for API failures

3. **API Endpoint** (`/api/quiz/log-attempt`):
   - Receives quiz attempt data from frontend
   - Validates required fields
   - Calls logging function

### Frontend (quiz.html)

1. **Question Tracking**:
   - Tracks time used per question
   - Logs attempts for both MCQ and numerical questions
   - Handles automatic submission when timer expires

2. **Data Collection**:
   - Extracts topic and level from URL parameters
   - Gets username from localStorage
   - Calculates time used (120 - remaining time)

## Usage

### For New Users:
1. Register or login for the first time
2. Personal worksheet is automatically created with headers
3. Start taking quizzes - all attempts are logged

### For Existing Users:
1. Login with existing credentials
2. If worksheet doesn't exist, it's created automatically
3. Continue taking quizzes - all attempts are logged

## Error Handling

- **Google Sheets Unavailable**: Logs are skipped, quiz continues normally
- **Worksheet Creation Failed**: User can still take quizzes, logs are skipped
- **API Failures**: Quiz continues, failed logs are reported to console

## Configuration

### Required Environment:
- Google Sheets API credentials in `service_account.json`
- Spreadsheet ID configured in `SPREADSHEET_ID`
- Required Python packages: `gspread`, `google-auth`, `bcrypt`

### Dependencies:
```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client bcrypt
```

## Data Flow

1. **User Registration/Login** → Worksheet created with headers
2. **Quiz Start** → Questions loaded, timer starts
3. **Question Answer** → Time calculated, attempt logged to Google Sheets
4. **Quiz Complete** → All attempts logged, results displayed

## Benefits

- **Individual Tracking**: Each user has their own worksheet
- **Real-time Logging**: Attempts logged immediately
- **Comprehensive Data**: Tracks all relevant metrics
- **Error Resilience**: Quiz continues even if logging fails
- **Easy Analysis**: Data structured for easy analysis in Google Sheets 