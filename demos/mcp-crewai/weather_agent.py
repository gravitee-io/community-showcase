from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import MCPServerAdapter
import os
# from langchain_openai import OpenAI

server_params = {
    "url": "http://localhost:8082/weather/mcp",
    "transport": "streamable-http"
}

llm = LLM(
    model="deepseek-ai/deepseek-r1",
    temperature=0.7,
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
    stream=True
)

try:
    with MCPServerAdapter(server_params) as tools:
        # print(f"Available tools from Streamable HTTP MCP server: {[tool.name for tool in tools]}")

        # Find the getWeatherForecast tool
        weather_tool = next((tool for tool in tools if tool.name == "getWeatherForecast"), None)
        if not weather_tool:
            print("getWeatherForecast tool not found on MCP server.")
        else:
            print("Weather tool args:", weather_tool)

            # # Manually call the tool
            # print("Calling weather tool manually...")
            # tool_result = weather_tool.run(
            #     latitude=48.8566,
            #     longitude=2.3522,
            #     current_weather=True
            # )

            # # print("Tool result:", tool_result)
            
            # Create an agent to summarize weather info
            http_agent = Agent(
                role="Weather Forecaster",
                goal="Summarize and present current weather in a friendly format.",
                backstory="An AI agent specialized in interpreting and presenting weather data for any city.",
                tools=[weather_tool], 
                llm=llm,
                verbose=True,
            )

            # Create a task using tool result as input
            http_task = Task(
                description=(
                    # f"The following is current weather data for Paris:\n\n{tool_result}\n\n"
                    "Summarize this in a human-readable format mentioning temperature, wind speed, and general condition."
                    "\nDo not include any thoughts or reasoning in the result, just the answer."
                ),
                expected_output="A friendly summary (4-5 lines) of the weather in Paris. Is it raining? How's the temperature? Should I take an umbrella? A perfect summary should include answers to these questions.",
                agent=http_agent
            )

            # Create and run the crew
            http_crew = Crew(
                agents=[http_agent],
                tasks=[http_task],
                verbose=True,
                process=Process.sequential
            )

            result = http_crew.kickoff()

except Exception as e:
    import traceback
    print("❌ An error occurred:\n")
    traceback.print_exc()