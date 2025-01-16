from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.embeddings import GPT4AllEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

from mbox_reader import MboxReader


def get_data(path="./data/Mail/mails.mbox", emails_to_process=10, start=0, ):
    mbox = MboxReader(path)

    current_mails = 0
    arxiv_contents = ""
    for i, message in tqdm(enumerate(mbox)):
        if i < start:
            continue
        payload = message.get_payload(decode=True)
        if payload:
            current_mails += 1
            if current_mails > emails_to_process:
                break
            soup = BeautifulSoup(payload, 'html.parser')
            body_text = soup.get_text().replace('"', '').replace("\n", "").replace("\t", "").strip()
            arxiv_contents += body_text + " "  # для красивого вывода на посмотреть здесь \n

    # Вот тут можно вытащить данные из текстового файлика, чтобы проверить на том что я скинула

    doc = Document(page_content=arxiv_contents,
                   metadata={"source": "local"})

    # split into different chunks
    # chunk_size and chunk_overlap are a hyperparameters we choose
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)

    # split the documents and convert to vector stores
    all_splits = text_splitter.split_documents([doc])
    vector_store = Chroma.from_documents(documents=all_splits,
                                         embedding=GPT4AllEmbeddings())
    return vector_store
