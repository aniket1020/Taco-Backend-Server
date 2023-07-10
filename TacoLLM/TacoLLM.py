import os
from langchain import PromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.llms import VertexAI

import chromadb
from langchain.chat_models import ChatVertexAI
from collections import defaultdict
from chromadb.config import Settings
from TacoLLM.constants import credentials_json
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_json

tandc_list = ""
for comp in os.listdir("datasets"):
    tandc_list += comp
    tandc_list += ": "
    for prod in os.listdir(f"datasets/{comp}"):
        prod_name = prod.split(".")[0]
        tandc_list += prod_name + ", "
    tandc_list = tandc_list[:-2]
    tandc_list += "\n\n"

company_names = ResponseSchema(
    name="Company_Names",
    description="Name of the companies"
)

product_names = ResponseSchema(
    name="Product_Names",
    description="Name of the products"
)
topics = ResponseSchema(
    name="topics",
    description="Keywords or topics discussed"
)

response_schema = [
    company_names,
    product_names,
    topics
]

output_parse = StructuredOutputParser.from_response_schemas(response_schema)
format_instructions = output_parse.get_format_instructions()

llm1_template = """
You have the company names and their products {tandc_list}. Here each line is formatted as "Company_Name": Name of the products separated by commas.\n

Based ONLY on the list that you are provided above, respond to the user query and output the company names, product names and the topics, discussed in the query.\n

For topics, DON'T INCLUDE the company name or product names. \n

If company name isn't in the list, then don't include it in the output\n

If product name is not mentioned explicitly, then provide the most relevant product from the list that you are provided.\n

User request: "{user_request}"
{format_instructions}
"""

llm_1_prompt_template = PromptTemplate(
    input_variables=["tandc_list", "user_request", "format_instructions"],
    template=llm1_template
)


def response_llm1(user_request):
    llm1_prompt = llm_1_prompt_template.format(
        tandc_list=tandc_list,
        user_request=user_request,
        format_instructions=format_instructions
    )

    llm1 = VertexAI(temperature=0.0)

    output = llm1.predict(llm1_prompt)

    llm1_output_dict = output_parse.parse(output)
    for key, val in llm1_output_dict.items():
        if not isinstance(val, list):
            llm1_output_dict[key] = val.split(",")
    return llm1_output_dict


# print(llm1_output_dict)
chroma_restore_client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="tandc-db"
    )
)

collection_name = "TandC-project"
restore_collection = chroma_restore_client.get_collection(name=collection_name)


def get_where_clause(output_dict):
    where_list = []
    for product_name in output_dict['Product_Names']:
        where_list.append({"product": product_name})
    return where_list


def get_relevant_sentences(llm1_output_dict, user_request):
    where_list = get_where_clause(llm1_output_dict)

    if len(where_list) == 1:

        query_results = restore_collection.query(
            query_texts=user_request,
            n_results=20,
            where=where_list[0]
        )
    else:
        query_results = restore_collection.query(
            query_texts=user_request,
            n_results=20,
            where={
                "$or": where_list
            }
        )

    relevant_dict = defaultdict(list)

    for doc, meta in zip(query_results['documents'][0], query_results['metadatas'][0]):
        # print(meta,doc)
        relevant_dict[meta['product']].append(doc)

    relevant_sentences = ""

    for key, value in relevant_dict.items():
        value = " ".join(value)
        relevant_sentences += f"Relevant document for {key}: "
        relevant_sentences += value
        relevant_sentences += "\n\n"
    return relevant_sentences


def get_response_llm2(relevant_sentences, user_request):
    llm_2 = ChatVertexAI(temperature=0.8, max_output_tokens=1024, top_p=0.8, top_k=4, do_sample=True)
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm_2,
        memory=memory,
        verbose=False
    )
    llm2_template = """
    You are a legal expert with a strong knowledge of companies terms and conditions. 

    Perform the following steps:

    Step 1: Check if the answer to the question {user_query} exists in the following relevant terms and conditions. \n
    {relevant_documents}\n\n. 


    Step 2: If the answer to the question {user_query} exists in the terms and conditions, return the answer. If there are links in the response, format them such that they are continous without gaps or new line characters.
    If the answer to the question {user_query} does not exist in the terms and conditions, respond with the following message:
    "Currently, I am  only trained on Terms and Conditions of certain companies. Therefore, I do not have an answer to your question.".

    Step 3: Re-check the response. Ensure that formatting of links is in one line.
    """

    llm2_prompt_template = PromptTemplate(
        input_variables=["relevant_documents", "user_query"],
        template=llm2_template
    )

    llm2_prompt = llm2_prompt_template.format(
        user_query=user_request,
        relevant_documents=relevant_sentences
    )

    output = conversation.predict(input=llm2_prompt)
    return output
