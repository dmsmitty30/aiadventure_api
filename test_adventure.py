import asyncio
import os
import json
from dotenv import load_dotenv
from app.services.chatgpt_service import askOpenAI_structured, developerMessage, assistantMessage, userMessage

# Load environment variables
load_dotenv()



responseType="new"

seed = developerMessage(f"""
    Create a choose-your-own adventure style novel based on the info provided by the user.
    You will return these pieces of information:
    - Title of Story (maximum 5 words)
    - Synopsis of Story (maximum 200 words)
    - Text of the first chapter of the story (500 words or less.
    - an array of 2-3 choices for the user to take after reading the text of the first chapter.
    """)

prompt = userMessage("Create a story involving a golden retriever that goes to space.")


'''
context = [

seed

]

async def test():
    response = await askOpenAI_structured(context, prompt, responseType)
    print(response)

asyncio.run(test())
'''
story={
  "title": "Barking Among the Stars",
  "synopsis": "When Max, an adventurous golden retriever, discovers a hidden spaceship in his backyard, curiosity takes over. His owner, a budding astronaut named Mia, is preparing for a mission to explore the outer reaches of space. Unbeknownst to Mia, Max hops aboard the ship just before launch. As the ship blasts off, Max embarks on an intergalactic adventure filled with alien encounters, zero-gravity fetch games, and the search for a lost spaceship. Will Max brave the cosmos to find his way back home? Join him on a journey through the stars and discover what it means to be a hero, even with four paws!",
  "text": "Max had always been a curious golden retriever. With his fluffy coat shimmering in the sunlight and his tail wagging furiously, he loved exploring every inch of the backyard. Little did he know that one ordinary day would turn extraordinary when he stumbled upon what seemed to be an old, rusty spaceship partially concealed by overgrown weeds. His nose twitched with excitement as he investigated the odd metallic object.\n\nThe spaceship wasn’t just an ordinary wreck; it had colors that sparkled like stars and markings unlike anything Max had ever seen. He sniffed around, letting instinct guide him. Just then, a large door creaked open as if inviting him inside. Max’s adventurous spirit took over. He trotted up the ramp and entered the ship, his paws echoing on the metallic floor.\n\nInside, Max noticed various shimmering buttons and screens flickering with lights. Before he could sniff out more, a familiar voice called out, \"Max! Where are you?\" It was Mia, his best friend and owner, dressed in a space suit, preparing for her mission to the stars.\n\nMax paused, unsure. The ship felt alive, and he wanted to explore. Just then, Mia hurried past him, completely unaware of his presence aboard the spacecraft. With a sudden whoosh, the ramp sealed shut, and alarms began to blare. \"All systems ready for launch!\" a robotic voice announced. \n\nMax’s heart raced—this was it! He was going to space! Before he could change his mind, the ground shook beneath him, and he felt the ship thrust upward into the azure sky, breaking through the atmosphere.\n\nMia, seated at the controls, smiled excitedly as she prepared for the unknown. \"I’ll make history today, the youngest astronaut to reach deep space!\" she declared.\n\nMeanwhile, Max was in the ship's cockpit, ears perked, looking out the window. The Earth was growing smaller and smaller, replaced by swirling clouds that scattered like cotton candy beneath them. It was beautiful!\n\nMoments later, they were in the vastness of space. Stars twinkled all around, like diamonds scattered on dark velvet. Max couldn’t contain his excitement; he bounded across the cabin in sheer joy, trying to chase the outer glow of those distant stars.\n\nThis was going to be the adventure of a lifetime! However, as Mia glanced at her control panel, a worried frown crossed her face. \"Oh no! The GPS is malfunctioning!\" she exclaimed. \n\nMax abruptly stopped dead in his tracks. A part of him sensed the growing tension. They were in a part of the universe where nobody could find them. His adventure had begun, but the stakes were higher than he realized. What if they got lost?\n\nThen, out of the corner of his eye, Max saw something flash outside a viewport, moving quickly across the expanse…",
  "options": [
    "Follow the flash outside",
    "Stay with Mia and help",
    "Bark to alert Mia about trouble"
  ]
}


assistant=assistantMessage(json.dumps(story, indent=2))
instruction=developerMessage("create the next chapter of the storyusing the user's next instruction.")
prompt = userMessage("Follow the flash outside.")

context = [

seed,
prompt,
assistant,
instruction,
prompt


]

responseType="node"

async def testNode():
    response = await askOpenAI_structured(context, prompt, responseType)
    print(response)

asyncio.run(testNode())