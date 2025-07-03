import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

CANAL_PRESENTACIONES_ID = 1390039236396322948  # #presentaciones
CANAL_GALERIA_ID = 1363992765532209203         # 🐉𝙶alería

intents = discord.Intents.default()
intents.message_content = True  # Necesario si luego deseas leer contenido de mensajes normales
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Slash commands sincronizados: {len(synced)} comandos")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

@bot.tree.command(name="presentacion", description="Envía tu presentación personal al canal de presentaciones")
@app_commands.describe(
    nombre="Tu nombre (máx 30 letras)",
    edad="Tu edad (ej: 21 años)",
    gustos="Tus gustos (máx 120 letras)",
    hobbies="Tus hobbies (máx 120 letras)",
    dato_curioso="Un dato curioso sobre ti (máx 150 letras)"
)
async def presentacion(
    interaction: discord.Interaction,
    nombre: str,
    edad: str,
    gustos: str,
    hobbies: str,
    dato_curioso: str
):
    await interaction.response.defer(ephemeral=True)

    # Validaciones de longitud
    if len(nombre) > 30 or len(gustos) > 120 or len(hobbies) > 120 or len(dato_curioso) > 150:
        await interaction.followup.send("❌ Uno de los campos supera el límite de caracteres.", ephemeral=True)
        return

    # Validación de edad
    if not edad.isdigit() or not (10 <= int(edad) <= 100):
        await interaction.followup.send("❌ La edad debe ser un número entre 10 y 100.", ephemeral=True)
        return

    user = interaction.user
    canal_presentaciones = bot.get_channel(CANAL_PRESENTACIONES_ID)
    canal_galeria = bot.get_channel(CANAL_GALERIA_ID)

    if not canal_presentaciones or not canal_galeria:
        await interaction.followup.send("❌ No se pudo encontrar los canales.", ephemeral=True)
        return

    await interaction.followup.send(
        "📸 Presentación registrada.\nAhora tienes **2 minutos con 30 segundos** para enviar tu imagen en el canal 🐉𝙶alería. Esta se mostrará en tu presentación. De no enviar, tu presentación no tendrá imagen.",
        ephemeral=True
    )

    await asyncio.sleep(200)  # Esperar 3 con 20

    imagen = None
    mensaje_imagen = None

    async for mensaje in canal_galeria.history(limit=50, after=interaction.created_at):
        if mensaje.author.id == user.id and mensaje.attachments:
            imagen = mensaje.attachments[0]
            mensaje_imagen = mensaje
            break

    # Construir embed
    embed = discord.Embed(
        title=f"🐈 Presentación de {user.display_name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="︿︿⟡ ⭐ Nombre", value=nombre, inline=False)
    embed.add_field(name="︿︿⟡ 🎂 Edad", value=edad, inline=False)
    embed.add_field(name="︿︿⟡ 🎯 Gustos", value=gustos, inline=False)
    embed.add_field(name="︿︿⟡ 🎨 Hobbies", value=hobbies, inline=False)
    embed.add_field(name="︿︿⟡ 🤔 Dato curioso", value=dato_curioso, inline=False)

    files = []
    if imagen:
        file = await imagen.to_file()
        embed.set_image(url=f"attachment://{file.filename}")
        files.append(file)

    await canal_presentaciones.send(embed=embed, files=files)

    # Borrar imagen original si se usó
    if mensaje_imagen:
        try:
            await mensaje_imagen.delete()
        except discord.Forbidden:
            print("❌ No tengo permiso para eliminar mensajes en Galería.")

    await interaction.followup.send("✅ Tu presentación ha sido publicada en #presentaciones.", ephemeral=True)

bot.run(TOKEN)
