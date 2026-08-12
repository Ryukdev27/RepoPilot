import streamlit as st
from agent import run_agent


st.set_page_config(
    page_title="GitHub AI Engineering Agent",
    page_icon="🤖",
    layout="wide",
)


st.title("🤖 GitHub AI Engineering Agent")

st.caption(
    "AI-powered software engineering automation using Gemini and GitHub."
)


with st.sidebar:

    st.header("Repository")

    owner = st.text_input(
        "GitHub Owner",
        value="Ryukdev27",
    )

    repo = st.text_input(
        "Repository",
        value="Echo-App",
    )


st.subheader("Engineering Task")

task = st.text_area(
    "Tell the agent what you want it to do",
    placeholder=(
        "Example: Read issue #1 and explain what needs to be fixed."
    ),
    height=150,
)


run = st.button(
    "🚀 Run Agent",
    type="primary",
    use_container_width=True,
)


if run:

    if not owner or not repo or not task:
        st.error("Please provide owner, repository and task.")

    else:

        st.subheader("Agent Activity")

        with st.spinner("Agent is working..."):

            try:

                result = run_agent(
                    owner=owner,
                    repo=repo,
                    task=task,
                )

            except Exception as e:

                st.error(f"Agent error: {e}")
                st.stop()


        logs = result.get("logs", [])

        for log in logs:
            if log.startswith("✓"):
                st.success(log)
            elif log.startswith("🔧"):
                st.info(log)
            else:
                st.write(log)


        st.divider()

        if result["status"] == "success":

            st.success("Agent completed successfully.")

            st.subheader("Result")

            st.write(result["message"])

        else:

            st.error("Agent did not complete successfully.")

            st.write(result["message"])