# 🎓 Live Class Monitoring System (Real-Time Focus Control)

A real-time classroom focus monitoring system built using Frappe Framework that ensures students remain inside the application during live sessions.

If a student leaves the app during Focus Mode, the system instantly detects it, updates attendance status, and notifies the teacher dashboard in real-time.

---

## 🚀 Core Features

- ✅ Teacher creates and starts live focus session
- ✅ Automatic Attendance record creation
- ✅ Student session joining validation
- ✅ Real-time monitoring using Frappe Realtime
- ✅ Instant alert when student leaves the app
- ✅ Dynamic teacher dashboard with live updates
- ✅ Attendance status tracking (Active / Idle / Left App / Absent)
- ✅ Session ending & final attendance freeze
- ✅ Historical session reports
- ✅ Live class integration (video/audio ready)
- ✅ Production-level event handling

---

## 🛠 Tech Stack

Backend:
- Python
- Frappe Framework
- Frappe Realtime (Socket.IO)
- MariaDB / MySQL

Frontend:
- JavaScript
- Custom Frappe Page (Teacher Dashboard)
- Dynamic UI updates
- Audio alert notifications

Deployment:
- Bench
- Docker (if deployed)

---

## 🧠 System Architecture

1️⃣ Teacher starts a Focus Session  
2️⃣ System automatically creates Attendance records for all students  
3️⃣ Students join session (validated against class)  
4️⃣ Attendance status set to "Active"  
5️⃣ Real-time listener monitors user activity  
6️⃣ If student leaves the app →  
   - Attendance status updated to "Left App"  
   - Alert record created  
   - Teacher dashboard notified instantly  
7️⃣ Teacher sees:
   - Live student list
   - Real-time status updates
   - Alert popup with sound  
8️⃣ When session ends:
   - Session status frozen
   - Final attendance report generated

---

## 📊 Attendance Status Flow

- Active → Student inside app
- Idle → No activity detected
- Left App → App focus lost
- Absent → Did not join session

---

## ⚡ Real-Time Implementation

Used Frappe Realtime to:

- Push instant notifications
- Update teacher dashboard without refresh
- Trigger popup alerts
- Play sound when student leaves

Example concept:

```javascript
frappe.realtime.on("student_left", function(data) {
    showAlert(data.student_name);
});
```

This ensures live monitoring capability.

---

## 🖥 Teacher Dashboard Features

- Live session information
- Student list (Joined & Absent)
- Real-time status updates
- Alerts panel
- Popup notification with sound
- Past session history

Custom Frappe page built for dynamic control.

---

## 🔐 Security & Validation

- Session-based validation
- Student-class matching verification
- Controlled API access
- Role-based permissions

---

## 📈 Scalability Considerations

- Event-driven architecture
- Real-time socket communication
- Modular attendance tracking
- Extendable for analytics

---

## 🔮 Future Enhancements

- AI-based focus detection
- Screen monitoring analytics
- Parent notification system
- Cloud deployment scaling
- Mobile app integration

---

## 👩‍💻 Author

Developed by Dinesh  
Python | Frappe | Real-Time Application Developer  
GitHub: https://github.com/dineshdj87

---

## 💡 Why This Project Is Strong

This project demonstrates:

✔ Real-time event handling  
✔ Full-stack development  
✔ Live monitoring system  
✔ State management  
✔ Dashboard architecture  
✔ Alert system design  
✔ Backend + frontend integration  
✔ Production-level application thinking  
