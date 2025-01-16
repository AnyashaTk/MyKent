from time import time

from langchain_community.llms import GPT4All

t0 = time()

llm = GPT4All(
    model=r"../model/saiga_mistral_7b.Q3_K_M.gguf",
)

print('llm loaded in ', time()-t0)
t0 = time()

print(llm.invoke("что такое Retrieval Augmented Generation?"))

print('answer generated in ', time()-t0)

