import os
import sys
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.mcp_tools.database import DatabaseTool
from src.mcp_tools.calendar_tool import CalendarTool
from src.mcp_tools.email_tool import EmailTool
from src.mcp_tools.analytics_tool import AnalyticsTool
from src.mcp_tools.slack_tool import SlackTool

load_dotenv()

class AgentService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file!")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'models/gemini-2.5-flash'
        
        self.db_tool = DatabaseTool()
        self.calendar_tool = CalendarTool()
        self.email_tool = EmailTool()

        self.analytics_tool = AnalyticsTool()
        self.slack_tool = SlackTool()
        
        self.sessions: Dict[str, list] = {}
        self.current_date = datetime.now()
        
        self.system_instruction = f"""You are an intelligent appointment scheduling assistant for a medical clinic.

Available doctors:
- Dr. Ahuja (Cardiology) - Available Mon-Wed 9 AM-5 PM, Fri 9 AM-12 PM
- Dr. Sharma (Pediatrics) - Available Mon-Fri 9 AM-5 PM

Current date: {self.current_date.strftime('%A, %B %d, %Y')}

When handling dates:
- "tomorrow" = {(self.current_date + timedelta(days=1)).strftime('%Y-%m-%d')}
- "today" = {self.current_date.strftime('%Y-%m-%d')}

You have access to these tools:
1. check_availability - Check doctor's available time slots
2. book_appointment - Book an appointment for a patient
3. get_report - Generate analytics reports (patient counts, appointment stats)

For analytics queries like "how many appointments today", "patients yesterday", use the get_report tool with the appropriate query_type:
- "today_appointments" - appointments today
- "tomorrow_appointments" - appointments tomorrow  
- "yesterday_visits" - unique patients yesterday
- "summary_report" - full summary report

Always use function calls for data retrieval. Never output raw JSON to the user.
Always be professional, friendly, and clear."""
        

        self.tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name='check_availability',
                        description='Check doctor availability',
                        parameters={
                            'type': 'object',
                            'properties': {
                                'doctor_name': {'type': 'string'},
                                'date': {'type': 'string'},
                                'time_preference': {'type': 'string'},
                            },
                            'required': ['doctor_name', 'date']
                        },
                    ),
                    types.FunctionDeclaration(
                        name='book_appointment',
                        description='Book an appointment',
                        parameters={
                            'type': 'object',
                            'properties': {
                                'doctor_name': {'type': 'string'},
                                'patient_name': {'type': 'string'},
                                'patient_email': {'type': 'string'},
                                'appointment_datetime': {'type': 'string'},
                            },
                            'required': ['doctor_name', 'patient_name', 'patient_email', 'appointment_datetime']
                        },
                    ),
                    types.FunctionDeclaration(
                        name='get_report',
                        description='Generate analytics reports such as appointment counts, patient stats, and summary reports',
                        parameters={
                            'type': 'object',
                            'properties': {
                                'query_type': {
                                    'type': 'string',
                                    'description': 'Type of report: today_appointments, tomorrow_appointments, yesterday_visits, or summary_report'
                                },
                                'doctor_name': {
                                    'type': 'string',
                                    'description': 'Optional: filter by doctor name'
                                },
                            },
                            'required': ['query_type']
                        },
                    ),
                ]
            )
        ]
    
    def get_session_history(self, session_id: str) -> list:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]
    
    def process_function_call(self, function_name: str, args: dict) -> dict:
            try:
                if function_name == "check_availability":
                    return self.db_tool.check_availability(
                        doctor_name=args.get("doctor_name"),
                        date=args.get("date"),
                        time_preference=args.get("time_preference")
                    )
            
                elif function_name == "book_appointment":
                    result = self.db_tool.book_appointment(
                        doctor_name=args.get("doctor_name"),
                        patient_name=args.get("patient_name"),
                        patient_email=args.get("patient_email"),
                        appointment_datetime=args.get("appointment_datetime")
                    )
                
                    if result.get("success"):
                        self.calendar_tool.create_event(
                            doctor_email=result["doctor_email"],
                            patient_name=result["patient"],
                            patient_email=result["patient_email"],
                            start_time_iso=result["time"]
                     )
                    
                        self.email_tool.send_confirmation(
                            to_email=result["patient_email"],
                            patient_name=result["patient"],
                            doctor_name=result["doctor"],
                            appointment_time=result["formatted_time"]
                        )
                
                    return result
            
                elif function_name == "get_report":
                    query_type = args.get("query_type", "summary_report")
                    doctor_name = args.get("doctor_name")

                    if query_type == "today_appointments":
                        result = self.analytics_tool.get_today_appointments(doctor_name)
                    elif query_type == "tomorrow_appointments":
                        result = self.analytics_tool.get_tomorrow_appointments(doctor_name)
                    elif query_type == "yesterday_visits":
                        result = self.analytics_tool.get_yesterday_visits()
                    elif query_type == "summary_report":
                        report_text = self.analytics_tool.generate_summary_report(doctor_name)

                         # Send to Slack
                        self.slack_tool.send_report(
                            report_title="Doctor Summary Report",
                            report_content=report_text
                        )
                
                        result = {
                            "report": report_text,
                            "sent_to_slack": self.slack_tool.enabled
                        }
                    else:
                        result = {"error": f"Unknown query type: {query_type}"}
            
                    return result
            
                else:
                    return {"error": f"Unknown function: {function_name}"}
        
            except Exception as e:
                return {"error": str(e)}
        
    
    
    
    def chat(self, message: str, session_id: str) -> dict:
        conversation_history = self.get_session_history(session_id)
        
        conversation_history.append(
            types.Content(role='user', parts=[types.Part(text=message)])
        )
        
        appointment_id = None
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=conversation_history,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        tools=self.tools,
                        temperature=0.7,
                    )
                )
                
                conversation_history.append(
                    types.Content(
                        role='model',
                        parts=response.candidates[0].content.parts
                    )
                )
                
                has_function_call = False
                function_responses = []
                
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        has_function_call = True
                        function_name = part.function_call.name
                        function_args = dict(part.function_call.args)
                        
                        result = self.process_function_call(function_name, function_args)
                        
                        if function_name == "book_appointment" and result.get("success"):
                            appointment_id = result.get("appointment_id")
                        
                        function_responses.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=function_name,
                                    response={'result': result}
                                )
                            )
                        )
                
                if has_function_call:
                    conversation_history.append(
                        types.Content(role='user', parts=function_responses)
                    )
                    continue
                else:
                    return {
                        "response": response.text,
                        "appointment_id": appointment_id
                    }
                    
            except Exception as e:
                return {
                    "response": f"I apologize, but I encountered an error: {str(e)}",
                    "appointment_id": None
                }
        
        return {
            "response": "I apologize, but I reached the maximum number of tool calls.",
            "appointment_id": None
        }
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

agent_service = AgentService()