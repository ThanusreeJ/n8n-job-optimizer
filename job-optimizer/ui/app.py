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

from utils.data_generator import generate_random_jobs, get_demo_machines, get_demo_constraint

# ... imports remain same ...

# Sidebar for input
st.sidebar.header("📥 Configuration")

# Sample data generator
if st.sidebar.button("🎲 Generate Random Data"):
    
    # 1. Generate 5 Random Jobs
    sample_jobs = generate_random_jobs(5)
    
    # 2. Get Standard Demo Machines & Constraints
    sample_machines = get_demo_machines()
    sample_constraint = get_demo_constraint()
    
    st.session_state.jobs = sample_jobs
    st.session_state.machines = sample_machines
    st.session_state.constraint = sample_constraint
    
    # Reset results on new data
    if 'result_baseline' in st.session_state: del st.session_state.result_baseline
    if 'result_batching' in st.session_state: del st.session_state.result_batching
    if 'result_final' in st.session_state: del st.session_state.result_final
    
    st.sidebar.success(f"✅ Generated {len(sample_jobs)} Random Jobs!")
    
    st.sidebar.success(f"✅ Generated {len(sample_jobs)} Random Jobs!")
    
# Persistent Data Preview
if st.session_state.jobs:
    with st.expander("📋 View Generated Input Data", expanded=True):
        data_preview = []
        for job in st.session_state.jobs:
            data_preview.append({
                "Job ID": job.job_id,
                "Product": job.product_type,
                "Processing (min)": job.processing_time,
                "Due Time": job.due_time.strftime("%H:%M"),
                "Priority": "⚡ RUSH" if job.priority == 'rush' else "Normal"
            })
        st.dataframe(pd.DataFrame(data_preview), use_container_width=True)
        st.info("💡 Note: Deadlines are TIGHT (09:00-11:00) to challenge the scheduler.")

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
                st.markdown("**Explanation:** Simple FIFO logic. Notice high Tardiness because Rush jobs waited in line.")

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
                # CRITICAL: Calculate KPIs so the Comparison Table doesn't crash
                schedule.calculate_kpis(st.session_state.machines, st.session_state.constraint)
                
                st.session_state.result_batching = schedule
                st.success("✅ AI Batching complete!")
                st.markdown("**Explanation:** AI grouped jobs by Product Type. Setup Time dropped, but load might be unbalanced.")

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
                # CRITICAL: Calculate KPIs
                schedule.calculate_kpis(st.session_state.machines, st.session_state.constraint)
                
                st.session_state.result_final = schedule
                st.success("✅ Workload balancing complete!")
                st.markdown("**Explanation:** Jobs moved from busy machines to free ones. Optimization Achieved!")

# Results display
st.header("📈 Results Dashboard")

# COMPARISON MATRIX (New Section)
if 'result_baseline' in st.session_state and 'result_final' in st.session_state:
    st.subheader("⚖️ Strategy Comparison")
    
    base_kpi = st.session_state.result_baseline.kpis
    batch_kpi = st.session_state.result_batching.kpis
    final_kpi = st.session_state.result_final.kpis
    
    comp_data = {
        "Metric": ["Total Tardiness (min)", "Setup Time (min)", "Load Imbalance (%)"],
        "Baseline (FIFO)": [base_kpi.total_tardiness, base_kpi.total_setup_time, f"{base_kpi.utilization_imbalance:.1f}"],
        "Batching (AI)": [batch_kpi.total_tardiness, batch_kpi.total_setup_time, f"{batch_kpi.utilization_imbalance:.1f}"],
        "Bottleneck (AI)": [final_kpi.total_tardiness, final_kpi.total_setup_time, f"{final_kpi.utilization_imbalance:.1f}"],
    }
    st.table(pd.DataFrame(comp_data))

# ... (Detailed Results Logic) ...
if 'result_final' in st.session_state:
    # ... (Show Final Schedule Table) ...
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
