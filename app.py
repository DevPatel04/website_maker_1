import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Initialize the language model
llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0.1,
)

# Streamlit app layout
st.title("Website Maker Chatbot")

# Initialize session state for chat history, website name, and architecture state
if "chat_history_architecture" not in st.session_state:
    st.session_state.chat_history_architecture = []

if "chat_history_content" not in st.session_state:
    st.session_state.chat_history_content = []

if "website_name" not in st.session_state:
    st.session_state.website_name = ""

if "architecture_created" not in st.session_state:
    st.session_state.architecture_created = False

if "website_architecture" not in st.session_state:
    st.session_state.website_architecture = ""

if "content_created" not in st.session_state:
    st.session_state.content_created = False

if "instructions_shown" not in st.session_state:
    st.session_state.instructions_shown = False

if "instructions_shown_content" not in st.session_state:
    st.session_state.instructions_shown_content = False

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Architecture", "Content Creation"])

if page == "Architecture":
    # Architecture Section
    st.session_state.content_created = False

    st.header("Architecture")
    user_input = st.chat_input("Describe your website or request an architecture change!")

    # Display chat history
    for message in st.session_state.chat_history_architecture:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input:
        # If website name is not set, use the first input to set it
        if not st.session_state.website_name:
            st.session_state.website_name = user_input
            st.success(f"Website name set to: {user_input}")
        
        website_name = st.session_state.website_name

        if not st.session_state.architecture_created:
            # Initial architecture creation
            prompt = f"""
            Design a comprehensive website architecture for {st.session_state.website_name} website by outlining all main pages along with their detailed subpages and content sections.

            The architecture should include:
            - Main Pages: Identify all the primary pages of the website (e.g., Home, About, Services, Blog, Contact).
            - Subpages and Sections: For each main page, list all necessary subpages and content sections. For example, under the Home page, include sections such as Hero Banner, Features, Testimonials, and Call-to-Action; under Services, include subpages for each service type and relevant content sections.
            - Navigation and Hierarchy: Describe how these pages and subpages are connected and organized to ensure intuitive navigation and a logical content hierarchy.

            The final output should be a clear, structured outline that serves as a blueprint for the website’s design and development.
            The final output must be in the proper format that is easy to understand and implement.
            """
            st.session_state.architecture_created = True
        else:
            # Handle architecture updates based on user input
            prompt = f"""
            Update the website architecture for {st.session_state.website_name}. 
            Please modify only the following sections based on the new requirements:
            - {user_input}

            Keep the overall structure and hierarchy as defined in the current blueprint, ensuring intuitive navigation and a consistent user experience. Provide the updated outline incorporating only the changes mentioned above.
            """

        # Define the chat prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert website maker."),
            ("human", prompt)
        ])

        # Always update the conversation chain
        st.session_state.conversation_chain = prompt_template | llm

        # Process user input
        st.session_state.chat_history_architecture.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Get response from the assistant
        with st.chat_message("assistant"):
            try:
                response = st.session_state.conversation_chain.invoke({"website_name": st.session_state.website_name})
                assistant_response = response.content if response else "Sorry, I couldn’t understand that."
            except Exception as e:
                assistant_response = f"An error occurred: {e}"

            st.markdown(assistant_response)

            # Add assistant response to chat history
            st.session_state.chat_history_architecture.append({
                "role": "assistant",
                "content": assistant_response
            })

            if st.session_state.architecture_created and not st.session_state.instructions_shown:
                st.info(
                    "If you want any change in the architecture, please provide the details in the following format for the better output:\n"
                    "- **[Specify section]**\n"
                    "- **[Specify additional changes]**\n"
                    "- **[Any other specific instructions or adjustments]**"
                )
                st.session_state.instructions_shown = True

            # Save architecture for content creation
            st.session_state.website_architecture = assistant_response

    else:
        st.info("Please enter your website name to get started or describe a change to update the architecture!")

elif page == "Content Creation":
    # Content Creation Section
    st.header("Content Creation")
    st.write("Last saved architecture:")
    st.write(st.session_state.website_architecture)

    # Display chat history
    for message in st.session_state.chat_history_content:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Describe the content you want to create or update!")

    if not st.session_state.content_created:
        prompt = f"""Create content for the following website architecture: {st.session_state.website_architecture}. 
Ensure the content is well-structured, engaging, and relevant to the specified sections.
"""
        st.session_state.content_created = True
    else: 
        if user_input:
            prompt = f"""Update content for the following website architecture: {st.session_state.website_architecture}. 
                Please modify only the following sections based on the new requirements:
                - {user_input}
                Give the other content as same as before.
                Ensure the content is well-structured, engaging, and relevant to the specified sections.
            """

    prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert website content creator."),
            ("human", prompt)
        ])

    st.session_state.conversation_chain = prompt_template | llm

    if not st.session_state.website_architecture:
        st.info("Please create an architecture first before creating content.")
        st.stop()

    st.subheader("Content Created")
    
    if user_input:
        # Process user input
        st.session_state.chat_history_content.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Get response from the assistant
        with st.chat_message("assistant"):
            try:
                response = st.session_state.conversation_chain.invoke({"website_architecture": st.session_state.website_architecture})
                assistant_response = response.content if response else "Sorry, I couldn’t understand that."
            except Exception as e:
                assistant_response = f"An error occurred: {e}"

            st.markdown(assistant_response)

            if not st.session_state.instructions_shown_content:
                st.info(
                    "If you want any change in the content, please provide the details in the following format for the better output:\n"
                    "- **[Specify section]**\n"
                    "- **[Specify additional changes]**\n"
                    "- **[Any other specific instructions or adjustments]**"
                )
                st.session_state.instructions_shown_content = True

            # Add assistant response to chat history
            st.session_state.chat_history_content.append({
                "role": "assistant",
                "content": assistant_response
            })