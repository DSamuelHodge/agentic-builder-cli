from restack_ai import Restack
from src.agents.testapp import Testapp

client = Restack()

async def main():
	await client.start_service(
		agents=[Testapp],
		workflows=[],
		functions=[]
	)

if __name__ == '__main__':
	import asyncio
	asyncio.run(main())
