import os
import requests
import nextcord
from nextcord.ext import tasks
from Bot.core import Core
from firebase_admin import db, get_app

# Use the existing Firebase app
firebase_app = get_app()
data_rled_ref = db.reference("data/RLED", app=firebase_app)
data_yled_ref = db.reference("data/YLED", app=firebase_app)

guild_ids: list[int] = [int(value) for value in os.getenv("GUILD_IDS").split(",")]

goout_users = {}  # Tracks users who are "out"

class Commands(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.bot = bot
        self.check_firebase_data.start()  # Start the task loop to check Firebase data

    @nextcord.slash_command(name="userinfo", description="Get user information")
    async def userinfo(self, ctx):
        member = ctx.user  # 取得發出指令的使用者
        roles = [role.name for role in member.roles[1:]]  # 取得使用者的身分, 不含 @everyone role

        await ctx.send(
            f"User name: {member.name}\n"
            f"User ID: {member.id}\n"
            f"Joined at: {member.joined_at}\n"
            f"Roles: {', '.join(roles)}"
        )

    # 使用者外出的斜線指令
    @nextcord.slash_command(name="goout", description="Mark yourself as out of home")
    async def goout(self, ctx):
        goout_users[ctx.user.id] = ctx.user  # 將用戶添加到 "出門" 列表
        await ctx.response.send_message(f"{ctx.user.name}, you are now marked as out of home.", ephemeral=True)

        # 如果您想發送另一條消息，請使用 followup
        await ctx.followup.send("您現在可以檢查家中燈光的狀態。")

    @tasks.loop(seconds=5)  # 每 5 秒檢查一次
    async def check_firebase_data(self):
        # Check the Firebase Realtime Database for changes
        rled_value = data_rled_ref.get()
        yled_value = data_yled_ref.get()

        # Define image URLs and local image path
        image_livingroom = "http://127.0.0.1:5001/img/light_on.png"
        image_entrance = "http://127.0.0.1:5001/img/light_on2.png"
        image_path = "light_on.png"

        if rled_value is True:  # If the value becomes True
            to_notify = list(goout_users.values())

            # Download the image to local storage
            response = requests.get(image_entrance)
            with open(image_path, 'wb') as f:
                f.write(response.content)

            # 通知使用者燈被打開了
            for user in to_notify:
                try:
                    await user.send(
                        f"{user.name}, 在你出門的時候，玄關的燈亮了!",
                        file=nextcord.File(image_path)  # Attach the downloaded image
                    )
                except Exception as e:
                    print(f"Failed to send message to {user.name}: {e}")
            # Clear the goout list once users are notified
            goout_users.clear()

        if yled_value is True:  # If the value becomes True
            to_notify = list(goout_users.values())

            # Download the image to local storage
            response = requests.get(image_livingroom )
            with open(image_path, 'wb') as f:
                f.write(response.content)

            for user in to_notify:
                try:
                    await user.send(
                        f"{user.name}, 在你出門的時候，客廳的燈亮了!",
                        file=nextcord.File(image_path)  # Attach the downloaded image
                    )
                except Exception as e:
                    print(f"Failed to send message to {user.name}: {e}")
            # Clear the goout list once users are notified
            goout_users.clear()

def setup(bot):
    bot.add_cog(Commands(bot))