import asyncio
import os
from dotenv import load_dotenv
from app.services.adventure_service import generate_new_node
# Load environment variables
load_dotenv()

def null_to_empty_string(value):
    return "" if value is None else value

async def test():
    adventure_id='676e3915d110a81ea62f30cc'
    node_id=0 
    selected_option=0
    end_after_insert=False


    result = await generate_new_node(adventure_id, node_id, selected_option, end_after_insert)
    print(result.get("title"))
    print("###PARSED RESULT###")
    print(result.get("text"))
    print("----")
    print("CALL TO ACTION: "+result.get("cta")) if result.get("cta") is not None else result.get("cta")
    n=1
    for option in result.get("options"):
        print(str(n)+":"+option)
        n=n+1

asyncio.run(test())