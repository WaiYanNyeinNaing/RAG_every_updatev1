#!/usr/bin/env python
"""
Monitor script to watch Gradio UI logs in real-time
Helps identify slow queries and issues
"""

import time
import os
from datetime import datetime

def monitor_log(log_file="gradio_ui.log"):
    """Monitor the Gradio UI log file"""
    
    print("="*60)
    print("RAG-Anything Gradio UI Monitor")
    print("="*60)
    print(f"Monitoring: {log_file}")
    print("Press Ctrl+C to stop\n")
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        print("Make sure the Gradio UI is running first.")
        return
    
    # Track query times
    query_start_times = {}
    
    with open(log_file, 'r') as f:
        # Go to end of file
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            line = line.strip()
            if not line:
                continue
            
            # Color coding for different log levels
            if "ERROR" in line:
                print(f"🔴 {line}")
            elif "WARNING" in line:
                print(f"🟡 {line}")
            elif "New query request:" in line:
                print(f"🔵 {line}")
                # Extract query from line
                if ":" in line:
                    query_text = line.split("New query request:")[-1].strip()
                    query_start_times[query_text] = time.time()
            elif "Query completed in" in line:
                print(f"✅ {line}")
                # Check for slow queries
                if "seconds" in line:
                    try:
                        seconds = float(line.split("in")[1].split("seconds")[0].strip())
                        if seconds > 10:
                            print(f"⚠️  SLOW QUERY: Took {seconds:.2f} seconds")
                    except:
                        pass
            elif "Query timed out" in line:
                print(f"⏱️  {line}")
            elif "Initializing LightRAG" in line:
                print(f"🚀 {line}")
            elif "Result length:" in line:
                print(f"📊 {line}")
            else:
                # Regular info messages
                if "INFO" in line:
                    # Skip verbose nano-vectordb messages
                    if "nano-vectordb" not in line:
                        print(f"   {line}")

if __name__ == "__main__":
    try:
        monitor_log()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {e}")