# import asyncio

# async def main():
#     print('hello')
#     await asyncio.sleep(1)
#     print('world')

# asyncio.run(main())

print("This is my file to test Python's execution methods.")
print("The variable __name__ tells me which context this file is running in.")
print("The value of __name__ is:", repr(__name__))

def hello():
    print("Hello World!")

if __name__ == "__main__":
    hello()

