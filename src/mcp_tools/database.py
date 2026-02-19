import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class DatabaseTool:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "appointments"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )
    
    def get_doctor_by_name(self, doctor_name: str) -> Optional[Dict]:
        """Find doctor by name"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM doctors WHERE name ILIKE %s",
                (f"%{doctor_name}%",)
            )
            result = cur.fetchone()
            return dict(result) if result else None
    
    def check_availability(self, doctor_name: str, date: str, time_preference: str = None) -> Dict:
        """Check doctor's availability for a specific date"""
        doctor = self.get_doctor_by_name(doctor_name)
        if not doctor:
            return {"error": f"Doctor {doctor_name} not found"}
        
        target_date = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = target_date.weekday()
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get doctor's working hours
            cur.execute("""
                SELECT start_time, end_time 
                FROM doctor_availability 
                WHERE doctor_id = %s AND day_of_week = %s
            """, (doctor['id'], day_of_week))
            
            availability = cur.fetchone()
            if not availability:
                return {
                    "available": False,
                    "message": f"Dr. {doctor['name']} is not available on {target_date.strftime('%A')}"
                }
            
            # Get existing appointments
            cur.execute("""
                SELECT appointment_time, duration_minutes 
                FROM appointments 
                WHERE doctor_id = %s 
                AND DATE(appointment_time) = %s 
                AND status != 'cancelled'
                ORDER BY appointment_time
            """, (doctor['id'], date))
            
            booked_slots = [dict(row) for row in cur.fetchall()]
        
        # Generate available time slots
        start_hour = availability['start_time'].hour
        end_hour = availability['end_time'].hour
        
        if time_preference:
            time_pref = time_preference.lower()
            if time_pref == 'morning':
                end_hour = min(end_hour, 12)
            elif time_pref == 'afternoon':
                start_hour = max(start_hour, 12)
                end_hour = min(end_hour, 17)
            elif time_pref == 'evening':
                start_hour = max(start_hour, 17)
        
        available_slots = []
        current_time = target_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = target_date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=30)
            
            # Check conflicts
            is_available = True
            for booking in booked_slots:
                booking_start = booking['appointment_time']
                booking_end = booking_start + timedelta(minutes=booking['duration_minutes'])
                
                if not (slot_end <= booking_start or current_time >= booking_end):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=30)
        
        return {
            "available": len(available_slots) > 0,
            "doctor": doctor['name'],
            "date": target_date.strftime('%A, %B %d, %Y'),
            "slots": available_slots,
            "doctor_id": doctor['id']
        }
    
    def book_appointment(self, doctor_name: str, patient_name: str, 
                        patient_email: str, appointment_datetime: str) -> Dict:
        """Book an appointment"""
        doctor = self.get_doctor_by_name(doctor_name)
        if not doctor:
            return {"error": f"Doctor {doctor_name} not found"}
        
        appt_time = datetime.fromisoformat(appointment_datetime)
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if slot is available
            cur.execute("""
                SELECT * FROM appointments 
                WHERE doctor_id = %s 
                AND appointment_time = %s 
                AND status != 'cancelled'
            """, (doctor['id'], appt_time))
            
            if cur.fetchone():
                return {"error": "This time slot is already booked"}
            
            # Book the appointment
            cur.execute("""
                INSERT INTO appointments 
                (doctor_id, patient_name, patient_email, appointment_time, duration_minutes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (doctor['id'], patient_name, patient_email, appt_time, 30))
            
            appointment_id = cur.fetchone()['id']
            self.conn.commit()
        
        return {
            "success": True,
            "appointment_id": appointment_id,
            "doctor": doctor['name'],
            "doctor_email": doctor['email'],
            "patient": patient_name,
            "patient_email": patient_email,
            "time": appt_time.isoformat(),
            "formatted_time": appt_time.strftime('%A, %B %d, %Y at %I:%M %p')
        }
    
    def close(self):
        self.conn.close()