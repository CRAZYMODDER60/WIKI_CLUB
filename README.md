# 📅 Telegram Scheduler Assistant Bot

A smart Telegram bot that helps users manage schedules and receive automated reminders with role-based access control and timezone-safe scheduling.

---

## 🚀 Features

- Interactive schedule creation wizard
- Quick command-based scheduling
- Automated reminder notifications
- Role-based access control system
- Dashboard-based navigation
- Timezone-aware scheduling
- Persistent storage using SQLite

---

## 🧠 Project Overview

The Telegram Scheduler Assistant Bot is designed to work as a productivity assistant directly inside Telegram. It allows authorized users to create event schedules and automatically sends reminder notifications before event start time.

The system is built using an event-driven and modular architecture, ensuring scalability, maintainability, and security.

---

## 🛠 Tech Stack

- Python – Core programming language  
- python-telegram-bot – Telegram bot framework  
- SQLite – Lightweight persistent database  
- AsyncIO – Asynchronous task handling  
- JobQueue – Reminder scheduling engine  
- ZoneInfo – Timezone management  

---

## 📂 Project Structure

telegram-scheduler-bot/
│
├── main.py          # Core bot logic and command handlers  
├── config.py        # Bot configuration and environment variables  
├── roles.json       # Stores admin and member role data  
├── schedule.db      # SQLite database storing schedules  
├── requirements.txt # Project dependencies  
└── README.md        # Project documentation  

---

## ⚙️ Setup & Installation

### 1. Clone Repository

git clone https://github.com/CRAZYMODDER60/WIKI_CLUB.git
cd WIKI_CLUB  

---

### 2. Install Dependencies

pip install -r requirements.txt  

---

### 3. Configure Bot

Set environment variables before running the bot:

export BOT_TOKEN="YOUR_BOT_TOKEN"  
export OWNER_ID="YOUR_TELEGRAM_USER_ID"  

(For Windows PowerShell)

setx BOT_TOKEN "YOUR_BOT_TOKEN"  
setx OWNER_ID "YOUR_TELEGRAM_USER_ID"  

---

### 4. Run the Bot

python main.py  

---

## 📘 Bot Commands

/start  
Opens dashboard menu  

/help  
Displays command help guide  

/viewschedule  
Shows all saved schedules  

/addadmin USER_ID  
Adds admin user (Owner only)  

/addmember USER_ID  
Adds member user (Admin and Owner)  

---

## 🧩 Interactive Scheduling Flow

1. User enters event title  
2. User enters event date  
3. User enters event time  
4. User selects target audience  
5. User confirms schedule  

---

## ⏰ Reminder Logic

The bot dynamically schedules reminders based on time difference between current time and event time.

Reminders are sent:

- 1 hour before event
- 30 minutes before event
- 10 minutes before event
- 1 minute before event
- At event start

---

## 🔐 Role-Based Access Control

Owner  
- Full system control  
- Can add admins and members  

Admin  
- Can add members  
- Can create schedules  

Member  
- Can receive event notifications  

Guest  
- No access to bot features  

---

## 💾 Database Design

The bot uses SQLite to store event schedules.

Schedules table stores:

- Event Title  
- Event DateTime  
- Target Role  
- Creator User ID  

---

## 🧪 Testing & Validation

- Functional command testing  
- Reminder accuracy testing  
- Role permission validation  
- Date and time input validation  
- Edge case scheduling verification  

---

## 🔮 Future Improvements

- Cloud database integration  
- Multi-timezone support  
- Natural language schedule input  
- Web dashboard interface  
- Event analytics and statistics  

---

## 👨‍💻 Author

Aryan Patel  
Developer and Automation Enthusiast

