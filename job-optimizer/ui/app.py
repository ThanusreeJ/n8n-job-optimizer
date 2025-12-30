"""
Job Optimizer - Production Schedule Optimizer
"""

import streamlit as st
import pandas as pd
from datetime import datetime, time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.job import Job
from models.machine import Machine
from models.constraint import Constraint
from utils.baseline_scheduler import BaselineScheduler
from agents.batching_agent import BatchingAgent
from agents.bottleneck_agent import BottleneckAgent

st.set_page_config(page_title="Multi-Agent Job Optimizer", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 0.85em;
        font-weight: 700;
        border-radius: 0.25rem;
        background-color: #28a745;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🚀 Multi-Agent Production Job Optimizer</p>', unsafe_allow_html=True)


with st.expander("ℹ️ System Capabilities", expanded=False):
    st.markdown("""
    - **Baseline Scheduler:** Standard FIFO approach for comparison
    - **Batching Optimization:** Groups similar jobs to minimize setup times
    - **Load Balancing:** Distributes work evenly across available machines
    """)

# Initialize session state
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'machines' not in st.session_state:
    st.session_state.machines = []
if 'constraint' not in st.session_state:
    st.session_state.constraint = None

# Sidebar for input
st.sidebar.header("📥 Configuration")

# Sample data generator
if st.sidebar.button("🎲 Generate Sample Data"):
    
    # Create sample jobs with TIGHT deadlines (to force tardiness in Baseline)
    sample_jobs = [
        # J001: 45m duration, Due 09:15 (Tight!)
        Job(job_id="J001", product_type="P_A", processing_time=45, due_time=time(9, 15), priority="normal", machine_options=["M1", "M2"]),
        # J002: RUSH, 40m duration, Due 09:00 (Very Tight!)
        Job(job_id="J002", product_type="P_A", processing_time=40, due_time=time(9, 0), priority="rush", machine_options=["M1", "M2"]),
        # J003: 35m duration, Due 09:30
        Job(job_id="J003", product_type="P_B", processing_time=35, due_time=time(9, 30), priority="normal", machine_options=["M1", "M3"]),
        # J004: 50m duration, Due 10:00
        Job(job_id="J004", product_type="P_B", processing_time=50, due_time=time(10, 0), priority="normal", machine_options=["M1", "M3"]),
        # J005: 30m duration, Due 10:30
        Job(job_id="J005", product_type="P_C", processing_time=30, due_time=time(10, 30), priority="normal", machine_options=["M2", "M3"]),
    ]
    
    # Create sample machines (setup times belong to Constraint, not Machine)
    sample_machines = [
        Machine(machine_id="M1", capabilities=["P_A", "P_B"]),
        Machine(machine_id="M2", capabilities=["P_A", "P_C"]),
        Machine(machine_id="M3", capabilities=["P_B", "P_C"]),
    ]
    
    # Create constraint with setup times
    sample_constraint = Constraint(
        shift_start=time(8, 0),
        shift_end=time(16, 0),
        max_overtime_minutes=30,
        setup_times={
            "P_A->P_B": 10, "P_B->P_A": 10,
            "P_A->P_C": 15, "P_C->P_A": 15,
            "P_B->P_C": 12, "P_C->P_B": 12
        }
    )
    
    st.session_state.jobs = sample_jobs
    st.session_state.machines = sample_machines
    st.session_state.constraint = sample_constraint
    
    st.sidebar.success("✅ Sample data generated successfully!")

# Display current data
if st.session_state.jobs:
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Jobs loaded:** {len(st.session_state.jobs)}")
    st.sidebar.write(f"**Machines:** {len(st.session_state.machines)}")

# Main content area
st.header("🎯 Optimization Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Run Baseline Scheduler (FIFO)", use_container_width=True):
        if not st.session_state.jobs:
            st.error("❌ Please generate or upload data first!")
        else:
            with st.spinner("Running baseline scheduler..."):
                baseline = BaselineScheduler()
                schedule, explanation = baseline.schedule(
                    st.session_state.jobs,
                    st.session_state.machines,
                    st.session_state.constraint
                )
                st.session_state.result_baseline = schedule
                st.success("✅ Baseline schedule complete!")

with col2:
    if st.button("🔄 Run Batching Optimization (AI)", use_container_width=True):
        if not st.session_state.jobs:
            st.error("❌ Please generate data first!")
        else:
            with st.spinner("Optimization Phase 1: AI Grouping Logic..."):
                batching_agent = BatchingAgent()
                schedule, explanation = batching_agent.create_batched_schedule(
                    st.session_state.jobs,
                    st.session_state.machines,
                    st.session_state.constraint
                )
                st.session_state.result_batching = schedule
                st.success("✅ AI Batching complete!")

with col3:
    if st.button("⚖️ Run Load Balancing (AI)", use_container_width=True):
        if not st.session_state.jobs:
            st.error("❌ Please generate data first!")
        elif 'result_batching' not in st.session_state:
            st.error("❌ Run Batching Optimization first!")
        else:
            with st.spinner("Optimization Phase 2: Balancing Machine Workloads..."):
                bottleneck_agent = BottleneckAgent()
                schedule, explanation = bottleneck_agent.rebalance_schedule(
                    st.session_state.result_batching,
                    st.session_state.machines,
                    st.session_state.constraint,
                    st.session_state.jobs
                )
                st.session_state.result_final = schedule
                st.success("✅ Workload balancing complete!")

# Results display
st.header("📈 Results Dashboard")

if 'result_final' in st.session_state:
    st.subheader("✅ Final Optimized Schedule")
    st.markdown("**Status:** Fully Optimized (Batching + Load Balancing Applied)")
    
    schedule = st.session_state.result_final
    
    if schedule.kpis:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tardiness", f"{schedule.kpis.total_tardiness} min", delta_color="inverse")
        with col2:
            st.metric("Setup Time", f"{schedule.kpis.total_setup_time} min", delta_color="inverse")
        with col3:
            st.metric("Setup Switches", schedule.kpis.num_setup_switches, delta_color="inverse")
        with col4:
            st.metric("Load Imbalance", f"{schedule.kpis.utilization_imbalance:.1f}%", delta_color="inverse")
    
    # Show schedule table
    schedule_data = []
    for machine_id, assignments in schedule.assignments.items():
        for assignment in assignments:
            schedule_data.append({
                "Machine": machine_id,
                "Job": assignment.job.job_id,
                "Product": assignment.job.product_type,
                "Start": assignment.start_time.strftime("%H:%M"),
                "End": assignment.end_time.strftime("%H:%M"),
                "Rush": "⚡ Yes" if assignment.job.is_rush else "No"
            })
    
    if schedule_data:
        df = pd.DataFrame(schedule_data)
        st.dataframe(df, use_container_width=True)

elif 'result_batching' in st.session_state:
    st.subheader("🔄 Optimization Phase 1 Results")
    st.markdown("**Status:** Batched for Efficiency (Load Balancing Pending)")
    
    schedule = st.session_state.result_batching
    
    if schedule.kpis:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tardiness", f"{schedule.kpis.total_tardiness} min")
        with col2:
            st.metric("Setup Switches", schedule.kpis.num_setup_switches)
        with col3:
            st.metric("Setup Time", f"{schedule.kpis.total_setup_time} min")

elif 'result_baseline' in st.session_state:
    st.subheader("📊 Baseline (FIFO) Results")
    st.markdown("**Status:** Unoptimized Reference Schedule")
    
    schedule = st.session_state.result_baseline
    
    if schedule.kpis:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tardiness", f"{schedule.kpis.total_tardiness} min")
        with col2:
            st.metric("Setup Time", f"{schedule.kpis.total_setup_time} min")

else:
    st.info("  run the optimizer.")

# Footer
st.markdown("---")
st.markdown("**Multi-Agent Job Optimizer** • Powered by Groq AI & LangChain")
