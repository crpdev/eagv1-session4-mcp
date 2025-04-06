import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 5
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

async def main():
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to Math MCP server...")
        math_server_params = StdioServerParameters(
            command="python",
            args=["math_server.py"]
        )

        # Create a Paint MCP server connection
        print("Establishing connection to Paint MCP server...")
        paint_server_params = StdioServerParameters(
            command="python",
            args=["paint_server.py"]
        )

        # Create a Gmail MCP server connection
        print("Establishing connection to Gmail MCP server...")
        gmail_server_params = StdioServerParameters(
            command="python",
            args=["gmail_server.py"]
        )

        async with stdio_client(math_server_params) as (math_read, math_write), \
            stdio_client(paint_server_params) as (paint_read, paint_write), \
            stdio_client(gmail_server_params) as (gmail_read, gmail_write):

            print("Connection established, creating session...")
            async with ClientSession(math_read, math_write) as math_session, \
                ClientSession(paint_read, paint_write) as paint_session, \
                ClientSession(gmail_read, gmail_write) as gmail_session:
                
                print("Session created, initializing...")
                await math_session.initialize()
                await paint_session.initialize()
                await gmail_session.initialize()
                
                # Get available tools
                print("Requesting tool list...")
                math_tools_result = await math_session.list_tools()
                paint_tools_result = await paint_session.list_tools()
                gmail_tools_result = await gmail_session.list_tools()
                
                math_tools = math_tools_result.tools
                paint_tools = paint_tools_result.tools
                gmail_tools = gmail_tools_result.tools

                print(f"Successfully retrieved {len(math_tools)} Math tools, {len(paint_tools)} Paint tools and {len(gmail_tools)} Gmail tools")

                # Create system prompt with available tools
                print("Creating system prompt...")
                
                tools_description = []
                
                # Add Math tools
                tools_description.append("MATH TOOLS:")
                for i, tool in enumerate(math_tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        print(f"Added description for Math tool: {tool_desc}")
                    except Exception as e:
                        print(f"Error processing Math tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                # Add Paint tools
                tools_description.append("\nPAINT TOOLS:")
                for i, tool in enumerate(paint_tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        print(f"Added description for Paint tool: {tool_desc}")
                    except Exception as e:
                        print(f"Error processing Paint tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                # Add Gmail tools
                tools_description.append("\nGMAIL TOOLS:")
                for i, tool in enumerate(gmail_tools):
                    try:
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            
                            if 'properties' in params:
                                param_details = []
                                for param_name, param_info in params['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            print(f"Added description for Gmail tool: {tool_desc}")
                    except Exception as e:
                        print(f"Error processing Gmail tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                    
                    tools_description = "\n".join(tools_description)
                    print("Successfully created tools description")
                
                print("Created system prompt...")
                
                system_prompt = f"""You are a math agent solving problems in iterations. You have access to various mathematical tools.

Available tools:
{tools_description}

Respond with EXACTLY ONE of these formats:
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   The parameters must match the required input types for the function.
   
   Example: For add(a: integer, b: integer), use:
   FUNCTION_CALL: add|5|3

   Example: To open paint open_paint(), use:
   FUNCTION_CALL: open_paint|

   Example: To draw a rectangle draw_rectangle(x: integer, y: integer, x1: integer, y1: integer), use:
   FUNCTION_CALL: draw_rectangle|650|420|1050|820   

   Example: To add text in paint add_text(text: str), use:
   FUNCTION_CALL: add_text|Final answer is 489  

   Example: To send an email send_email(to: str, subject: str, body: str), use:
   FUNCTION_CALL: send_email|user@example.com|Math Result - Iteration 1|The result of adding 45 and 444 is 489     

2. For final answers:
   FINAL_ANSWER: [number]

DO NOT include multiple responses. Give ONE response at a time.
Make sure to provide parameters in the correct order as specified in the function signature."""

                query = """Add 45 and 444. Then draw a rectangle in Paint and add the result inside it. Finally, send an email with the results."""
                print("Starting iteration loop...")
                
                # Use global iteration variables
                global iteration, last_response
                
                while iteration < max_iterations:
                    print(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break

                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        
                        print(f"Calling function {func_name} with params {params}")
                        try:
                            # Determine which session to use based on the function name
                            if func_name in [tool.name for tool in math_tools]:
                                print("func_name is present in math_tools")
                                # Find the specific tool with the matching name
                                matching_tool = None
                                for tool in math_tools:
                                    if tool.name == func_name:
                                        matching_tool = tool
                                        break
                                
                                if matching_tool is None:
                                    print(f"Error: Could not find tool with name {func_name}")
                                    continue
                                
                                # Prepare arguments according to the tool's input schema
                                arguments = {}
                                for (param_name, param_info), value in zip(matching_tool.inputSchema['properties'].items(), params):
                                    # Convert the value to the correct type based on the schema
                                    print(f"{param_name}: {param_info}")
                                    if param_info['type'] == 'integer':
                                        arguments[param_name] = int(value)
                                    elif param_info['type'] == 'number':
                                        arguments[param_name] = float(value)
                                    elif param_info['type'] == 'array':
                                        # Handle array types if needed
                                        arguments[param_name] = eval(value)
                                    else:
                                        arguments[param_name] = value
                                print(f"Executing MCP tool call with arguments: {arguments}")
                                result = await math_session.call_tool(func_name, arguments=arguments)
                            elif func_name in [tool.name for tool in paint_tools]:
                                print("func_name is present in paint_tools")
                                # Find the specific tool with the matching name
                                matching_tool = None
                                for tool in paint_tools:
                                    if tool.name == func_name:
                                        matching_tool = tool
                                        break
                                
                                if matching_tool is None:
                                    print(f"Error: Could not find tool with name {func_name}")
                                    continue
                                
                                # Prepare arguments according to the tool's input schema
                                arguments = {}
                                if params and params[0]:  # Only process params if they exist and are not empty
                                    for (param_name, param_info), value in zip(matching_tool.inputSchema['properties'].items(), params):
                                        # Convert the value to the correct type based on the schema
                                        print(f"{param_name}: {param_info}")
                                        if param_info['type'] == 'integer':
                                            arguments[param_name] = int(value)
                                        elif param_info['type'] == 'number':
                                            arguments[param_name] = float(value)
                                        elif param_info['type'] == 'array':
                                            # Handle array types if needed
                                            arguments[param_name] = eval(value)
                                        else:
                                            arguments[param_name] = value
                                
                                print(f"Executing MCP tool call with arguments: {arguments}")
                                result = await paint_session.call_tool(func_name, arguments=arguments)
                            elif func_name in [tool.name for tool in gmail_tools]:
                                print("func_name is present in gmail_tools")
                                # Find the specific tool with the matching name
                                matching_tool = None
                                for tool in gmail_tools:
                                    if tool.name == func_name:
                                        matching_tool = tool
                                        break
                                
                                if matching_tool is None:
                                    print(f"Error: Could not find tool with name {func_name}")
                                    continue
                                
                                # Prepare arguments according to the tool's input schema
                                arguments = {}
                                if params and params[0]:  # Only process params if they exist and are not empty
                                    for (param_name, param_info), value in zip(matching_tool.inputSchema['properties'].items(), params):
                                        # Convert the value to the correct type based on the schema
                                        print(f"{param_name}: {param_info}")
                                        if param_info['type'] == 'integer':
                                            arguments[param_name] = int(value)
                                        elif param_info['type'] == 'number':
                                            arguments[param_name] = float(value)
                                        elif param_info['type'] == 'array':
                                            # Handle array types if needed
                                            arguments[param_name] = eval(value)
                                        else:
                                            arguments[param_name] = value
                                
                                print(f"Executing MCP tool call with arguments: {arguments}")
                                result = await gmail_session.call_tool(func_name, arguments=arguments)
                                if func_name == "send_email":
                                    email_sent = True
                            else:
                                print(f"Unknown function: {func_name}")
                                continue
                            
                            print(f"Function call result: {result}")
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                if isinstance(result.content[0], str):
                                    iteration_result = result.content[0]
                                else:
                                    iteration_result = result.content[0].text
                            else:
                                iteration_result = str(result)
                                
                            print(f"Full result received: {iteration_result}")
                            
                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                f"and the function returned {iteration_result}."
                            )
                            last_response = iteration_result

                        except Exception as e:
                            print(f"Error calling tool: {e}")
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break

                    elif response_text.startswith("FINAL_ANSWER:"):
                        print("\n=== Agent Execution Complete ===")

                    iteration += 1

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
    
    
