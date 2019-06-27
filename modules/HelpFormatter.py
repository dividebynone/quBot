from discord.ext import commands
from main import lang
import discord

class HelpFormatter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0x339900
        bot.remove_command('help')
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='help')
    async def help(self, ctx, command = None, subcommand = None):
        if command:
            cmds_list = [x.name for x in self.bot.commands]
            if command.lower() in cmds_list:
                command = self.bot.get_command(command)
                if not (command.description or command.help):
                     embed = discord.Embed(title=lang["helpformatter_nohelp_parameter"], color=self.module_embed_color)
                else:
                    if subcommand:
                        subcommands_list = [x.name for x in self.bot.walk_commands() if x.name not in cmds_list]
                        subcommands_list = list(dict.fromkeys(subcommands_list))
                        if subcommand in subcommands_list:
                            command = self.bot.get_command(f'{command} {subcommand}')
                    if command.aliases:
                        aliases = '|'.join(command.aliases)
                        aliases = f'[{aliases}]'
                    else:
                        aliases = ''
                    embed = discord.Embed(title=f'**{self.bot.command_prefix}{command.qualified_name}**', description=command.description, color=self.module_embed_color)
                    embed.add_field(name=f'{lang["notes_string"]}:', value=command.help)
                    embed.add_field(name=f'{lang["usage_string"]}:', value=f'```CSS\n{self.bot.command_prefix}{command.qualified_name}{aliases} {command.signature}\n```', inline=False)
                    embed.set_footer(text=f'{lang["module_string"]}: {command.cog_name}')
            else:
                embed = discord.Embed(title=lang["helpformatter_cmd_not_found"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["helpformatter_help"], description=lang["helpformatter_help_description"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpFormatter(bot))