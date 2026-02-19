import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Dict, List

class AnalyticsTool:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "appointments"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD", "")
        )
    
    def get_appointments_count(self, date: str, doctor_name: str = None) -> Dict:
        """Get count of appointments for a specific date"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            if doctor_name:
                # Get doctor ID
                cur.execute("SELECT id FROM doctors WHERE name ILIKE %s", (f"%{doctor_name}%",))
                doctor = cur.fetchone()
                if not doctor:
                    return {"error": f"Doctor {doctor_name} not found"}
                
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM appointments
                    WHERE DATE(appointment_time) = %s
                    AND doctor_id = %s
                    AND status != 'cancelled'
                """, (date, doctor['id']))
            else:
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM appointments
                    WHERE DATE(appointment_time) = %s
                    AND status != 'cancelled'
                """, (date,))
            
            result = cur.fetchone()
            return {
                "date": date,
                "doctor": doctor_name or "All doctors",
                "count": result['count']
            }
    
    def get_appointments_by_date_range(self, start_date: str, end_date: str, 
                                      doctor_name: str = None) -> Dict:
        """Get appointments in a date range"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            if doctor_name:
                cur.execute("SELECT id FROM doctors WHERE name ILIKE %s", (f"%{doctor_name}%",))
                doctor = cur.fetchone()
                if not doctor:
                    return {"error": f"Doctor {doctor_name} not found"}
                
                cur.execute("""
                    SELECT 
                        DATE(appointment_time) as date,
                        COUNT(*) as count
                    FROM appointments
                    WHERE DATE(appointment_time) BETWEEN %s AND %s
                    AND doctor_id = %s
                    AND status != 'cancelled'
                    GROUP BY DATE(appointment_time)
                    ORDER BY date
                """, (start_date, end_date, doctor['id']))
            else:
                cur.execute("""
                    SELECT 
                        DATE(appointment_time) as date,
                        COUNT(*) as count
                    FROM appointments
                    WHERE DATE(appointment_time) BETWEEN %s AND %s
                    AND status != 'cancelled'
                    GROUP BY DATE(appointment_time)
                    ORDER BY date
                """, (start_date, end_date))
            
            results = [dict(row) for row in cur.fetchall()]
            total = sum(r['count'] for r in results)
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "doctor": doctor_name or "All doctors",
                "total_appointments": total,
                "daily_breakdown": results
            }
    
    def get_patient_visits(self, date: str) -> Dict:
        """Get unique patient count for a date"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT COUNT(DISTINCT patient_email) as unique_patients
                FROM appointments
                WHERE DATE(appointment_time) = %s
                AND status != 'cancelled'
            """, (date,))
            
            result = cur.fetchone()
            return {
                "date": date,
                "unique_patients": result['unique_patients']
            }
    
    def get_today_appointments(self, doctor_name: str = None) -> Dict:
        """Get today's appointments"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_appointments_count(today, doctor_name)
    
    def get_tomorrow_appointments(self, doctor_name: str = None) -> Dict:
        """Get tomorrow's appointments"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        return self.get_appointments_count(tomorrow, doctor_name)
    
    def get_yesterday_visits(self) -> Dict:
        """Get yesterday's unique patient count"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        return self.get_patient_visits(yesterday)
    
    def generate_summary_report(self, doctor_name: str = None) -> str:
        """Generate a comprehensive summary report"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Get data
        yesterday_visits = self.get_patient_visits(yesterday)
        today_appts = self.get_appointments_count(today, doctor_name)
        tomorrow_appts = self.get_appointments_count(tomorrow, doctor_name)
        
        # Format report
        doctor_label = f"Dr. {doctor_name}" if doctor_name else "All Doctors"
        
        report = f"""*📊 Appointment Summary Report*
*Doctor:* {doctor_label}
*Generated:* {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

*📅 Yesterday ({yesterday})*
- Unique patients visited: *{yesterday_visits['unique_patients']}*

*📅 Today ({today})*
- Scheduled appointments: *{today_appts['count']}*

*📅 Tomorrow ({tomorrow})*
- Scheduled appointments: *{tomorrow_appts['count']}*

_Report generated automatically by Doctor Report Bot_
"""
        
        return report
    
    def close(self):
        self.conn.close()