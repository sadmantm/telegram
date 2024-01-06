from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import time
from telethon.tl.types import User, ChannelParticipantSelf, ChannelParticipantCreator
import os
import sys
import io

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
class TelegramBot:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_file = f"{phone}.session"
        self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)

    def connect(self):
        if os.path.exists(self.session_file):
            self.client.start()
        else:
            self.client.connect()
            if not self.client.is_user_authorized():
                self.client.send_code_request(self.phone)
                self.client.sign_in(self.phone, input('Digite o código:'))

    def get_my_groups(self):
        groups = []

        chats = self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=200,
            hash=0))

        for chat in chats.chats:
            try:
                if chat.megagroup == True:
                    groups.append(chat)
            except:
                continue

        print("Escolha o grupo de onde deseja extrair os membros:")
        for i, group in enumerate(groups):
            print(f"{i} - {group.title}")

        escolha = int(input("Digite o número correspondente ao grupo: "))
        grupo_origem = groups[escolha]

        return grupo_origem

    def choose_target_group(self):
        groups = []

        chats = self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=999,
            hash=0))

        for chat in chats.chats:
            try:
                if chat.megagroup == True:
                    groups.append(chat)
            except:
                continue

        print("Escolha o grupo para adicionar os membros:")
        for i, group in enumerate(groups):
            print(f"{i} - {group.title}")

        escolha = int(input("Digite o número correspondente ao grupo: "))
        grupo_alvo = groups[escolha]

        return grupo_alvo

    def get_members_of_group(self, target_group):
        all_participants = self.client.get_participants(
            target_group, aggressive=True)
        return all_participants

    def is_valid_member(self, member):
        # Verificar se o membro é um usuário real, não é um bot e não é restrito
        return isinstance(member, User) and not member.bot and not member.restricted

    def add_member_to_group(self, user, target_group):
        target_group_entity = InputPeerChannel(
            target_group.id, target_group.access_hash)

        try:
            print(f"Adicionando usuário {user.id} ao grupo...")
            user_to_add = InputPeerUser(user.id, user.access_hash)

            self.client(InviteToChannelRequest(
                target_group_entity, [user_to_add]))
            time.sleep(5)
            print("Usuário adicionado com sucesso!")
            return True

        except PeerFloodError:
            print("Erro de Flood. tentando novamente em 10 segundos")
            time.sleep(10)
            return False

        except UserPrivacyRestrictedError:
            print("Usuário não permite ser adicionado no grupo")
            time.sleep(20)
            return False

        except Exception as e:
            print(f"Erro ao adicionar usuário: {str(e)}")
            return False

    def confirm_add_members(self, count):
        print(f"Você está prestes a adicionar {count} membros ao grupo.")
        confirm = input("Deseja continuar? (Digite 'S' para sim ou 'N' para não): ").strip().lower()
        return confirm == 's'

# Exemplo de uso
if __name__ == "__main__":
    api_id = int(input('API ID: '))
    api_hash = input('API HASH: ')
    phone = input('TELEFONE: ')

    bot = TelegramBot(api_id, api_hash, phone)
    bot.connect()
    
    while True:  # Adiciona um loop para continuar selecionando grupos
        source_group = bot.get_my_groups()
        group_members = [member for member in bot.get_members_of_group(source_group) if bot.is_valid_member(member)]

        target_group = bot.choose_target_group()

        # Informa ao usuário quantos membros serão adicionados e pede confirmação
        print(f"\nVocê está prestes a adicionar {len(group_members)} membros ao grupo de destino.")
        if not bot.confirm_add_members(len(group_members)):
            print("Operação cancelada pelo usuário.")
            continue  # Retorna ao início do loop

        # Adiciona membros ao grupo de destino
        for member in group_members:
            bot.add_member_to_group(member, target_group)

        # Após adicionar membros, pergunta se deseja continuar
        again = input("Deseja adicionar membros a outro grupo? (Digite 'S' para sim ou 'N' para não): ").strip().lower()
        if again != 's':
            print("Operação finalizada. Encerrando o script.")
            break  # Encerra o loop e o script