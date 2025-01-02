import asyncio

from twikit import Client

client = Client("en-US")

USERNAME = "Vtlvs1847621"
EMAIL = "atlastsl117@gmail.com"
PASSWORD = "Ledessins0!"


async def main():
    try:
        await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
        print("Client connected")
        # Search Latest Tweets
        tweets = await client.search_tweet('From:@KR93200', 'Latest')
        for tweet in tweets:
            print(tweet)
        await tweets.next()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
