import streamlit as st
import os
from dotenv import load_dotenv
from rag_system import HealthRAG, MLX_AVAILABLE

load_dotenv()

def main():
    st.set_page_config(
        page_title="Personal Health & Fitness Advisor",
        page_icon="🏃‍♂️",
        layout="wide"
    )
    
    st.title("🏃‍♂️ Personal Health & Fitness Advisor")
    st.markdown("*Your AI-powered nutrition and fitness consultant*")
    
    # Backend and Model selection sidebar
    st.sidebar.title("⚙️ Model Settings")
    
    # Backend selection - MLX default
    backend_options = []
    if MLX_AVAILABLE:
        backend_options.append("mlx")
    backend_options.append("ollama")
    
    backend_choice = st.sidebar.selectbox(
        "Choose Backend:",
        backend_options,
        help="MLX: Native Apple Silicon (faster) | Ollama: Docker-based"
    )
    
    # Model selection based on backend
    if backend_choice == "mlx":
        model_options = [
            "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit"
        ]
        help_text = "70B MLX model optimized for Apple Silicon"
    else:
        model_options = ["llama3.1:70b"]
        help_text = "70B: May fail due to memory (43GB needed)"
    
    model_choice = st.sidebar.selectbox(
        "Choose Model:",
        model_options,
        help=help_text
    )
    
    if "rag_system" not in st.session_state:
        default_backend = "mlx" if MLX_AVAILABLE else "ollama"
        default_model = "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit" if MLX_AVAILABLE else "llama3.1:70b"
        st.session_state.rag_system = HealthRAG(backend=default_backend)
        st.session_state.current_model = default_model
        st.session_state.current_backend = default_backend
    
    # Switch backend if changed
    if backend_choice != st.session_state.current_backend:
        st.session_state.rag_system.switch_backend(backend_choice, model_choice)
        st.session_state.current_backend = backend_choice
        st.session_state.current_model = model_choice
        st.sidebar.success(f"Switched to {backend_choice} backend")
    # Switch model if changed (same backend)
    elif model_choice != st.session_state.current_model:
        if backend_choice == "mlx":
            st.session_state.rag_system.llm.switch_model(model_choice)
        else:
            st.session_state.rag_system.llm.switch_model(model_choice)
        st.session_state.current_model = model_choice
        st.sidebar.success(f"Switched to {model_choice}")
    
    # Show current setup
    st.sidebar.info(f"Backend: {st.session_state.current_backend}")
    st.sidebar.info(f"Model: {st.session_state.current_model}")
    
    # MLX availability status
    if MLX_AVAILABLE:
        st.sidebar.success("✅ MLX Available")
    else:
        st.sidebar.warning("⚠️ MLX Not Available")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about nutrition, fitness, or health..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner(f"Thinking with {st.session_state.current_model}..."):
                response, response_time = st.session_state.rag_system.query(prompt)
            
            st.markdown(response)
            st.caption(f"⏱️ Response time: {response_time:.1f}s | Backend: {st.session_state.current_backend} | Model: {st.session_state.current_model}")
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()