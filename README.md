🏨 Hotel Management Software

A Python-based hotel management system that helps manage hotel reservations, guest records, and room availability efficiently.
This application uses MySQL for persistent data storage and provides a simple, modular interface for managing hotel operations.

✨ Features

📌 Add, update, and delete guest records

📌 Book and cancel reservations

📌 Manage room availability and assignments

📌 Persist data with MySQL

📌 Modular Python code for easy extension and maintenance

📂 Project Structure
hotel-management-software/
├── he.py               # Main application script
├── README.md           # Documentation
├── requirements.txt    # Python dependencies (if any)


🖼️ UI Screenshot Placeholders

Replace these placeholders with your actual screenshots (save images to a screenshots/ folder):

Dashboard / Home Screen
<img width="744" height="496" alt="image" src="https://github.com/user-attachments/assets/8e21e233-f19c-4d3b-b806-d24e45643212" />


Reservation Management
<img width="727" height="916" alt="image" src="https://github.com/user-attachments/assets/12b9b972-146f-4879-97c2-2494acbaf549" />


Amenities
 <img width="284" height="553" alt="image" src="https://github.com/user-attachments/assets/c6fe24de-5cf6-4007-9312-ef8b6bbdb749" />

Final Billing

<img width="284" height="590" alt="image" src="https://github.com/user-attachments/assets/64156585-4249-4d20-8cd1-87356ba71198" />


⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/Jitesh-vador/hotel-management-software.git
cd hotel-management-software

2. (Optional) Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Set up MySQL database

Install and start MySQL.

Create a database (example name hotel_db):

CREATE DATABASE hotel_db;


Update your database credentials in the script or config file, for example:

DB_HOST = "localhost"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "hotel_db"

5. Initialize the database schema

Initialize using MySql Python Connector 

6. Run the application
python he.py

🚀 Usage

Start the app:

python he.py


Use the on-screen menu or prompts to:

Add a new guest record

Create, view, update, or cancel reservations

Check room availability and assignments

Update guest or booking information

🛠️ Tech Stack

Language: Python

Database: MySQL

Common Libraries (add what you used): mysql-connector-python / tkinter
🔮 Future Enhancements

 Add user roles (Admin, Receptionist, Manager)

 Add reporting: occupancy, revenue, guest history

 Implement CSV/Excel import-export for bookings and guests

 Add authentication and role-based access control

🤝 Contributing

Contributions are welcome!

Fork the repository

Create a feature branch: git checkout -b feature/your-feature

Commit your changes: git commit -m "Add feature"

Push: git push origin feature/your-feature

Open a Pull Request and describe your changes


🙌 Acknowledgments

Thanks to the open-source Python community and MySQL for the tools that make projects like this possible.
