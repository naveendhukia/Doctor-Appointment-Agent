import os
import json
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from mcp_tools.database import DatabaseTool
from mcp_tools.calendar_tool import CalendarTool
from mcp_tools.email_tool import EmailTool

load_dotenv()
console = Console()

class AppointmentAgentGemini:
    def __init__(self):
        # Configure Gemini with new SDK
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file!")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'models/gemini-2.5-flash'
        
        # Initialize tools
        console.print("[bold cyan]Initializing tools...[/bold cyan]")
        self.db_tool = DatabaseTool()
        console.print("✅ Database connected")
        
        self.calendar_tool = CalendarTool()
        self.email_tool = EmailTool()
        
        self.current_date = datetime.now()
        self.conversation_history = []
        
        # System instructions
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

Workflow:
1. When user asks about availability, use check_availability tool
2. Present available slots clearly in 12-hour format (e.g., 10:00 AM)
3. When user wants to book, ask for patient name and email if not provided
4. Use book_appointment with exact datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
5. Confirm booking success with all details

Always be professional, friendly, and clear."""

        # Define tools
        self.tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name='check_availability',
                        description='Check a doctor\'s availability for a specific date and return available time slots',
                        parameters={
                            'type': 'object',
                            'properties': {
                                'doctor_name': {
                                    'type': 'string',
                                    'description': 'Name of the doctor (e.g., Dr. Ahuja, Dr. Sharma)'
                                },
                                'date': {
                                    'type': 'string',
                                    'description': 'Date in YYYY-MM-DD format'
                                },
                                'time_preference': {
                                    'type': 'string',
                                    'description': 'Optional: morning, afternoon, or evening'
                                },
                            },
                            'required': ['doctor_name', 'date']
                        },
                    ),
                    types.FunctionDeclaration(
                        name='book_appointment',
                        description='Book an appointment for a patient with a doctor at a specific time',
                        parameters={
                            'type': 'object',
                            'properties': {
                                'doctor_name': {
                                    'type': 'string',
                                    'description': 'Name of the doctor'
                                },
                                'patient_name': {
                                    'type': 'string',
                                    'description': 'Full name of the patient'
                                },
                                'patient_email': {
                                    'type': 'string',
                                    'description': 'Email address of the patient'
                                },
                                'appointment_datetime': {
                                    'type': 'string',
                                    'description': 'Appointment datetime in ISO format: YYYY-MM-DDTHH:MM:SS (e.g., 2026-02-17T10:00:00)'
                                },
                            },
                            'required': ['doctor_name', 'patient_name', 'patient_email', 'appointment_datetime']
                        },
                    ),
                ]
            )
        ]
    
    def process_function_call(self, function_name: str, args: dict) -> dict:
        """Execute tool calls and return results"""
        try:
            if function_name == "check_availability":
                result = self.db_tool.check_availability(
                    doctor_name=args.get("doctor_name"),
                    date=args.get("date"),
                    time_preference=args.get("time_preference")
                )
                return result
            
            elif function_name == "book_appointment":
                result = self.db_tool.book_appointment(
                    doctor_name=args.get("doctor_name"),
                    patient_name=args.get("patient_name"),
                    patient_email=args.get("patient_email"),
                    appointment_datetime=args.get("appointment_datetime")
                )
                
                if result.get("success"):
                    # Create calendar event
                    calendar_event_id = self.calendar_tool.create_event(
                        doctor_email=result["doctor_email"],
                        patient_name=result["patient"],
                        patient_email=result["patient_email"],
                        start_time_iso=result["time"]
                    )
                    
                    # Send confirmation email
                    email_sent = self.email_tool.send_confirmation(
                        to_email=result["patient_email"],
                        patient_name=result["patient"],
                        doctor_name=result["doctor"],
                        appointment_time=result["formatted_time"]
                    )
                    
                    result["calendar_event_created"] = calendar_event_id is not None
                    result["email_sent"] = email_sent
                
                return result
            
            else:
                return {"error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def chat_message(self, user_message: str) -> str:
        """Send message to Gemini and handle function calls"""
        
        # Add user message to history
        self.conversation_history.append(
            types.Content(
                role='user',
                parts=[types.Part(text=user_message)]
            )
        )
        
        # Call Gemini with function calling
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=self.conversation_history,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        tools=self.tools,
                        temperature=0.7,
                    )
                )
                
                # Add response to history
                self.conversation_history.append(
                    types.Content(
                        role='model',
                        parts=response.candidates[0].content.parts
                    )
                )
                
                # Check for function calls
                has_function_call = False
                function_responses = []
                
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        has_function_call = True
                        function_name = part.function_call.name
                        function_args = dict(part.function_call.args)
                        
                        console.print(f"[dim]🔧 Calling function: {function_name}[/dim]")
                        
                        # Execute function
                        result = self.process_function_call(function_name, function_args)
                        
                        console.print(f"[dim]✓ Function completed[/dim]\n")
                        
                        # Prepare function response
                        function_responses.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=function_name,
                                    response={'result': result}
                                )
                            )
                        )
                
                if has_function_call:
                    # Add function responses to history
                    self.conversation_history.append(
                        types.Content(
                            role='user',
                            parts=function_responses
                        )
                    )
                    # Continue loop to get final response
                    continue
                else:
                    # Got final text response
                    return response.text
                    
            except Exception as e:
                console.print(f"[bold red]Error in API call:[/bold red] {e}")
                return "I apologize, but I encountered an issue. Could you please rephrase your request?"
        
        return "I apologize, but I reached the maximum number of tool calls. Please try again."
    
    def run(self):
        """Run the interactive agent"""
        console.print(Panel.fit(
            "[bold blue]🏥 Doctor Appointment Scheduling Agent (Gemini)[/bold blue]\n"
            "I can help you schedule appointments with our doctors.\n\n"
            "Try saying:\n"
            "  • 'Check Dr. Ahuja's availability tomorrow morning'\n"
            "  • 'Book appointment with Dr. Sharma on Friday at 2 PM'\n\n"
            "Type 'quit' or 'exit' to end the conversation.",
            border_style="blue"
        ))
        
        while True:
            try:
                user_input = console.input("\n[bold green]You:[/bold green] ")
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    console.print("\n[bold blue]Agent:[/bold blue] Goodbye! Have a great day! 👋")
                    break
                
                if not user_input.strip():
                    continue
                
                # Get agent response
                response = self.chat_message(user_input)
                
                # Display response
                console.print(f"\n[bold blue]Agent:[/bold blue] {response}")
                
            except KeyboardInterrupt:
                console.print("\n\n[bold blue]Agent:[/bold blue] Goodbye! Have a great day! 👋")
                break
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {e}")
                import traceback
                console.print(traceback.format_exc())
        
        # Cleanup
        self.db_tool.close()


def main():
    agent = AppointmentAgentGemini()
    agent.run()


if __name__ == "__main__":
    main()