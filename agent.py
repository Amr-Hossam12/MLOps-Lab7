from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

# Import your local modules
from state import AgentState
from nodes import supervisor_node, data_loader_node, insight_generator_node, chart_creator_node

# --- GRAPH SETUP ---

# Initialize Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("DataLoader", data_loader_node)
workflow.add_node("InsightGenerator", insight_generator_node)
workflow.add_node("ChartCreator", chart_creator_node)

# Add Edges (Workers always report back to Supervisor)
workflow.add_edge("DataLoader", "Supervisor")
workflow.add_edge("InsightGenerator", "Supervisor")
workflow.add_edge("ChartCreator", "Supervisor")

# Conditional Routing (Supervisor decides next step)
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next_step"],
    {
        "DataLoader": "DataLoader",
        "InsightGenerator": "InsightGenerator",
        "ChartCreator": "ChartCreator",
        "FINISH": END,
    }
)

workflow.add_edge(START, "Supervisor")

# Compile with Memory and Interrupt
checkpointer = MemorySaver()
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["ChartCreator"], # Stop before writing code
)

# --- EXECUTION LOOP ---

if __name__ == "__main__":
    print("--- 🔍 Data Analyst Swarm ---")
    
    # 1. Connectivity Check
    MODEL_NAME = "qwen3:1.7b"
    print(f"[System]: Checking connection to Ollama model '{MODEL_NAME}'...")
    try:
        from langchain_ollama import ChatOllama
        llm_test = ChatOllama(model=MODEL_NAME)
        llm_test.invoke("test")
        print("[System]: Connection successful.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR]: Could not connect to Ollama model '{MODEL_NAME}'.")
        print("1. Make sure Ollama is running.")
        print(f"2. Make sure you have pulled this specific model: 'ollama pull {MODEL_NAME}'")
        exit()

    # 2. User Input
    user_input = input("\nEnter a topic for analysis (e.g., 'Video Game Sales 2024'): ")
    
    # Thread ID is required for MemorySaver to track state
    config = {"configurable": {"thread_id": "analyst_session_01"}}
    current_input = {"messages": [HumanMessage(content=user_input)]}
    
    while True:
        try:
            # Stream the execution
            events = graph.stream(current_input, config=config, stream_mode="values")
            
            for event in events:
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    
                    # --- LIVE LOGGING ---
                    if last_msg.name == "DataLoader":
                         print(f"\n\033[93m[Data Loader]:\033[0m Generated dataset sample.")
                         # Optional: print first few chars
                         # print(event.get('dataset_sample')[:200] + "...")
                    
                    elif last_msg.name == "InsightGenerator":
                        print(f"\n\033[94m[Insight Generator]:\033[0m\n{event.get('analysis_report')}")
                    
                    elif last_msg.name == "ChartCreator":
                        print(f"\033[96m[Chart Creator]:\033[0m Visualization code generated.")

            # Handle Interrupt (Pause before ChartCreator)
            snapshot = graph.get_state(config)
            if snapshot.next:
                print(f"\n---- ⏸️  Paused before node: {snapshot.next} ----")
                print("Review the insights above. Proceed to generate Python Chart Code?")
                approve = input("(yes/no): ")
                
                if approve.lower() == "yes":
                    current_input = None # Resume with existing state
                else:
                    print("Process terminated by user.")
                    break
            else:
                # Finished
                final_state = snapshot.values
                if final_state.get("chart_code"):
                    print(f"\n\033[92m[Final Chart Code]:\033[0m\n{final_state.get('chart_code')}")
                    
                    # Save clean code to file
                    raw_code = final_state.get('chart_code')
                    clean_code = raw_code.replace("```python", "").replace("```", "")
                    
                    filename = "visualize.py"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(clean_code)
                    print(f"\n[System]: Visualization code saved to '{filename}'")
                
                # Generate Mermaid Code for Assignment
                print("\n--- COPY CODE BELOW FOR MERMAID DIAGRAM ---")
                print(graph.get_graph().draw_mermaid())
                print("-------------------------------------------")
                break
                
        except Exception as e:
            print(f"Error during execution: {e}")
            break