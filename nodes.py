from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Initialize models
llm = ChatOllama(model="qwen3:1.7b", temperature=0)

def supervisor_node(state):
    """Orchestrates the workflow: Loader -> Analyst -> Chart Maker -> Finish"""
    
    # 1. If we have no data, start with the Data Loader
    if not state.get("dataset_sample"):
        return {"next_step": "DataLoader"}
    
    # 2. If we have data but no analysis, send to Insight Generator
    if state.get("dataset_sample") and not state.get("analysis_report"):
        return {"next_step": "InsightGenerator"}
    
    # 3. If we have analysis but no chart, send to Chart Creator
    if state.get("analysis_report") and not state.get("chart_code"):
        return {"next_step": "ChartCreator"}
    
    # 4. If everything is done, finish
    return {"next_step": "FINISH"}

def data_loader_node(state):
    """Generates synthetic data for the demo"""
    topic = state['messages'][0].content
    print(f"--- 🔄 Generating Synthetic Data for: {topic} ---")
    
    prompt = f"""
    Generate a realistic synthetic dataset in CSV format about: {topic}.
    Include headers. Create 10 rows of data with at least 3 numerical columns and 1 categorical column.
    Output ONLY the CSV data, no other text.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "messages": [HumanMessage(content="Data Loaded", name="DataLoader")],
        "dataset_sample": response.content
    }

def insight_generator_node(state):
    """Analyzes the dataset"""
    print("--- 💡 Generating Insights ---")
    data = state['dataset_sample']
    
    prompt = f"""
    Analyze the following CSV dataset:
    {data}
    
    Provide 3 key business insights or trends based on the numbers.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "messages": [HumanMessage(content=response.content, name="InsightGenerator")],
        "analysis_report": response.content
    }

def chart_creator_node(state):
    """Writes Python code to visualize the data"""
    print("--- 📊 Creating Chart Code ---")
    data = state['dataset_sample']
    
    prompt = f"""
    Write Python code using Matplotlib/Seaborn to visualize this dataset:
    {data}
    
    The code should:
    1. Load the data from a string (IOString).
    2. Create a bar chart or line chart.
    3. Save the plot as 'chart_output.png'.
    
    Return ONLY the Python code block.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "messages": [HumanMessage(content="Chart Code Generated", name="ChartCreator")],
        "chart_code": response.content
    }