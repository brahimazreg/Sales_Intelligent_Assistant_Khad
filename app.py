
import streamlit as st

from services.query_pipeline import ask_assistant


# Configuration
st.set_page_config(
    page_title="Sales Intelligent Assistant Khady",
    page_icon="🤖",
    layout="centered"
)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []


# Titre
st.title("🤖 Sales Intelligent Assistant Khady")

st.write(
    "Posez vos questions sur vos clients, produits, "
    "commandes et fournisseurs."
)

st.divider()


# Affichage de toutes les anciennes conversations
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Affichage du SQL
        if message.get("sql"):
            with st.expander("Voir la requête SQL générée"):
                st.code(message["sql"], language="sql")

        # Affichage des résultats
        if message.get("rows") is not None:
            with st.expander("Voir les résultats SQL"):
                st.dataframe(
                    message["rows"],
                    use_container_width=True
                )


# Zone de saisie de la question
question = st.chat_input("Posez votre question ici...")


if question:

    # Afficher et mémoriser la question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Générer la réponse
    with st.chat_message("assistant"):

        with st.spinner("Analyse de votre question..."):

            try:
                response = ask_assistant(question)

                answer = response["answer"]
                sql = response["sql"]
                rows = response["result"]["rows"]

                st.markdown(answer)

                with st.expander("Voir la requête SQL générée"):
                    st.code(sql, language="sql")

                with st.expander("Voir les résultats SQL"):
                    st.dataframe(
                        rows,
                        use_container_width=True
                    )

                # Mémoriser la réponse complète
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sql": sql,
                    "rows": rows
                })

            except Exception as error:

                error_message = f"Une erreur est survenue : {error}"

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
