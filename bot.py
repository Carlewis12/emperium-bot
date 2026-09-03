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
# CONFIGURACIÓN DE CANALES Y ENLACES
# ==========================================

# 1. ID de tu canal de texto privado para los reportes de staff (Cámbiala si es necesario)
CANAL_STAFF_ID = 1545125674661060708 

# 2. Diccionario con los enlaces que verá el jugador (enmascarados al servidor principal)
# (Reemplaza los ceros '000000000000000000' por la ID numérica real de cada canal de texto de tu servidor)
ENLACES_JUGADOR = {
    1490416172099964938: "https://grabify.link/ACB8Z8",  # EMPERIUM ACADEMY VIII
    1517174430558847109: "https://grabify.link/855ZYH",  # VX EMPERIUM
    1437457282190278788: "https://grabify.link/X7YVR6",  # UMBRA EMPERIUM
    1478823940410445825: "https://grabify.link/ITZQJ7",  # SOKAR EMPERIUM
    1358550246807830639: "https://grabify.link/2WGW0O",  # AESIR EMPRIUM
    1348303113748091002: "https://grabify.link/CZW556",  # NOIRE EMPERIUM
    1335735630696808514: "https://grabify.link/9T9HKA",  # THEMIS EMPERIUM
}

# 3. Diccionario con los enlaces reales de Grabify para el panel privado del staff
ENLACES_GRABIFY = {
    1490416172099964938: "https://grabify.link/track/JT3OHZ",  # EMPERIUM ACADEMY VIII
    1517174430558847109: "https://grabify.link/track/QHE7PO",  # VX EMPERIUM
    1437457282190278788: "https://grabify.link/track/LG90GF",  # UMBRA EMPERIUM
    1478823940410445825: "https://grabify.link/track/8A022M",  # SOKAR EMPERIUM
    1358550246807830639: "https://grabify.link/track/323HOB",  # AESIR EMPRIUM
    1348303113748091002: "https://grabify.link/track/NT88ZS",  # NOIRE EMPERIUM
    1335735630696808514: "https://grabify.link/track/RFSP0X",  # THEMIS EMPERIUM
    
}

# ==========================================
# CLASE DEL BOTÓN Y LÓGICA DE CHECK-IN
# ==========================================

class CheckinButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirmar Asistencia", style=discord.ButtonStyle.primary, emoji="📋")
    async def confirm_attendance(self, interaction: discord.Interaction, button: Button):
        canal_id = interaction.channel.id
        
        # Buscamos los enlaces correspondientes usando la ID numérica del canal
        link_jugador = ENLACES_JUGADOR.get(canal_id)
        link_grabify_real = ENLACES_GRABIFY.get(canal_id)
        
        if not link_jugador or not link_grabify_real:
            await interaction.response.send_message(
                f"❌ Este canal no está configurado en el sistema de check-in. (ID detectada: `{canal_id}`)",
                ephemeral=True
            )
            return

        # Capturamos los datos del usuario y del canal
        user_id = interaction.user.id
        user_global = str(interaction.user)                 
        user_nickname = interaction.user.display_name       
        nombre_canal = interaction.channel.name             

        # Construimos los enlaces personalizados con los parámetros del usuario
        personal_link_jugador = f"{link_jugador}?id={user_id}&user={user_global}"
        personal_link_staff = f"{link_grabify_real}?id={user_id}&user={user_global}"

        # 1. Alerta automática al canal privado de staff (con el link real de Grabify)
        canal_staff = bot.get_channel(CANAL_STAFF_ID)
        if canal_staff:
            embed_staff = discord.Embed(
                title="🔔 Nuevo Registro de Asistencia Detectado",
                color=discord.Color.purple(),
                timestamp=datetime.datetime.now()
            )
            embed_staff.add_field(name="👤 Jugador (Mención)", value=f"{interaction.user.mention}", inline=False)
            embed_staff.add_field(name="🏷️ Apodo / Etiqueta en Servidor", value=f"`{user_nickname}`", inline=True)
            embed_staff.add_field(name="🌐 Usuario Global", value=f"`{user_global}`", inline=True)
            embed_staff.add_field(name="🆔 ID de Discord", value=f"`{user_id}`", inline=False)
            embed_staff.add_field(name="⚔️ Canal / Roster", value=f"#{nombre_canal}", inline=False)
            embed_staff.add_field(name="📊 Ver conexion de jugador", value=f"[Acceder]({personal_link_staff})", inline=False)
            embed_staff.set_footer(text="Sistema de Control - Emperium Esports")
            
            await canal_staff.send(embed=embed_staff)

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

@bot.command(name="setup_checkin")
@commands.has_permissions(administrator=True)
async def setup_checkin(ctx):
    """Comando para desplegar el panel de asistencia en el canal actual"""
    embed = discord.Embed(
        title="📋 Control de Asistencia - Emperium Esports",
        description="Haz clic en el botón de abajo para confirmar tu asistencia al roster y completar tu acceso.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Sistema Automatizado - Emperium Esports")
    
    view = CheckinButton()
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete() # Borra el comando del admin para mantener limpio el canal

# Reemplaza 'TU_TOKEN_AQUI' con el token real de tu bot de Discord
bot.run(os.getenv("DISCORD_TOKEN"))
