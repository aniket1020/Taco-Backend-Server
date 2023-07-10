from TacoLLM.TacoLLM import *


def handleRequest(inputQuery):
    llm1_response = response_llm1(inputQuery)
    valid_product_names = ['Apple_Fitness+',
                           'Apple_icloud',
                           'Apple_Maps',
                           'Apple_MediaServices',
                           'Apple_Music',
                           'Apple_News+',
                           'Apple_Store',
                           'Apple_TV+',
                           'Apple_Website',
                           'Google_Cloud',
                           'Google_Drive',
                           'Google_Gmail',
                           'Google_Maps',
                           'Google_Playstore',
                           'Lyft',
                           'Instagram',
                           'Meta',
                           'Reddit',
                           'Snapchat',
                           'Twitter',
                           'Uber']
    if len(llm1_response['Product_Names']) == 0:
        return f"The product is based on a Question-Answering agent on top of the Terms and Conditions of companies. Please " \
               f"ask a relevant question."
    for product_name in llm1_response['Product_Names']:
        if product_name not in valid_product_names:
            return f"Currently, we are supporting {', '.join(valid_product_names)}, please ask questions about the " \
                   f"products mentioned here."
    relevant_sentences = get_relevant_sentences(llm1_response, inputQuery)

    # print(relevant_sentences)
    llm2_output = get_response_llm2(relevant_sentences, inputQuery)
    return llm2_output
