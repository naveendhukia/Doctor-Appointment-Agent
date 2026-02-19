import os
import json
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from mcp_tools.database import DatabaseTool
from mcp_tools.calendar_tool import CalendarTool
from mcp_tools.email_tool import EmailTool

load_dotenv()
console = Console()

class AppointmentAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.conversation_history = []
        
        # Initialize tools
        console.print("[bold cyan]Initializing tools...[/bold cyan]")
        self.db_tool = DatabaseTool()
        console.print("✅ Database connected")
        
        self.calendar_tool = CalendarTool()
        self.email_tool = EmailTool()
        
        # Get current date for relative date parsing
        self.current_date = datetime.now()
        
        # System prompt
        self.system_prompt = f"""You are an intelligent appointment scheduling assistant for a medical clinic.

Available doctors:
- Dr. Ahuja (Cardiology) - Available Mon-Wed 9 AM-5 PM, Fri 9 AM-12 PM
- Dr. Sharma (Pediatrics) - Available Mon-Fri 9 AM-5 PM

Current date and time: {self.current_date.strftime('%A, %B %d, %Y')}

When handling date references:
- "tomorrow" = {(self.current_date + timedelta(days=1)).strftime('%Y-%m-%d')}
- "today" = {self.current_date.strftime('%Y-%m-%d')}
- Calculate "next Friday", "next Monday" etc. based on current date

Workflow for booking:
1. Parse user's request and identify: doctor, date, time preference
2. Use check_availability to see available slots
3. Present slots clearly to user
4. When user selects a slot, ask for patient name and email if not provided
5. Use book_appointment with complete details including the exact datetime
6. Confirm success with appointment details

Always be professional, friendly, and clear. Ask for missing information one question at a time.
Format times in 12-hour format (e.g., 2:00 PM) when talking to users.
"""
        
        # Define tools for Claude
        self.tools = [
            {
                "name": "check_availability",
                "description": "Check a doctor's availability for a specific date. Returns available time slots in 30-minute intervals.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor (e.g., 'Dr. Ahuja', 'Dr. Sharma')"
                        },
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format"
                        },
                        "time_preference": {
                            "type": "string",
                            "enum": ["morning", "afternoon", "evening", "any"],
                            "description": "Optional time preference. morning=9AM-12PM, afternoon=12PM-5PM, evening=5PM+"
                        }
                    },
                    "required": ["doctor_name", "date"]
                }
            },
            {
                "name": "book_appointment",
                "description": "Book an appointment for a patient. All fields are required. Returns confirmation with appointment ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor"
                        },
                        "patient_name": {
                            "type": "string",
                            "description": "Full name of the patient"
                        },
                        "patient_email": {
                            "type": "string",
                            "description": "Email address of the patient (must be valid email format)"
                        },
                        "appointment_datetime": {
                            "type": "string",
                            "description": "Appointment date and time in ISO format: YYYY-MM-DDTHH:MM:SS (e.g., 2026-02-20T15:00:00)"
                        }
                    },
                    "required": ["doctor_name", "patient_name", "patient_email", "appointment_datetime"]
                }
            }
        ]
    
    def process_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Execute tool calls and return results"""
        try:
            if tool_name == "check_availability":
                result = self.db_tool.check_availability(
                    doctor_name=tool_input["doctor_name"],
                    date=tool_input["date"],
                    time_preference=tool_input.get("time_preference")
                )
                return json.dumps(result, indent=2)
            
            elif tool_name == "book_appointment":
                # Book in database
                result = self.db_tool.book_appointment(
                    doctor_name=tool_input["doctor_name"],
                    patient_name=tool_input["patient_name"],
                    patient_email=tool_input["patient_email"],
                    appointment_datetime=tool_input["appointment_datetime"]
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
                
                return json.dumps(result, indent=2)
            
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def chat(self, user_message: str) -> str:
        """Process a user message and return the agent's response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Keep calling Claude until we get a final text response
        while True:
            # Call Claude API
            response = self.client.messages.create(
                model="gpt-5-mini",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.conversation_history
            )
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Build assistant message with text and tool uses
                assistant_message = {"role": "assistant", "content": []}
                
                for block in response.content:
                    if block.type == "text":
                        assistant_message["content"].append({
                            "type": "text",
                            "text": block.text
                        })
                    elif block.type == "tool_use":
                        assistant_message["content"].append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                        
                        # Execute the tool
                        console.print(f"[dim]🔧 Using tool: {block.name}[/dim]")
                        tool_result = self.process_tool_call(block.name, block.input)
                        console.print(f"[dim]✓ Tool completed[/dim]\n")
                
                # Add assistant message to history
                self.conversation_history.append(assistant_message)
                
                # Add tool results to history
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_result_content = self.process_tool_call(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result_content
                        })
                
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continue the loop to get Claude's next response
                continue
            
            else:
                # We got a final text response
                final_text = ""
                assistant_content = []
                
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text
                        assistant_content.append({
                            "type": "text",
                            "text": block.text
                        })
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                
                return final_text
    
    def run(self):
        """Run the interactive agent"""
        console.print(Panel.fit(
            "[bold blue]🏥 Doctor Appointment Scheduling Agent[/bold blue]\n"
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
                response = self.chat(user_input)
                
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
    agent = AppointmentAgent()
    agent.run()


if __name__ == "__main__":
    main()