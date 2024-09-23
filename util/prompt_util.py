# Create  product prompt based on features provided.
from prompts import *
def generate_product_prompt(max_price: str, min_price: str, max_discount: str, min_discount:str, radio_training_focus:str, product_info: str):
    product_prompt = ""
    diff_prompt = ""
    # Inputting features into prompt
    if(is_float(max_price)):
        prompt = f"The maximum acceptable price for the product in the market is {max_price}. If the sales representative quotes a price exceeding this limit, firmly request them to adjust it within the acceptable range."
        ex = f"Example Interaction 1:\n User: Our product is priced at $8000. System: That exceeds our acceptable price range. Please adjust it to $5000 or below."
        product_prompt = product_prompt + f"\n{prompt}\n{ex}"
    if (is_float(min_price)):
        prompt = f"The minimum market price for the product is {min_price}. If the sales representative offers a price lower than this, ask them to provide the correct price; otherwise, you may terminate the conversation."
        ex = f"User: Our product is available for $500.\n System: Please provide a realistic figure. Please provide the correct price."
        product_prompt = product_prompt + f"\n{prompt}\n{ex}"

    if (is_float(max_discount)):
        prompt = f"The maximum discount you can offer is {max_discount}. If the sales representative quotes a discount exceeding this limit, ask them to provide a realistic figure."
        ex = f"User: We're offering a 40% discount. System: Be realistic man otherwise I will have to cut the conversation"
        product_prompt = product_prompt + f"\n{prompt}\n{ex}"

    if (is_float(min_discount)):
        prompt = "The minimum discount in market is " + min_discount + ". If the sales representative offers a discount lower than this, inquire if they are aware of the current discount rates."
        ex = "User: We can offer a 5% discount. \n User: The minimum market discount rate is 10%. Are you aware of the current discount rates?"
        product_prompt = product_prompt+"\n"+prompt+"\n"+ex

    # Product info to prompt
    if len(product_info)>0:
        prompt = f"The product you're interested in has the following key features:\n{product_info}\n If the sales representative mentions additional key features not listed above, remind them of the existing features you know and suggest they learn more about the product's specifications before continuing the conversation."
        ex = "User: Our product also includes a 24/7 customer support feature. \n System: I appreciate the additional information, but the core features I've been informed of do not include 24/7 customer support. Lets continue only when you properly know the features. Ending the conversation"
        product_prompt = f"{product_prompt}\n{prompt}\n{ex}"

    if radio_training_focus.lower() == "objection handling":
        product_prompt = f"{product_prompt}\n{objection_handling_prompt}"
        diff_prompt = "Based on the system prompt, identify 5 very challenging questions based for testing objection handling of  user and ask them to user."

    elif radio_training_focus.lower() == "negotiation":
        product_prompt = f"{product_prompt}\n{negotiation_prompt}"
        diff_prompt = "Based on the system prompt, identify 5 very challenging questions  for testing negotiation skill of   user and ask them to user."

    elif radio_training_focus.lower() == "product knowledge":
        product_prompt = f"{product_prompt}\n{product_knowledge_prompt}"
        diff_prompt = "Based on the system prompt, identify 5 very challenging questions based on product knowledge and ask the to user to test their product knowledge. If the answer provided by user is incorrect, tell him"

    else:
        product_prompt = f"{product_prompt}\n{overall_prompt}"
        diff_prompt = "Based on the system prompt, identify 5 very challenging questions and ask them to user. If the answer provided by user is incorrect, tell him"

    return product_prompt, diff_prompt

# checks if a string is float.
def is_float(string):
    if len(string.strip())<1:
        return False
    if string.replace(".", "").isnumeric():
        return True
    else:
        return False

dictv = {
    "Smith Urology Center": prompt_smith_urology_center,
    "Walmart": prompt_walmart,
    "Meeting Analyser Corp": prompt_meeting_analyzer_corp,
    "Prestige Gastro Clinic": prompt_prestige_gastro_clinic,
    "Kulkarni Animal Bite Clinic": prompt_kulkarni_animal_clinic,
    "Joy Hospital": prompt_joy_hospital,
    "IDE": prompt_ide,
    "Cybernetic Innovations": prompt_cyber_innovation,
    "City Health Department": prompt_city_health,
    "TechAim": prompt_techaim,
    "Salesperson": prompt_salesguy
}