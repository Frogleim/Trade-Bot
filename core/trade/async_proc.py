import asyncio


async def func_a():
    while True:
        print("Function A is running")
        await asyncio.sleep(1)
        print("Function A is done")


async def func_b(stop_event):
    count = 0
    while True:
        count += 1
        print("Function B is running")
        if count == 5:
            print(count)
            print('Sleeping')
            stop_event.set()  # Set event to pause func_b
            await asyncio.sleep(1)  # Sleep for 1 second
            stop_event.clear()  # Clear event to resume func_b
            count = 0  # Reset count after resuming
        await asyncio.sleep(0.1)  # To allow event check without blocking


# Simulate streaming
async def main():
    print("Main function is running")
    stop_event = asyncio.Event()
    results = await asyncio.gather(func_a(), func_b(stop_event))
    print("Main function is done")
    print(results)


asyncio.run(main())
