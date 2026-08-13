import streamlit as st

from agent import run_agent


st.set_page_config(
    page_title="GitHub AI Engineer",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 GitHub AI Engineering Agent")
st.caption(
    "Gemini 3.5 Flash • GitHub • Automated Testing • Pull Requests"
)

col1, col2 = st.columns(2)

with col1:
    owner = st.text_input(
        "GitHub Owner",
        placeholder="e.g. octocat",
    )

with col2:
    repo = st.text_input(
        "Repository",
        placeholder="e.g. hello-world",
    )

task = st.text_area(
    "Engineering Task",
    placeholder=(
        "Describe the coding task you want the AI engineer to perform..."
    ),
    height=140,
)

if st.button(
    "🚀 Run AI Engineer",
    type="primary",
    use_container_width=True,
):

    if not owner.strip():
        st.warning("Enter a GitHub owner.")
        st.stop()

    if not repo.strip():
        st.warning("Enter a GitHub repository.")
        st.stop()

    if not task.strip():
        st.warning("Enter an engineering task.")
        st.stop()

    st.divider()
    st.subheader("Agent Activity")

    try:

        with st.spinner(
            "Gemini 3.5 Flash is engineering..."
        ):

            result = run_agent(
                owner=owner.strip(),
                repo=repo.strip(),
                task=task.strip(),
            )

        for log in result.get("logs", []):
            st.write(log)

        if result.get("status") == "success":

            st.success(
                "Engineering task completed successfully!"
            )

            if result.get("message"):
                st.markdown("### 🤖 Agent Summary")
                st.write(result["message"])

        else:

            st.error(
                "The engineering task did not complete."
            )

            if result.get("message"):
                st.write(result["message"])

    except Exception as e:

        st.error(f"Agent error: {e}")