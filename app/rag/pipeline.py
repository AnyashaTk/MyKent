from langchain import hub
from langchain_community.llms import GPT4All
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from rag_data_prepare import get_data


class RAG_system:
    def __init__(self):
        self.llm = GPT4All(  # TheBloke/saiga_mistral_7b-GGUF
            model=r"../model/saiga_mistral_7b.Q3_K_M.gguf",
        )
        vector_store = get_data('../data/messages.mbox')
        retriever = vector_store.as_retriever()
        rag_prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.qa_chain = (
            # {"role": "user", "content":
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | rag_prompt
                | self.llm
                | StrOutputParser()
            # }
        )

    def __call__(self, question=None, *args, **kwargs):
        if not question:
            question = "Что ты можешь рассказать про региональный хакатон «Лидеры цифровой трансформации»?"
        # return self.qa_chain.invoke("Перечисли названия мероприятий, куда здесь есть приглашения")
        return self.qa_chain.invoke(question)


if __name__ == "__main__":
    rag = RAG_system()
    while True:
        question = input('Введите вопрос по сообщениям: ')
        if question == "хватит":
            break
        print(rag(question=question))

