import os
import re

import chromadb
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm


# Adding \n at end of each sentence and \n\n at end of each paragraph
# It will help in recursive splitter
def add_line_breaks(text):
    sentence_splits = text.split(".")
    sentence_with_delimiter = ".\n".join(sentence_splits)
    # If number of whitespaces is more than 2, then it is another paragraph
    sentence_with_delimiter = re.sub(r' {2,}', '\n\n', sentence_with_delimiter)
    return sentence_with_delimiter


# What to pass in the where clause
def get_where_clause(output_dict):
    where_list = []
    for product_names in output_dict['Product_Names']:
        where_list.append({"product": product_names})
    return where_list


def initializeContext():
    documents = []
    metadata = []

    # Getting all the documents and metadata, and storing it in a list
    for comp in tqdm(os.listdir("datasets")):
        for prod in os.listdir(f"datasets\{comp}"):
            # if prod == "Apple Fitness+.docx":continue
            loader = TextLoader(f"datasets\{comp}\{prod}", autodetect_encoding=True)
            doc = loader.load()
            text = add_line_breaks(doc[0].page_content)
            documents.append(text)
            metadata.append({"company": comp, "product": prod.split(".")[0]})

    # Recursive splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)

    # Split each element in the list
    split_list = [text_splitter.split_text(element) for element in documents]

    splitted_docs = []
    splitted_metadata = []

    # Aggregating the split texts
    for idx, docs in enumerate(split_list):
        curr_metadata = metadata[idx]
        if isinstance(docs, list):
            for doc in docs:
                splitted_docs.append(doc)
                splitted_metadata.append(curr_metadata)
        else:
            splitted_docs.append(docs)
            splitted_metadata.append(curr_metadata)

    chroma_client = chromadb.Client()
    collection_name = "TandC-project"

    # Vector database
    if len(chroma_client.list_collections()) > 0 and collection_name in [chroma_client.list_collections()[0].name]:
        chroma_client.delete_collection(name=collection_name)

    print(f"Creating collection: '{collection_name}'")
    collection = chroma_client.create_collection(name=collection_name)

    print("Building the vector database")
    collection.add(
        documents=splitted_docs,
        metadatas=splitted_metadata,
        ids=[f"id{i}" for i in range(1, len(splitted_docs) + 1)]
    )

    # TODO: Add further context initialization code
